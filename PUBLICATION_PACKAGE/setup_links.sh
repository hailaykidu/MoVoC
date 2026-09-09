#!/bin/bash

# Navigate to publication package
cd "$(dirname "$0")"
REPO_ROOT=$(cd .. && pwd)

echo "Setting up publication package structure..."
echo ""

# Create subdirectories
mkdir -p 1_CODE 2_CONFIG 3_DATA 4_MODELS 5_RESULTS/validation_results 6_SCRIPTS 7_DOCUMENTATION 8_ARCHIVE

# 1. CODE - Link training and evaluation scripts
echo "Linking code files..."
ln -sf $REPO_ROOT/scripts/train*.py 1_CODE/ 2>/dev/null || true
ln -sf $REPO_ROOT/scripts/evaluate*.py 1_CODE/ 2>/dev/null || true
ln -sf $REPO_ROOT/scripts/zero_shot*.py 1_CODE/ 2>/dev/null || true
ln -sf $REPO_ROOT/requirements.txt . 2>/dev/null || true

# 2. CONFIG - Link YAML configurations
echo "Linking configuration files..."
ln -sf $REPO_ROOT/configs/*.yaml 2_CONFIG/ 2>/dev/null || true

# 3. DATA - Link data directories
echo "Linking data directories..."
ln -sf $REPO_ROOT/data/train 3_DATA/ 2>/dev/null || true
ln -sf $REPO_ROOT/data/test 3_DATA/ 2>/dev/null || true
ln -sf $REPO_ROOT/data/extrinsic 3_DATA/ 2>/dev/null || true

# 4. MODELS - Link all 16 complete model directories
echo "Linking 16 complete models..."
# EN→Amharic
ln -sf $REPO_ROOT/experiments/en_am/bpe/seed_43 4_MODELS/en_am_bpe_seed43
ln -sf $REPO_ROOT/experiments/en_am/bpe/seed_44 4_MODELS/en_am_bpe_seed44
ln -sf $REPO_ROOT/experiments/en_am/wordpiece/seed_42 4_MODELS/en_am_wordpiece_seed42
ln -sf $REPO_ROOT/experiments/en_am/wordpiece/seed_43 4_MODELS/en_am_wordpiece_seed43
ln -sf $REPO_ROOT/experiments/en_am/wordpiece/seed_44 4_MODELS/en_am_wordpiece_seed44
ln -sf $REPO_ROOT/experiments/en_am/movoc_tok/seed_42 4_MODELS/en_am_movoc_seed42
ln -sf $REPO_ROOT/experiments/en_am/movoc_tok/seed_43 4_MODELS/en_am_movoc_seed43

# EN→Tigrinya
ln -sf $REPO_ROOT/experiments/en_ti/bpe/seed_42 4_MODELS/en_ti_bpe_seed42
ln -sf $REPO_ROOT/experiments/en_ti/bpe/seed_43 4_MODELS/en_ti_bpe_seed43
ln -sf $REPO_ROOT/experiments/en_ti/bpe/seed_44 4_MODELS/en_ti_bpe_seed44
ln -sf $REPO_ROOT/experiments/en_ti/wordpiece/seed_42 4_MODELS/en_ti_wordpiece_seed42
ln -sf $REPO_ROOT/experiments/en_ti/wordpiece/seed_43 4_MODELS/en_ti_wordpiece_seed43
ln -sf $REPO_ROOT/experiments/en_ti/wordpiece/seed_44 4_MODELS/en_ti_wordpiece_seed44
ln -sf $REPO_ROOT/experiments/en_ti/movoc_tok/seed_42 4_MODELS/en_ti_movoc_seed42
ln -sf $REPO_ROOT/experiments/en_ti/movoc_tok/seed_43 4_MODELS/en_ti_movoc_seed43
ln -sf $REPO_ROOT/experiments/en_ti/movoc_tok/seed_44 4_MODELS/en_ti_movoc_seed44

# 5. RESULTS - Copy result files
echo "Copying result tables and validation results..."
cp $REPO_ROOT/results/TABLE_3_FINAL_CLEAN.md 5_RESULTS/ 2>/dev/null || true
cp $REPO_ROOT/results/TABLE_3_FINAL.md 5_RESULTS/ 2>/dev/null || true

# Copy individual validation results
for lang in en_am en_ti; do
  for tok in bpe wordpiece movoc_tok; do
    for seed in 42 43 44; do
      result_file="$REPO_ROOT/experiments/$lang/$tok/seed_$seed/validation_results.json"
      if [ -f "$result_file" ]; then
        cp "$result_file" "5_RESULTS/validation_results/${lang}_${tok}_seed${seed}.json" 2>/dev/null || true
      fi
    done
  done
done

# 6. SCRIPTS - Link SLURM job submission scripts
echo "Linking SLURM scripts..."
ln -sf $REPO_ROOT/slurm/*.sbatch 6_SCRIPTS/ 2>/dev/null || true

# 7. DOCUMENTATION - Link documentation files
echo "Linking documentation..."
ln -sf $REPO_ROOT/README.md 7_DOCUMENTATION/
ln -sf $REPO_ROOT/DATA_MANIFEST.md 7_DOCUMENTATION/
ln -sf $REPO_ROOT/MODEL_MANIFEST.md 7_DOCUMENTATION/
ln -sf $REPO_ROOT/CITATION.md 7_DOCUMENTATION/
ln -sf $REPO_ROOT/docs/* 7_DOCUMENTATION/ 2>/dev/null || true

# 8. ARCHIVE - Link incomplete experiments
echo "Linking archive..."
ln -sf $REPO_ROOT/archive/incomplete_experiments 8_ARCHIVE/
ln -sf $REPO_ROOT/archive/ARCHIVE_README.md 8_ARCHIVE/

echo ""
echo "✅ Publication package setup complete!"
echo ""
ls -lh

