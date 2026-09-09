# 🔍 CORRECTED PRE-PUSH RECONCILIATION REPORT

## CRITICAL CLARIFICATION

**There is NO authoritative v2 TABLE 3 that reproduces the published paper.**

The MoVoC v2 repository explicitly states:

> "The original evaluation artifacts were not recovered. The checkpoints, predictions and scoring pipeline that produced these figures are not preserved in this repository, and the metric scale of the BLEU column is unresolved."

---

## 📚 HIERARCHY OF AUTHORITY

### 1. **PUBLISHED PAPER (Most Authoritative)**
**Source:** arXiv:2509.08812 — "MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages"  
**Location in v2:** `/original/published_results/README.md`  
**Status:** Original values, NOT reproduced, NOT reconstructed  
**Preservation:** Frozen, never overwritten

### 2. **v2 TABLE 3 (Reconstruction Attempt)**
**Source:** `v2/table3/table3_final.csv`  
**Status:** "Reconstruction-v2 extrinsic MT evaluation" (NOT direct reproduction)  
**Training Scale:** 75,000 steps (vs ~416K baseline)  
**Known Issue:** BLEU below 2 in every cell (undertrained, not usable)  
**Scoring Pipeline:** NOT the original pipeline (unavailable)  
**Conclusion:** "None of these runs reached a translation regime where a BLEU or chrF++ difference is trustworthy"

### 3. **Current marianmt-tokenizer-comparison (This Repository)**
**Training Scale:** Full-scale (8,470,130 steps mentioned in Phase 2)  
**Status:** Independent research, different scale than v2  
**Relationship to v2:** Neither reproduction nor reconstruction

---

## 📊 PUBLISHED TABLE 3 (AUTHORITATIVE VALUES)

These are the paper's own reported figures:

```
Language Pair    | Tokenizer   | BLEU           | ChrF++
─────────────────────────────────────────────────────────
EN → Amharic     | BPE         | 0.2150 ± 0.0120 | 16.2000 ± 1.05
EN → Amharic     | WordPiece   | 0.2340 ± 0.0155 | 16.5000 ± 1.00
EN → Amharic     | MoVoC-Tok   | 0.2455 ± 0.0108 | 17.8500 ± 0.95 ⭐
EN → Tigrinya    | BPE         | 0.1720 ± 0.0095 | 7.2000 ± 0.85
EN → Tigrinya    | WordPiece   | 0.1880 ± 0.0088 | 7.5000 ± 0.80
EN → Tigrinya    | MoVoC-Tok   | 0.2050 ± 0.0080 | 8.1000 ± 0.75 ⭐
EN → Tigre       | BPE         | 0.0950 ± 0.0080 | 4.0000 ± 0.70
EN → Tigre       | WordPiece   | 0.1025 ± 0.0075 | 4.3000 ± 0.65
EN → Tigre       | MoVoC-Tok   | 0.1175 ± 0.0068 | 5.1500 ± 0.60 ⭐
EN → Ge'ez       | BPE         | 0.0480 ± 0.0070 | 3.0500 ± 0.55
EN → Ge'ez       | WordPiece   | 0.0550 ± 0.0065 | 3.2500 ± 0.60
EN → Ge'ez       | MoVoC-Tok   | 0.0660 ± 0.0060 | 3.9500 ± 0.50 ⭐
```

**Key claim:** "MoVoC-Tok outperforms BPE on precision in all four languages" and in downstream translation metrics.

---

## 🔄 RECONCILIATION: Current Repository vs. Published Paper

### Current Repository TABLE 3 Status

From `results/TABLE_3_FINAL.md`:

```
EN→Tigrinya (Phase 1, undertrained):
  BPE BLEU: 0.809 ± 0.247
  MoVoC-Tok BLEU: 0.367 ± 0.030

EN→Amharic (Phase 1, undertrained):
  BPE BLEU: 0.502 ± 0.072
  MoVoC-Tok BLEU: 0.899 ± 0.003
```

### Comparison

| Aspect | Published Paper | v2 Reconstruction | Current Repo | Status |
|--------|-----------------|-------------------|--------------|--------|
| **Scale** | ~416K steps | 75K steps (5.5× under) | 8.47M steps (full) | Different |
| **Source** | Original pipeline | Reconstructed (unavailable) | Own experiments | Different |
| **Metrics** | BLEU 0.17-0.25 | BLEU 0.0-1.5 | BLEU 0.37-0.90 | Different |
| **Zero-shot included** | Yes (4 languages) | Yes (4 languages) | No (omitted) | Different |
| **Finding** | MoVoC wins all 4 | Inconclusive (undertrained) | MoVoC wins 1/2 | Different |

---

## 🚨 DECISION FRAMEWORK

### THE FUNDAMENTAL QUESTION

**Is this repository intended to:**

- [ ] **A) Reproduce the published paper?**
  → Must match published values (0.2455 BLEU for EN→am MoVoC-Tok)
  → Would require getting original scoring pipeline (UNAVAILABLE)
  → Not feasible

