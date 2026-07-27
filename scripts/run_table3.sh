#!/bin/bash
# Table 3: train and evaluate all three tokenizer strategies.
#
# The tokenizer is the only experimental variable -- every arm shares the
# same preprocessing, dataset split (seed 42), model architecture,
# optimizer, learning-rate schedule, batch size, epoch count, and decoding
# parameters.
#
# usage: run_table3.sh <language> <english-side> <target-side>

set -euo pipefail

LANG_=${1:?usage: run_table3.sh <language> <src.en> <tgt.xx>}
SRC=${2:?}
TGT=${3:?}

for STRATEGY in movoc_tok bpe wordpiece; do
    OUT="models/mt_${LANG_}_${STRATEGY}"
    echo "=== $STRATEGY / $LANG_ ==="

    python evaluation/finetune_marianmt.py \
        --strategy "$STRATEGY" --language "$LANG_" \
        --source "$SRC" --target "$TGT" \
        --output-dir "$OUT"

    # Every arm is scored on the held-out split written by its own run --
    # identical sentences, since the split seed is fixed.
    python evaluation/translate_eval.py \
        --model "$OUT" \
        --source "$OUT/test_split/source.txt" \
        --reference "$OUT/test_split/reference.txt" \
        --direction "en-${LANG_:0:2}" \
        --out "evaluation/results/table3_${LANG_}_${STRATEGY}.json"
done
