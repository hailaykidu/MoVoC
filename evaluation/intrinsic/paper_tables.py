"""
paper_tables.py -- reconstructed evaluation following the MoVoC evaluation
protocol (Findings of EMNLP 2025), Tables 2 and 4.

This is NOT a reproduction of the published numbers. It recomputes the
paper's intrinsic metrics from the reconstructed implementation and the
released annotations, and reports them in the paper's table layout.

Two things differ from `evaluate.py`, both deliberate:

1. **Held-out evaluation.** `movoc/annotation.py` points GOLD_SOURCES at
   the *same file* as VOCAB_SOURCES for Amharic, Ge'ez and Tigre, so those
   languages are scored on the words that built their vocabulary. This
   script partitions each annotation set into disjoint construction and
   evaluation halves with a fixed seed, and scores only the held-out half.
   `--leaky` reproduces the old behaviour for comparison.

2. **Table 2 is MoVoC-Tok only**, per the paper's layout (one MorphScore
   per language), while Table 4 compares MoVoC-Tok against BPE.

Usage
    python scripts/paper_tables.py                  # held-out (default)
    python scripts/paper_tables.py --leaky          # in-sample, for contrast
"""

import argparse
import json
import random
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from movoc import annotation, io, tokenizer
from movoc.metrics import (boundaries_from_triple, renyi_entropy,
                           normalized_renyi_entropy)
from movoc.utils import gold_triples

ROOT = Path(__file__).resolve().parent.parent.parent
END = tokenizer.END
SPLIT_SEED = 42
HELD_OUT_FRACTION = 0.5

# ISO 639-3, as the paper's Table 2 labels them.
ISO = {"amharic": "amh", "tigrinya": "tir", "geez": "gez", "tigre": "tig"}
LABEL = {"amharic": "Amharic", "tigrinya": "Tigrinya",
         "geez": "Ge'ez", "tigre": "Tigre"}
LANGS = ("amharic", "tigrinya", "geez", "tigre")
# The paper's row orderings differ between the two tables and are preserved
# exactly: Table 2 lists amh, tir, gez, tig; Table 4 lists Amharic, Tigrinya,
# Tigre, Ge'ez.
TABLE2_ORDER = ("amharic", "tigrinya", "geez", "tigre")
TABLE4_ORDER = ("amharic", "tigrinya", "tigre", "geez")
# The paper's own "No. Items" figures, reproduced verbatim in the table so its
# presentation is preserved. The actually evaluated counts are reported in the
# verification notes; see docs/TABLE2_ITEM_COUNT_DISCREPANCY.md.
PAPER_ITEMS = {"amharic": "80k", "tigrinya": "80k",
               "geez": "20k", "tigre": "32k"}


def boundaries_of(toks: list) -> set:
    cuts, pos = set(), 0
    for t in toks[:-1]:
        pos += len(t)
        cuts.add(pos)
    return cuts


def precision_from_cuts(pred, gold, segmentable_only=True) -> float:
    tp = fp = 0
    for p, g in zip(pred, gold):
        if segmentable_only and not g:
            continue
        tp += len(p & g)
        fp += len(p - g)
    return tp / (tp + fp) if (tp + fp) else 0.0


def recall_from_cuts(pred, gold) -> float:
    """MorphScore: recall of gold boundaries, excluding unsegmented words."""
    hit = total = 0
    for p, g in zip(pred, gold):
        if not p:
            continue
        total += len(g)
        hit += len(p & g)
    return hit / total if total else 0.0


def merge_segmenter(merge_path: Path):
    ranks = tokenizer.load_merges(merge_path)

    def seg(word: str) -> list:
        return [t[:-len(END)] if t.endswith(END) else t
                for t in tokenizer.encode(word, ranks)]
    return seg, {"artifact": str(merge_path.relative_to(ROOT)),
                 "merges": len(ranks)}


# Reverse of the ByteLevel alphabet: maps the printable stand-in characters
# a ByteLevel tokenizer emits back to the raw bytes they represent.
def _byte_decoder():
    """GPT-2 / ByteLevel byte<->unicode table, rebuilt exactly.

    `ByteLevel.alphabet()` returns the 256 stand-in characters as an unordered
    set, so sorting it does NOT recover the byte order. The mapping has to be
    reconstructed with the same algorithm the tokenizer uses.
    """
    bs = (list(range(ord("!"), ord("~") + 1))
          + list(range(ord("\xa1"), ord("\xac") + 1))
          + list(range(ord("\xae"), ord("\xff") + 1)))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


_BYTE_DECODER = _byte_decoder()


def _debyte(token: str) -> str:
    """Turn one ByteLevel token back into text.

    A ByteLevel BPE emits tokens like 'ĠáĬĵ', where each character stands for
    one raw byte. Measuring len() on that counts *bytes*, so for Ethiopic
    (3 bytes per character) every boundary offset is inflated ~3x and cannot
    align with the character-based gold cuts -- which silently drives
    boundary precision toward zero. Decoding first is what makes the offsets
    comparable.
    """
    if not _BYTE_DECODER:
        return token
    try:
        raw = bytes(_BYTE_DECODER[c] for c in token)
    except KeyError:
        return token                                    # not byte-level
    return raw.decode("utf-8", errors="ignore")


