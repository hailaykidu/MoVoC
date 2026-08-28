"""
score_tigre_movoc_tok.py -- fill the two pending Tigre MoVoC-Tok cells.

Computes ONLY Tigre MoVoC-Tok:
  Table 2  MorphScore
  Table 4  Morpheme Boundary Precision, Renyi Entropy (alpha=2)

Reuses paper_tables.py's segmenters, held-out split and metric code verbatim,
so the Tigre numbers are produced by exactly the same pipeline as the
already-completed languages. Nothing for Amharic, Tigrinya, Ge'ez, or any BPE
arm is recomputed or rewritten -- this script only merges its one result into
the existing paper_tables.json.

Refuses to report a partial merge table: if the build timed out and left a
stub, it says so and exits without producing a number.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import paper_tables as PT
from movoc.metrics import boundaries_from_triple

# A genuine 32k-target run leaves tens of thousands of merges. The stub the
# timed-out/pre-fix run left behind is 1 line. Anything under this is treated
# as partial and refused rather than reported.
MIN_USABLE_MERGES = 100


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alpha", type=float, default=2.0)
    ap.add_argument("--min-merges", type=int, default=MIN_USABLE_MERGES)
    ap.add_argument("--tables", type=Path,
                    default=ROOT / "evaluation/results/paper_tables.json")
    args = ap.parse_args()

    merges_path = PT.io.MODELS / "movoc_tok_merges_tigre.txt"
    if not merges_path.exists():
        raise SystemExit(f"no merge table at {merges_path}")

    n_lines = sum(1 for _ in open(merges_path, encoding="utf-8"))
    if n_lines < args.min_merges:
        print(f"REFUSING TO REPORT: {merges_path.name} holds only {n_lines} "
              f"merges (< {args.min_merges}).")
        print("The Tigre build did not complete. No partial-merge value is "
              "substituted; the Tigre MoVoC-Tok cells stay pending.")
        raise SystemExit(2)

    seg, meta = PT.merge_segmenter(merges_path)
    print(f"loaded MoVoC-Tok merge table: {meta['merges']} merges")

    triples, prov = PT.held_out_gold("tigre", leaky=False)
    words = [w for w, _ in triples]
    gold_cuts = [boundaries_from_triple(*t) for _, t in triples]
    print(f"held-out items evaluated: {len(triples)}")

    scores = PT.score_arm(seg, words, gold_cuts, args.alpha)
    print(f"\nTigre MoVoC-Tok")
    print(f"  MorphScore          {scores['morphscore']}")
    print(f"  Boundary Precision  {scores['boundary_precision']}")
    print(f"  Renyi Entropy       {scores['renyi_entropy']}")

    # Merge into the existing report without disturbing any other row.
    if args.tables.exists():
        report = json.loads(args.tables.read_text(encoding="utf-8"))
        for row in report.get("rows", []):
            if row.get("language") == "tigre":
                row.setdefault("arms", {})["MoVoC-Tok"] = dict(meta, **scores)
                row["n_items"] = len(triples)
                row["provenance"] = prov
                break
        args.tables.write_text(json.dumps(report, indent=2,
                                          ensure_ascii=False),
                               encoding="utf-8")
        print(f"\nupdated {args.tables.relative_to(ROOT)} (tigre row only)")


if __name__ == "__main__":
    main()
