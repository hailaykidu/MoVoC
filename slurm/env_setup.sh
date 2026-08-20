#!/usr/bin/env bash
# Shared environment-activation snippet, sourced (not executed) by every
# sbatch script in this directory. Builds/activates a dedicated venv from
# requirements.txt -- never silently relies on whatever module happens to
# be loaded in the submitting shell.
#
# `module load conda` (or `module load mamba`) is required before `conda`
# is on PATH on this host; we use a plain venv instead to avoid depending
# on any specific named conda environment (none of the existing ones, e.g.
# `tigrinya_mt`, have the right package set -- see docs/slurm_protocol.md).
set -euo pipefail

# Trust the caller's REPO_ROOT if it already set one (every sbatch script
# that sources this file computes REPO_ROOT from SLURM_SUBMIT_DIR first,
# since BASH_SOURCE[0] is unreliable under sbatch -- see the NOTE in each
# .sbatch file). Only fall back to deriving it here for direct, non-sbatch
# sourcing of this file.
if [ -z "${REPO_ROOT:-}" ]; then
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
VENV_DIR="${REPO_ROOT}/.venv"

# System python3 on this host is already confirmed to have
# transformers==4.51.3, torch==2.5.1+cu118, sacrebleu==2.6.0,
# sentencepiece==0.2.1 (see requirements.txt). We still create an isolated
# venv so the pipeline's dependency set is pinned and reproducible
# regardless of what else changes in the base environment over time.
if [ ! -d "${VENV_DIR}" ]; then
    echo "[env_setup] Creating venv at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}" --system-site-packages
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[env_setup] Installing/verifying requirements.txt (idempotent)"
pip install --quiet --disable-pip-version-check -r "${REPO_ROOT}/requirements.txt" || {
    echo "[env_setup] WARNING: pip install reported an issue; continuing with --system-site-packages fallback (torch/transformers/sacrebleu/sentencepiece are already present system-wide)."
}

export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"
cd "${REPO_ROOT}"

echo "[env_setup] python: $(which python3)"
echo "[env_setup] repo:   ${REPO_ROOT}"
