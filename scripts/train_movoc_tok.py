"""
train_movoc_tok.py -- Algorithm 1, Step 6: Train_MoVoC_Model(V_MoVoC).

This implements MoVoC-Tok (paper Sec 3.3): morpheme-aware subword
segmentation. It is deliberately *not* "the Step 5 vocabulary handed to a
stock BPE tokenizer" -- a conventional BPE trained on V_MoVoC still learns
data-driven merges that can join subwords across a morpheme boundary.

Sec 3.3 constrains the merge process itself:

    max_V  sum_i log P(BPE(w_i; V, M_i))    s.t. no merge unit crosses M_i

i.e. for a word w_i with known morpheme segmentation M_i, a merge candidate
(a, b) is admissible only if the merged unit a+b lies wholly inside one
morpheme of M_i. Merges spanning a boundary are never counted and so never
enter the merge table.

Implementation: standard BPE merge learning over a word-frequency table,
with one change -- each word carries its morpheme boundary offsets, and a
pair is only counted toward merge frequency when both symbols fall inside
the same morpheme. Everything else (greedy highest-frequency merge, apply,
repeat) is ordinary BPE.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

EMPTY = {"", "-", "–", "—", "_", "None", "null"}
FIELDS_ORDERED = [
    ("Prefix", "Root", "Infix", "Suffix", "Clitic"),
    ("prefix", "root", "infix", "suffix", "clitic"),
]
END = "</w>"


def clean(val) -> str:
    if val is None:
        return ""
    v = str(val).strip().strip("-").strip("–").strip()
    return "" if v in EMPTY else v


def segmentation_of(entry: dict) -> tuple:
    """(word, [morpheme, ...]) in surface order, or (word, []) if unusable."""
    word = clean(entry.get("word") or entry.get("Word"))
    if not word:
        return "", []
    for scheme in FIELDS_ORDERED:
        if any(k in entry for k in scheme):
            parts = [clean(entry.get(k)) for k in scheme]
            return word, [p for p in parts if p]
    return word, []


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


def main():
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Algorithm 1 Step 6: MoVoC-Tok")
    p.add_argument("--amharic-corpus", type=Path, required=True)
    p.add_argument("--tigrinya-corpus", type=Path, required=True)
    p.add_argument("--vocab-dir", type=Path, default=here / "vocab")
    p.add_argument("--max-lines", type=int, default=300_000,
                   help="lines read per corpus for merge learning; "
                        "0 or negative means the full corpus")
    p.add_argument("--min-freq", type=int, default=2)
    args = p.parse_args()
    if args.max_lines is not None and args.max_lines <= 0:
        args.max_lines = None          # full corpus

    config = json.load(open(args.vocab_dir / "movoc_config.json", encoding="utf-8"))
    print("Algorithm 1, Step 6 -- Train_MoVoC_Model(V_MoVoC)")
    print(f"  V_MoVoC = {config['v_movoc']} tokens")

    data = here / "data/morphemes"
    langs = {
        "amharic": (args.amharic_corpus,
                    [data / "amharic_morphemes.json"]),
        "tigrinya": (args.tigrinya_corpus,
                     [data / "tigrinya_morphemes.json"]),
    }

    all_merges = {}
    for lang, (corpus, ann) in langs.items():
        print(f"\n  [{lang}]")
        cons = load_constraints(ann)
        print(f"    morpheme-boundary constraints: {len(cons)} words")
        wf = word_frequencies(corpus, args.max_lines)
        print(f"    word types (freq >= {args.min_freq}): "
              f"{sum(1 for f in wf.values() if f >= args.min_freq)}")
        n_merges = config["s_bpe"]
        merges = learn_merges(wf, cons, n_merges, args.min_freq)
        all_merges[lang] = merges
        print(f"    learned {len(merges)} constrained merges")

        out = args.vocab_dir / f"movoc_tok_merges_{lang}.txt"
        with open(out, "w", encoding="utf-8") as f:
            f.write("#version: movoc-tok constrained-merge BPE\n")
            for a, b in merges:
                f.write(f"{a} {b}\n")
        print(f"    -> {out}")

    meta = dict(config)
    meta["movoc_tok"] = {
        lang: {"merges": len(m)} for lang, m in all_merges.items()
    }
    meta["movoc_tok_max_lines"] = args.max_lines
    with open(args.vocab_dir / "movoc_config.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("\nStep 6 complete -- merges constrained to respect morpheme boundaries.")


if __name__ == "__main__":
    main()
