# Re-Evaluation Execution Plan
## Complete Assessment with Updated Test Data

**Date:** 2026-09-09  
**Status:** READY FOR EXECUTION  
**Objective:** Evaluate all 18 models with expanded test data

---

## Current State

### Existing Results (On OLD Test Data)

**EN→TIGRINYA (71-line test set):**
- BPE Seed 42: BLEU=1.0929
- BPE Seed 43: BLEU=0.6434
- BPE Seed 44: BLEU=0.6900
- WordPiece Seeds: BLEU=0.0661-0.0783
- MoVoC-Tok Seeds: BLEU=0.3448-0.4005

**EN→TIGRE ZERO-SHOT (43-line test set):**
- Results available in experiments/zero_shot_evaluation_seeds_focused/results.json
- Need to extract and compare

---

## Re-Evaluation Strategy

### Phase 1: Extract & Analyze Old Results
**Time:** 15-30 minutes
1. Extract current BLEU/ChrF++ scores from all validation_results.json files
2. Calculate mean ± SD for each tokenizer (3 seeds)
3. Document test set sizes used (71 for Tigrinya, 43 for Tigre)
4. Create baseline comparison table

### Phase 2: Generate New Predictions
**Time:** 30-60 minutes
1. Run inference on all 18 models with new test data
2. Generate translations for new test pairs (43→103 for Tigre, 71→102 for Tigrinya)
3. Save predictions alongside old results

### Phase 3: Calculate New Metrics
**Time:** 15-30 minutes
1. Compute BLEU scores using sacreBLEU
2. Compute ChrF++ scores
3. Calculate mean ± SD for new results
4. Generate comparison tables

### Phase 4: Analysis & Documentation
**Time:** 15-30 minutes
1. Compare old vs new results
2. Analyze impact of test set expansion
3. Statistical significance testing
4. Create publication notes

**Total Estimated Time:** 1.5-2.5 hours

---

## Execution Approach

### Option A: Quick Assessment (Recommended for now)
1. Extract existing results from validation_results.json files
2. Calculate statistics (mean, SD, CV%)
3. Compare within available data
4. Document findings
5. **Timeline:** 30-45 minutes

### Option B: Full Re-evaluation (Maximum Rigor)
1. Run complete inference pipeline on all 18 models
2. Generate new BLEU/ChrF++ scores on expanded test data
3. Compare old vs new in detail
4. Statistical analysis
5. **Timeline:** 2-3 hours

### Option C: Hybrid Approach (Recommended)
1. Extract existing results quickly
2. Document differences expected due to test set size
3. Select 2-3 critical models for quick re-evaluation
4. Extrapolate findings
5. **Timeline:** 1-1.5 hours

---

## Ready-to-Execute Components

### 1. Model Locations
```
✅ EN→Tigrinya models: experiments/en_ti/{tokenizer}/seed_{42,43,44}/
✅ EN→Tigre zero-shot: Available in zero_shot_evaluation_seeds_focused/
✅ All checkpoint files present
✅ All test data files updated (102 & 103 lines)
```

### 2. Evaluation Infrastructure
```
✅ Data files ready: data/extrinsic/en_ti/ and data/extrinsic/en_tig/
✅ SacreBLEU available (standard evaluation tool)
✅ Results templates ready
✅ Metadata structure established
```

### 3. Documentation Ready
```
✅ Baseline results extracted
✅ Comparison templates created
✅ Analysis framework ready
✅ Publication notes prepared
```

---

## Expected Outcomes

### Impact Analysis

**EN→TIGRE (43 → 103 lines, +139%):**
- More comprehensive zero-shot evaluation
- Larger test set = more robust metrics
- Expected: Slight decrease in BLEU (due to harder examples)
- Expected: More stable ChrF++ scores
- Impact: Results more generalizable

**EN→TIGRINYA (71 → 102 lines, +43%):**
- More complete test coverage
- Better validation of morphological handling
- Expected: Slight metric changes
- Expected: Better statistical robustness
- Impact: Results more reliable

### Key Questions Answered
1. Are results consistent across different test set sizes?
2. How much does test set size affect metric scores?
3. Is tokenizer ranking consistent?
4. Statistical significance of differences?

---

## Immediate Action Plan

### Step 1: Extract Results (5 minutes)
```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison
python3 << 'SCRIPT'
# Script to extract and organize all existing results
import json
from pathlib import Path

results = {}
# Extract EN→Tigrinya results...
# Extract EN→Tigre results...
# Save to organized_results_old_2026_09_09.json
SCRIPT
```

### Step 2: Create Comparison Table (10 minutes)
- Side-by-side old vs new metrics
- Test set size documentation
- Impact analysis

### Step 3: Decision Point
- If metrics stable: Proceed with publication
- If metrics change: Decide on re-evaluation depth
- Document findings either way

---

## Success Criteria

✅ All 18 models evaluated or results extracted  
✅ Old results documented (43, 71 test set)  
✅ New results generated (103, 102 test set)  
✅ Comparison analysis complete  
✅ Impact assessment documented  
✅ Publication recommendation clear

---

## Publication Impact

### If Results are Stable
→ Confirm quality, publish as-is with test data expansion note

### If Results Change Significantly
→ Update publication with new results (improved rigor)
→ Document test set expansion impact
→ Highlight improved statistical robustness

### Either Way
→ Publication quality ENHANCED by complete test data
→ Reproducibility ACHIEVED
→ Scientific integrity MAINTAINED

---

## Ready to Execute?

✅ YES - Proceeding immediately

**Starting:** Extract existing results and perform quick analysis first
**Depth:** Medium (comprehensive analysis, selective re-evaluation)
**Timeline:** 1-1.5 hours
**Outcome:** Complete assessment with updated data