def hf_segmenter(model_path: Path):
    from tokenizers import Tokenizer as HFTokenizer
    import json as _json
    tok = HFTokenizer.from_file(str(model_path))
    spec = _json.loads(Path(model_path).read_text(encoding="utf-8"))
    byte_level = (spec.get("pre_tokenizer") or {}).get("type") == "ByteLevel"

    def seg(word: str) -> list:
        out = []
        for t in tok.encode(word).tokens:
            if t.startswith("##"):
                t = t[2:]
            if byte_level:
                t = _debyte(t)
            # ByteLevel marks word starts with a space stand-in; drop it so
            # pieces concatenate back to the bare surface form.
            t = t.lstrip(" ")
            if t:
                out.append(t)
        return out
    return seg, {"artifact": str(model_path.relative_to(ROOT)),
                 "vocab_size": tok.get_vocab_size(),
                 "byte_level": byte_level}


def held_out_gold(lang: str, leaky: bool):
    """Gold triples for `lang`, excluding words used to build the vocabulary.

    Returns (triples, provenance). For Amharic, Ge'ez and Tigre the gold and
    vocabulary files are identical, so a disjoint split is the only way to
    score on unseen words. Tigrinya has a genuinely separate gold file; its
    23-word overlap with the post-edited set is removed too.
    """
    gold_path = annotation.GOLD_SOURCES[lang]
    vocab_path = annotation.VOCAB_SOURCES[lang]
    triples = gold_triples(gold_path)
    total = len(triples)

    prov = {
        "gold_file": str(gold_path.relative_to(ROOT)),
        "vocab_file": str(vocab_path.relative_to(ROOT)),
        "same_file": gold_path == vocab_path,
        "total_scorable": total,
    }

    if leaky:
        prov.update(mode="in-sample (leaky)", held_out=total, excluded=0)
        return triples, prov

    if gold_path == vocab_path:
        # Split the single file: half builds the vocabulary, half evaluates.
        idx = list(range(total))
        random.Random(SPLIT_SEED).shuffle(idx)
        keep = set(idx[: int(total * HELD_OUT_FRACTION)])
        out = [t for i, t in enumerate(triples) if i in keep]
        prov.update(mode="held-out split of shared file",
                    split_seed=SPLIT_SEED,
                    held_out_fraction=HELD_OUT_FRACTION,
                    held_out=len(out), excluded=total - len(out))
        return out, prov

    # Separate gold file: drop any word that also appears in the vocab source.
    vocab_words = {annotation.clean(e.get("word") or e.get("Word"))
                   for e in annotation.load(vocab_path)}
    out = [(w, t) for w, t in triples if w not in vocab_words]
    prov.update(mode="separate gold file, overlap removed",
                held_out=len(out), excluded=total - len(out))
    return out, prov


def score_arm(seg, words, gold_cuts, alpha):
    segs = [seg(w) for w in words]
    pred_cuts = [boundaries_of(s) for s in segs]
    counts = Counter(t for s in segs for t in s)
    return {
        "morphscore": round(100 * recall_from_cuts(pred_cuts, gold_cuts), 1),
        "boundary_precision": round(
            100 * precision_from_cuts(pred_cuts, gold_cuts), 1),
        "renyi_entropy": round(normalized_renyi_entropy(counts, alpha), 2),
        "renyi_entropy_nats": round(renyi_entropy(counts, alpha), 4),
        "distinct_tokens": len(counts),
        "segmented_words": sum(1 for c in pred_cuts if c),
    }


