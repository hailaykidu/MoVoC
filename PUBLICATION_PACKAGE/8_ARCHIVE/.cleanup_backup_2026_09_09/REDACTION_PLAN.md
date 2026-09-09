# 🔍 Redaction Plan — Publication Preparation

**Purpose:** Identify all instances requiring redaction before public release  
**Scope:** Sensitive paths, job IDs, usernames  
**Status:** PLAN ONLY — No files modified yet  
**Date:** 2026-09-08

---

## 📋 PART 1: REQUIRED REDACTIONS (Before Public Release)

Critical sensitive information that must be removed or replaced.

---

### 1. README.md

**Status:** REVIEW — Contains absolute paths

#### Issue 1.1: User path reference
- **File:** `README.md`
- **Type:** Absolute path exposure
- **Current Text Location:** Multiple instances throughout file
- **Risk Level:** HIGH — Exposes user identity
- **Pattern to Find:** `/homes/neumann/teklehaymanot/marianmt-tokenizer-comparison`
- **Replacement:** `./` or `<repository-root>`
- **Estimated Instances:** 5-8

#### Issue 1.2: Email reference (check for legitimacy)
- **File:** `README.md`
- **Type:** Email address
- **Risk Level:** Check if personal or institutional
- **Action:** Review for legitimacy before redacting

**Redaction Action Plan:**
```
Search for: /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison
Replace with: ./
Or replace with: <repository-root>

Example transformation:
BEFORE: /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/data/train/
AFTER: ./data/train/
```

---

### 2. results/TABLE_3_FINAL.md

**Status:** CRITICAL — Contains job IDs and paths

#### Issue 2.1: Job ID references (in footnotes)
- **File:** `results/TABLE_3_FINAL.md`
- **Type:** SLURM job IDs in documentation
- **Instances Found:** ~15-19 throughout file
- **Risk Level:** MEDIUM — Exposes GPU cluster job tracking
- **Job IDs to Replace:**
  - 69563 (Tigrinya training)
  - 69317 (Amharic training)
  - 70088 (Zero-shot evaluation original)
  - 70153 (Zero-shot evaluation fixed)
  - 70064, 70085 (Zero-shot attempts)
  - 66832, 66902 (Training cancellations)

**Redaction Action Plan:**

**Location 2.1a:** Footnote explaining job 69563_44
```
Search for: SLURM job 69563_44
Replace with: [SLURM Job A]
Or remove entirely if just tracking note
```

**Location 2.1b:** Footnote explaining job 70088 (zero-shot error)
```
Search for: job 70088
Replace with: [SLURM Job B]
```

**Location 2.1c:** Footnote explaining job 70153 (fixed version)
```
Search for: job 70153
Replace with: [SLURM Job C]
```

**Location 2.1d:** Footnotes explaining failed runs
```
Search for: job 66832, job 66902
Replace with: [Training Job]
```

#### Issue 2.2: Absolute paths in notes
- **File:** `results/TABLE_3_FINAL.md`
- **Type:** References to `/slurm/logs/` or `/homes/` paths
- **Instances Found:** ~3-5
- **Risk Level:** MEDIUM

**Redaction Action Plan:**
```
Search for: /slurm/logs/
Replace with: <cluster-logs>/
Or just remove the path reference

Search for: /homes/neumann/
Replace with: <user-home>/
```

---

### 3. docs/experiment_status.md (or similar docs)

**Status:** REVIEW — May contain paths and references

#### Issue 3.1: Cluster paths
- **File:** `docs/experiment_status.md` (check if exists)
- **Type:** References to /slurm/, /home/, /scratch/
- **Risk Level:** MEDIUM
- **Action:** Search and replace with generic markers

**Redaction Action Plan:**
```
Search for: /slurm/logs/
Replace with: <SLURM_LOGS>/

Search for: /homes/neumann/teklehaymanot/
Replace with: <REPO_ROOT>/
```

---

### 4. docs/convergence_analysis.md (or similar)

**Status:** REVIEW — May contain job tracking references

#### Issue 4.1: Job ID references
- **File:** `docs/convergence_analysis.md`
- **Type:** Job IDs in historical notes
- **Risk Level:** LOW-MEDIUM (historical documentation)

**Redaction Action Plan:**
```
Search for: job 69563, job 69317, job 70088, etc.
Replace with: [Job X]
Or remove if only historical tracking
```

---

### 5. scripts/*.py files

**Status:** CRITICAL — May contain hardcoded paths

#### Issue 5.1: Hardcoded user paths in Python scripts
- **Files:** All `.py` files in `scripts/` directory
- **Type:** Hardcoded `/homes/neumann/teklehaymanot/` paths
- **Risk Level:** HIGH — Affects code functionality if paths are absolute
- **Estimated Files:** 5-10 scripts
- **Estimated Instances:** 10-20

**Redaction Action Plan:**

