"""
run_intrinsic_eval.py -- intrinsic evaluation (paper Sec 6).

Two families of measure:

  Morpheme boundary quality
    - Boundary Precision (Nouri and Yangarber, 2016): of the boundaries a
      tokenizer predicts, what fraction are real gold morpheme boundaries.
    - MorphScore (Arnett and Bergen, 2025): of the gold boundaries, what
      fraction the tokenizer also marks. Words the tokenizer leaves whole
      are excluded rather than scored zero.

  Vocabulary consistency
    - Renyi entropy (order alpha) over the token distribution produced on
      the evaluation text. Compared like-for-like against the baseline,
      it says how evenly a tokenizer spreads probability mass over its
      vocabulary rather than concentrating it on a few frequent tokens.

MoVoC-Tok (constrained merges, Step 6) is compared against a plain BPE
tokenizer trained on the same corpus at the same size, so the only
difference between the two arms is the morpheme constraint.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from movoc.metrics import boundary_precision, morphscore, renyi_entropy  # noqa: E402

EMPTY = {"", "-", "–", "—", "_", "None", "null"}
END = "</w>"


def clean(val) -> str:
    if val is None:
        return ""
    v = str(val).strip().strip("-").strip("–").strip()
    return "" if v in EMPTY else v


ETH_START, ETH_END = 0x1200, 0x1357


def _syllable(ch: str):
    """(consonant, vowel-order) for an Ethiopic fidel, else (None, None).

    The Ge'ez script is a syllabary: each character encodes a consonant
    plus a vowel, laid out in blocks of eight vowel orders per consonant.
    """
    o = ord(ch)
    if ETH_START <= o <= ETH_END:
        return (o - ETH_START) // 8, (o - ETH_START) % 8
    return None, None


def align_morphemes(word: str, parts: list) -> list:
    """Match `parts` against `word`, tolerating fidel fusion at boundaries.

    Ge'ez-script morphemes rarely concatenate literally. Where a root ends
    in a consonant and the following suffix begins with a vowel character,
    the two merge into a single fidel that keeps the root's consonant and
    takes the suffix's vowel -- ጥበብ + አኛ surfaces as ጥበበኛ, with ብ and አ
    fusing into በ. Returns the surface span lengths for each part, or []
    if the parts cannot be aligned at all.
    """
    spans, pos = [], 0
    for i, part in enumerate(parts):
        if not part:
            spans.append(0)
            continue
        if word.startswith(part, pos):
            spans.append(len(part))
            pos += len(part)
            continue
        # Try fusion: all but the final character match literally, and the
        # final character shares its consonant with the surface character.
        head = part[:-1]
        if head and word.startswith(head, pos):
            j = pos + len(head)
            if j < len(word):
                c_part, _ = _syllable(part[-1])
                c_word, _ = _syllable(word[j])
                if c_part is not None and c_part == c_word:
                    spans.append(len(head) + 1)
                    pos = j + 1
                    continue
        # A suffix whose leading vowel was absorbed by the previous fidel.
        if i > 0 and len(part) > 1 and word.startswith(part[1:], pos):
            spans.append(len(part) - 1)
            pos += len(part) - 1
            continue
        return []
    return spans if pos == len(word) else []


def gold_triples(path: Path) -> list:
    """(word, (prefix, root, suffix)) for every usable gold entry.

    Entries are rewritten to the surface spans the metrics can compare:
    boundary offsets are character positions in `word`, so each morpheme is
    replaced by the substring it actually occupies after fusion.
    """
    out = []
    for e in json.load(open(path, encoding="utf-8")):
        word = clean(e.get("word") or e.get("Word"))
        pre = clean(e.get("prefix") or e.get("Prefix"))
        root = clean(e.get("root") or e.get("Root"))
        suf = clean(e.get("suffix") or e.get("Suffix"))
        if not word or not root:
            continue
        if pre + root + suf == word:
            out.append((word, (pre, root, suf)))
            continue
        spans = align_morphemes(word, [pre, root, suf])
        if not spans:
            continue
        a, b = spans[0], spans[0] + spans[1]
        out.append((word, (word[:a], word[a:b], word[b:])))
    return out


def load_merges(path: Path) -> dict:
    ranks = {}
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split(" ")
            if len(parts) == 2:
                ranks[(parts[0], parts[1])] = len(ranks)
    return ranks


def apply_merges(word: str, ranks: dict) -> list:
    """Standard BPE application: repeatedly apply the lowest-ranked merge."""
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


def predicted_triple(word: str, ranks: dict) -> tuple:
    """Convert a tokenization into a (prefix, root, suffix)-shaped triple.

    The metrics compare boundary *offsets*, so what matters is where the
    cuts fall, not which slot they land in. A word tokenized into n pieces
    contributes its first cut and last cut; words left whole contribute no
    boundary, which is what MorphScore treats as unsegmented.
    """
    toks = [t[:-len(END)] if t.endswith(END) else t for t in apply_merges(word, ranks)]
    toks = [t for t in toks if t]
    if len(toks) <= 1:
        return ("", word, "")
    if len(toks) == 2:
        return (toks[0], toks[1], "")
    return (toks[0], "".join(toks[1:-1]), toks[-1])


def token_counter(words, ranks) -> Counter:
    c = Counter()
    for w in words:
        c.update(t for t in apply_merges(w, ranks))
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
        ranks = load_merges(merge_path)
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
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Intrinsic evaluation")
    p.add_argument("--vocab-dir", type=Path, default=here / "vocab")
    p.add_argument("--alpha", type=float, default=2.0,
                   help="Renyi entropy order (default 2.0)")
    p.add_argument("-o", "--out", type=Path,
                   default=here / "results/intrinsic_eval.json")
    args = p.parse_args()

    data = here / "data/morphemes"
    targets = [
        ("tigrinya", data / "Tigriyna_Morphem.json"),
        ("amharic", data / "amharic_morphemes.json"),
        ("tigre", data / "tigre_morphems.json"),
        ("geez", data / "Geez_Morphem.json"),
    ]

    rows = []
    for lang, gold in targets:
        if not gold.exists():
            continue
        movoc = args.vocab_dir / f"movoc_tok_merges_{lang}.txt"
        bpe = args.vocab_dir / f"bpe_merges_{lang}.txt"
        rows.append(evaluate(lang, gold, movoc, bpe, args.alpha))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"alpha": args.alpha, "results": rows},
              open(args.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    hdr = f"{'language':10} {'gold':>6} {'arm':10} {'BoundPrec':>10} {'MorphScore':>11} {'Renyi':>8}"
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
