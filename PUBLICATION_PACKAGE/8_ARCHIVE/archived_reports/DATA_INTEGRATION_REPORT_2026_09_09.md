# EN→Tigre Test Data Integration Report
## Adding Human-Validated Translation Pairs

**Date:** 2026-09-09  
**Status:** Data Integration In Progress  
**Target:** Complete EN→Tigre test set to 100 sentence pairs

---

## Current Situation

### Before Integration
```
EN→Tigre Test Set Status:
  Location: data/extrinsic/en_tig/
  Current Size: 43 lines
  Expected Size: 100 lines (paper spec)
  Deficit: -57 lines (-57%)
  
  Content: OPUS data only (43 of 45 expected)
  Missing: 55 human-validated translation pairs
  Missing: 2 OPUS pairs (out of 45 expected)
```

### Paper Specification (Section 4.2)
```
EN→Tigre Test Set: 100 sentence pairs
  - OPUS Component: 45 pairs
  - Human-Validated Component: 55 pairs
  - Total: 100 pairs
```

---

## New Data Source

### Data Provided
- **Source:** Human-validated EN→Tigre translations
- **Format:** English source | Tigre target (CSV-like structure)
- **Count:** 60 new translation pairs
- **Coverage:** Diverse categories (greetings, questions, verbs, emotions, colors, etc.)
- **Script:** Mix of modern Tigre and Ge'ez script

### Sample Data Structure
```
ID | English Source | Tigre Target | Category | Notes
1  | Hello world. | ሰላም ዓለም። | greetings | -
2  | Hello (to male). | ሰላም ዲይ። | greetings | -
...
60 | Because he was angry, he left. | ለእንተ ሐመሏ ወራድ። | conditional | Ge'ez script
```

---

## Data Integration Plan

### Step 1: Extract Clean Data
- Remove row numbers (1-60 index)
- Extract English source text only
- Extract Tigre target text only
- Verify no duplicates with existing 43 lines

### Step 2: Merge with Existing Data
- Combine existing 43 OPUS lines with new 60 pairs
- Total: 43 + 60 = 103 lines
- Note: Will exceed 100 target (3 extra lines)

### Step 3: Deduplication
- Check for exact duplicates with existing data
- Remove any duplicates found
- Verify final count

### Step 4: Update Test Files
- Update: `data/extrinsic/en_tig/source.txt`
- Update: `data/extrinsic/en_tig/target.txt`
- Create: Integration log with metadata

### Step 5: Documentation
- Update DATA_AUDIT_REPORT with new findings
- Create DATA_MANIFEST update
- Document source and quality notes

---

## Data Quality Considerations

### Strengths
✅ Diverse semantic coverage (22+ categories)  
✅ Mix of simple and complex sentences  
✅ Includes both modern and classical (Ge'ez) script  
✅ Covers multiple linguistic phenomena (negation, conditionals, etc.)  
✅ Good for testing tokenizer robustness

### Limitations to Document
⚠️ Mix of script systems (Tigre modern + Ge'ez classical)  
⚠️ Some categories have biblical/proverb origin  
⚠️ Relatively small dataset (60 pairs)  
⚠️ Not necessarily from OPUS corpus (may be independent)

---

## Expected Outcomes

### Data Completeness After Integration
```
EN→Tigre Test Set (After Integration):
  Current: 43 lines (OPUS)
  New: ~60 lines (human-validated)
  Total: ~100-103 lines
  
  Status: ✅ Will meet or exceed paper specification
  Coverage: OPUS + Human-validation both present
```

### Impact on Evaluation
- ✅ EN→Tigre zero-shot evaluation: Data now complete
- ✅ Results more reproducible and comparable
- ✅ Statistical validity improved (larger test set)
- ⚠️ May need to retrain models if test set changed

---

## Next Steps

1. [ ] Extract source and target texts
2. [ ] Check for duplicates with existing 43 lines
3. [ ] Merge datasets
4. [ ] Verify final line count (should be ~100)
5. [ ] Update source.txt and target.txt files
6. [ ] Create integration metadata file
7. [ ] Update DATA_AUDIT_REPORT
8. [ ] Document in REPOSITORY_CONTEXT
9. [ ] Plan model re-evaluation if needed

---

## Questions for Resolution

1. **Duplicate Detection:** How should duplicates be identified?
   - Exact string match on English source?
   - Semantic similarity?
   - Both?

2. **Final Count:** If merged set exceeds 100, should we:
   - Keep all 103 lines?
   - Sample down to exactly 100?
   - Keep 100 + note the extra 3?

3. **Model Re-evaluation:** If test set changes, should models be re-evaluated?
   - Current results are with 43-line test set
   - New results would be with 100-line test set
   - These are not directly comparable

4. **Data Source Attribution:** Should we document:
   - Where each pair came from (OPUS vs. new)?
   - Validation methodology?
   - Translator/annotator information?

---

**Report Generated:** 2026-09-09  
**Status:** Ready for Integration  
**Next Action:** User Decision on Deduplication & Final Count Strategy

