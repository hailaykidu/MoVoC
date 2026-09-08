# Experiment Status

This document tracks the status of the 18 MarianMT fine-tuning runs (2 language pairs × 3 tokenizers × 3 seeds) as of 2026-09-01.

## Summary

| Language Pair | Tokenizer   | Seeds | Status | Notes |
|---------------|-------------|-------|--------|-------|
| **en_ti**     | BPE         | 42,43,44 | ❓ | Not yet started or status unknown |
| **en_ti**     | WordPiece   | 42,43,44 | ❓ | Not yet started or status unknown |
| **en_ti**     | MoVoC-Tok   | 42,43,44 | ❓ | Not yet started or status unknown |
| **en_am**     | BPE         | 42 | **❌ FAILED** | See details below |
| **en_am**     | BPE         | 43,44 | ❓ | Not yet started or status unknown |
| **en_am**     | WordPiece   | 42,43,44 | ❓ | Not yet started or status unknown |
| **en_am**     | **MoVoC-Tok** | **42,43** | ❓ | Not yet started or status unknown |
| **en_am**     | **MoVoC-Tok** | **44** | **⚠️ INCOMPLETE** | See details below |

## Detailed Status

### ❌ EN→AM BPE seed 42: FAILED

**Status:** `FAILED`  
**Date:** 2026-08-28  
**Root Cause:** `resume_from_checkpoint=True` hardcoded in `training.py:192` without checking if a checkpoint exists.

**What happened:**
- Job started with an empty checkpoints directory
- Code attempted `trainer.train(resume_from_checkpoint=True)` unconditionally
- Trainer raised `ValueError: No valid checkpoint found in output directory`
- No checkpoint was ever created; job failed immediately

**Error log:**
```
ValueError: No valid checkpoint found in output directory 
(/experiments/en_am/bpe/seed_42/checkpoints)
```

**Action needed:** 
- ✓ **FIXED** in current code: `training.py:191-192` now uses conditional resume:
  ```python
  resume_checkpoint = checkpoint_dir if checkpoint_dir.exists() and any(checkpoint_dir.iterdir()) else None
  trainer.train(resume_from_checkpoint=resume_checkpoint)
  ```
- **Next step:** Resubmit this run with the corrected code

---

### ⚠️ EN→AM MoVoC-Tok seed 44: INCOMPLETE

**Status:** `INCOMPLETE`  
**Training Attempts:** [Job IDs] (see experiments/ directory for checkpoint history)  
**Latest Checkpoint:** `checkpoint-10000` (reached ~10K steps)

**What happened:**
1. **Training Attempt 1:** Manually cancelled after reaching `checkpoint-10000`
   - Walltime: 12 hours allocated; ran ~8-10 hours
   - Training completed to `max_steps=10000` (partial run, not full training)
   
2. **Training Attempt 2:** Restarted to complete evaluation, but got stuck
   - Training previously completed; resumed from `checkpoint-10000`
   - Job hung on `trainer.predict()` for 9+ hours trying to evaluate full 752,900-example validation set
   - Cancelled after exceeding 12-hour walltime

**Scale of the problem:**
- **Target:** Full training run ≈ 8.47M steps (estimated 102 hours on A100 GPU)
- **Actual:** Reached 10K steps (0.12% of target; ~6 minutes of training)
- **Evaluation bottleneck:** 752,900 validation examples × beam search = hours of inference

**Evaluation artifact (excluded from paper):**
- **File:** `experiments/en_am/movoc_tok/seed_44/validation_results.json`
- **Date:** 2026-08-31 13:12:31Z
- **Metrics:**
  - chrF++: 2.3606
  - BLEU: 0.0127
- **Why excluded:**
  - Evaluated on **10K-example subset** (1.3% of full validation set), not full 752.9K
  - Used **greedy decoding** (num_beams=1), different from paper's beam search
  - Makes this incomparable to properly-conducted evaluations
  - **Not included in any paper table or analysis**

**Action needed:**

Option A (Recommended): **Complete training run**
- Allocate ≥ 110 hours walltime for a full-length run
- Re-run from scratch (or resume from checkpoint if resubmitting soon)
- Let full training complete to natural convergence

Option B: **Accept reduced-step protocol consistently**
- Explicitly decide to use `max_steps=10000` for ALL 18 runs
- Re-run all incomplete/untouched runs with this reduced step target
- Re-evaluate all runs consistently on same subset and decoding settings
- This would make results comparable, but deviates from experimental protocol

---

## Files Modified for Recovery

**Fixed code:**
- `src/marianmt_comparison/training.py:191-192` — conditional resume_from_checkpoint

**New evaluation utilities:**
- `scripts/evaluate_checkpoint.py` — full validation set evaluation with beam search
- `scripts/evaluate_checkpoint_fast.py` — fast evaluation on validation subset

**Status tracking:**
- `experiments/en_am/bpe/seed_42/status.json` — updated with reason and action
- `experiments/en_am/movoc_tok/seed_44/status.json` — updated with detailed context
- `docs/experiment_status.md` — this file

---

## Running Next

When resuming experiments:

### Re-run EN→AM BPE seed 42 (quick fix):
```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison
sbatch slurm/train_one.sbatch  # Will pick up array task from SLURM_ARRAY_TASK_ID
# Or explicitly:
MAX_STEPS=none python3 scripts/train.py --language_pair en_am --tokenizer bpe --seed 42
```

### Complete EN→AM MoVoC seed 44 training:
```bash
# Requires ~110 hours walltime
sbatch -t 120:00:00 slurm/train_one.sbatch
# Or with explicit seed:
MAX_STEPS=none python3 scripts/train.py --language_pair en_am --tokenizer movoc_tok --seed 44
```

### Monitor queue:
```bash
squeue -u teklehaymanot
squeue -j <JOB_ID> -o "%.20j %.2t %.10M %.10L %.20N"
```

---

## Reference

- Experimental protocol: `docs/experimental_protocol.md`
- SLURM submission protocol: `docs/slurm_protocol.md`
- Job manifest: `results/job_manifest.json` (auto-generated after pipeline)
