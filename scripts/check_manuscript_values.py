#!/usr/bin/env python3
"""Check that every numeric in a manuscript traces to the frozen V2 tables.

The repository is authoritative: a value appearing in the manuscript but not in
v2/table{2,3,4}/*_final.csv means the manuscript is out of sync.

Usage:
    python3 scripts/check_manuscript_values.py path/to/main.tex
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "v2/table2/table2_final.csv": ["items_evaluated", "morphscore"],
    "v2/table3/table3_final.csv": ["bleu_mean", "bleu_std", "chrf_mean", "chrf_std"],
    "v2/table4/table4_final.csv": ["precision", "renyi_alpha2", "morphscore", "words"],
}
# Values that legitimately appear in a manuscript without coming from a results
# table: the arXiv id, section numbers, the entropy parameter, the MoVoC ratio,
# the Table 3 training-scale caveat (75,000 vs ~416,000 optimizer steps, 5.5x,
# final loss 3.00-3.59, sourced from v2/table3/PROVENANCE.md), the published
# Table 4 precision range (74.6-88.3, sourced from
# original/published_results/README.md) cited when contrasting it against
# the current reproduction's range, and the Ge'ez precision margin (0.4326 -
# 0.4301 = 0.0025), a computed difference between two table4_final.csv values
# rather than a value in the CSV itself.
ALLOW = {"2509.08812", "2.0", "0.7142857142857143",
         "75,000", "416,000", "5.5", "3.00", "3.59",
         "74.6", "88.3", "0.0025",
         "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "5.1", "5.2"}


def canon(v: str) -> str:
    """Strip padded decimals so 0.0140 and 0.014 compare equal."""
    return v.rstrip("0").rstrip(".") if "." in v else v


def dataset_values() -> set:
    """Counts documented in data/README.md, plus their column totals.

    data/README.md is authoritative for dataset counts. The manuscript may also
    cite the totals across languages, which are sums of the documented rows, so
    those are derived here rather than hard-coded.
    """
    out, path = set(), ROOT / "data/README.md"
    if not path.exists():
        print("warning: missing data/README.md", file=sys.stderr)
        return out
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        found = [c for c in cells if re.fullmatch(r"[\d,]+", c) and any(ch.isdigit() for ch in c)]
        if len(found) >= 2:
            rows.append([int(c.replace(",", "")) for c in found[:2]])
        for c in found:
            out.add(c)
            out.add(c.replace(",", ""))
    for total in (sum(r[0] for r in rows), sum(r[1] for r in rows)):
        if total:
            out.add(f"{total:,}")
            out.add(str(total))
    return out


def frozen_values() -> set:
    out = dataset_values()
    for rel, cols in SOURCES.items():
        path = ROOT / rel
        if not path.exists():
            print(f"warning: missing source {rel}", file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for c in cols:
                    v = (row.get(c) or "").strip()
                    if v:
                        out.add(v)
                        out.add(canon(v))
                        # tables render thousands with separators
                        if v.isdigit():
                            out.add(f"{int(v):,}")
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    tex = Path(sys.argv[1])
    if not tex.exists():
        print(f"error: {tex} not found", file=sys.stderr)
        return 2

    ok = frozen_values()
    text = tex.read_text(encoding="utf-8")
    # Ignore comment lines -- they carry provenance notes, not printed values.
    body = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("%"))

    stray = sorted({
        n for n in re.findall(r"\b\d+(?:,\d{3})*\.\d+\b|\b\d+(?:,\d{3})+\b", body)
        if n not in ok and canon(n) not in ok and n not in ALLOW
    })

    if stray:
        print(f"values not traceable to the frozen V2 tables ({len(stray)}):")
        for n in stray:
            print(f"   {n}")
        print("\nThe repository is authoritative. Correct the manuscript.")
        return 1
    print("OK -- every numeric traces to v2/table{2,3,4}/*_final.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