- [ ] **B) Reconstruct at v2 scale for reproducibility?**
  → Match v2 (75K steps, FLORES200+OPUS)
  → Accept undertrained limitations
  → Would take ~40 GPU hours, duplicates existing work

- [ ] **C) Independent full-scale experiments?**
  → Keep current work (8.47M steps)
  → Document as "alternative training scale"
  → Be transparent about divergence from published paper
  → Include zero-shot results (if available)

---

## 📋 WHAT YOU ACTUALLY HAVE

### ✅ Present in Current Repository

1. **Data:**
   - Training data (unknown corpus)
   - Test data (FLORES200? OPUS? Unclear)
   - Intrinsic evaluation data

2. **Tokenizers:**
   - All 6 artifacts (BPE, MoVoC-Tok, WordPiece × 2 languages)

3. **Models:**
   - 28+ trained models (experiments/ directory)
   - Training logs and checkpoints

4. **Results:**
   - Intrinsic evaluation (TABLE 2 & 4 content)
   - Phase 1 baseline results
   - Phase 2 full validation
   - Phase 3 zero-shot (exists but omitted from publication)

### ❌ NOT Present

1. **Reproducing published paper:** Original scoring pipeline unavailable
2. **Matching v2 reconstruction:** Training scale different (8.47M vs 75K)
3. **Dataset documentation:** FLORES200/OPUS usage unclear
4. **Zero-shot integration:** Exists but separated from TABLE 3

---

## 🎯 THREE LEGITIMATE OPTIONS

### OPTION A: ACKNOWLEDGE INDEPENDENCE ⭐ RECOMMENDED

**Position:** This is independent research at full training scale

**Actions:**
1. Keep current TABLE_3_FINAL.md as "Full-Scale Experiments"
2. Add section: "Relationship to Published Paper"
   - Note: "Our experiments use full-scale training (8.47M steps) vs published paper's reported scale"
   - Note: "Results are NOT comparable to published TABLE 3"
   - Note: "We do not claim to reproduce the paper"
3. Include zero-shot results with clear labeling
4. Document dataset source (FLORES200? OPUS? Custom?)
5. Create supplementary results comparing findings

**Advantages:**
- Honest about what the work actually is
- Shows your own contribution
- No false claims of reproduction
- Transparent methodology

**File structure:**
```
results/
  ├── TABLE_3_FULL_SCALE_EXPERIMENTS.md (current work)
  ├── RELATIONSHIP_TO_PUBLISHED_PAPER.md (transparency)
  ├── ZERO_SHOT_SUPPLEMENTARY.csv
  └── comparison_with_published_findings.md
```

---

### OPTION B: ALIGN WITH v2 RECONSTRUCTION

**Position:** Match v2 scale and methodology for compatibility

**Actions:**
1. Obtain v2's training configuration (75K steps, FLORES200+OPUS)
2. Retrain at v2 scale (if time/resources permit)
3. Evaluate on FLORES200+OPUS (matching v2)
4. Report with v2's caveats: "Undertrained, not usable translation regime"
5. Include zero-shot in publication table (matching v2)
6. Use v2 CSV format

**Advantages:**
- Aligned with published open reconstruction
- Comparable to v2 work
- Clear dataset specification
- Caveats documented

**Disadvantages:**
- Requires ~40 GPU hours
- Duplicates v2's work
- Undertrained results not compelling

---

### OPTION C: PUBLISH AS-IS WITH FULL TRANSPARENCY

**Position:** Document exactly what was done, with all caveats

**Actions:**
1. Keep current experiments (full-scale training)
2. Add comprehensive "Methods" documentation:
   - Training scale: 8.47M steps (vs published ~416K baseline)
   - Dataset source: Specify exact corpus used
   - Tokenizer versions: Specify exact vocab sizes
   - Evaluation: FLORES200? OPUS? Mix?
3. Create comparison table:
   ```
   | Paper Published | v2 Reconstruction | Our Experiments |
   |---|---|---|
   | 0.2455 | 1.4937 | 0.8987 |
   ```
4. Add disclaimer: "Not a reproduction. Independent full-scale training."
5. Include zero-shot with confidence intervals

**Advantages:**
- Completely transparent
- Shows your full work
- Honest about differences
- Publishable as independent research

---

## 🛡️ DATA PROTECTION

✅ MoVoC v2 Repository:
- NOT modified
- NOT overwritten  
- Used as READ-ONLY reference
- Remains authoritative

⚠️ Sensitive Information to Redact:
- Job IDs (69563_44, 70088, etc.)
- SLURM paths
- HPC allocations
- Email addresses
- Personal timestamps

---

## ✋ DECISION REQUIRED

Before proceeding to push, choose:

1. **OPTION A:** Acknowledge independence (full-scale experiments)
2. **OPTION B:** Align with v2 reconstruction (retrain at 75K steps)
3. **OPTION C:** Publish as-is with full transparency

**Reply with:** `OPTION A`, `OPTION B`, or `OPTION C`

---

**Status:** ⏳ **AWAITING YOUR DECISION**

The reconciliation has revealed that **no authoritative TABLE 3 exists in v2 that reproduces the published paper**. Your choice above determines the correct framing for the repository.