def build_arms(lang: str):
    """MoVoC-Tok and the BPE baseline for one language, when available.

    Ge'ez and Tigre arms are built by scripts/build_extended_arms.py from the
    paper's own Ge'ez (Kibra Negest) and Tigre corpus sources.
    """
    arms = {}
    merges = io.MODELS / f"movoc_tok_merges_{lang}.txt"
    if merges.exists() and merges.stat().st_size > 0:
        seg, meta = merge_segmenter(merges)
        if meta.get("merges", 0) > 0:
            arms["MoVoC-Tok"] = (seg, meta)
    bpe = io.VOCABULARY / f"bpe_{lang}.json"
    if bpe.exists():
        arms["BPE"] = hf_segmenter(bpe)
    return arms


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--alpha", type=float, default=2.0)
    p.add_argument("--leaky", action="store_true",
                   help="score in-sample, as evaluate.py does")
    p.add_argument("-o", "--out", type=Path,
                   default=ROOT / "evaluation/results/paper_tables.json")
    args = p.parse_args()

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()

    rows = []
    for lang in LANGS:
        triples, prov = held_out_gold(lang, args.leaky)
        if not triples:
            rows.append({"language": lang, "iso": ISO[lang],
                         "error": "no scorable held-out entries",
                         "provenance": prov})
            continue
        words = [w for w, _ in triples]
        gold_cuts = [boundaries_from_triple(*t) for _, t in triples]
        arms = build_arms(lang)
        # For the extended languages, record how much of the scored gold set
        # actually appears in the tokenizer's training corpus. Low overlap
        # means the tokenizer is being scored on largely unseen words.
        ext_corpus = ROOT / f"data/raw/extended/{lang}_words.txt"
        if ext_corpus.exists():
            ctypes = set(ext_corpus.read_text(encoding="utf-8").split())
            seen = sum(1 for w in words if w in ctypes)
            prov = dict(prov, corpus=str(ext_corpus.relative_to(ROOT)),
                        corpus_types=len(ctypes),
                        gold_words_in_corpus=seen,
                        gold_in_corpus_pct=round(100 * seen / len(words), 1))
        row = {"language": lang, "iso": ISO[lang],
               "n_items": len(triples), "provenance": prov, "arms": {}}
        for name, (seg, meta) in arms.items():
            row["arms"][name] = dict(meta,
                                     **score_arm(seg, words, gold_cuts,
                                                 args.alpha))
        rows.append(row)

    report = {
        "title": "Reconstructed evaluation following the MoVoC evaluation protocol",
        "not_a_reproduction": (
            "Values are computed fresh from the reconstructed implementation. "
            "They are not the paper's reported numbers and are not comparable "
            "to them."),
        "generated": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "alpha": args.alpha,
        "evaluation_mode": "in-sample (leaky)" if args.leaky else "held-out",
        "metric_implementation": "movoc/metrics.py",
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    by_lang = {r["language"]: r for r in rows}

    # ---- Table 2: MoVoC-Tok MorphScore, one row per language ----
    print("\nTable 2 -- Morphological dataset and MoVoC-Tok MorphScore")
    print(f"({'in-sample' if args.leaky else 'held-out'}, alpha={args.alpha})\n")
    print("| Language (ISO 639-3) | No. Items | MorphScore ↑ |")
    print("|---|---|---|")
    for lang in TABLE2_ORDER:
        r = by_lang.get(lang)
        if r is None:
            continue
        name = f"{LABEL[lang]} ({ISO[lang]})"
        arm = r.get("arms", {}).get("MoVoC-Tok")
        score = arm["morphscore"] if arm else "not available"
        print(f"| {name} | {PAPER_ITEMS[lang]} | {score} |")

    print("\nVerification notes -- actual evaluated item counts")
    print("| Language (ISO 639-3) | Paper No. Items | Actually evaluated |")
    print("|---|---|---|")
    for lang in TABLE2_ORDER:
        r = by_lang.get(lang)
        if r is None:
            continue
        print(f"| {LABEL[lang]} ({ISO[lang]}) | {PAPER_ITEMS[lang]} | "
              f"{r.get('n_items', 0):,} |")
    print("\nThe \"No. Items\" column reproduces the paper's own figures so its "
          "presentation is preserved.")
    print("MorphScore values are independently computed and are not adjusted "
          "toward the published values.")
    print("See docs/TABLE2_ITEM_COUNT_DISCREPANCY.md for why the counts "
          "cannot be reached.")

    # ---- Table 4: boundary precision + Renyi entropy, MoVoC-Tok vs BPE ----
    print(f"\nTable 4 -- Boundary precision and Renyi entropy "
          f"(alpha={args.alpha}, 32k vocabulary)\n")
    print("| Language | Tokenization | Precision ↑ | Rényi Entropy ↓ |")
    print("|---|---|---|---|")
    for lang in TABLE4_ORDER:
        r = by_lang.get(lang)
        if r is None:
            continue
        for arm in ("MoVoC-Tok", "BPE"):
            a = r.get("arms", {}).get(arm)
            if not a:
                print(f"| {LABEL[lang]} | {arm} | not available "
                      f"| not available |")
                continue
            print(f"| {LABEL[lang]} | {arm} | {a['boundary_precision']} | "
                  f"{a['renyi_entropy']} |")

    print("\nVerification notes -- BPE vocabulary actually achieved "
          "(paper setting: 32k)")
    print("| Language | Requested | Achieved |")
    print("|---|---|---|")
    for lang in TABLE4_ORDER:
        a = (by_lang.get(lang) or {}).get("arms", {}).get("BPE")
        if a and a.get("vocab_size"):
            print(f"| {LABEL[lang]} | 32,000 | {a['vocab_size']:,} |")
    print("\nRenyi entropy is normalized to [0, 1]; lower indicates a "
          "sharper, more consistent segmentation distribution.")
    print("Values are independently computed and are not adjusted toward the "
          "published values.")

    try:
        shown = args.out.relative_to(ROOT)
    except ValueError:
        shown = args.out
    print(f"\nwrote {shown}")


if __name__ == "__main__":
    main()
