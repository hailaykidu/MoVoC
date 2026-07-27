"""
tokenizer.py -- BPE training and MoVoC-Tok constrained-merge training.

Two things live here, both from the paper:

  Train_BPE(P, s_BPE)      Algorithm 1, Step 3. A plain byte-level BPE model
                           per language, trained on its corpus.

  Train_MoVoC_Model(V)     Algorithm 1, Step 6 -- MoVoC-Tok, Sec 3.3. Not the
                           Step 5 vocabulary handed to a stock tokenizer: the
                           merge process itself is constrained so no merge
                           unit crosses a morpheme boundary.

                               max_V sum_i log P(BPE(w_i; V, M_i))
                               s.t. no merge unit crosses M_i

                           Each word carries the boundary offsets implied by
                           its annotation, and a pair is counted toward merge
                           frequency only when both symbols fall inside the
                           same morpheme.

Encoding and decoding go through the trained tokenizer objects; the merge
tables are saved alongside so MoVoC-Tok segmentation is reproducible.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

from tokenizers import (Tokenizer, models, trainers, pre_tokenizers,
                        decoders, normalizers)

from .annotation import clean, segmentation_of

SPECIAL_TOKENS = ["<unk>", "<s>", "</s>", "<pad>", "<mask>"]
END = "</w>"


def corpus_lines(path: Path, max_lines: int | None):
    """Stream a corpus so a 1.6 GB file never lands in memory at once."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            line = line.strip()
            if line:
                yield line


def train_bpe(corpus: Path, vocab_size: int, out_dir: Path, lang: str,
              max_lines: int | None = None) -> Tokenizer:
    """Algorithm 1, Step 3: Train_BPE(P, s_BPE) for one language."""
    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    # NFC matches the corpus cleaning used elsewhere in this project; Ge'ez
    # script has composed forms that must normalize consistently.
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)
    tokenizer.decoder = decoders.ByteLevel()

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=SPECIAL_TOKENS,
        show_progress=True,
    )

    tokenizer.train_from_iterator(corpus_lines(corpus, max_lines), trainer=trainer)

    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(out_dir / f"bpe_{lang}.json"))

    vocab = tokenizer.get_vocab()
    print(f"[{lang}] trained: {len(vocab)} tokens -> {out_dir / f'bpe_{lang}.json'}")
    return tokenizer



def train_wordpiece(corpus: Path, vocab_size: int, out_dir: Path, lang: str,
                    max_lines: int | None = None) -> Tokenizer:
    """Train a WordPiece baseline (paper Sec 4.3).

    The paper analyses BPE and WordPiece as baseline subword tokenizers,
    both from the Hugging Face tokenizers library. Trained on the same
    corpus at the same vocabulary size as Train_BPE so the comparison is
    like-for-like; WordPiece uses whitespace pre-tokenization and its own
    continuing-subword prefix rather than byte-level encoding.
    """
    tokenizer = Tokenizer(models.WordPiece(unk_token="<unk>", max_input_chars_per_word=100))
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    tokenizer.decoder = decoders.WordPiece()

    trainer = trainers.WordPieceTrainer(
        vocab_size=vocab_size,
        special_tokens=SPECIAL_TOKENS,
        show_progress=True,
    )

    tokenizer.train_from_iterator(corpus_lines(corpus, max_lines), trainer=trainer)

    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(out_dir / f"wordpiece_{lang}.json"))

    vocab = tokenizer.get_vocab()
    print(f"[{lang}] wordpiece: {len(vocab)} tokens -> "
          f"{out_dir / f'wordpiece_{lang}.json'}")
    return tokenizer


def boundary_offsets(word: str, morphemes: list) -> set:
    """Character positions inside `word` where a morpheme boundary falls.

    Morphemes are matched left-to-right against the surface form. If they do
    not concatenate to the word (templatic morphology, fusion at the fidel
    boundary), we return an empty set: no reliable boundary, so no constraint
    is imposed for that word rather than a wrong one.
    """
    if not morphemes:
        return set()
    pos, cuts = 0, set()
    for m in morphemes:
        idx = word.find(m, pos)
        if idx < 0:
            return set()
        if idx > pos:              # unmatched material before this morpheme
            cuts.add(idx)
        pos = idx + len(m)
        cuts.add(pos)
    cuts.discard(len(word))
    return cuts


