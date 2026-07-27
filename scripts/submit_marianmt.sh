#!/bin/bash
#SBATCH --job-name=movoc-mt
#SBATCH --partition=ampere
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/mt_%x_%j.out
#SBATCH --error=logs/mt_%x_%j.err

# Extrinsic evaluation, paper Sec 4.3: MarianMT fine-tuning.
# Resources match the reported setup -- 1 GPU, 6 CPU cores, 32 GB RAM,
# 24 h maximum runtime.
#
# usage: sbatch submit_marianmt.sh <strategy> <language> <src> <tgt> [dev.en dev.xx]

set -euo pipefail

STRATEGY=${1:?usage: submit_marianmt.sh <strategy> <language> <src> <tgt> [dev.en dev.xx]}
LANGUAGE=${2:?}
SRC=${3:?}
TGT=${4:?}
DEV_SRC=${5:-}
DEV_TGT=${6:-}

DEV_ARGS=()
if [[ -n "$DEV_SRC" && -n "$DEV_TGT" ]]; then
    DEV_ARGS=(--valid-source "$DEV_SRC" --valid-reference "$DEV_TGT")
fi

mkdir -p logs models

python evaluation/finetune_marianmt.py \
    --strategy "$STRATEGY" --language "$LANGUAGE" \
    --source "$SRC" --target "$TGT" \
    --output-dir "models/mt_${LANGUAGE}_${STRATEGY}" \
    "${DEV_ARGS[@]}"
