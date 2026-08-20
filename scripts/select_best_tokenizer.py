#!/usr/bin/env python3
"""Step 4-5 of the model-selection procedure (spec section 8):

  - Read results/{language_pair}/summary.csv (validation-only aggregation,
    already computed by scripts/aggregate_results.py from all 9 runs).
  - Select the tokenizer with the highest MEAN validation chrF++ across
    seeds 42/43/44 (never a single best seed).
  - Write results/{language_pair}/best_tokenizer.json.
  - Print the exact follow-up evaluate.py command(s) needed to produce the
    held-out test score for the selected tokenizer (test set must remain
    untouched until this point).

This script does NOT itself run test-set evaluation -- it only decides
which tokenizer's test results should subsequently be produced, so the
"test set touched only after selection" ordering is structurally enforced
by requiring this script to run (and be inspected) before
scripts/evaluate.py --split test is ever invoked for real numbers.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import VALID_SEEDS, results_dir  # noqa: E402
from marianmt_comparison.selection import TokenizerSummary, select_best_tokenizer  # noqa: E402


def load_summary(language_pair: str) -> list[TokenizerSummary]:
    path = results_dir(language_pair) / "summary.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run scripts/aggregate_results.py first.")
    summaries = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            summaries.append(
                TokenizerSummary(
                    tokenizer=row["tokenizer"],
                    seed_count=int(row["seed_count"]),
                    validation_chrfpp_mean=float(row["validation_chrfpp_mean"]),
                    validation_chrfpp_std=float(row["validation_chrfpp_std"]),
                    test_chrfpp_mean=float(row["test_chrfpp_mean"]) if row["test_chrfpp_mean"] else None,
                    test_chrfpp_std=float(row["test_chrfpp_std"]) if row["test_chrfpp_std"] else None,
                )
            )
    return summaries


def main() -> int:
    exit_code = 0
    for language_pair in ("en_ti", "en_am"):
        print(f"\n=== Selecting best tokenizer for {language_pair} ===")
        try:
            summaries = load_summary(language_pair)
        except FileNotFoundError as exc:
            print(f"  SKIP: {exc}")
            exit_code = 1
            continue

        if not summaries:
            print(
                "  SKIP: summary.csv has no tokenizer rows yet (no runs have completed and been "
                "aggregated). Run scripts/train.py + scripts/evaluate.py + scripts/aggregate_results.py first."
            )
            exit_code = 1
            continue

        incomplete = [s for s in summaries if s.seed_count < len(VALID_SEEDS)]
        if incomplete:
            print(
                f"  WARNING: some tokenizers do not yet have all {len(VALID_SEEDS)} seeds completed: "
                f"{[(s.tokenizer, s.seed_count) for s in incomplete]}. Selection below is based on "
                "whatever is currently available and should be re-run once all 9 runs finish."
            )

        for s in summaries:
            print(f"  {s.tokenizer}: mean_val_chrF++={s.validation_chrfpp_mean:.4f} (std={s.validation_chrfpp_std:.4f}, n={s.seed_count})")

        best = select_best_tokenizer(summaries)
        print(f"  SELECTED: {best.tokenizer} (mean_val_chrF++={best.validation_chrfpp_mean:.4f})")

        out = {
            "language_pair": language_pair,
            "selection_metric": "chrF++",
            "selection_split": "validation",
            "selected_tokenizer": best.tokenizer,
            "seeds": list(VALID_SEEDS),
            "mean_validation_chrfpp": best.validation_chrfpp_mean,
            "std_validation_chrfpp": best.validation_chrfpp_std,
            "all_tokenizer_summaries": [s.to_dict() for s in summaries],
        }
        out_path = results_dir(language_pair) / "best_tokenizer.json"
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"  Wrote {out_path}")

        print(
            f"\n  Next step -- evaluate the SELECTED tokenizer ({best.tokenizer}) on the held-out "
            f"test set (test set must remain untouched for the other tokenizers):"
        )
        for seed in VALID_SEEDS:
            print(
                f"    python3 scripts/evaluate.py --language_pair {language_pair} "
                f"--tokenizer {best.tokenizer} --seed {seed} --split test"
            )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
