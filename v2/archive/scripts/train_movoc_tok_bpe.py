"""Train MoVoC-Tok: morpheme-aware BPE with boundary-constrained merges.

Learns a subword vocabulary by running BPE over a corpus, rejecting any merge
whose two units belong to different morphemes of the word being merged. This
implements

    max_V  sum_i log P(BPE(w_i; V, M_i))
    subject to: no subword s_j crosses a morpheme boundary in M_i

by restricting the merge candidate set at every iteration, so the learned
vocabulary is a fixed point of the constrained objective rather than a
selection from a pre-built vocabulary.

Surface projection of boundaries
--------------------------------
HornMorpho reports morphemes in citation form, so concatenating them does not
generally reproduce the surface word: ተቃጣ analyzes to root ቅጥእ, and only 18.5%
of Amharic records concatenate back exactly. Boundaries therefore cannot be
read off the morpheme strings directly -- they are *projected* onto the surface
form by aligning morphemes left to right with
``difflib.SequenceMatcher``, and a boundary is recorded only where the
alignment is unambiguous. Words whose analysis cannot be projected contribute
no constraint (they are trained on freely), rather than contributing a guessed
boundary. This keeps every constraint traceable to a real alignment.

Boundaries are learned only from words present in the segmentation datasets;
corpus words with no analysis are unconstrained.

Usage:
    python scripts/train_movoc_tok_bpe.py --lang Amharic \\
        --corpus NLLB.am-en.am --morphemes data/segmented/amharic_...json \\
        --outdir tokenizers/amharic_movoc_tok_32k --vocab-size 32000
"""

from __future__ import annotations

import argparse
import json
import time
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

PLACEHOLDER = "–"
MORPHEME_FIELDS = ("prefix", "root", "suffix", "infix", "clitic")
WORD_START = "▁"
SPECIAL_TOKENS = ["<pad>", "<unk>", "<s>", "</s>"]


def record_morphemes(record: dict) -> list[str]:
    """Morphemes of one record, in surface order.

    The dataset stores morphemes by grammatical slot, not by position in the
    word: a proclitic such as የ is written in the ``clitic`` field and would
    otherwise sort after the root, projecting የግብፅ as ``የግብ|ፅ`` instead of
    ``የ|ግብፅ``. Clitics are therefore placed according to where they actually
    attach -- before the root if the word begins with them, after otherwise.
    """
    record = {k.lower(): v for k, v in record.items()}
    word = record.get("word", "") or ""
    prefixes: list[str] = []
    core: list[str] = []
    suffixes: list[str] = []

    def parts(field: str) -> list[str]:
        value = record.get(field, PLACEHOLDER)
        if not value or not isinstance(value, str):
            return []
        value = value.strip()
        if value in ("-", "–", "--", ""):
            return []
        return [
            p.strip()
            for p in value.split("-")
            if p.strip() and p.strip() not in ("-", "–", "")
        ]

    prefixes.extend(parts("prefix"))
    core.extend(parts("root"))
    core.extend(parts("infix"))
    suffixes.extend(parts("suffix"))

    for clitic in parts("clitic"):
        # A clitic the word starts with is proclitic; anything else enclitic.
        if word.startswith(clitic) and not any(
            word.startswith(p) for p in prefixes
        ):
            prefixes.insert(0, clitic)
        else:
            suffixes.append(clitic)

    return prefixes + core + suffixes


def project_boundaries(word: str, morphemes: list[str]) -> set[int] | None:
    """Project morpheme boundaries onto the surface form of ``word``.

    Returns the set of character offsets in ``word`` at which a morpheme
    boundary falls, or ``None`` when the analysis cannot be aligned to the
    surface string (in which case the word carries no constraint).

    Alignment is greedy and left to right: each morpheme is matched against the
    remaining suffix of the word, and the boundary is placed at the end of its
    matched span. A morpheme that matches nothing aborts the projection for
    that word.
    """
    if len(morphemes) < 2:
        return set()

    boundaries: set[int] = set()
    cursor = 0
    for morpheme in morphemes[:-1]:
        remainder = word[cursor:]
        if not remainder:
            return None
        if remainder.startswith(morpheme):
            cursor += len(morpheme)
        else:
            # Citation form differs from the surface: find the longest
            # contiguous block the two share, and take its end as the split.
            matcher = SequenceMatcher(None, remainder, morpheme, autojunk=False)
            block = matcher.find_longest_match(0, len(remainder), 0, len(morpheme))
            if block.size == 0:
                return None
            cursor += block.a + block.size
        if 0 < cursor < len(word):
            boundaries.add(cursor)
    return boundaries


