# Re-Evaluation Plan: Updated Test Data Assessment
## EN→Tigre & EN→Tigrinya (All 3 Seeds)

**Date:** 2026-09-09  
**Trigger:** Data expansion completed (43→103 for Tigre, 71→102 for Tigrinya)  
**Objective:** Re-evaluate all models with complete test sets  
**Status:** INITIATED

---

## Evaluation Scope

### Models to Re-Evaluate

**EN→Tigre Zero-Shot Transfer:**
- BPE + Seed 42
- BPE + Seed 43
- BPE + Seed 44
- WordPiece + Seed 42, 43, 44
- MoVoC-Tok + Seed 42, 43, 44

**EN→Tigrinya Direct:**
- BPE + Seed 42, 43, 44
- WordPiece + Seed 42, 43, 44
- MoVoC-Tok + Seed 42, 43, 44

**Total Evaluations:** 18 (9 per language pair)

---

## Test Data Changes

### EN→Tigre
```
OLD: 43 test pairs (OPUS only)
NEW: 103 test pairs (OPUS 43 + Human-validated 60)
Change: +60 pairs (+139%)
Impact: Larger, more comprehensive test set
```

### EN→Tigrinya
```
OLD: 71 test pairs (mostly OPUS)
NEW: 102 test pairs (OPUS 71 + Human-validated 31)
Change: +31 pairs (+43%)
Impact: Larger, more comprehensive test set
```

---

## Expected Outcome

### Comparison Metrics
- Old vs New results for same models
- Impact of test set expansion on BLEU/ChrF++
- Consistency across different test set sizes
- Statistical stability verification

### Documentation
- Side-by-side comparison tables
- Analysis of performance changes
- Statistical interpretation
- Publication notes

---

## Next Action

Ready to execute re-evaluation with expanded test data.