For each Python file in scripts/:
```
Search for: /homes/neumann/teklehaymanot/
Determine if hardcoded or constructed:
  - If hardcoded: Replace with Path.cwd() or configurable path
  - If in example: Replace with generic path indicator
  
Example:
BEFORE: REPO_ROOT = Path("/homes/neumann/teklehaymanot/marianmt-tokenizer-comparison")
AFTER: REPO_ROOT = Path(__file__).parent.parent  # Relative to script location
```

#### Issue 5.2: Data paths in scripts
- **Pattern:** References to data directories by absolute path
- **Action:** Review each script for path construction method
- **Risk:** May break if paths are hardcoded

**Specific Scripts to Review:**
- `scripts/train_en_ti_full_validation.py`
- `scripts/train_en_am_full_validation_correct_tok.py`
- `scripts/zero_shot_evaluation_seeds_focused.py`
- `scripts/evaluate_checkpoint.py`
- `scripts/verify_*.py`

---

### 6. src/marianmt_comparison/*.py

**Status:** CRITICAL — May contain hardcoded paths

#### Issue 6.1: Hardcoded paths in source modules
- **Files:** All `.py` files in `src/marianmt_comparison/`
- **Type:** Absolute paths to data/models/configs
- **Risk Level:** HIGH — Affects reproducibility if paths are absolute
- **Estimated Instances:** 5-15

**Redaction Action Plan:**

For each module:
```
Search for: /homes/neumann/teklehaymanot/
If found:
  - Replace with relative path: Path(__file__).parent.parent.parent / "data"
  - Or use environment variables: os.getenv("PROJECT_ROOT", ".")
  - Or pass as configuration parameter
```

**Critical Files to Check:**
- `src/marianmt_comparison/config.py` (likely contains paths)
- `src/marianmt_comparison/data.py` (likely contains data loading paths)
- `src/marianmt_comparison/training.py` (may reference model paths)

---

### 7. slurm/*.sbatch files

**Status:** REVIEW — May contain cluster-specific information

#### Issue 7.1: Paths in SLURM job scripts
- **Files:** All `.sbatch` files in `slurm/` directory
- **Type:** Absolute paths to cluster directories
- **Risk Level:** MEDIUM — Exposes cluster topology
- **Estimated Instances:** 5-10

**Redaction Action Plan:**

For each SBATCH file:
```
Search for: /homes/neumann/teklehaymanot/
Replace with: ${PROJECT_ROOT}
Or replace with: $(pwd)

Search for: /slurm/
Replace with: ${SLURM_OUTPUT_DIR}
```

#### Issue 7.2: Account codes or allocation info
- **Check:** SLURM directives like `#SBATCH --account=`
- **Action:** Remove if contains project codes
- **Risk Level:** MEDIUM if present

---

### 8. migrate_experiments.sh

**Status:** REVIEW — May contain absolute paths

#### Issue 8.1: Script paths
- **File:** `migrate_experiments.sh`
- **Type:** Shell script with absolute paths
- **Risk Level:** MEDIUM

**Redaction Action Plan:**
```
Search for: /homes/neumann/teklehaymanot/
Replace with: $(cd "$(dirname "$0")" && pwd)
Or use $PROJECT_ROOT variable
```

---

## 📋 PART 2: OPTIONAL REDACTIONS (Historical/Non-Critical)

Lower-risk items that can be redacted for cleanliness but are not critical.

---

### Optional Item 1: Job tracking in version control

**Location:** Git commit messages, release notes
**Type:** Historical job IDs
**Risk Level:** LOW (historical record)
**Action:** Can be kept for documentation value, or redact if preferred

**Example:**
```
KEEP: "Fix zero-shot evaluation script (Job 70088)"
OR REDACT TO: "Fix zero-shot evaluation script"
```

---

### Optional Item 2: CHANGELOG or historical notes

**Files:** Any CHANGELOG.md, NOTES.md, historical docs
**Type:** Job IDs and paths in historical context
**Risk Level:** LOW (not in public-facing docs by default)
**Action:** Redact for consistency, but not critical

---

### Optional Item 3: Configuration files with example paths

