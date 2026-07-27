"""
build_vocab.py -- Algorithm 1, Steps 4 and 5.

Step 4: Extract Morphemes
    V_morpheme,am <- extract_morphemes(P_am, s_morpheme)
    V_morpheme,ti <- extract_morphemes(P_ti, s_morpheme)

    "extract_morphemes(P, s_morpheme) ... performs frequency-based morpheme
    extraction from a corpus that has already been segmented using a
    rule-based morphological analyzer. All resulting morphemes across the
    corpus are collected, and their frequencies are computed. The morphemes
    are sorted by descending frequency, and the top s_morpheme morphemes are
    selected."

Step 5: Merge All Vocabularies
    V_MoVoC <- V_BPE,am u V_BPE,ti u V_morpheme,am u V_morpheme,ti

Morphemes come from the post-edited/annotated morpheme sets in
data/morphemes/. Where a language has fewer than s_morpheme distinct
morphemes available, every morpheme it has is taken -- Top-k over a set
smaller than k is that whole set.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

# Placeholders used across the annotation files to mean "no morpheme here".
EMPTY = {"", "-", "–", "—", "_", "None", "null"}

# Field names differ between the Amharic file (capitalized, five-way) and the
# hand-annotated sets (lowercase, three- or four-way).
FIELDS = ("Prefix", "Root", "Suffix", "Infix", "Clitic",
          "prefix", "root", "suffix", "infix", "clitic")


def morphemes_of(entry: dict) -> list:
    """Every non-placeholder morpheme in one annotation record."""
    out = []
    for key in FIELDS:
        if key not in entry:
            continue
        val = entry[key]
        if val is None:
            continue
        # Strip whitespace on both sides of the affix hyphens too: some gold
        # entries carry a trailing space (e.g. "ዘይ ") that would otherwise
        # make the morpheme a distinct, unmatchable token.
        val = str(val).strip().strip("-").strip("–").strip()
        if val and val not in EMPTY:
            out.append(val)
    return out


def extract_morphemes(path: Path, k: int) -> tuple:
    """Algorithm 1, Step 4: frequency-rank morphemes, take the top k."""
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)

    counts = Counter()
    for entry in entries:
        counts.update(morphemes_of(entry))

    top = [m for m, _ in counts.most_common(k)]
    return top, len(counts), len(entries)


def main():
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Algorithm 1 Steps 4-5")
    p.add_argument("--amharic-morphemes", type=Path,
                   default=here / "data/morphemes/amharic_morphemes.json")
    p.add_argument("--tigrinya-morphemes", type=Path,
                   default=here / "data/morphemes/Tigriyna_Morphem.json")
    p.add_argument("--vocab-dir", type=Path, default=here / "vocab")
    args = p.parse_args()

    config = json.load(open(args.vocab_dir / "bpe_config.json", encoding="utf-8"))
    s_morpheme = config["s_morpheme"]

    print("Algorithm 1, Step 4 -- extract morphemes "
          f"(s_morpheme = {s_morpheme} per language)")

    v_morph = {}
    for lang, path in (("amharic", args.amharic_morphemes),
                       ("tigrinya", args.tigrinya_morphemes)):
        top, available, n_entries = extract_morphemes(path, s_morpheme)
        v_morph[lang] = top
        note = "" if available >= s_morpheme else \
               f"  (only {available} distinct morphemes exist; all taken)"
        print(f"  {lang:9} {n_entries:7} entries -> {available:6} distinct "
              f"-> selected {len(top):6}{note}")

    print("\nAlgorithm 1, Step 5 -- merge all vocabularies")
    v_bpe = {}
    for lang in ("amharic", "tigrinya"):
        toks = [l.rstrip("\n") for l in
                open(args.vocab_dir / f"vocab_bpe_{lang}.txt", encoding="utf-8")]
        v_bpe[lang] = toks
        print(f"  V_BPE,{lang[:2]}      = {len(toks):6}")
    for lang in ("amharic", "tigrinya"):
        print(f"  V_morpheme,{lang[:2]} = {len(v_morph[lang]):6}")

    # Union, per Step 5. Order is deterministic: BPE first (both languages),
    # then morphemes, each preserving its own rank order.
    merged = []
    seen = set()
    for group in (v_bpe["amharic"], v_bpe["tigrinya"],
                  v_morph["amharic"], v_morph["tigrinya"]):
        for tok in group:
            if tok not in seen:
                seen.add(tok)
                merged.append(tok)

    total_before = sum(len(g) for g in
                       (v_bpe["amharic"], v_bpe["tigrinya"],
                        v_morph["amharic"], v_morph["tigrinya"]))
    print(f"\n  sum of parts   = {total_before}")
    print(f"  V_MoVoC        = {len(merged)}  "
          f"({total_before - len(merged)} overlapping tokens collapsed)")

    out = args.vocab_dir / "vocab_movoc.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(merged) + "\n")

    meta = dict(config)
    meta.update({
        "v_bpe_amharic": len(v_bpe["amharic"]),
        "v_bpe_tigrinya": len(v_bpe["tigrinya"]),
        "v_morpheme_amharic": len(v_morph["amharic"]),
        "v_morpheme_tigrinya": len(v_morph["tigrinya"]),
        "v_movoc": len(merged),
    })
    with open(args.vocab_dir / "movoc_config.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\nStep 7 -- returned V_MoVoC: {out}")


if __name__ == "__main__":
    main()
