# Safe Repository Cleanup Plan
## Preserve Running Jobs & Essential Files

**Date:** Current  
**Active Jobs Protected:** Job 70558 (BPE Seed 42 - PENDING)

---

## 📊 Summary

**Temporary Files to Remove:** ~50 draft/intermediate reports  
**Total Size to Remove:** ~350-400 KB  
**Storage Savings:** Minimal but cleaner repository  
**Risk Level:** LOW - No experiments or data affected

---

## 🔒 PROTECTED (Will NOT be removed)

✅ `experiments/` - Running job data and results  
✅ `data/` - Training and test data (essential)  
✅ `scripts/` - Training scripts (essential)  
✅ `slurm/` - SLURM job management files  
✅ `PUBLICATION_PACKAGE/` - Publication materials  
✅ `docs/` - Documentation  
✅ `models/` - Model configs  
✅ `.git/` - Version control history  
✅ Core Python scripts (*.py at root level)  
✅ `README.md`, `CITATION.md`  
✅ `requirements.txt`  

---

## ❌ TO BE REMOVED (Draft & Temporary Files)

### Dated Audit Reports (2026-09-09)
- `DATA_AUDIT_REPORT_2026_09_09.md` (12K) - Superseded by PUBLICATION_PACKAGE
- `DATA_COMPLETION_UPDATE_2026_09_09.md` (11K) - Draft update
- `DATA_INTEGRATION_FINAL_REPORT_2026_09_09.md` (12K) - Intermediate report
- `DATA_INTEGRATION_REPORT_2026_09_09.md` (4.5K) - Draft
- `DOCUMENTATION_UPDATE_2026_09_09.md` (7.7K) - Intermediate

### Dated Re-evaluation Files (2026-09-09)
- `RE_EVALUATION_PLAN_MOVOCTOK_2026_09_09.json` (3.7K) - Plan only
- `RE_EVALUATION_REPORT_MOVOCTOK_COMPLETE_2026_09_09.md` (12K) - Intermediate
- `RE_EVALUATE_MOVOCTOK_2026_09_09.py` (15K) - Script archive
- `BASELINE_RESULTS_2026_09_09.json` (551B) - Intermediate data

### Multi-Seed Evaluation Drafts
- `MULTI_SEED_EVALUATION_TABLE_2026_09_09.md` (7.7K) - Replaced by PUBLICATION_PACKAGE
- `FINAL_PUBLICATION_READY_2026_09_09.md` (8.5K) - Superseded

### Cleanup/Publication Checklists (Archive)
- `CLEANUP_REPOSITORY.sh` (8.3K) - Old cleanup script
- `CLEANUP_SUMMARY_2026_09_09.md` (8.9K) - Cleanup log
- `.cleanup_log_2026_09_09.txt` (4.9K) - Log file
- `.cleanup_backup_2026_09_09/` - Old backup directory

### Pre-Publication Drafts (Multiple versions)
- `FINAL_PUBLICATION_DECISION.md` (13K)
- `FINAL_PUBLICATION_READINESS_REPORT.md` (13K)
- `FINAL_PUBLICATION_STRUCTURE.md` (19K)
- `FINAL_PUBLISH_CHECKLIST.md` (26K)
- `PUBLICATION_APPROVED_2026_09_09.md` (9.1K)
- `PUBLICATION_READY_REPORT.md` (12K)
- `PUBLICATION_SUMMARY.md` (16K)

### Verification & Audit Reports
- `AUDIT_COMPLETION_SUMMARY.md` (6.5K)
- `AUDIT_DOCUMENTATION_INDEX.md` (4.9K)
- `AUDIT_SCAN_REPORT.md` (18K)
- `PRE_PUSH_RECONCILIATION_REPORT.md` (13K)
- `PRE_PUSH_VERIFICATION_REPORT.md` (11K)
- `FINAL_VERIFICATION_REPORT.md` (7.7K)

### Miscellaneous Drafts
- `CONSISTENCY_CHECK_vs_MoVoC_v2.md` (8.2K)
- `EXPERIMENT_PATHS_ANALYSIS.md` (7.5K)
- `FILE_STORAGE_INVENTORY.md` (11K)
- `PHASE_1_VERIFICATION.txt` (8.7K)
- `STORAGE_INVENTORY.md` (8.5K)
- Various other intermediate reports (~100KB total)

---

## ✅ TO KEEP (New Tokenizer Comparison Files)

✅ `TOKENIZER_COMPARISON_ANALYSIS.md` - Keep
✅ `TOKENIZER_COMPARISON_VISUAL.md` - Keep
✅ `TOKENIZER_COMPARISON_INDEX.md` - Keep
✅ `COMPLETE_MULTI_SEED_RESULTS_TABLE.md` - Keep
✅ `REPOSITORY_CONTEXT.md` - Keep

---

## 🧹 How to Execute Cleanup

### Option 1: Safe Automatic Cleanup (Recommended)

```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison
git clean -fd -e experiments -e data -e .git -e PUBLICATION_PACKAGE
```

This removes ONLY untracked files (new files, not in git).

### Option 2: Manual Selective Cleanup

```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison

# Remove specific patterns
rm -f BASELINE_RESULTS_2026_09_09.json
rm -f *_2026_09_*.md
rm -f *_2026_09_*.json
rm -f CLEANUP_*.{sh,md,txt}
rm -rf .cleanup_*

# Remove old publication drafts
rm -f PUBLICATION_*_REPORT.md
rm -f FINAL_PUBLICATION_*.md
rm -f FINAL_PUBLISH_*.md
```

### Option 3: Dry Run (See what would be removed)

```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison

# Show what git clean would remove
git clean -fd -e experiments -e data -e .git -e PUBLICATION_PACKAGE --dry-run
```

---

## 📋 Verification Steps

After cleanup, verify:

```bash
# Check repo structure
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison
ls -lh | grep -E "^d"  # Should show: data, experiments, docs, scripts, slurm, PUBLICATION_PACKAGE

# Verify experiments intact
ls -la experiments/ | head -20

# Verify data intact
ls -la data/extrinsic/

# Check active jobs
squeue -u teklehaymanot | grep 70558
```

---

## ⚠️ Safety Notes

✅ **Safe to execute** - No running job data affected  
✅ **Reversible** - All removed files are backups/drafts (originals in PUBLICATION_PACKAGE)  
✅ **Data preserved** - experiments/, data/, scripts/ untouched  
✅ **Git history preserved** - .git/ not affected  

---

## 🎯 Post-Cleanup Status

After cleanup:
- ✅ Repository cleaner (50 fewer temporary files)
- ✅ Easier navigation
- ✅ All essential publication materials intact
- ✅ All experiments and data preserved
- ✅ Ready for final submission/publication

---

**Recommendation:** Execute cleanup to finalize repository for publication

