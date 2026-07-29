#!/bin/bash
# Reconstructed evaluation following the MoVoC experimental methodology.
# Six runs: 3 tokenizers x 2 languages. Only the tokenizer differs; the
# backbone, data policy, hyperparameters, seed and decoding are identical.
#
# Checkpoints and logs are written under experiments/tokenizer_comparison/
# rather than models/, so a run is tied to this experiment.
set -euo pipefail
cd "$(dirname "$0")/../.."

CAP=1398173                      # Amharic capped to Tigrinya's corpus size
EXP=experiments/tokenizer_comparison
mkdir -p "$EXP/checkpoints" "$EXP/logs"

declare -A SRC=( [amharic]="../NLLB.am-en.en" [tigrinya]="../Machine_Translation/data/NLLB.en-ti.en" )
declare -A TGT=( [amharic]="../NLLB.am-en.am" [tigrinya]="../Machine_Translation/data/NLLB.en-ti.ti" )

for lang in amharic tigrinya; do
  for tok in bpe wordpiece movoc_tok; do
    sbatch --job-name="tc_${lang}_${tok}" \
           --partition=ampere --gres=gpu:1 --cpus-per-task=6 --mem=32G \
           --time=24:00:00 \
           --output="$EXP/logs/${lang}_${tok}_%j.out" \
           --error="$EXP/logs/${lang}_${tok}_%j.err" \
           --wrap="python evaluation/finetune_marianmt.py \
                     --strategy $tok --language $lang \
                     --source ${SRC[$lang]} --target ${TGT[$lang]} \
                     --output-dir $EXP/checkpoints/${lang}_${tok} \
                     --max-samples $CAP"
  done
done
