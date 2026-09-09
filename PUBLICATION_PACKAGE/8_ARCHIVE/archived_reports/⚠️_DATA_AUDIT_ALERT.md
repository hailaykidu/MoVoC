# ⚠️ CRITICAL DATA AUDIT ALERT
## Repository Data Completeness Issues

**ALERT LEVEL:** ⚠️ **HIGH PRIORITY**  
**DATE:** 2026-09-09  
**STATUS:** **REQUIRES IMMEDIATE RESOLUTION BEFORE PUBLICATION**

---

## 🚨 Critical Finding

When the repository was audited against the published paper's dataset specifications (Section 4.2), **SIGNIFICANT DATA COMPLETENESS ISSUES** were discovered.

---

## The Issue in Numbers

### Paper Specification vs. Repository Reality

```
EN→AMHARIC:
  Paper:       100 test pairs ✅
  Repository:  100 test pairs ✅
  Status:      COMPLETE ✅

EN→TIGRINYA:
  Paper:       100 test pairs (74 OPUS + 26 human-validated)
  Repository:  71 lines ❌
  Missing:     29 lines (29% deficit)
  Status:      INCOMPLETE ❌

EN→TIGRE:
  Paper:       100 test pairs (45 OPUS + 55 human-validated)
  Repository:  43 lines ❌
  Missing:     57 lines (57% deficit)
  Missing ALL: 55 human-validated examples ❌
  Status:      SEVERELY INCOMPLETE ❌

EN→GE'EZ:
  Paper:       100 test pairs (newly created, Mermru.com)
  Repository:  100 test pairs ✅
  Status:      COMPLETE ✅
```

---

## Critical Questions Needing Answers

### Question 1: EN→Tigrinya (71 vs 100 lines)
- [ ] Were 29 lines intentionally removed?
- [ ] Is this a data preprocessing/filtering artifact?
- [ ] Were lines that failed validation excluded?
- [ ] Was this a data corruption issue?

**Action Needed:** Clarify why 71 instead of 100

---

### Question 2: EN→Tigre (43 vs 100 lines)
**CRITICAL:** The repository has:
- ✅ ~43 OPUS lines (expected 45, missing 2)
- ❌ **0 human-validated lines (expected 55, missing ALL 55)**

**This is NOT a rounding issue - the entire human-validation component is missing.**

- [ ] Where are the 55 human-validated EN→Tigre sentence pairs?
- [ ] Were they in a different location?
- [ ] Were they lost/deleted?
- [ ] Are they in a separate file/directory?

**Action Needed:** Locate or reconstruct the 55 missing human-validated Tigre test pairs

---

### Question 3: Directory Naming
- [ ] Why is Tigre named "en_tig" (abbreviated) instead of "en_tigre"?
- [ ] Is this intentional abbreviation or a typo?
- [ ] Are there separate directories for OPUS vs. human-validated data?

---

## Impact on Results

### Severity for Each Evaluation

| Evaluation | Data | Severity | Impact |
|-----------|------|----------|--------|
| EN→Amharic | 100/100 ✅ | None | No impact |
| EN→Tigrinya | 71/100 ❌ | MODERATE | Results based on 71% of spec data |
| EN→Tigre (ZS) | 43/100 ❌ | **CRITICAL** | Results based only on OPUS, missing all human-validation |
| EN→Ge'ez (ZS) | 100/100 ✅ | None | No impact |

### On Zero-Shot Experiments
- **EN→Ge'ez Transfer:** Not affected (complete)
- **EN→Tigre Transfer:** **SEVERELY COMPROMISED** (only 43% of test data, no human-validation)

---

## What Must Happen Before Publication

### 🔴 MUST DO (Non-negotiable)
1. **Determine the cause:**
   - Is incomplete data intentional (different train/test split)?
   - Is it accidental (data loss/corruption)?
   - Is it from preprocessing/filtering?

2. **Locate missing data:**
   - Search entire repository for Tigre data
   - Check if data is in different location/format
   - Verify if 55 human-validated pairs exist anywhere

3. **Document the discrepancy:**
   - If data is intentionally different, explain why
   - Update DATA_MANIFEST.md with actual test set sizes
   - Add note to publication explaining deviation

