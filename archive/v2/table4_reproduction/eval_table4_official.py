"""Table 4 regeneration under the OFFICIAL MoVoC methodology.

Applies the three corrections identified by the audits:

  1. Renyi entropy is NORMALISED: H_alpha / log(support), matching
     movoc/metrics.py::normalized_renyi_entropy. The paper's 0.39-0.49 range
     is on this scale.
  2. Gold boundaries use the paper's CUMULATIVE-LENGTH rule
     (movoc/metrics.py::boundaries_from_triple): offsets are cumulative
     morpheme lengths; the surface string is never consulted and no word is
     excluded for non-concatenation.
  3. MoVoC-Tok is the 32k artifact, matching Table 4's "for 32k Vocabularies".

Aggregation follows the official code: micro-average
(total matched / total predicted) over words that carry >=1 gold boundary
(segmentable_only=True), reported as a percentage.

Intrinsic only. No MT, no BLEU, no chrF++.

Tigre and Ge'ez: no in-language MoVoC-Tok exists at any size (paper Sec. 4.1
states no BPE training data was obtained for them). Table 4 nonetheless reports
MoVoC-Tok rows for both, so a cross-lingual substitute is required. The choice
is NOT specified by the paper; it is applied here as a documented assumption and
flagged in every output.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
import unicodedata
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

AMSEG = Path("/homes/neumann/teklehaymanot/amseg")
ANN = AMSEG / "data/annotations"
HF = AMSEG / "tokenizers/hf"
OUT = Path("/homes/neumann/teklehaymanot/movoc_table4_repro/results_intrinsic_official")

PLACEHOLDERS = {"-", "–", "—", "", "None", "null"}
WORD_START, CONTINUING = "▁", "##"

DATASETS = {
    "Amharic": ("amharic/postedited_morphemes.json", "Word",
                ("Prefix", "Root", "Infix", "Suffix", "Clitic")),
    "Tigrinya": ("tigrinya/gold_morphemes.json", "word",
                 ("prefix", "root", "suffix")),
    "Tigre": ("tigre/manual_morphemes.json", "word",
              ("prefix", "root", "infix", "suffix", "clitic")),
    "Ge'ez": ("geez/manual_morphemes.json", "word",
              ("prefix", "root", "infix", "suffix")),
}

# MoVoC-Tok per language. Tigre/Ge'ez have no in-language model; the Tigrinya
# 32k model is applied cross-lingually as a documented assumption -- Tigrinya is
# the nearest trained Ethio-Semitic relative and Ge'ez is their shared ancestor.
MOVOC = {
    "Amharic": ("movoc_tok_32k_amharic", "in-language"),
    "Tigrinya": ("movoc_tok_32k_tigrinya", "in-language"),
    "Tigre": ("movoc_tok_32k_tigrinya", "cross-lingual (assumption)"),
    "Ge'ez": ("movoc_tok_32k_tigrinya", "cross-lingual (assumption)"),
}
BPE_DIR = "bpe_32k"


def normalize(s: str) -> str:
    return unicodedata.normalize("NFC", str(s)).strip()


def morphemes_of(rec: dict, keys) -> list[str]:
    out = []
    for k in keys:
        v = rec.get(k)
        if v is None:
            continue
        v = normalize(v)
        if v in PLACEHOLDERS:
            continue
        v = v.replace("-", "").replace("–", "").strip()
        if v and v not in PLACEHOLDERS:
            out.append(v)
    return out


def boundaries_cumulative(parts: list[str]) -> set:
    """Paper rule: cumulative lengths of all parts but the last.

    Mirrors movoc/metrics.py::boundaries_from_triple. The surface string is
    never consulted, so this never fails.
    """
    b, pos = set(), 0
    for p in parts[:-1]:
        pos += len(p)
        b.add(pos)
    return b


def pieces_surface(pieces: list[str]) -> list[str]:
    out = []
    for p in pieces:
        t = p[len(WORD_START):] if p.startswith(WORD_START) else p
        t = t[len(CONTINUING):] if t.startswith(CONTINUING) else t
        if t:
            out.append(t)
    return out


def renyi(counts: Counter, alpha: float = 2.0) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values()]
    s = sum(p ** alpha for p in probs)
    return (1.0 / (1.0 - alpha)) * math.log(s) if s > 0 else 0.0


def normalized_renyi(counts: Counter, alpha: float = 2.0) -> float:
    """H_alpha / log(support), in [0, 1]. Base cancels; matches the paper scale."""
    support = len(counts)
    if support <= 1:
        return 0.0
    return renyi(counts, alpha) / math.log(support)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    bpe = AutoTokenizer.from_pretrained(str(HF / BPE_DIR))
    movoc_cache = {}
    print(f"  BPE  {BPE_DIR}  vocab={len(bpe)}")

    ds_stats, prec_rows, ent_rows, examples, perf = [], [], [], [], []

    for lang, (fname, wkey, mkeys) in DATASETS.items():
        recs = json.loads((ANN / fname).read_text(encoding="utf-8"))
        if args.smoke:
            recs = recs[:args.smoke]

        mdir, mode = MOVOC[lang]
        if mdir not in movoc_cache:
            movoc_cache[mdir] = AutoTokenizer.from_pretrained(str(HF / mdir))
        toks = {"MoVoC-Tok": movoc_cache[mdir], "BPE": bpe}

        words, golds, n_single = [], [], 0
        morph_count = 0
        for r in recs:
            w = normalize(r.get(wkey, ""))
            if not w:
                continue
            ms = morphemes_of(r, mkeys)
            if len(ms) < 2:
                n_single += 1          # no gold boundary -> segmentable_only skip
                continue
            gb = boundaries_cumulative(ms)
            if not gb:
                n_single += 1
                continue
            words.append(w); golds.append(gb); morph_count += len(ms)

        ds_stats.append({"language": lang, "source_file": fname,
                         "records_in_source": len(recs),
                         "words_evaluated": len(words),
                         "excluded_no_gold_boundary": n_single,
                         "excluded_unaligned_to_surface": 0,
                         "morphemes_evaluated": morph_count,
                         "gold_boundaries": sum(len(g) for g in golds),
                         "movoc_tok_model": mdir, "movoc_tok_mode": mode})
        print(f"{lang}: eval={len(words)} skipped_no_boundary={n_single} "
              f"movoc={mdir} ({mode})")

        for tname, tok in toks.items():
            t0 = time.time()
            enc = tok(words, add_special_tokens=False)
            counts, matched, predicted = Counter(), 0, 0
            for i, ids in enumerate(enc["input_ids"]):
                surf = pieces_surface(tok.convert_ids_to_tokens(ids))
                counts.update(surf)
                pb = boundaries_cumulative(surf)   # same rule both sides
                matched += len(pb & golds[i]); predicted += len(pb)
            secs = time.time() - t0
            micro = 100.0 * matched / predicted if predicted else 0.0
            Hn = normalized_renyi(counts, 2.0)
            Hraw = renyi(counts, 2.0)

            prec_rows.append({"language": lang, "tokenizer": tname,
                              "precision_micro_pct": round(micro, 4),
                              "words_scored": len(words),
                              "predicted_boundaries": predicted,
                              "matched_boundaries": matched})
            ent_rows.append({"language": lang, "tokenizer": tname,
                             "renyi_normalized_alpha2": round(Hn, 4),
                             "renyi_raw_nats_alpha2": round(Hraw, 4),
                             "distinct_tokens": len(counts),
                             "total_tokens": sum(counts.values())})
            perf.append({"language": lang, "tokenizer": tname,
                         "words": len(words), "tokens": sum(counts.values()),
                         "seconds": round(secs, 3),
                         "words_per_sec": round(len(words) / secs, 1) if secs else 0})
            print(f"  {lang:9} {tname:10} precision={micro:6.2f}%  "
                  f"renyi_norm={Hn:.4f}  (raw {Hraw:.3f} nats)")

            rng = random.Random(42)
            for i in rng.sample(range(len(words)), min(100, len(words))):
                surf = pieces_surface(tok.convert_ids_to_tokens(enc["input_ids"][i]))
                pb = boundaries_cumulative(surf)
                inter = len(pb & golds[i])
                examples.append({"language": lang, "tokenizer": tname,
                                 "word": words[i],
                                 "gold_boundaries": "|".join(map(str, sorted(golds[i]))),
                                 "tokenizer_output": " ".join(surf),
                                 "predicted_boundaries": "|".join(map(str, sorted(pb))),
                                 "correct": inter, "predicted": len(pb),
                                 "precision": round(inter / len(pb), 4) if pb else ""})

    def dump(name, rows):
        if not rows:
            return
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    dump("dataset_statistics.csv", ds_stats)
    dump("boundary_precision.csv", prec_rows)
    dump("renyi_entropy.csv", ent_rows)
    dump("boundary_examples.csv", examples)
    dump("performance_log.csv", perf)

    table = []
    for lang in DATASETS:
        for tname in ("MoVoC-Tok", "BPE"):
            p = next(r for r in prec_rows if r["language"] == lang and r["tokenizer"] == tname)
            e = next(r for r in ent_rows if r["language"] == lang and r["tokenizer"] == tname)
            d = next(r for r in ds_stats if r["language"] == lang)
            table.append({"language": lang, "tokenization": tname,
                          "precision": round(p["precision_micro_pct"], 1),
                          "renyi_alpha2_normalized": round(e["renyi_normalized_alpha2"], 2),
                          "movoc_tok_mode": d["movoc_tok_mode"] if tname == "MoVoC-Tok" else "",
                          "words": d["words_evaluated"]})
    dump("table4_reproduction.csv", table)

    tex = ["\\begin{tabular}{llrr}", "\\hline",
           "Language & Tokenization & Precision $\\uparrow$ & R\\'enyi Entropy $\\downarrow$ \\\\",
           "\\hline"]
    for r in table:
        tex.append(f"{r['language']} & {r['tokenization']} & "
                   f"{r['precision']:.1f} & {r['renyi_alpha2_normalized']:.2f} \\\\")
    tex += ["\\hline", "\\end{tabular}"]
    (OUT / "table4_reproduction.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")

    print("\n=== Table 4 (official methodology) ===")
    print(f"{'Language':10} {'Tokenization':12} {'Precision':>10} {'Renyi':>8}")
    for r in table:
        print(f"{r['language']:10} {r['tokenization']:12} "
              f"{r['precision']:>10.1f} {r['renyi_alpha2_normalized']:>8.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