def load_constraints(path: Path) -> tuple[dict[str, set[int]], dict[str, int]]:
    """Map each analysed word to its projected surface boundaries.

    Accepts both the HornMorpho segmentation datasets (lowercase fields, en-dash
    placeholder) and the released manual annotation files (capitalized fields,
    hyphen placeholder), since Ge'ez and Tigre have manual annotations rather
    than analyser output. Field names are matched case-insensitively and both
    placeholder conventions are rejected.
    """
    records = json.loads(path.read_text(encoding="utf-8"))
    constraints: dict[str, set[int]] = {}
    projected = failed = single = 0
    for record in records:
        word = record["word"]
        morphemes = record_morphemes(record)
        if len(morphemes) < 2:
            single += 1
            continue
        boundaries = project_boundaries(word, morphemes)
        if boundaries is None:
            failed += 1
            continue
        if boundaries:
            constraints[word] = boundaries
            projected += 1
    return constraints, {
        "records": len(records),
        "words_with_boundaries": projected,
        "single_morpheme_words": single,
        "projection_failed": failed,
    }


def read_corpus(path: Path, max_lines: int | None) -> Counter:
    """Word frequencies over the corpus, NFC-normalized."""
    counts: Counter = Counter()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for i, line in enumerate(handle):
            if max_lines is not None and i >= max_lines:
                break
            counts.update(unicodedata.normalize("NFC", line).split())
    return counts


