"""
evaluate.py -- intrinsic evaluation (paper Sec 6).

  Boundary Precision (Nouri and Yangarber, 2016) -- of the boundaries a
  tokenizer predicts, what fraction are real gold morpheme boundaries.

  MorphScore (Arnett and Bergen, 2025) -- of the gold boundaries, what
  fraction the tokenizer also marks. Words left whole are excluded rather
  than scored zero.

  Renyi entropy -- vocabulary consistency over the token distribution the
  tokenizer produces on the evaluation words.

Gold sets are the held-out Tigrinya standard and the manual Ge'ez and Tigre
annotations; see movoc/annotation.py.
"""

import argparse
from collections import Counter
from pathlib import Path

from movoc import annotation, io, tokenizer
from movoc.metrics import boundary_precision, morphscore, renyi_entropy
from movoc.utils import gold_triples

END = tokenizer.END


def predicted_triple(word: str, ranks: dict) -> tuple:
    """Convert a tokenization into a (prefix, root, suffix)-shaped triple.

    The metrics compare boundary *offsets*, so what matters is where the
    cuts fall, not which slot they land in. A word tokenized into n pieces
    contributes its first cut and last cut; words left whole contribute no
    boundary, which is what MorphScore treats as unsegmented.
    """
    toks = [t[:-len(END)] if t.endswith(END) else t for t in tokenizer.encode(word, ranks)]
    toks = [t for t in toks if t]
    if len(toks) <= 1:
        return ("", word, "")
    if len(toks) == 2:
        return (toks[0], toks[1], "")
    return (toks[0], "".join(toks[1:-1]), toks[-1])


def token_counter(words, ranks) -> Counter:
    c = Counter()
    for w in words:
        c.update(t for t in tokenizer.encode(w, ranks))
    return c


def evaluate(lang: str, gold_path: Path, movoc_merges: Path,
             bpe_merges: Path, alpha: float) -> dict:
    gold = gold_triples(gold_path)
    if not gold:
        return {"language": lang, "error": "no scorable gold entries"}
    words = [w for w, _ in gold]
    gold_tr = [t for _, t in gold]

    row = {"language": lang, "gold_words": len(gold)}
    for name, merge_path in (("movoc_tok", movoc_merges), ("bpe", bpe_merges)):
        if not merge_path.exists():
            continue
        ranks = tokenizer.load_merges(merge_path)
        pred = [predicted_triple(w, ranks) for w in words]
        counts = token_counter(words, ranks)
        segmented = sum(1 for p in pred if p[0] or p[2])
        row[name] = {
            "merges": len(ranks),
            "boundary_precision": round(boundary_precision(pred, gold_tr), 4),
            "morphscore": round(morphscore(pred, gold_tr), 4),
            "renyi_entropy": round(renyi_entropy(counts, alpha), 4),
            "distinct_tokens": len(counts),
            "segmented_words": segmented,
        }
    return row




def main():
    p = argparse.ArgumentParser(description="Intrinsic evaluation")
    p.add_argument("--alpha", type=float, default=2.0,
                   help="Renyi entropy order")
    p.add_argument("-o", "--out", type=Path,
                   default=io.RESULTS / "intrinsic_eval.json")
    args = p.parse_args()

    rows = []
    for lang, gold in annotation.GOLD_SOURCES.items():
        if not gold.exists():
            continue
        rows.append(evaluate(
            lang, gold,
            io.MODELS / f"movoc_tok_merges_{lang}.txt",
            io.MODELS / f"bpe_merges_{lang}.txt",
            args.alpha))

    io.write_json(args.out, {"alpha": args.alpha, "results": rows})

    hdr = (f"{'language':10} {'gold':>6} {'arm':10} {'BoundPrec':>10} "
           f"{'MorphScore':>11} {'Renyi':>8}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if "error" in r:
            print(f"{r['language']:10} {r['error']}")
            continue
        for arm in ("movoc_tok", "bpe"):
            if arm in r:
                a = r[arm]
                print(f"{r['language']:10} {r['gold_words']:6} {arm:10} "
                      f"{a['boundary_precision']:10.4f} {a['morphscore']:11.4f} "
                      f"{a['renyi_entropy']:8.4f}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
