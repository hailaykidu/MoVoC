#!/usr/bin/env bash
#SBATCH --job-name=mtcmp-smoke
#SBATCH --partition=ampere
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=slurm/logs/smoke_%j.out
#SBATCH --error=slurm/logs/smoke_%j.err
# --account=<YOUR_ACCOUNT>   # <-- set this if your site requires an explicit account; `sacctmgr show associations user=$USER` lists yours.
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

echo "=== Smoke test: en_ti / bpe / seed 42 / small subset ==="
python3 scripts/train.py --smoke_test
echo "=== Smoke test PASSED ==="