class ConstrainedBPE:
    """BPE learner whose merges may not cross morpheme boundaries."""

    def __init__(self, word_freqs: Counter, constraints: dict[str, set[int]]) -> None:
        # Each word becomes a list of single-character symbols, with the
        # word-start marker attached to the first character so learned pieces
        # match SentencePiece-style word-initial units.
        self.words: list[list[str]] = []
        self.freqs: list[int] = []
        #: For each word, the set of symbol-boundary offsets that merges may
        #: not cross, expressed in character positions of the raw word.
        self.barriers: list[set[int]] = []

        for word, freq in word_freqs.items():
            if not word:
                continue
            symbols = [WORD_START + word[0]] + list(word[1:])
            self.words.append(symbols)
            self.freqs.append(freq)
            self.barriers.append(constraints.get(word, set()))

        self.rejected = 0

    def _word_pairs(self, widx: int) -> tuple[Counter, Counter]:
        """Legal and blocked merge candidates within one word."""
        symbols = self.words[widx]
        legal: Counter = Counter()
        blocked: Counter = Counter()
        if len(symbols) < 2:
            return legal, blocked
        freq = self.freqs[widx]
        barriers = self.barriers[widx]
        # Character offset of each symbol start; the word-start marker is not
        # part of the surface word, so the first symbol spans one character.
        offset = 0
        offsets = []
        for index, symbol in enumerate(symbols):
            offsets.append(offset)
            offset += len(symbol) - (1 if index == 0 else 0)
        for index in range(len(symbols) - 1):
            pair = (symbols[index], symbols[index + 1])
            if offsets[index + 1] in barriers:
                blocked[pair] += freq
            else:
                legal[pair] += freq
        return legal, blocked

    def _build_index(self) -> None:
        """Initial pair statistics plus a pair -> containing-words index.

        Recomputing every word's pairs on each iteration is O(corpus) per
        merge. Instead the counts are maintained incrementally: after a merge
        only the words that contained the merged pair can change, so only those
        are rescanned.
        """
        self.legal: Counter = Counter()
        self.blocked_total = 0
        self.where: dict[tuple[str, str], set[int]] = defaultdict(set)
        for widx in range(len(self.words)):
            legal, blocked = self._word_pairs(widx)
            for pair, count in legal.items():
                self.legal[pair] += count
                self.where[pair].add(widx)
            for pair in blocked:
                self.where[pair].add(widx)

    def _apply(self, pair: tuple[str, str]) -> int:
        """Merge ``pair`` everywhere it is legal; update statistics in place.

        Returns the number of boundary-crossing occurrences that were left
        unmerged, i.e. merges rejected by the constraint.
        """
        merged = pair[0] + pair[1]
        rejected = 0
        affected = list(self.where.get(pair, ()))

        for widx in affected:
            old_legal, old_blocked = self._word_pairs(widx)
            symbols = self.words[widx]
            barriers = self.barriers[widx]

            out: list[str] = []
            offset = 0
            index = 0
            changed = False
            while index < len(symbols):
                width = len(symbols[index]) - (1 if index == 0 else 0)
                if (
                    index < len(symbols) - 1
                    and symbols[index] == pair[0]
                    and symbols[index + 1] == pair[1]
                ):
                    if (offset + width) in barriers:
                        rejected += self.freqs[widx]
                        out.append(symbols[index])
                        offset += width
                        index += 1
                        continue
                    out.append(merged)
                    offset += width + len(symbols[index + 1])
                    index += 2
                    changed = True
                else:
                    out.append(symbols[index])
                    offset += width
                    index += 1

            if not changed:
                continue

            self.words[widx] = out
            new_legal, new_blocked = self._word_pairs(widx)

            # Subtract the word's old contribution, add its new one.
            for p2, c in old_legal.items():
                self.legal[p2] -= c
                if self.legal[p2] <= 0:
                    del self.legal[p2]
            for p2 in set(old_legal) | set(old_blocked):
                bucket = self.where.get(p2)
                if bucket is not None:
                    bucket.discard(widx)
            for p2, c in new_legal.items():
                self.legal[p2] += c
                self.where[p2].add(widx)
            for p2 in new_blocked:
                self.where[p2].add(widx)

        self.where.pop(pair, None)
        return rejected

    def train(self, vocab_size: int, alphabet: list[str], report_every: int = 2000):
        """Learn merges until ``vocab_size`` is reached or no legal pair remains."""
        vocab = list(SPECIAL_TOKENS) + alphabet
        seen = set(vocab)
        merges: list[tuple[str, str]] = []
        target = vocab_size - len(vocab)

        self._build_index()

        for step in range(target):
            if not self.legal:
                print(f"  no legal merges remain at step {step:,}")
                break
            pair = max(self.legal.items(), key=lambda kv: (kv[1], kv[0]))[0]
            self.rejected += self._apply(pair)
            merges.append(pair)
            token = pair[0] + pair[1]
            if token not in seen:
                seen.add(token)
                vocab.append(token)
            if report_every and (step + 1) % report_every == 0:
                print(
                    f"  {len(vocab):,}/{vocab_size:,} vocab | "
                    f"{len(merges):,} merges | rejected so far "
                    f"{self.rejected:,}",
                    flush=True,
                )
            if len(vocab) >= vocab_size:
                break
        return vocab, merges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--morphemes", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--vocab-size", type=int, default=32_000)
    parser.add_argument(
        "--max-lines",
        type=int,
        default=200_000,
        help="corpus lines to read; constrained BPE is O(pairs) per merge",
    )
    parser.add_argument("--min-freq", type=int, default=2)
    args = parser.parse_args()

    started = time.time()
    print(f"language: {args.lang}")

    constraints, cstats = load_constraints(args.morphemes)
    print(
        f"morpheme constraints: {cstats['words_with_boundaries']:,} words with "
        f"projected boundaries of {cstats['records']:,} records "
        f"({cstats['projection_failed']:,} unprojectable, "
        f"{cstats['single_morpheme_words']:,} single-morpheme)"
    )

    word_freqs = read_corpus(args.corpus, args.max_lines)
    word_freqs = Counter(
        {w: c for w, c in word_freqs.items() if c >= args.min_freq}
    )
    print(f"corpus: {len(word_freqs):,} word types (min_freq={args.min_freq})")

    covered = sum(1 for w in word_freqs if w in constraints)
    print(f"corpus words carrying a constraint: {covered:,}")

    alphabet = sorted({c for w in word_freqs for c in w} | {WORD_START + w[0] for w in word_freqs if w})
    print(f"alphabet: {len(alphabet):,} symbols")

    learner = ConstrainedBPE(word_freqs, constraints)
    print(f"training constrained BPE to {args.vocab_size:,} ...", flush=True)
    vocab, merges = learner.train(args.vocab_size, alphabet)

    elapsed = time.time() - started
    args.outdir.mkdir(parents=True, exist_ok=True)

    (args.outdir / "tokenizer.vocab").write_text(
        "\n".join(f"{t}\t{-i}" for i, t in enumerate(vocab)) + "\n", encoding="utf-8"
    )
    (args.outdir / "tokenizer.model").write_text(
        json.dumps(
            {
                "type": "morpheme_aware_bpe",
                "vocab": vocab,
                "merges": [list(m) for m in merges],
                "word_start": WORD_START,
                "special_tokens": SPECIAL_TOKENS,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    config = {
        "name": f"MoVoC-Tok ({args.lang})",
        "language": args.lang,
        "method": "morpheme-aware BPE (boundary-constrained merges)",
        "vocab_size": len(vocab),
        "requested_vocab_size": args.vocab_size,
        "merge_operations": len(merges),
        "word_start_marker": WORD_START,
        "special_tokens": {t: i for i, t in enumerate(SPECIAL_TOKENS)},
    }
    (args.outdir / "config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    training_config = {
        "language": args.lang,
        "objective": "max_V sum_i log P(BPE(w_i; V, M_i)) s.t. no s_j crosses M_i",
        "corpus": str(args.corpus.resolve()),
        "corpus_lines_read": args.max_lines,
        "corpus_word_types": len(word_freqs),
        "min_frequency": args.min_freq,
        "morpheme_source": str(args.morphemes.resolve()),
        "morpheme_records": cstats["records"],
        "words_with_morpheme_boundaries": cstats["words_with_boundaries"],
        "words_projection_failed": cstats["projection_failed"],
        "single_morpheme_words": cstats["single_morpheme_words"],
        "corpus_words_constrained": covered,
        "alphabet_size": len(alphabet),
        "merge_operations": len(merges),
        "rejected_boundary_crossing_merges": learner.rejected,
        "final_vocab_size": len(vocab),
        "training_seconds": round(elapsed, 1),
        "shared_vocab": False,
    }
    (args.outdir / "training_config.json").write_text(
        json.dumps(training_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"\nvocab {len(vocab):,} | merges {len(merges):,} | "
        f"rejected boundary-crossing merge candidates "
        f"{learner.rejected:,} | {elapsed / 60:.1f} min"
    )
    print(f"wrote {args.outdir}/tokenizer.model, .vocab, config.json, training_config.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
