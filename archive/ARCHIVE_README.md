# Archive: Incomplete & Failed Experiments

**Purpose:** Preserve incomplete training runs and failed experiments without cluttering the main repository

**Structure:**
```
archive/
└── incomplete_experiments/
    └── en_am/
        ├── bpe/
        │   └── seed_42_failed/          (Failed run)
        └── movoc_tok/
            └── seed_44_incomplete/      (Incomplete run)
```

---

## Contents

### EN→AM BPE Seed 42 (FAILED)

**Location:** `archive/incomplete_experiments/en_am/bpe/seed_42_failed/`

**Status:** Training failed

**Reason:** Checkpoint resume error during training initialization
- Error: `No valid checkpoint found in output directory`
- Cause: `resume_from_checkpoint=True` was hardcoded without checking if checkpoint exists
- Date: 2026-08-28
- Result: No model checkpoint, no validation_results.json

**Files:**
- `checkpoints/` — Empty (no checkpoints created)
- `embedding_adaptation_report.json` — Partial metadata

**Recommendation:** This run can be restarted with corrected training code if needed.

---

### EN→AM MoVoC-Tok Seed 44 (INCOMPLETE)

**Location:** `archive/incomplete_experiments/en_am/movoc_tok/seed_44_incomplete/`

**Status:** Training incomplete (~0.12% of full run)

**Reason:** Insufficient GPU time allocation
- Target: 8,470,130 training steps (~102 hours GPU time)
- Reached: checkpoint-10000 (~0.12% of target)
- Walltime limit: 12 hours per job
- Result: Manually cancelled training attempts (2 total)

**Files:**
- `checkpoints/checkpoint-3388052/` — Partial training checkpoint
- `checkpoints/checkpoint-4235065/` — Partial training checkpoint
- `validation_results.json` — Evaluation on subset (NOT comparable to full runs)
  - Evaluated on 10K of 752.9K validation examples
  - Used greedy decoding (num_beams=1), not beam search
  - BLEU: 0.0127 | ChrF++: 2.36 | Date: 2026-08-31

**Recommendation:** Either:
1. Complete the full training run with increased GPU time allocation (>110 hours)
2. Accept the incomplete run as preliminary result (not comparable to other cells)
3. Implement reduced-step protocol consistently across all runs

---

## Why Archive?

**Rationale for moving to archive:**

1. **Cleaner main repository** — Experiments/ contains only complete, comparable experiments
2. **Preserved git history** — Files moved (not deleted) using `git mv`, preserving all history
3. **Available for reference** — Incomplete runs remain in archive for future analysis
4. **Clear publication** — TABLE_3_FINAL_CLEAN.md excludes incomplete data, marking them as archived

**Impact on git logs:**
- ✅ All commit history preserved
- ✅ Author information intact
- ✅ Dates and messages unchanged
- ✅ Only file paths updated (via `git mv`)
- ✅ No data lost

---

## Accessing Archived Data

### To view an archived experiment:

```bash
# View failed BPE seed 42
ls archive/incomplete_experiments/en_am/bpe/seed_42_failed/

# View incomplete MoVoC-Tok seed 44
ls archive/incomplete_experiments/en_am/movoc_tok/seed_44_incomplete/
```

### To restore to main experiments (if needed):

```bash
git mv archive/incomplete_experiments/en_am/bpe/seed_42_failed experiments/en_am/bpe/seed_42
git mv archive/incomplete_experiments/en_am/movoc_tok/seed_44_incomplete experiments/en_am/movoc_tok/seed_44
```

---

## Publication Status

**Main Results (Published):** 16/18 experiments
- EN→TI: 9/9 complete ✅
- EN→AM: 7/9 complete ✅
  - BPE: 2/3 (seed 42 archived)
  - WordPiece: 3/3 ✅
  - MoVoC-Tok: 2/3 (seed 44 archived)

**Archived (Not Published):** 2/18 experiments
- EN→AM BPE seed 42 — FAILED
- EN→AM MoVoC-Tok seed 44 — INCOMPLETE

**Result:** Clean, publication-ready repository with complete results + archived incomplete runs

---

## Git Commands Used

```bash
# Create archive structure
mkdir -p archive/incomplete_experiments/en_am/{bpe,movoc_tok}

# Move with git (preserves history)
git mv experiments/en_am/bpe/seed_42 \
  archive/incomplete_experiments/en_am/bpe/seed_42_failed

git mv experiments/en_am/movoc_tok/seed_44 \
  archive/incomplete_experiments/en_am/movoc_tok/seed_44_incomplete

# Commit with message
git add archive/ results/
git commit -m "Archive incomplete experiments to clean repository

- Move EN→AM BPE seed_42 (failed) to archive
- Move EN→AM MoVoC-Tok seed_44 (incomplete) to archive
- Create clean TABLE_3_FINAL.md with 16 comparable experiments only
- Preserve all git history via git mv (not delete)
- Archive structure documents incomplete data separately

Result: Publication-ready repository with 16/18 complete experiments
Main results in results/TABLE_3_FINAL_CLEAN.md
Incomplete runs preserved in archive/incomplete_experiments/"
```

---

**Generated:** 2026-09-09  
**Archive Strategy:** Move incomplete data, preserve git history, publish clean results  
**Status:** Ready for deployment

