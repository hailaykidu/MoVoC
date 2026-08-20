#!/usr/bin/env bash
#SBATCH --job-name=mtcmp-aggregate
#SBATCH --partition=ampere
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=slurm/logs/aggregate_%j.out
#SBATCH --error=slurm/logs/aggregate_%j.err
# --account=<YOUR_ACCOUNT>   # <-- set this if your site requires an explicit account.
# CPU-only step: aggregates CSV/JSON results and writes final_report.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "${REPO_ROOT}/slurm/logs"
# shellcheck disable=SC1091
source "${REPO_ROOT}/slurm/env_setup.sh"

echo "=== Aggregating results (validation-only summary at this stage) ==="
python3 scripts/aggregate_results.py

echo "=== Selecting best tokenizer per language pair (validation chrF++ only) ==="
python3 scripts/select_best_tokenizer.py || true
# `|| true`: select_best_tokenizer.py exits 1 if a language pair has no
# completed runs yet, which is expected mid-sweep; the pipeline driver
# (pipeline.sbatch) checks results/pipeline_status.json rather than this
# job's own exit code to decide whether the full sweep succeeded.
