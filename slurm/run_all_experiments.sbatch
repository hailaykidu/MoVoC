#!/usr/bin/env bash
# NOT an sbatch script itself (no #SBATCH directives) -- this is a small
# driver invoked by slurm/pipeline.sbatch's "full" stage. It submits the
# 18-way training array, the 18-way validation-evaluation array (chained
# afterok the training array), and the aggregation job (chained afterok
# the evaluation array), then prints the submitted job IDs.
#
# You normally do not run this file directly -- run
# `PIPELINE_STAGE=full sbatch slurm/pipeline.sbatch`, which calls this
# script for you after verification+smoke test have already passed.
set -euo pipefail

# NOTE: sbatch copies the script to a root-owned spool dir before executing,
# so BASH_SOURCE[0]-derived paths break under sbatch. Use SLURM_SUBMIT_DIR
# (repo root, per the `cd repo && sbatch slurm/...` usage contract) with a
# BASH_SOURCE fallback for direct (non-sbatch) invocation.
if [ -n "${SLURM_SUBMIT_DIR:-}" ] && [ -f "${SLURM_SUBMIT_DIR}/pyproject.toml" ]; then
    REPO_ROOT="${SLURM_SUBMIT_DIR}"
else
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
cd "${REPO_ROOT}"
mkdir -p slurm/logs

echo "[run_all_experiments] Submitting 18-way training array..."
TRAIN_JOB_ID=$(sbatch --parsable slurm/train_one.sbatch)
echo "[run_all_experiments] train array job id: ${TRAIN_JOB_ID}"

echo "[run_all_experiments] Submitting 18-way validation-evaluation array (afterok:${TRAIN_JOB_ID})..."
EVAL_JOB_ID=$(sbatch --parsable --dependency=afterok:"${TRAIN_JOB_ID}" slurm/evaluate_all.sbatch)
echo "[run_all_experiments] eval array job id: ${EVAL_JOB_ID}"

echo "[run_all_experiments] Submitting aggregation job (afterok:${EVAL_JOB_ID})..."
AGG_JOB_ID=$(sbatch --parsable --dependency=afterok:"${EVAL_JOB_ID}" slurm/aggregate.sbatch)
echo "[run_all_experiments] aggregate job id: ${AGG_JOB_ID}"

python3 - "$TRAIN_JOB_ID" "$EVAL_JOB_ID" "$AGG_JOB_ID" <<'PYEOF'
import json, sys
from pathlib import Path
train_id, eval_id, agg_id = sys.argv[1:4]
status_path = Path("results/pipeline_status.json")
status_path.parent.mkdir(parents=True, exist_ok=True)
status = {}
if status_path.exists():
    status = json.loads(status_path.read_text(encoding="utf-8"))
status["full_stage"] = {
    "train_array_job_id": train_id,
    "eval_array_job_id": eval_id,
    "aggregate_job_id": agg_id,
    "submitted": True,
}
status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
PYEOF

echo "[run_all_experiments] Submitted. Track with: squeue -u \$USER"
echo "[run_all_experiments] Once ${AGG_JOB_ID} completes, inspect results/final_report.md and results/*/best_tokenizer.json."
