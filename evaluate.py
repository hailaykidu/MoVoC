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


def triple_from_tokens(word: str, toks: list) -> tuple:
    """Convert a tokenization into a (prefix, root, suffix)-shaped triple.

    The metrics compare boundary *offsets*, so what matters is where the
    cuts fall, not which slot they land in. A word tokenized into n pieces
    contributes its first cut and last cut; words left whole contribute no
    boundary, which is what MorphScore treats as unsegmented.
    """
    toks = [t for t in toks if t]
    if len(toks) <= 1:
        return ("", word, "")
    if len(toks) == 2:
        return (toks[0], toks[1], "")
    return (toks[0], "".join(toks[1:-1]), toks[-1])


def merge_segmenter(merge_path: Path):
    """Tokenize with a MoVoC-Tok / character-level BPE merge table."""
    ranks = tokenizer.load_merges(merge_path)

    def seg(word: str) -> list:
        return [t[:-len(END)] if t.endswith(END) else t
                for t in tokenizer.encode(word, ranks)]
    return seg, {"merges": len(ranks)}


def hf_segmenter(model_path: Path):
    """Tokenize with a saved Hugging Face tokenizer (BPE or WordPiece).

    Continuation markers are stripped so the pieces concatenate back to the
    surface form and boundary offsets stay comparable across arms.
    """
    from tokenizers import Tokenizer as HFTokenizer
    tok = HFTokenizer.from_file(str(model_path))

    def seg(word: str) -> list:
        out = []
        for t in tok.encode(word).tokens:
            if t.startswith("##"):
                t = t[2:]
            out.append(t)
        return [t for t in out if t]
    return seg, {"vocab_size": tok.get_vocab_size()}


def evaluate(lang: str, gold_path: Path, arms: dict, alpha: float) -> dict:
    """Score every arm in `arms` (name -> (segmenter, meta)) on one language."""
    gold = gold_triples(gold_path)
    if not gold:
        return {"language": lang, "error": "no scorable gold entries"}
    words = [w for w, _ in gold]
    gold_tr = [t for _, t in gold]

    row = {"language": lang, "gold_words": len(gold)}
    for name, (seg, meta) in arms.items():
        segs = [seg(w) for w in words]
        pred = [triple_from_tokens(w, s) for w, s in zip(words, segs)]
        counts = Counter(t for s in segs for t in s)
        row[name] = dict(meta, **{
            "boundary_precision": round(boundary_precision(pred, gold_tr), 4),
            "morphscore": round(morphscore(pred, gold_tr), 4),
            "renyi_entropy": round(renyi_entropy(counts, alpha), 4),
            "distinct_tokens": len(counts),
            "segmented_words": sum(1 for p in pred if p[0] or p[2]),
        })
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
        arms = {}
        merges = io.MODELS / f"movoc_tok_merges_{lang}.txt"
        if merges.exists():
            arms["movoc_tok"] = merge_segmenter(merges)
        for name, fname in (("bpe", f"bpe_{lang}.json"),
                            ("wordpiece", f"wordpiece_{lang}.json")):
            path = io.VOCABULARY / fname
            if path.exists():
                arms[name] = hf_segmenter(path)
        if not arms:
            continue
        rows.append(evaluate(lang, gold, arms, args.alpha))

    io.write_json(args.out, {"alpha": args.alpha, "results": rows})

    hdr = (f"{'language':10} {'gold':>6} {'arm':10} {'BoundPrec':>10} "
           f"{'MorphScore':>11} {'Renyi':>8}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if "error" in r:
            print(f"{r['language']:10} {r['error']}")
            continue
        for arm in ("movoc_tok", "bpe", "wordpiece"):
            if arm in r:
                a = r[arm]
                print(f"{r['language']:10} {r['gold_words']:6} {arm:10} "
                      f"{a['boundary_precision']:10.4f} {a['morphscore']:11.4f} "
                      f"{a['renyi_entropy']:8.4f}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
