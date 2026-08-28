#!/bin/bash
#SBATCH --job-name=movoc-mt-eval
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=evaluation/results/mt_eval_%j.out
#SBATCH --error=evaluation/results/mt_eval_%j.err

# Extrinsic evaluation, paper Sec 5.1: BLEU and chrF++ for the fine-tuned
# MarianMT model. Resources match the reported setup.

set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${MOVOC_ENV:-movoc}"

MODEL=${1:?usage: submit_translate_eval.sh <model-dir> <src> <ref> <direction>}
SRC=${2:?}
REF=${3:?}
DIR=${4:?}

python evaluation/translate_eval.py \
    --model "$MODEL" --source "$SRC" --reference "$REF" --direction "$DIR"
