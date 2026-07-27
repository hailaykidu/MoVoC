#!/bin/bash
# Table 3: train and evaluate all three tokenizer strategies.
#
# The tokenizer is the only experimental variable -- every arm shares the
# same preprocessing, training data, model architecture, optimizer,
# learning-rate schedule, batch size, epoch count, and decoding parameters.
#
# Evaluation data is external, never carved out of the training corpus:
#   Amharic, Tigrinya  FLORES-200 dev for validation (Goyal et al., 2022)
#   all languages      100 OPUS sentence pairs for the final test
#
# usage: run_table3.sh <language> <train.en> <train.xx> <test.en> <test.xx> [dev.en dev.xx]

set -euo pipefail

LANG_=${1:?usage: run_table3.sh <language> <train.en> <train.xx> <test.en> <test.xx> [dev.en dev.xx]}
TRAIN_SRC=${2:?}
TRAIN_TGT=${3:?}
TEST_SRC=${4:?}
TEST_TGT=${5:?}
DEV_SRC=${6:-}
DEV_TGT=${7:-}

DEV_ARGS=()
if [[ -n "$DEV_SRC" && -n "$DEV_TGT" ]]; then
    DEV_ARGS=(--valid-source "$DEV_SRC" --valid-reference "$DEV_TGT")
fi

for STRATEGY in movoc_tok bpe wordpiece; do
    OUT="models/mt_${LANG_}_${STRATEGY}"
    echo "=== $STRATEGY / $LANG_ ==="

    python evaluation/finetune_marianmt.py \
        --strategy "$STRATEGY" --language "$LANG_" \
        --source "$TRAIN_SRC" --target "$TRAIN_TGT" \
        --output-dir "$OUT" "${DEV_ARGS[@]}"

    # Every arm is scored on the same external OPUS test set.
    python evaluation/translate_eval.py \
        --model "$OUT" \
        --source "$TEST_SRC" --reference "$TEST_TGT" \
        --direction "en-${LANG_:0:2}" \
        --out "evaluation/results/table3_${LANG_}_${STRATEGY}.json"
done
