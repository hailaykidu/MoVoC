"""
create_vocab.py

extract_morphemes(): frequency-based morpheme extraction from a corpus,
per the MoVoC paper's Algorithm 1, Step 4:

    "extract_morphemes(P, s_morpheme) refers to a procedure that performs
    frequency-based morpheme extraction from a corpus that has already
    been segmented using a rule-based morphological analyzer... All
    resulting morphemes across the corpus are collected, and their
    frequencies are computed. The morphemes are sorted by descending
    frequency, and the top s_morpheme morphemes are selected."

Uses movoc.segmenter.MorphemeSegmenter (see that module's docstring for
why this is a rule-based stripper rather than HornMorpho, as originally
planned).
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from movoc.segmenter import MorphemeSegmenter


def extract_morphemes(corpus_path: str, language: str, k: int, max_lines: int | None = None) -> list:
    segmenter = MorphemeSegmenter(language)
    counts = Counter()

    with open(corpus_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            for word in line.strip().split():
                seg = segmenter.segment_word(word)
                counts.update(seg.morphemes())

    return [morph for morph, _freq in counts.most_common(k)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--k", type=int, required=True, help="number of top morphemes to keep")
    parser.add_argument("--max-lines", type=int, default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    print(f"--- extracting top-{args.k} morphemes for {args.language} ---")
    morphemes = extract_morphemes(args.corpus, args.language, args.k, args.max_lines)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for m in morphemes:
            f.write(m + "\n")

    print(f"  wrote {len(morphemes)} morphemes to {out_path}")


if __name__ == "__main__":
    main()