4. **Update results interpretation:**
   - Note that results use different test set sizes
   - Qualify comparisons with paper results
   - Explain impact on reproducibility

### 🟡 SHOULD DO (Highly recommended)
1. **Recover/reconstruct missing data** if possible
2. **Re-run evaluations** with complete data
3. **Compare results** (incomplete vs. complete data)
4. **Document any differences** in performance

### 🔵 REQUIRED FOR PUBLICATION
1. **Add disclaimer** in publication acknowledging data discrepancy
2. **Cite DATA_AUDIT_REPORT_2026_09_09.md** in methods section
3. **Explain rationale** for any deviations from paper
4. **Qualify results** with data completeness notes

---

## File References

### For Investigation
- **Data Audit:** [DATA_AUDIT_REPORT_2026_09_09.md](DATA_AUDIT_REPORT_2026_09_09.md)
- **Context:** [REPOSITORY_CONTEXT.md](REPOSITORY_CONTEXT.md)
- **Data Locations:**
  - `data/extrinsic/en_ti/` (71 lines found, 100 expected)
  - `data/extrinsic/en_tig/` (43 lines found, 100 expected)
  - `data/extrinsic/en_am/` (100 lines, correct)
  - `data/extrinsic/en_gz/` (100 lines, correct)

### For Fixing
- **Data Manifest:** `data/README.md`, `data/metadata/`
- **Publication Package:** `PUBLICATION_PACKAGE/5_RESULTS/`

---

## Timeline

⚠️ **THIS MUST BE RESOLVED BEFORE PUBLICATION**

```
2026-09-09:   🔴 ALERT ISSUED (This document)
2026-09-09:   Investigate cause of incomplete data
Before Submit: 🔴 RESOLVE all discrepancies
Before Submit: 🟡 Document findings & rationale
Before Submit: 🔵 Add publication disclaimers
```

---

## Checklist for Resolution

**Investigation (Required):**
- [ ] Confirm why EN→Tigrinya has 71 vs 100 lines
- [ ] Confirm why EN→Tigre has 43 vs 100 lines
- [ ] Locate the 55 missing human-validated EN→Tigre pairs (if they exist)
- [ ] Check if data was intentionally subset
- [ ] Check if data exists in different location

**Documentation (Required Before Publication):**
- [ ] Update DATA_MANIFEST.md with accurate counts
- [ ] Add note in REPOSITORY_CONTEXT.md explaining discrepancy
- [ ] Update PUBLICATION_PACKAGE/5_RESULTS/ with data-size notes
- [ ] Add disclaimer to any publication using this data

**Recovery (Recommended):**
- [ ] If data lost: Download replacement from OPUS corpus
- [ ] If data filtered: Explain filtering criteria
- [ ] If intentional subset: Justify subset rationale

**Verification (Before Publishing):**
- [ ] All test set sizes documented
- [ ] Discrepancy explained and justified
- [ ] Impact on results assessed
- [ ] Publication includes proper disclaimers

---

## Questions for the Data Keeper

**To whoever prepared/owns the data:**

1. Why does EN→Tigrinya have 71 test pairs instead of 74 (OPUS) + 26 (human-validated) = 100?
2. Where are the 55 human-validated EN→Tigre test pairs?
3. Why is the EN→Tigre directory named "en_tig" instead of "en_tigre"?
4. Was the test set size reduction intentional or accidental?
5. Can the missing data be recovered or replaced?

---

## Summary

### Current State
❌ Test data **does not match** published paper specifications  
❌ 29 lines missing from EN→Tigrinya  
❌ **57 lines missing from EN→Tigre (including ALL human-validated component)**  
⚠️ **This affects publication validity and reproducibility**

### Required Action
🔴 **INVESTIGATION AND RESOLUTION REQUIRED IMMEDIATELY**

Before this repository can be published:
1. Determine why data is incomplete
2. Locate missing data if it exists
3. Document findings and rationale
4. Add proper disclaimers to publication
5. Verify all test sets are accounted for

### Next Step
→ See [DATA_AUDIT_REPORT_2026_09_09.md](DATA_AUDIT_REPORT_2026_09_09.md) for detailed audit findings

---

**ALERT STATUS:** 🔴 **CRITICAL - REQUIRES IMMEDIATE ATTENTION**

**Do not proceed with publication until this alert is addressed and resolved.**

