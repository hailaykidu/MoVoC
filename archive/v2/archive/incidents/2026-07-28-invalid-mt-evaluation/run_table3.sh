#!/bin/bash
# Table 3 extrinsic evaluation (paper Sec 5.1).
# 4 tokenizers x 2 languages x 2 directions, OPUS test sets, BLEU + chrF++.
# Nothing about tokenization, vocabulary, preprocessing or decoding is
# altered here: each checkpoint decodes with the tokenizer it was trained
# with, and translate_eval.py supplies the settings from Sec 4.3.
set -u
cd "$(dirname "$0")/../.."
OUT=evaluation/results
for lang in amharic tigrinya; do
  case $lang in
    amharic)  code=am ;;
    tigrinya) code=ti ;;
  esac
  for tok in marian movoc_tok bpe wordpiece; do
    M=movoc/models/mt_${lang}_${tok}
    [ -d "$M" ] || { echo "SKIP missing $M"; continue; }
    for dir in en-${code} ${code}-en; do
      if [ "$dir" = "en-${code}" ]; then
        S=movoc/data/evaluation/$lang/test.en; R=movoc/data/evaluation/$lang/test.${code}
      else
        S=movoc/data/evaluation/$lang/test.${code}; R=movoc/data/evaluation/$lang/test.en
      fi
      echo "=== $lang $tok $dir ==="
      python movoc/evaluation/translate_eval.py \
        --model "$M" --source "$S" --reference "$R" --direction "$dir" \
        -o ${OUT}/${lang}_${tok}.json 2>&1 | tee -a ${OUT}/logs/${lang}_${tok}.log
    done
  done
done
echo "=== DONE ==="