def load_constraints(paths: list) -> dict:
    """word -> set of interior boundary offsets, from the annotation files."""
    cons = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for entry in json.load(f):
                word, morphs = segmentation_of(entry)
                if not word or len(morphs) < 2:
                    continue
                cuts = boundary_offsets(word, morphs)
                if cuts:
                    cons[word] = cuts
    return cons


def word_frequencies(corpus: Path, max_lines: int | None) -> Counter:
    counts = Counter()
    with open(corpus, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            counts.update(line.split())
    return counts


def _admissible_pairs(symbols: list, cuts: set):
    """Yield (index, pair) for every adjacent pair not spanning a boundary."""
    offset = 0
    for i in range(len(symbols) - 1):
        nxt = offset + len(symbols[i])
        if not (cuts and nxt in cuts):
            yield i, (symbols[i], symbols[i + 1])
        offset = nxt


def learn_merges(word_freq: Counter, constraints: dict, num_merges: int,
                 min_freq: int = 2, verbose_every: int = 500) -> list:
    """Constrained BPE merge learning, incremental.

    Same result as rescanning every word each step, but maintains a running
    pair-frequency table plus a pair -> {words containing it} index, so a
    merge only touches the words that actually contain the merged pair.
    That turns O(types x merges) into something proportional to the work
    actually done, which is what makes full-corpus training feasible.
    """
    words = {}
    for w, f in word_freq.items():
        if f < min_freq or not w:
            continue
        words[w] = [c for c in w] + [END]

    pair_freq = Counter()
    pair_words = defaultdict(set)
    for w, symbols in words.items():
        freq = word_freq[w]
        cuts = constraints.get(w)
        for _, pair in _admissible_pairs(symbols, cuts):
            pair_freq[pair] += freq
            pair_words[pair].add(w)

    merges = []
    for step in range(num_merges):
        if not pair_freq:
            break
        # Ties are common (hundreds of pairs share a frequency at any given
        # step), so break them on the pair itself. Without this the merge
        # table depends on dict iteration order and is not reproducible.
        (a, b), freq = max(pair_freq.items(), key=lambda kv: (kv[1], kv[0]))
        if freq < min_freq:
            break
        merges.append((a, b))
        merged = a + b

        for w in list(pair_words.get((a, b), ())):
            symbols = words.get(w)
            if symbols is None:
                continue
            wfreq = word_freq[w]
            cuts = constraints.get(w)

            # Withdraw this word's current pair contributions...
            for _, pair in _admissible_pairs(symbols, cuts):
                pair_freq[pair] -= wfreq
                if pair_freq[pair] <= 0:
                    del pair_freq[pair]
                s = pair_words.get(pair)
                if s is not None:
                    s.discard(w)

            out, i = [], 0
            while i < len(symbols):
                if i < len(symbols) - 1 and symbols[i] == a and symbols[i + 1] == b:
                    out.append(merged)
                    i += 2
                else:
                    out.append(symbols[i])
                    i += 1
            words[w] = out

            # ...and re-add them for the rewritten symbol sequence.
            for _, pair in _admissible_pairs(out, cuts):
                pair_freq[pair] += wfreq
                pair_words[pair].add(w)

        pair_freq.pop((a, b), None)
        pair_words.pop((a, b), None)

        if verbose_every and (step + 1) % verbose_every == 0:
            print(f"    merge {step + 1}/{num_merges}: {a!r}+{b!r} (freq {freq})",
                  flush=True)

    return merges




def save_merges(merges: list, path: Path) -> None:
    """Persist a MoVoC-Tok merge table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("#version: movoc-tok constrained-merge BPE\n")
        for a, b in merges:
            f.write(f"{a} {b}\n")


def load_merges(path: Path) -> dict:
    """Read a merge table into {(a, b): rank}."""
    ranks = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split(" ")
            if len(parts) == 2:
                ranks[(parts[0], parts[1])] = len(ranks)
    return ranks


def encode(word: str, ranks: dict) -> list:
    """Apply merges to one word, lowest rank first (standard BPE inference)."""
    symbols = [c for c in word] + [END]
    while len(symbols) > 1:
        best, best_rank = None, None
        for i in range(len(symbols) - 1):
            r = ranks.get((symbols[i], symbols[i + 1]))
            if r is not None and (best_rank is None or r < best_rank):
                best, best_rank = i, r
        if best is None:
            break
        symbols[best:best + 2] = [symbols[best] + symbols[best + 1]]
    return symbols


def decode(tokens: list) -> str:
    """Inverse of encode: concatenate, dropping the end-of-word marker."""
    return "".join(t[:-len(END)] if t.endswith(END) else t for t in tokens)
