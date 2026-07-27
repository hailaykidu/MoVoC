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
from movoc.metrics import (boundary_precision, morphscore, renyi_entropy,
                           normalized_renyi_entropy)
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


def vocab_segmenter(vocab_path: Path):
    """Segment by longest match over a vocabulary, no merge table.

    This scores V_MoVoC (Algorithm 1, Step 5) as it stands -- the union of
    the per-language BPE and morpheme vocabularies -- before MoVoC-Tok's
    constrained merges (Step 6) are trained. Greedy longest-match is the
    segmentation a bare vocabulary supports; it is not MoVoC-Tok, and is
    reported separately as `movoc_vocab`.
    """
    vocab = set(io.read_vocabulary(vocab_path))
    vocab.discard("")

    def seg(word: str) -> list:
        out, i = [], 0
        while i < len(word):
            for j in range(len(word), i, -1):
                if word[i:j] in vocab:
                    out.append(word[i:j])
                    i = j
                    break
            else:
                out.append(word[i])
                i += 1
        return out
    return seg, {"vocab_size": len(vocab)}


def sentencepiece_segmenter(model_path: Path):
    """Tokenize with a SentencePiece model (Unigram or BPE).

    Used for the published shared Ge'ez-script tokenizer
    (Hailay/geez-en-shared-tokenizer). The leading word marker is stripped
    so pieces concatenate back to the surface form, keeping boundary
    offsets comparable with the other arms.
    """
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=str(model_path))

    def seg(word: str) -> list:
        return [t.lstrip("\u2581") for t in sp.encode(word, out_type=str)
                if t.lstrip("\u2581")]
    return seg, {"vocab_size": sp.get_piece_size()}


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
            # Paper Table 4 scales: precision as a percentage, Renyi
            # normalized to [0, 1]. Raw nats kept alongside.
            "boundary_precision": round(100 * boundary_precision(pred, gold_tr), 1),
            "morphscore": round(100 * morphscore(pred, gold_tr), 1),
            "renyi_entropy": round(normalized_renyi_entropy(counts, alpha), 2),
            "renyi_entropy_nats": round(renyi_entropy(counts, alpha), 4),
            "distinct_tokens": len(counts),
            "segmented_words": sum(1 for p in pred if p[0] or p[2]),
        })
    return row




def main():
    p = argparse.ArgumentParser(description="Intrinsic evaluation")
    p.add_argument("--alpha", type=float, default=2.0,
                   help="Renyi entropy order")
    p.add_argument("--sentencepiece", type=Path, default=None,
                   help="SentencePiece .model to score as an extra baseline")
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
        movoc_vocab = io.VOCABULARY / "vocab_movoc.txt"
        if movoc_vocab.exists():
            arms["movoc_vocab"] = vocab_segmenter(movoc_vocab)
        if args.sentencepiece:
            arms["sp_shared"] = sentencepiece_segmenter(args.sentencepiece)
        for name, fname in (("bpe", f"bpe_{lang}.json"),
                            ("wordpiece", f"wordpiece_{lang}.json")):
            path = io.VOCABULARY / fname
            if path.exists():
                arms[name] = hf_segmenter(path)
        if not arms:
            continue
        rows.append(evaluate(lang, gold, arms, args.alpha))

    io.write_json(args.out, {
        "alpha": args.alpha,
        "arms": {
            "movoc_tok": "MoVoC-Tok (paper Sec 3.3): constrained-merge BPE, "
                         "merges forbidden from crossing morpheme boundaries",
            "movoc_vocab": "baseline -- greedy longest-match over V_MoVoC "
                           "(Algorithm 1 Step 5); no constrained merges",
            "bpe": "baseline -- plain byte-level BPE (HF tokenizers)",
            "wordpiece": "baseline -- WordPiece (HF tokenizers), paper Sec 4.3",
            "sp_shared": "baseline -- published SentencePiece Unigram tokenizer; "
                         "not the paper's method",
        },
        "note": "Only movoc_tok is the paper's method; every other arm is a "
                "baseline. Gold sets are held out for Tigrinya only -- for "
                "Amharic, Ge'ez and Tigre the gold file also feeds vocabulary "
                "construction, so those scores are optimistic.",
        "results": rows,
    })

    hdr = (f"{'language':10} {'gold':>6} {'arm':10} {'BoundPrec':>10} "
           f"{'MorphScore':>11} {'Renyi':>8}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if "error" in r:
            print(f"{r['language']:10} {r['error']}")
            continue
        for arm in ("movoc_tok", "movoc_vocab", "bpe", "wordpiece", "sp_shared"):
            if arm in r:
                a = r[arm]
                print(f"{r['language']:10} {r['gold_words']:6} {arm:10} "
                      f"{a['boundary_precision']:10.1f} {a['morphscore']:11.1f} "
                      f"{a['renyi_entropy']:8.2f}")
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
