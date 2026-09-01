#!/usr/bin/env bash
#SBATCH --job-name=mtcmp-train
#SBATCH --partition=ampere
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --array=0-17
#SBATCH --output=slurm/logs/train_%A_%a.out
#SBATCH --error=slurm/logs/train_%A_%a.err
# --account=<YOUR_ACCOUNT>   # <-- set this if your site requires an explicit account.
#
# Array index -> fixed (language_pair, tokenizer, seed) triple. This mapping
# is deterministic and MUST NOT change between submissions -- retries must
# resubmit the exact same array index (and hence the exact same
# configuration; see docs/slurm_protocol.md "no-hyperparameter-changes" policy).
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
mkdir -p "${REPO_ROOT}/slurm/logs"
# shellcheck disable=SC1091
source "${REPO_ROOT}/slurm/env_setup.sh"

LANGUAGE_PAIRS=(en_ti en_am)
TOKENIZERS=(bpe wordpiece movoc_tok)
SEEDS=(42 43 44)

IDX=${SLURM_ARRAY_TASK_ID}
N_TOK=${#TOKENIZERS[@]}
N_SEED=${#SEEDS[@]}
N_PER_LP=$((N_TOK * N_SEED))

LP_IDX=$((IDX / N_PER_LP))
REM=$((IDX % N_PER_LP))
TOK_IDX=$((REM / N_SEED))
SEED_IDX=$((REM % N_SEED))

LANGUAGE_PAIR=${LANGUAGE_PAIRS[$LP_IDX]}
TOKENIZER=${TOKENIZERS[$TOK_IDX]}
SEED=${SEEDS[$SEED_IDX]}

echo "=== Array task ${IDX}: language_pair=${LANGUAGE_PAIR} tokenizer=${TOKENIZER} seed=${SEED} ==="
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-none} SLURM_ARRAY_JOB_ID=${SLURM_ARRAY_JOB_ID:-none}"

# Optional: pass MAX_STEPS via environment variable
TRAIN_CMD="python3 scripts/train.py --language_pair \"${LANGUAGE_PAIR}\" --tokenizer \"${TOKENIZER}\" --seed \"${SEED}\""
if [ -n "${MAX_STEPS:-}" ]; then
    TRAIN_CMD="$TRAIN_CMD --max_steps ${MAX_STEPS}"
    echo "Training with max_steps=${MAX_STEPS}"
fi

eval "$TRAIN_CMD"
STATUS=$?

# Record the SLURM job id into the run's status.json for job_manifest.json.
RUN_DIR="${REPO_ROOT}/experiments/${LANGUAGE_PAIR}/${TOKENIZER}/seed_${SEED}"
python3 - "$RUN_DIR" "${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-unknown}}_${SLURM_ARRAY_TASK_ID:-0}" <<'PYEOF'
import json, sys
from pathlib import Path
run_dir = Path(sys.argv[1])
job_id = sys.argv[2]
status_path = run_dir / "status.json"
if status_path.exists():
    d = json.loads(status_path.read_text(encoding="utf-8"))
    d["slurm_job_id"] = job_id
    d["log_path"] = f"slurm/logs/train_{job_id}.out"
    status_path.write_text(json.dumps(d, indent=2), encoding="utf-8")
PYEOF

exit ${STATUS}
