#!/bin/bash
# Multi-seed tokenizer comparison -- reconstructed evaluation following the
# MoVoC evaluation protocol (Table 3 layout).
#
# 18 independent training runs: 3 tokenizers x 2 trainable languages x 3 seeds.
# Each run trains from the pretrained backbone with its own seed and writes its
# own checkpoint; no checkpoint is reused across seeds.
#
# Tigre and Ge'ez receive NO training -- they are evaluated zero-shot from every
# trained checkpoint, which is the paper's own setup for Tigre (Sec 5.1) and an
# ADDITIONAL zero-shot evaluation for Ge'ez.
#
# Training hyperparameters are unchanged from the verified configuration in
# evaluation/finetune_marianmt.py: lr 1.44e-07, 3 epochs, batch 8, max_len 128,
# linear schedule, fp32. The tokenizer and the seed are the only variables.
set -euo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJ"

CAP=1398173                # Amharic capped to Tigrinya's corpus size
EXP=experiments/multiseed
mkdir -p "$EXP"/{checkpoints,logs,predictions,results}

# Corpora as ABSOLUTE paths. sbatch --wrap does not inherit this script's
# working directory on the compute node, so relative paths resolve against
# the job's cwd and fail. Verified line counts: am-en 16,137,053 pairs;
# en-ti 1,398,173 pairs.
PARALLEL="$(cd "$PROJ/.." && pwd)"
declare -A SRC=(
  [amharic]="$PARALLEL/../NLLB.am-en.en"
  [tigrinya]="$PARALLEL/mt_finetune/data/all.en"
)
declare -A TGT=(
  [amharic]="$PARALLEL/../NLLB.am-en.am"
  [tigrinya]="$PARALLEL/mt_finetune/data/all.ti"
)

for lang in amharic tigrinya; do
  for f in "${SRC[$lang]}" "${TGT[$lang]}"; do
    [[ -f "$f" ]] || { echo "missing corpus: $f" >&2; exit 1; }
  done
done

for seed in 42 43 44; do
  for lang in amharic tigrinya; do
    for tok in bpe wordpiece movoc_tok; do
      out="$EXP/checkpoints/${lang}_${tok}_seed${seed}"
      sbatch --job-name="ms_${lang}_${tok}_s${seed}" \
             --partition=ampere --gres=gpu:1 --cpus-per-task=6 --mem=32G \
             --time=24:00:00 \
             --output="$EXP/logs/${lang}_${tok}_seed${seed}_%j.out" \
             --error="$EXP/logs/${lang}_${tok}_seed${seed}_%j.err" \
             --wrap="cd $PROJ && python evaluation/finetune_marianmt.py \
                       --strategy $tok --language $lang \
                       --source ${SRC[$lang]} --target ${TGT[$lang]} \
                       --output-dir $PROJ/$out \
                       --seed $seed \
                       --max-samples $CAP"
    done
  done
done

echo "submitted 18 runs -> $EXP/checkpoints/"
echo "score with: python scripts/score_multiseed.py"
