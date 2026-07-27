#!/bin/bash
#SBATCH --job-name=movoc-marianmt
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=evaluation/results/marianmt_%j.out
#SBATCH --error=evaluation/results/marianmt_%j.err

# Extrinsic evaluation, paper Sec 4.3: MarianMT fine-tuning.
# Resources match the reported setup -- 1 GPU, 6 CPU cores, 32 GB RAM,
# 24 h maximum runtime. The environment is Conda-managed for
# reproducibility; set MOVOC_ENV to the environment name.

set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${MOVOC_ENV:-movoc}"

SRC=${1:?usage: submit_marianmt.sh <source.en> <target.xx> <output-dir>}
TGT=${2:?}
OUT=${3:?}

python evaluation/finetune_marianmt.py \
    --source "$SRC" \
    --target "$TGT" \
    --output-dir "$OUT"
