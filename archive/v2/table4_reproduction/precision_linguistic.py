"""Linguistically-grounded precision sensitivity analysis (Amharic, Ge'ez).

SENSITIVITY ANALYSIS ONLY. The official Table 4 reproduction is untouched and
continues to report official exact-match precision.

Variants:
  A  abugida-aware matching: exact, +/-1, fusion-aware
  B  root-preservation: root vs affix boundary precision
  C  multi-morpheme subsets (>=3, >=4 morphemes)
  D  morpheme-span overlap: Jaccard and span F1
  E  error typology: exact miss, off-by-one, off-by-two, root split, affix merge

Fusion-aware matching (Variant A.3) is defined as follows. Ethiopic syllables
occupy U+1200..U+137F in families of 8: codepoint (cp - 0x1200) // 8 selects the
consonant family and (cp - 0x1200) % 8 the vowel order. A morpheme boundary in an
abugida can fall *inside* a syllable, because one character carries both the
final consonant of one morpheme and the initial vowel of the next. A predicted
boundary at position p is therefore credited against a gold boundary g when:

    p == g                                        (exact), or
    |p - g| == 1 and the character straddled by the pair is Ethiopic and
    carries a non-zero vowel order (i.e. it is a fused, non-base form)

The vowel-order condition is what makes this narrower than blanket +/-1: a
boundary is forgiven only where the orthography actually fuses. Base forms
(vowel order 0) get no credit, and non-Ethiopic characters get none.
"""

from __future__ import annotations

import csv
import json
import statistics
import unicodedata
from pathlib import Path

from transformers import AutoTokenizer

AMSEG = Path("/homes/neumann/teklehaymanot/amseg")
ANN = AMSEG / "data/annotations"
HF = AMSEG / "tokenizers/hf"
OUT = Path("/homes/neumann/teklehaymanot/movoc_table4_repro/results_precision_linguistic")

PH = {"-", "–", "—", "", "None", "null"}
WS, CONT = "▁", "##"
ETH_LO, ETH_HI = 0x1200, 0x137F

DATASETS = {
    "Amharic": ("amharic/postedited_morphemes.json", "Word",
                ("Prefix", "Root", "Infix", "Suffix", "Clitic"), "Root",
                "movoc_tok_32k_amharic"),
    "Ge'ez": ("geez/manual_morphemes.json", "word",
              ("prefix", "root", "infix", "suffix"), "root",
              "movoc_tok_32k_tigrinya"),
}


def norm(s):
    return unicodedata.normalize("NFC", str(s)).strip()


def clean(v):
    if v is None:
        return ""
    v = norm(v)
    if v in PH:
        return ""
    v = v.replace("-", "").replace("–", "").strip()
    return "" if v in PH else v


def is_fused(ch: str) -> bool:
    """Ethiopic syllable carrying a non-base vowel order."""
    if not ch:
        return False
    cp = ord(ch)
    return ETH_LO <= cp <= ETH_HI and ((cp - ETH_LO) % 8) != 0


def fusion_ok(word: str, p: int, g: int) -> bool:
    """Credit p against g under abugida fusion (see module docstring)."""
    if p == g:
        return True
    if abs(p - g) != 1:
        return False
    idx = min(p, g)                      # the character straddled by the pair
    return 0 <= idx < len(word) and is_fused(word[idx])


def match(pred: set, gold: set, mode: str, word: str) -> int:
    if mode == "exact":
        return len(pred & gold)
    unused, hits = set(gold), 0
    for p in sorted(pred):
        best = None
        for g in unused:
            ok = (abs(p - g) <= 1) if mode == "tol1" else fusion_ok(word, p, g)
            if ok and (best is None or abs(p - g) < abs(p - best)):
                best = g
        if best is not None:
            unused.discard(best)
            hits += 1
    return hits


def cuts(parts):
    c, pos = set(), 0
    for p in parts[:-1]:
        pos += len(p)
        c.add(pos)
    return c


def spans(parts):
    out, pos = [], 0
    for p in parts:
        out.append((pos, pos + len(p)))
        pos += len(p)
    return out


