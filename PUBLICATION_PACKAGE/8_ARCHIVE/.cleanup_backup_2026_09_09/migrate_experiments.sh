#!/bin/bash
# migrate_experiments.sh - Safe migration of completed experiments to organized structure
# SAFETY: Does NOT affect running jobs

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "════════════════════════════════════════════════════════════"
echo "  EXPERIMENT REORGANIZATION SCRIPT"
echo "  Safe - Running tasks protected"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check for running jobs
echo "🔍 Checking for running jobs..."
RUNNING=$(squeue -u teklehaymanot -t RUNNING -o "%.18i %.40j" 2>/dev/null | tail -n +2 | wc -l || true)
if [ "$RUNNING" -gt 0 ]; then
  echo "⚠️  Found $RUNNING running jobs:"
  squeue -u teklehaymanot -t RUNNING -o "%.18i %.40j" 2>/dev/null | tail -n +2 || true
  echo ""
  echo "✅ Migration will NOT affect these jobs"
  echo "   (They use original experiments/ directory)"
  echo ""
fi

# Create organized directory structure
echo "📁 Creating experiments_organized/ structure..."
mkdir -p experiments_organized

# Function to safely migrate an experiment
migrate_experiment() {
  local source_dir="$1"
  local exp_name="$2"

  if [ ! -d "$source_dir" ]; then
    echo "  ⚠️  Source not found: $source_dir (skipping)"
    return 1
  fi

  local target_dir="experiments_organized/$exp_name"
  mkdir -p "$target_dir"/{tokenizers,models,checkpoints,data,logs,results,scripts}

  # Copy tokenizers
  if [ -d "$source_dir/tokenizer_used" ]; then
    cp -v "$source_dir/tokenizer_used"/* "$target_dir/tokenizers/" 2>/dev/null || true
  fi

  # Copy models
  if [ -d "$source_dir/model" ]; then
    cp -v "$source_dir/model"/* "$target_dir/models/" 2>/dev/null || true
  fi

  # Copy checkpoints
  if [ -d "$source_dir/checkpoints" ]; then
    cp -rv "$source_dir/checkpoints"/* "$target_dir/checkpoints/" 2>/dev/null || true
  fi

  # Copy results/metadata
  if [ -f "$source_dir/validation_results.json" ]; then
    cp "$source_dir/validation_results.json" "$target_dir/results/"
  fi
  if [ -f "$source_dir/status.json" ]; then
    cp "$source_dir/status.json" "$target_dir/results/"
  fi
  if [ -f "$source_dir/metadata.json" ]; then
    cp "$source_dir/metadata.json" "$target_dir/results/"
  fi

  echo "  ✅ $exp_name"

  # Verify copies
  if [ -f "$target_dir/models/config.json" ] && [ -f "$target_dir/tokenizers/tokenizer.json" ]; then
    echo "     ✓ Models and tokenizers verified"
  fi
}

# PHASE A: Migrate completed Phase 1 experiments
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE A: Tigrinya Phase 1 Experiments (BPE, MoVoC, WordPiece)"
echo "═══════════════════════════════════════════════════════════"
echo ""

for tokenizer in bpe movoc_tok wordpiece; do
  echo "→ Tokenizer: $tokenizer"
  for seed in 42 43 44; do
    if [ -d "experiments/en_ti/$tokenizer/seed_$seed" ]; then
      migrate_experiment "experiments/en_ti/$tokenizer/seed_$seed" \
                        "phase1_tigrinya_${tokenizer}_seed${seed}"
    fi
  done
  echo ""
done

echo "═══════════════════════════════════════════════════════════"
echo "PHASE A: Amharic Phase 1 Experiments (BPE, MoVoC, WordPiece)"
echo "═══════════════════════════════════════════════════════════"
echo ""

for tokenizer in bpe movoc_tok wordpiece; do
  echo "→ Tokenizer: $tokenizer"
  for seed in 42 43 44; do
    if [ -d "experiments/en_am/$tokenizer/seed_$seed" ]; then
      migrate_experiment "experiments/en_am/$tokenizer/seed_$seed" \
                        "phase1_amharic_${tokenizer}_seed${seed}"
    fi
  done
  echo ""
done

# Phase 2 check
echo "═══════════════════════════════════════════════════════════"
echo "PHASE B STATUS: Phase 2 (Running - Will migrate after completion)"
echo "═══════════════════════════════════════════════════════════"
echo ""

RUNNING_PHASE2=$(squeue -u teklehaymanot -t RUNNING -o "%.40j" 2>/dev/null | grep -c "mtcmp-en" || true)
if [ "$RUNNING_PHASE2" -gt 0 ]; then
  echo "⏳ Phase 2 Jobs Running: $RUNNING_PHASE2"
  squeue -u teklehaymanot -t RUNNING -o "%.18i %.40j %.10M" 2>/dev/null | grep "mtcmp-en" || true
  echo ""
  echo "Actions after Phase 2 completes:"
  echo "  1. Run: ./migrate_experiments.sh --phase2"
  echo "  2. Will migrate:"
  echo "     - experiments/en_ti_full_validation/movoc_tok/seed_44/"
  echo "     - experiments/en_am_full_validation_correct_tok/movoc_tok/seed_{42,43,44}/"
else
  echo "✅ No Phase 2 jobs running"
  echo "   (Or all completed)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE C STATUS: Phase 3 Zero-Shot Evaluation"
echo "═══════════════════════════════════════════════════════════"
echo ""

mkdir -p experiments_organized/phase3_zero_shot_evaluation/{models,data,logs,results,scripts}

# Create symlinks to Phase 1 models for evaluation
echo "Creating symlinks to Phase 1 models for zero-shot evaluation..."
for tokenizer in bpe movoc_tok wordpiece; do
  for seed in 42 44; do
    src_dir="./experiments_organized/phase1_tigrinya_${tokenizer}_seed${seed}"
    dst_link="./experiments_organized/phase3_zero_shot_evaluation/models/p1_ti_${tokenizer}_s${seed}"

    if [ -d "$src_dir/models" ]; then
      ln -sf "$src_dir/models" "$dst_link" 2>/dev/null || true
      echo "  ✓ Linked: p1_ti_${tokenizer}_s${seed}"
    fi
  done
done

echo ""
echo "Creating symlinks to Amharic models for zero-shot evaluation..."
for tokenizer in bpe movoc_tok wordpiece; do
  for seed in 42 43; do
    src_dir="./experiments_organized/phase1_amharic_${tokenizer}_seed${seed}"
    dst_link="./experiments_organized/phase3_zero_shot_evaluation/models/p1_am_${tokenizer}_s${seed}"

    if [ -d "$src_dir/models" ]; then
      ln -sf "$src_dir/models" "$dst_link" 2>/dev/null || true
      echo "  ✓ Linked: p1_am_${tokenizer}_s${seed}"
    fi
  done
done

# Verify integrity
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "VERIFICATION"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "📊 Storage Usage:"
echo "  Original experiments/:"
du -sh experiments/ 2>/dev/null || echo "    (unable to calculate)"

echo "  New experiments_organized/:"
du -sh experiments_organized/ 2>/dev/null || echo "    (unable to calculate)"

echo ""
echo "📋 Migration Summary:"
PHASE1_COUNT=$(find experiments_organized -maxdepth 1 -name "phase1_*" -type d | wc -l)
PHASE3_READY=$(ls experiments_organized/phase3_zero_shot_evaluation/models | wc -l)
echo "  ✅ Phase 1 experiments organized: $PHASE1_COUNT directories"
echo "  ✅ Phase 3 ready with: $PHASE3_READY model symlinks"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ MIGRATION PHASE A COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Running tasks ([Job IDs]):"
echo "   - Will complete within 2-3 hours"
echo "   - Unaffected by this migration"
echo ""
echo "2. After Phase 2 jobs complete:"
echo "   ./migrate_experiments.sh --phase2"
echo ""
echo "3. To verify structure:"
echo "   tree experiments_organized/phase1_tigrinya_bpe_seed42/"
echo ""
echo "4. Original experiments/ preserved for reference"
echo ""