**Files:** configs/*.yaml, configs/*.json
**Type:** Example paths that may reference user environment
**Risk Level:** LOW if clearly marked as examples
**Action:** Optional—consider replacing with template variables

**Example:**
```
BEFORE: data_path: /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/data
AFTER: data_path: ${PROJECT_ROOT}/data
```

---

### Optional Item 4: Old SLURM logs

**Location:** slurm/logs/*.out, slurm/logs/*.err
**Type:** Historical job output files
**Risk Level:** LOW (output only)
**Action:** Can delete for cleanliness (saves 50 MB), but not required

---

## 🎯 REDACTION PRIORITY & EFFORT

### Must Do (High Priority)

| Item | Files | Instances | Effort | Impact |
|------|-------|-----------|--------|--------|
| Absolute paths in scripts/*.py | 5-10 | 10-20 | 1.5 hours | Critical for functionality |
| Paths in src/ modules | 3-5 | 5-15 | 1 hour | Critical for reproducibility |
| Job IDs in results/TABLE_3_FINAL.md | 1 | 15-19 | 30 min | Medium priority |
| SLURM script paths | 5-10 | 5-10 | 30 min | Medium priority |
| README.md paths | 1 | 5-8 | 20 min | Low-medium priority |

**Total Effort (Must Do):** 3.5-4 hours

---

### Should Do (Medium Priority)

| Item | Files | Instances | Effort | Impact |
|------|-------|-----------|--------|--------|
| Paths in docs/ | 3-5 | 5-10 | 30 min | Documentation consistency |
| migrate_experiments.sh paths | 1 | 3-5 | 15 min | Script functionality |
| Config template paths | 3-5 | 5-10 | 20 min | Configuration clarity |

**Total Effort (Should Do):** 1-1.5 hours

---

### Nice to Do (Low Priority)

| Item | Files | Instances | Effort | Impact |
|------|-------|-----------|--------|--------|
| Job IDs in historical notes | Multiple | 10-15 | 30 min | Cleanliness only |
| Old SLURM logs cleanup | Logs | ~50 | Delete | 50 MB savings |
| Changelog/notes redaction | 1-2 | ~5 | 15 min | Consistency only |

**Total Effort (Nice to Do):** 1 hour

---

## 📊 SUMMARY TABLE

| Category | Files Affected | Total Instances | Estimated Time | Can Skip? |
|----------|---|---|---|---|
| **REQUIRED** | 10-15 | 50-75 | 3.5-4 hours | NO |
| Optional (Medium) | 5-8 | 15-25 | 1-1.5 hours | YES |
| Optional (Low) | 5-10 | 15-70 | 1 hour | YES |

---

## ✅ EXECUTION CHECKLIST

Once redactions are approved, use this order:

### Phase 1: Code Redactions (Critical)
- [ ] Review scripts/*.py for hardcoded paths
- [ ] Replace /homes/neumann/teklehaymanot/ with relative paths
- [ ] Review src/ modules for hardcoded paths
- [ ] Replace absolute paths with Path-based construction
- [ ] Review slurm/*.sbatch for paths
- [ ] Replace cluster paths with variables

### Phase 2: Documentation Redactions (Important)
- [ ] Redact job IDs in results/TABLE_3_FINAL.md
- [ ] Replace paths in results/TABLE_3_FINAL.md
- [ ] Replace paths in README.md
- [ ] Replace paths in docs/ files
- [ ] Replace paths in migrate_experiments.sh

### Phase 3: Optional Cleanup (Polish)
- [ ] Remove job IDs from historical notes (if desired)
- [ ] Redact config template paths (if desired)
- [ ] Delete old SLURM logs (if desired)

### Phase 4: Verification
- [ ] Spot-check scripts for remaining /homes/ paths
- [ ] Verify all data paths are now relative or configurable
- [ ] Run `grep -r "/homes/neumann" .` to confirm
- [ ] Run `grep -r "slurm/logs" .` to confirm

---

## 📝 REDACTION LOG TEMPLATE

**For tracking which redactions were completed:**

```
REDACTION LOG — 2026-09-08
===========================

Phase 1: Code Redactions
- [ ] scripts/train_en_ti_full_validation.py — 3 instances replaced
- [ ] scripts/train_en_am_full_validation_correct_tok.py — 2 instances replaced
- [ ] src/marianmt_comparison/config.py — 5 instances replaced
- [ ] src/marianmt_comparison/data.py — 4 instances replaced
- [ ] slurm/submit_*.sbatch — 8 instances replaced

Phase 2: Documentation Redactions
- [ ] results/TABLE_3_FINAL.md — 18 job IDs replaced
- [ ] README.md — 6 paths replaced
- [ ] docs/experiment_status.md — 4 paths replaced

Phase 3: Optional Cleanup
- [ ] Deleted .venv/ directory (500 MB)
- [ ] Deleted __pycache__/ directories (5 MB)
- [ ] Deleted .pytest_cache/ (1 MB)

Verification
- [ ] `grep -r "/homes/neumann" .` returns 0 results
- [ ] `grep -r "slurm/logs" .` returns 0 results
- [ ] Scripts execute without path errors
```

---

## 🛑 IMPORTANT NOTES

**DO NOT EXECUTE THESE REDACTIONS YET:**
This is a PLAN ONLY. No files have been modified.

**Required Approval Before Execution:**
1. Review this plan carefully
2. Verify all items are correctly identified
3. Approve the redaction strategy
4. Execute redactions in order

**Backup Recommendation:**
Before executing redactions, consider:
- Creating a git branch: `git checkout -b redaction-cleanup`
- So changes can be reviewed and reverted if needed

**Testing After Redaction:**
- Run training scripts with `--help` to verify path handling
- Check config loading works with relative paths
- Verify SLURM submission scripts still function

---

**Status:** ✅ PLAN COMPLETE — Ready for approval and execution  
**No files modified yet**  
**Awaiting authorization to proceed**

