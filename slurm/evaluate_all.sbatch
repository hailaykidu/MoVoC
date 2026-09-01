#!/usr/bin/env bash
#SBATCH --job-name=mtcmp-eval
#SBATCH --partition=ampere
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --array=0-17
#SBATCH --output=slurm/logs/eval_%A_%a.out
#SBATCH --error=slurm/logs/eval_%A_%a.err
# --account=<YOUR_ACCOUNT>   # <-- set this if your site requires an explicit account.
#
# Validation-set evaluation for all 18 runs (same array index mapping as
# train_one.sbatch). Test-set evaluation is intentionally NOT performed
# here -- see slurm/pipeline.sbatch and scripts/select_best_tokenizer.py:
# the held-out test set is only evaluated for the tokenizer selected by
# mean validation chrF++, as a separate, later step.
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

echo "=== Array task ${IDX}: evaluate language_pair=${LANGUAGE_PAIR} tokenizer=${TOKENIZER} seed=${SEED} (validation) ==="

python3 scripts/evaluate.py --language_pair "${LANGUAGE_PAIR}" --tokenizer "${TOKENIZER}" --seed "${SEED}" --split validation
