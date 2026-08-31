#!/usr/bin/env python3
"""Aggregate all per-run validation (and, if present, test) results for a
language pair into results/{language_pair}/{validation_per_seed.csv,
test_per_seed.csv,summary.csv}.

Also scans experiments/{language_pair}/*/*/status.json to build
results/job_manifest.json and results/failures.json (spec sections 10-13),
identifying COMPLETED/FAILED/MISSING for every expected run.

Run after all training+evaluation for a language pair (or at any point, to
get a current-state snapshot -- MISSING is a normal, expected status before
the full sweep completes).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import (  # noqa: E402
    VALID_SEEDS,
    VALID_TOKENIZERS,
    results_dir,
    run_experiment_dir,
)
from marianmt_comparison.selection import SeedResult, summarize_by_tokenizer  # noqa: E402


def gather_language_pair(language_pair: str) -> tuple[list[dict], list[dict], list[SeedResult]]:
    val_rows, test_rows, seed_results = [], [], []

    for tokenizer_name in VALID_TOKENIZERS:
        for seed in VALID_SEEDS:
            run_dir = run_experiment_dir(language_pair, tokenizer_name, seed)
            val_path = run_dir / "validation_results.json"
            test_path = run_dir / "test_results.json"

            val_chrf = None
            if val_path.exists():
                v = json.loads(val_path.read_text(encoding="utf-8"))
                val_chrf = v["chrf_plus_plus"]
                val_rows.append(
                    {
                        "language_pair": language_pair,
                        "tokenizer": tokenizer_name,
                        "seed": seed,
                        "chrf_plus_plus": v["chrf_plus_plus"],
                        "bleu": v["bleu"],
                        "sacrebleu_version": v["sacrebleu_version"],
                        "chrf_signature": v["chrf_signature"],
                    }
                )

            test_chrf = None
            if test_path.exists():
                t = json.loads(test_path.read_text(encoding="utf-8"))
                test_chrf = t["chrf_plus_plus"]
                test_rows.append(
                    {
                        "language_pair": language_pair,
                        "tokenizer": tokenizer_name,
                        "seed": seed,
                        "chrf_plus_plus": t["chrf_plus_plus"],
                        "bleu": t["bleu"],
                        "sacrebleu_version": t["sacrebleu_version"],
                        "chrf_signature": t["chrf_signature"],
                    }
                )

            if val_chrf is not None:
                seed_results.append(
                    SeedResult(tokenizer=tokenizer_name, seed=seed, validation_chrfpp=val_chrf, test_chrfpp=test_chrf)
                )

    return val_rows, test_rows, seed_results


def write_csv(rows: list[dict], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_job_manifest_and_failures() -> tuple[dict, dict]:
    job_manifest = {"jobs": []}
    failures = {"failures": []}

    for language_pair in ("en_ti", "en_am"):
        for tokenizer_name in VALID_TOKENIZERS:
            for seed in VALID_SEEDS:
                run_dir = run_experiment_dir(language_pair, tokenizer_name, seed)
                status_path = run_dir / "status.json"
                entry = {
                    "language_pair": language_pair,
                    "tokenizer": tokenizer_name,
                    "seed": seed,
                    "run_dir": str(run_dir.relative_to(REPO_ROOT)),
                }
                if not status_path.exists():
                    entry["status"] = "MISSING"
                    job_manifest["jobs"].append(entry)
                    continue
                status = json.loads(status_path.read_text(encoding="utf-8"))
                entry["status"] = status.get("status", "UNKNOWN")
                entry["slurm_job_id"] = status.get("slurm_job_id")
                job_manifest["jobs"].append(entry)
                if entry["status"] == "FAILED":
                    failures["failures"].append(
                        {
                            **entry,
                            "stage": status.get("stage"),
                            "error": status.get("error"),
                            "log_path": status.get("log_path"),
                        }
                    )
    return job_manifest, failures


def generate_final_report() -> Path:
    """Auto-generate results/final_report.md (spec section 16). Reads only
    already-written results/*, data/manifests/*, and
    data/manifests/model_verification_report.json / tokenizer_manifest.json
    -- never re-computes scores itself. Contains no absolute paths outside
    this repo and no cluster hostnames/usernames (spec section 13)."""
    lines = ["# Final Report: MarianMT Tokenizer Comparison", ""]
    lines.append(
        "Auto-generated by `scripts/aggregate_results.py`. Do not hand-edit; "
        "re-run the aggregation step to regenerate this file."
    )
    lines.append("")
    lines.append("## Experimental configuration")
    lines.append("")
    lines.append("- Tokenizers compared: BPE, WordPiece, MoVoC-Tok (all pre-trained, read-only)")
    lines.append("- Language pairs: English->Tigrinya (en_ti), English->Amharic (en_am)")
    lines.append("- Seeds: 42, 43, 44 (mean+std reported; best single seed is never selected)")
    lines.append("- Learning rate: 1.44e-7 (fixed for all 18 runs; see README 'Known caveats')")
    lines.append("- Evaluation metric: chrF++ (sacrebleu, char_order=6 word_order=2 beta=2 lowercase=False whitespace=False), BLEU secondary")
    lines.append("")

    tok_manifest_path = REPO_ROOT / "data" / "manifests" / "tokenizer_manifest.json"
    if tok_manifest_path.exists():
        tok_manifest = json.loads(tok_manifest_path.read_text(encoding="utf-8"))
        lines.append("## Tokenizer information")
        lines.append("")
        lines.append("| Language pair | Tokenizer | Class | Vocab size (len) | Cross-lingual reuse |")
        lines.append("|---|---|---|---|---|")
        for t in tok_manifest.get("tokenizers", []):
            if t["name"] == "marian_original":
                continue
            lines.append(
                f"| {t['language_pair']} | {t['name']} | {t['tokenizer_class']} | "
                f"{t['vocab_size_len']} | {t['cross_lingual_reuse']} |"
            )
        lines.append("")
        cross = [t for t in tok_manifest.get("tokenizers", []) if t.get("cross_lingual_reuse")]
        if cross:
            lines.append("**Cross-lingual reuse warning(s):**")
            for t in cross:
                lines.append(
                    f"- `{t['language_pair']}/{t['name']}`: {t['warning']} "
                    f"(measured Amharic fertility={t['amharic_fertility']}, UNK rate={t['amharic_unk_rate']})"
                )
            lines.append("")
    else:
        lines.append("## Tokenizer information")
        lines.append("")
        lines.append("_Not yet available -- run `scripts/verify_tokenizers.py`._")
        lines.append("")

    model_report_path = REPO_ROOT / "data" / "manifests" / "model_verification_report.json"
    if model_report_path.exists():
        model_report = json.loads(model_report_path.read_text(encoding="utf-8"))
        lines.append("## MarianMT checkpoint resolution")
        lines.append("")
        seen = {}
        for c in model_report.get("combinations", []):
            lp = c["language_pair"]
            if lp in seen:
                continue
            seen[lp] = c.get("model_resolution", {})
        for lp, res in seen.items():
            lines.append(f"- **{lp}**: requested `{res.get('requested_identifier')}` -> status=`{res.get('status')}`. {res.get('message', '')}")
        lines.append("")

    for language_pair in ("en_ti", "en_am"):
        lines.append(f"## Results: {language_pair}")
        lines.append("")
        out_dir = results_dir(language_pair)
        summary_path = out_dir / "summary.csv"
        if summary_path.exists():
            lines.append("### Mean +/- SD validation chrF++ by tokenizer")
            lines.append("")
            lines.append("| Tokenizer | Seeds | Validation chrF++ (mean) | Validation chrF++ (std) | Test chrF++ (mean) | Test chrF++ (std) |")
            lines.append("|---|---|---|---|---|---|")
            with open(summary_path, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    lines.append(
                        f"| {row['tokenizer']} | {row['seed_count']} | {row['validation_chrfpp_mean']} | "
                        f"{row['validation_chrfpp_std']} | {row['test_chrfpp_mean'] or 'n/a'} | {row['test_chrfpp_std'] or 'n/a'} |"
                    )
            lines.append("")
        else:
            lines.append("_No results yet -- run the training + evaluation + aggregation pipeline._")
            lines.append("")

        best_path = out_dir / "best_tokenizer.json"
        if best_path.exists():
            best = json.loads(best_path.read_text(encoding="utf-8"))
            lines.append(
                f"**Selected tokenizer (highest mean validation chrF++):** `{best['selected_tokenizer']}` "
                f"(mean={best['mean_validation_chrfpp']}, std={best['std_validation_chrfpp']}, "
                f"selection_split={best['selection_split']})"
            )
            lines.append("")

    job_manifest_path = REPO_ROOT / "results" / "job_manifest.json"
    if job_manifest_path.exists():
        jm = json.loads(job_manifest_path.read_text(encoding="utf-8"))
        n_completed = sum(1 for j in jm["jobs"] if j["status"] == "COMPLETED")
        n_failed = sum(1 for j in jm["jobs"] if j["status"] == "FAILED")
        n_missing = sum(1 for j in jm["jobs"] if j["status"] == "MISSING")
        lines.append("## Run status")
        lines.append("")
        lines.append(f"- COMPLETED: {n_completed}")
        lines.append(f"- FAILED: {n_failed}")
        lines.append(f"- MISSING: {n_missing}")
        lines.append(f"- Total expected: {len(jm['jobs'])}")
        lines.append("")
        failed = [j for j in jm["jobs"] if j["status"] == "FAILED"]
        if failed:
            lines.append("### Failed runs")
            lines.append("")
            lines.append("| Language pair | Tokenizer | Seed | SLURM job ID |")
            lines.append("|---|---|---|---|")
            for j in failed:
                lines.append(f"| {j['language_pair']} | {j['tokenizer']} | {j['seed']} | {j.get('slurm_job_id', 'n/a')} |")
            lines.append("")
            lines.append("See `results/failures.json` (local artifact) for full diagnostic messages and log paths.")
            lines.append("")

    lines.append("## Reproduction")
    lines.append("")
    lines.append("Every run's `metadata.json` (in its `experiments/<pair>/<tokenizer>/seed_<seed>/` directory) "
                  "records the exact model identifier/revision, tokenizer identifier, dataset manifest, "
                  "learning rate, batch size, epochs, optimizer, scheduler, sacrebleu version, chrF++ signature, "
                  "git commit, and timestamp needed to reproduce this run.")
    lines.append("")

    report_path = REPO_ROOT / "results" / "final_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    for language_pair in ("en_ti", "en_am"):
        print(f"=== Aggregating {language_pair} ===")
        val_rows, test_rows, seed_results = gather_language_pair(language_pair)
        out_dir = results_dir(language_pair)

        write_csv(
            val_rows,
            out_dir / "validation_per_seed.csv",
            ["language_pair", "tokenizer", "seed", "chrf_plus_plus", "bleu", "sacrebleu_version", "chrf_signature"],
        )
        write_csv(
            test_rows,
            out_dir / "test_per_seed.csv",
            ["language_pair", "tokenizer", "seed", "chrf_plus_plus", "bleu", "sacrebleu_version", "chrf_signature"],
        )

        summaries = summarize_by_tokenizer(seed_results)
        write_csv(
            [s.to_dict() for s in summaries],
            out_dir / "summary.csv",
            [
                "tokenizer",
                "seed_count",
                "validation_chrfpp_mean",
                "validation_chrfpp_std",
                "test_chrfpp_mean",
                "test_chrfpp_std",
            ],
        )
        print(f"  validation rows: {len(val_rows)}, test rows: {len(test_rows)}, tokenizer summaries: {len(summaries)}")

    job_manifest, failures = build_job_manifest_and_failures()
    (REPO_ROOT / "results" / "job_manifest.json").write_text(json.dumps(job_manifest, indent=2), encoding="utf-8")
    (REPO_ROOT / "results" / "failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")

    n_completed = sum(1 for j in job_manifest["jobs"] if j["status"] == "COMPLETED")
    n_failed = sum(1 for j in job_manifest["jobs"] if j["status"] == "FAILED")
    n_missing = sum(1 for j in job_manifest["jobs"] if j["status"] == "MISSING")
    print(f"\nJob manifest: {n_completed} COMPLETED, {n_failed} FAILED, {n_missing} MISSING (of {len(job_manifest['jobs'])} expected).")

    report_path = generate_final_report()
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
