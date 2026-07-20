"""
run_intrinsic_eval.py

Compares MoVoC-Tok (our rule-based segmenter) against a plain BPE baseline
using MorphScore and Boundary Precision (movoc.metrics), against the
project's one genuinely real gold-standard test set: the 206
manually-segmented Tigrinya words in
../data/ሃይላይ_ኪዱ_Tigriyna_Morphem.json.

This is the only language in this project where we have real expert
gold data to evaluate against -- Amharic/Tigre/Ge'ez have no equivalent
gold set here, so no fabricated "results" are reported for those.

USAGE
    python run_intrinsic_eval.py --bpe-vocab-size 1400 --max-lines 200000
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from train_bpe import train_bpe
from movoc.segmenter import MorphemeSegmenter
from movoc.metrics import boundary_precision, morphscore, renyi_entropy

GOLD_PATH = Path(__file__).resolve().parent.parent / "data" / "ሃይላይ_ኪዱ_Tigriyna_Morphem.json"
CORPUS_PATH = (
    Path(__file__).resolve().parents[5] / "MoVoC_Tok" / "02_cleaning" / "corpus_clean" / "tigrinya.txt"
)


def load_gold():
    with open(GOLD_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    words, gold_triples = [], []
    for e in entries:
        prefix = "" if e["prefix"] == "-" else e["prefix"].strip("-")
        suffix = "" if e["suffix"] == "-" else e["suffix"].strip("-")
        words.append(e["word"])
        gold_triples.append((prefix, e["root"], suffix))
    return words, gold_triples


def bpe_triples(tokenizer, words):
    """Approximate a (prefix, root, suffix) triple from a BPE tokenizer's
    subword split: first piece = prefix-like, last piece = suffix-like,
    middle (possibly multi-piece) joined = root -- just enough structure
    to compute boundary positions comparably to the gold/MoVoC triples.
    """
    triples = []
    for w in words:
        pieces = tokenizer.encode(w).tokens
        if len(pieces) <= 1:
            triples.append(("", w, ""))
        elif len(pieces) == 2:
            triples.append(("", pieces[0], pieces[1]))
        else:
            triples.append((pieces[0], "".join(pieces[1:-1]), pieces[-1]))
    return triples


def movoc_triples(segmenter, words):
    return [(s.prefix, s.root, s.suffix) for s in (segmenter.segment_word(w) for w in words)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bpe-vocab-size", type=int, default=1400)
    parser.add_argument("--max-lines", type=int, default=200_000)
    parser.add_argument("--out", default="../results/intrinsic_eval_report.json")
    args = parser.parse_args()

    print(f"--- loading gold Tigrinya morpheme set from {GOLD_PATH} ---")
    words, gold = load_gold()
    print(f"  {len(words)} gold entries")

    print(f"--- training plain BPE baseline (vocab_size={args.bpe_vocab_size}) ---")
    bpe_tokenizer = train_bpe(str(CORPUS_PATH), args.bpe_vocab_size, args.max_lines)

    print("--- running MoVoC-Tok (rule-based segmenter) ---")
    segmenter = MorphemeSegmenter("tigrinya")
    movoc_pred = movoc_triples(segmenter, words)

    print("--- running plain BPE baseline ---")
    bpe_pred = bpe_triples(bpe_tokenizer, words)

    report = {
        "gold_set": str(GOLD_PATH),
        "n_words": len(words),
        "MoVoC-Tok": {
            "boundary_precision": boundary_precision(movoc_pred, gold),
            "morphscore": morphscore(movoc_pred, gold),
        },
        "BPE": {
            "boundary_precision": boundary_precision(bpe_pred, gold),
            "morphscore": morphscore(bpe_pred, gold),
        },
    }

    movoc_token_freqs = Counter()
    for p in movoc_pred:
        movoc_token_freqs.update([m for m in p if m])
    bpe_token_freqs = Counter()
    for w in words:
        bpe_token_freqs.update(bpe_tokenizer.encode(w).tokens)
    report["MoVoC-Tok"]["renyi_entropy"] = renyi_entropy(movoc_token_freqs)
    report["BPE"]["renyi_entropy"] = renyi_entropy(bpe_token_freqs)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n=== Results (Tigrinya, 206-word gold set) ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    main()