def surface(pieces):
    out = []
    for p in pieces:
        t = p[len(WS):] if p.startswith(WS) else p
        t = t[len(CONT):] if t.startswith(CONT) else t
        if t:
            out.append(t)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bpe = AutoTokenizer.from_pretrained(str(HF / "bpe_32k"))
    cache = {}
    v_rows, root_rows, span_rows, err_rows = [], [], [], []

    for lang, (fname, wkey, mkeys, rootkey, mdir) in DATASETS.items():
        if mdir not in cache:
            cache[mdir] = AutoTokenizer.from_pretrained(str(HF / mdir))
        arms = {"MoVoC-Tok": cache[mdir], "BPE": bpe}

        words, golds, gspans, rootb, nmor = [], [], [], [], []
        for r in json.loads((ANN / fname).read_text(encoding="utf-8")):
            w = norm(r.get(wkey, ""))
            if not w:
                continue
            parts, rootpos = [], None
            for k in mkeys:
                c = clean(r.get(k))
                if not c:
                    continue
                if k == rootkey and rootpos is None:
                    rootpos = len(parts)
                parts.append(c)
            if len(parts) < 2:
                continue
            g = cuts(parts)
            if not g:
                continue
            # boundaries delimiting the root span (Variant B)
            rb = set()
            if rootpos is not None:
                sp = spans(parts)
                s, e = sp[rootpos]
                if s > 0:
                    rb.add(s)
                if e < sum(len(p) for p in parts):
                    rb.add(e)
            words.append(w); golds.append(g); gspans.append(spans(parts))
            rootb.append(rb & g); nmor.append(len(parts))

        for tname, tok in arms.items():
            enc = tok(words, add_special_tokens=False)
            segs = [surface(tok.convert_ids_to_tokens(i)) for i in enc["input_ids"]]
            preds = [cuts(s) for s in segs]

            # ---- Variant A ----
            for mode, label in (("exact", "A1 exact (official)"),
                                ("tol1", "A2 +/-1 tolerance"),
                                ("fusion", "A3 fusion-aware")):
                tp = fp = 0
                for i, p in enumerate(preds):
                    m = match(p, golds[i], mode, words[i])
                    tp += m; fp += len(p) - m
                v_rows.append({"language": lang, "tokenizer": tname, "variant": label,
                               "subset": "all", "words": len(words),
                               "precision": round(100 * tp / (tp + fp), 2) if tp + fp else 0.0})

            # ---- Variant C ----
            for lo, label in ((3, "C >=3 morphemes"), (4, "C >=4 morphemes")):
                idx = [i for i in range(len(words)) if nmor[i] >= lo]
                if not idx:
                    continue
                tp = fp = 0
                for i in idx:
                    m = match(preds[i], golds[i], "exact", words[i])
                    tp += m; fp += len(preds[i]) - m
                v_rows.append({"language": lang, "tokenizer": tname, "variant": label,
                               "subset": f">={lo} morphemes", "words": len(idx),
                               "precision": round(100 * tp / (tp + fp), 2) if tp + fp else 0.0})

            # ---- Variant B ----
            rt_tp = rt_tot = af_tp = af_tot = 0
            for i, p in enumerate(preds):
                rb = rootb[i]; ab = golds[i] - rb
                rt_tot += len(rb); rt_tp += len(p & rb)
                af_tot += len(ab); af_tp += len(p & ab)
            root_rows.append({"language": lang, "tokenizer": tname,
                              "root_boundaries": rt_tot,
                              "root_recall_pct": round(100 * rt_tp / rt_tot, 2) if rt_tot else 0.0,
                              "affix_boundaries": af_tot,
                              "affix_recall_pct": round(100 * af_tp / af_tot, 2) if af_tot else 0.0})

            # ---- Variant D ----
            jac, f1s = [], []
            for i, s in enumerate(segs):
                ps = set(spans(s)); gs = set(gspans[i])
                inter = len(ps & gs); union = len(ps | gs)
                jac.append(inter / union if union else 0.0)
                pr = inter / len(ps) if ps else 0.0
                rc = inter / len(gs) if gs else 0.0
                f1s.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
            span_rows.append({"language": lang, "tokenizer": tname,
                              "words": len(words),
                              "span_jaccard_mean": round(statistics.mean(jac), 4),
                              "span_f1_mean": round(statistics.mean(f1s), 4)})

            # ---- Variant E ----
            cnt = {"exact_hit": 0, "off_by_one": 0, "off_by_two": 0,
                   "other_miss": 0, "root_split": 0, "affix_merge": 0}
            for i, p in enumerate(preds):
                g = golds[i]; rb = rootb[i]
                sp = gspans[i]
                rootspan = None
                for (s, e) in sp:
                    if s in rb or e in rb:
                        rootspan = (s, e)
                for b in p:
                    if b in g:
                        cnt["exact_hit"] += 1
                    elif any(abs(b - x) == 1 for x in g):
                        cnt["off_by_one"] += 1
                    elif any(abs(b - x) == 2 for x in g):
                        cnt["off_by_two"] += 1
                    else:
                        cnt["other_miss"] += 1
                    # root split: a predicted cut strictly inside the root span
                    if rootspan and rootspan[0] < b < rootspan[1]:
                        cnt["root_split"] += 1
                # affix merge: a gold affix boundary the tokenizer never produced
                cnt["affix_merge"] += len((g - rb) - p)
            tot = max(sum(len(p) for p in preds), 1)
            err_rows.append({"language": lang, "tokenizer": tname,
                             "predicted_boundaries": tot,
                             **{k: round(100 * v / tot, 2) for k, v in cnt.items()}})
            print(f"  {lang} {tname} done")

    def dump(name, rows):
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    dump("precision_variants_linguistic.csv", v_rows)
    dump("root_boundary_scores.csv", root_rows)
    dump("span_overlap_scores.csv", span_rows)
    dump("error_type_analysis.csv", err_rows)

    print("\n=== Variant A/C precision ===")
    for r in v_rows:
        print(f"  {r['language']:8} {r['tokenizer']:10} {r['variant']:22} "
              f"n={r['words']:>7} {r['precision']:>7}")
    print("\n=== Variant B root/affix ===")
    for r in root_rows:
        print(f"  {r['language']:8} {r['tokenizer']:10} root={r['root_recall_pct']:>6}% "
              f"affix={r['affix_recall_pct']:>6}%")
    print("\n=== Variant D spans ===")
    for r in span_rows:
        print(f"  {r['language']:8} {r['tokenizer']:10} jaccard={r['span_jaccard_mean']} "
              f"span_f1={r['span_f1_mean']}")
    print("\n=== Variant E errors (% of predicted boundaries) ===")
    for r in err_rows:
        print(f"  {r['language']:8} {r['tokenizer']:10} exact={r['exact_hit']} "
              f"off1={r['off_by_one']} off2={r['off_by_two']} other={r['other_miss']} "
              f"root_split={r['root_split']} affix_merge={r['affix_merge']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
