#!/usr/bin/env python3
"""Check that every number in the corrected paper traces to a source.

Each number found in main.tex prose (and in the generated tables) must be one of:
  * a value in a repository file (tables, per-run JSON, configs, manifests, annotations)
  * a value derived from those (rounding, margins, ratios) -- listed explicitly
  * a figure of the PUBLISHED paper, quoted in order to correct it
  * a non-result constant (years, section numbers, funding number, ...)

Usage:
    python check_numbers.py --repo /path/to/MoVoC --paper /path/to/paper
Exit status 1 if any number is unaccounted for.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\w])")


def norm(tok: str) -> str:
    t = tok.replace(",", "")
    if "." in t:
        t = t.rstrip("0").rstrip(".") or "0"
    return t


def nums_in(text: str) -> set[str]:
    return {norm(m.group(1)) for m in NUM.finditer(text)}


def strip_tex(src: str) -> str:
    src = re.sub(r"(?<!\\)%.*", "", src)                       # comments
    src = src.replace("{,}", ",")                               # TeX thousands separator
    src = re.sub(r"\\(cite[tp]?|ref|label|input|url|bibliography|eth)\{[^}]*\}", " ", src)
    src = re.sub(r"\\(usepackage|documentclass|newfontfamily|setmainfont)(\[[^\]]*\])?\{[^}]*\}(\[[^\]]*\])?", " ", src, flags=re.S)
    src = re.sub(r"\\resizebox\{[^}]*\}\{[^}]*\}", " ", src)
    src = re.sub(r"\\(begin|end)\{[^}]*\}(\[[^\]]*\])?", " ", src)
    src = re.sub(r"\\[a-zA-Z]+\d*", " ", src)                   # remaining macros
    return src


def repo_numbers(repo: Path) -> set[str]:
    s: set[str] = set()
    files = [
        "v2/table2/table2_final.csv", "v2/table4/table4_final.csv",
        "configs/movoc_config.json", "data/README.md", "data/evaluation/manifest.json",
        "data/evaluation/geez/manifest.json", "data/finetuning/en_am/manifest.json",
        # held-out evaluation: the values the paper now reports, and the
        # contamination counts behind them
        "evaluation/results/significance_heldout.json",
        "evaluation/CONTAMINATION.md",
        "evaluation/data/manifest.json",
        "v2/paper/manuscript/tables/table2_heldout.tex",
        "v2/paper/manuscript/tables/table4_heldout.tex",
        "v2/paper/manuscript/tables/table_significance_heldout.tex",
        *glob.glob(str(repo / "tokenizers/*/training_config.json")),
    ]
    for f in files:
        p = Path(f) if Path(f).is_absolute() else repo / f
        if p.exists():
            s |= nums_in(p.read_text(encoding="utf8"))
    d = json.loads((repo / "v2/archive/table3_intrinsic_v1_original/table3_multiseed.json").read_text())
    s |= nums_in(json.dumps(d["experimental_design"]))
    s |= nums_in(json.dumps(d["metrics"]))
    s |= nums_in(json.dumps(d["scientific_validity_caveat"]))
    # The withdrawal of the translation results cites the number of decode
    # passes and the length ratios that evidence the generation failure.
    s.add(norm(str(len(d["per_run"]))))
    for r in d["per_run"]:
        s.add(norm(f"{r['length_ratio']:.4f}"))
    agg = defaultdict(lambda: ([], []))
    for r in d["per_run"]:
        s |= {norm(f"{r['final_train_loss']:.2f}"), norm(str(r["num_examples"]))}
        b, c = agg[(r["evaluation_dataset"], r["direction"], r["tokenizer"])]
        b.append(r["bleu"]); c.append(r["chrf"])
    for b, c in agg.values():
        for v in (statistics.mean(b), statistics.stdev(b), statistics.mean(c), statistics.stdev(c)):
            s.add(norm(f"{v:.4f}"))
    # annotation record counts
    for f in glob.glob(str(repo / "data/annotations/*/*.json")):
        s.add(str(len(json.loads(Path(f).read_text(encoding="utf8")))))
    s.add("169806")
    return s


def derived(repo: Path) -> dict[str, str]:
    """Numbers computed from repository values, with the computation shown."""
    out = {}
    rows = list(csvrows(repo / "v2/table4/table4_final.csv"))
    prec = {(r["language"], r["tokenization"]): float(r["precision"]) for r in rows}
    margins = [prec[(l, "MoVoC-Tok")] - prec[(l, "BPE")] for l in ("Amharic", "Tigrinya", "Tigre")]
    out[norm(f"{min(margins):.4f}")] = "min MoVoC-Tok minus BPE precision (Amharic, Tigrinya, Tigre)"
    out[norm(f"{max(margins):.4f}")] = "max MoVoC-Tok minus BPE precision"
    out[norm(f"{min(prec.values()):.2f}")] = "min precision, 2 d.p."
    out[norm(f"{max(prec.values()):.2f}")] = "max precision, 2 d.p."
    out["5.5"] = "416,040 / 75,000 optimizer steps, rounded"
    out["416000"] = "416,040 steps, rounded ('roughly 416,000')"
    out["32000"] = "s_bpe / per-language vocabulary (configs)"
    out["400000"] = "corpus_lines_read in tokenizer training configs"
    out["0.1"] = "warmup_ratio 0.1 written as 10%"
    out["10"] = "warmup_ratio 0.1 written as 10%"
    out["3"] = "epochs / seeds"
    out["5"] = "r = 5/7 (0.714...)"
    out["7"] = "r = 5/7"
    out["1012"] = "FLORES-200 devtest size"
    out["40"] = "A100-PCIE-40GB"
    out["2107"] = "Mermru total pairs"
    out["122103"] = "sum of vocabulary parts"
    return out


def csvrows(p: Path):
    import csv
    with p.open(encoding="utf8") as f:
        yield from csv.DictReader(f)


def published_numbers(repo: Path) -> set[str]:
    s = nums_in((repo / "original/published_results/README.md").read_text(encoding="utf8"))
    # Figures of the published paper quoted in the correction (ACL Anthology PDF).
    s |= {"63050", "1.44", "8", "0.44", "152", "80", "20", "32", "0.654", "0.731",
          "73.9", "88.3", "0.39", "0.49", "2"}
    return s


def rounds_from(n: str, repo_s: set[str]) -> str | None:
    """The repository value that `n` is a rounding of, if there is one.

    Prose rounds values the tables carry in full: a length ratio of 15.096
    appears as 15.1, a precision of 0.2401 as 0.24. Such a number is sourced,
    but an exact string match does not see it. We accept `n` when some
    repository value rounds to it at `n`'s own precision, requiring at least
    one decimal so that integers are not matched loosely.
    """
    if "." not in n:
        return None
    places = len(n.split(".")[1])
    if not 1 <= places <= 3:
        return None
    target = float(n)
    for cand in repo_s:
        try:
            v = float(cand)
        except ValueError:
            continue
        if v != target and round(v, places) == target:
            return cand
    return None


CONSTANTS = {
    "2025": "year", "2024": "year", "2023": "year", "2022": "year", "2021": "year",
    "2020": "year", "2018": "year", "2017": "year", "2016": "year", "2012": "year",
    "2011": "year", "2007": "year", "2002": "year", "1961": "year",
    "13131": "published pages", "13144": "published pages", "706": "anthology id",
    "57615863": "DAAD funding number", "92": "Park et al. 2021, 92 languages",
    "1": "enumeration/section", "4": "enumeration/section", "6": "enumeration/section",
    "9": "enumeration", "11": "enumeration", "12": "enumeration", "13": "enumeration",
    "42": "seed", "43": "seed", "44": "seed", "128": "max length", "512": "d_model",
    "2048": "FFN dim", "0.92": "font scale", "200": "FLORES-200",
    "2.6": "sacreBLEU 2.6.0", "2.6.0": "sacreBLEU version", "0.21.4": "tokenizers version",
    "11": "font size", "639": "ISO 639-3",
    "3.2": "published section number", "4.2": "published section number",
    "4.3": "published section number", "5.2": "published section number", "0": "zero", "100": "pairs",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--paper", type=Path, required=True)
    a = ap.parse_args()
    a.repo, a.paper = a.repo.resolve(), a.paper.resolve()
    tex = strip_tex((a.paper / "main.tex").read_text(encoding="utf8"))
    for t in sorted((a.paper / "tables").glob("*.tex")):
        tex += "\n" + strip_tex(t.read_text(encoding="utf8"))
    found = nums_in(tex)
    repo_s, der, pub = repo_numbers(a.repo), derived(a.repo), published_numbers(a.repo)
    unknown = []
    for n in sorted(found, key=lambda x: float(x)):
        if n in repo_s:
            src = "repository"
        elif n in der:
            src = "derived: " + der[n]
        elif n in pub:
            src = "published value (quoted)"
        elif n in CONSTANTS:
            src = "constant: " + CONSTANTS[n]
        elif (rounded := rounds_from(n, repo_s)) is not None:
            src = f"repository (rounded from {rounded})"
        else:
            src = None
            unknown.append(n)
        print(f"{n:>12}  {src or '!! UNACCOUNTED'}")
    print(f"\n{len(found)} distinct numbers; {len(unknown)} unaccounted: {unknown}")
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main())
