# REPOSITORY STRUCTURE CONSISTENCY CHECK
## marianmt-tokenizer-comparison vs. MoVoC v2 (Authoritative)

---

## 🔍 FINDINGS

### ✅ ALIGNED ELEMENTS

| Element | Status | Details |
|---------|--------|---------|
| **Intrinsic Results (TABLE 2)** | ✅ ALIGNED | Both repos report MorphScore from AMSEG evaluation |
| **Intrinsic Results (TABLE 4)** | ✅ ALIGNED | Precision + Rényi entropy structure matches |
| **Data Organization** | ✅ ALIGNED | `data/train/`, `data/test/`, `data/intrinsic/`, `data/extrinsic/` |
| **Tokenizers** | ✅ ALIGNED | 6 tokenizers (BPE, WordPiece, MoVoC-Tok × 2 languages) |
| **Core Structure** | ✅ ALIGNED | docs/, scripts/, results/, src/ all present |
| **Evaluation Phases** | ✅ ALIGNED | Phase 1 (baseline), Phase 2 (full-val), Phase 3 (zero-shot) |

### ⚠️ INCONSISTENCIES DETECTED

#### 1. **TABLE 3 (MarianMT) Results**

**Authoritative v2 Structure (MoVoC repo):**
```
Language Pair | Dataset | Type       | Tokenizer   | BLEU       | ChrF++
─────────────────────────────────────────────────────────────────────
EN → Amharic  | flores  | supervised | BPE         | 1.4937±0.0866 | 21.5573±0.2167
EN → Amharic  | flores  | supervised | MoVoC-Tok   | 0.7907±0.0363 | 18.3999±0.1711
EN → Tigrinya | flores  | supervised | BPE         | 1.2557±0.2135 | 10.8757±0.0708
EN → Tigrinya | flores  | supervised | MoVoC-Tok   | 0.2710±0.0775 | 7.8489±0.2845
EN → Tigre    | opus    | zero-shot  | BPE         | 1.1460±0.0535 | 10.3310±0.6563
EN → Tigre    | opus    | zero-shot  | MoVoC-Tok   | 0.1677±0.0632 | 5.5903±0.6641
EN → Ge'ez    | opus    | zero-shot  | BPE         | 0.0195±0.0059 | 5.0322±0.0504
EN → Ge'ez    | opus    | zero-shot  | MoVoC-Tok   | 0.0150±0.0012 | 4.8138±0.1196
```

**Current marianmt-tokenizer-comparison:**
```
Shows ONLY undertrailled Phase 1/2 results:
- Phase 1: BPE BLEU 0.809, MoVoC-Tok BLEU 0.367 (EN→TI)
- Phase 1: BPE BLEU 0.502, MoVoC-Tok BLEU 0.899 (EN→AM)
- Incomplete experiments with seed failures noted
- Zero-shot results OMITTED ("Omitted from main results")
```

**Issue:** The authoritative v2 TABLE 3 reports MoVoC results trained to full convergence on FLORES200 + OPUS datasets with proper beam search evaluation. Current repo shows undertrained Phase 1/2 checkpoints, not the final converged models.

---

#### 2. **Model Training Data & Datasets**

**Authoritative v2 (from table3_final.csv):**
- **FLORES200:** 1,012 examples (en→am, en→ti supervised)
- **OPUS:** 100 examples (en→am supervised), 71 examples (en→ti supervised), 43 examples (en→tig zero-shot), 100 examples (en→gez zero-shot)
- Training data: OPUS corpus (mentioned as "NLLB" fine-tuning corpus)

**Current marianmt-tokenizer-comparison:**
- `data/train/en_am/` — Amharic training data (unknown corpus)
- `data/train/en_ti/` — Tigrinya training data (unknown corpus)
- `data/test/` — Has en_geez, en_tigre directories
- **Issue:** No reference to FLORES200 vs OPUS corpus distinction; no clear dataset lineage documentation

---

#### 3. **Intrinsic Evaluation Files**

**Authoritative v2:**
- `v2/table2/table2_final.csv` — 12 rows (4 languages × 3 tokenizers)
- `v2/table4/table4_final.csv` — 12 rows (same structure)
- `scripts/evaluate_intrinsic.py` — the **authoritative producer** of these values

**Current marianmt-tokenizer-comparison:**
- `Intrinsic_Evaluation/results/table2_final_results.json` — JSON format
- `Intrinsic_Evaluation/results/table4_32k_results.json` — JSON format  
- **Issue:** CSV structure doesn't match v2; field names / organization may differ

---

#### 4. **Zero-Shot Evaluation Placement**

**Authoritative v2:**
- TABLE 3 explicitly includes zero-shot rows (EN→Tigre, EN→Ge'ez)
- Clear `evaluation_type: "zero_shot"` column
- Results integrated with supervised evaluations

**Current marianmt-tokenizer-comparison:**
- `experiments/zero_shot_evaluation_seeds_focused/results.json` — exists
- `results/phase3_zeroshot/` — directory exists
- **But:** TABLE_3_FINAL.md states "**Omitted from main results**"
- **Issue:** Zero-shot results NOT included in the publication table, unlike v2

---

#### 5. **Evaluation Metrics & Reporting Format**

**Authoritative v2 TABLE 3 columns:**
```
direction | evaluation_dataset | evaluation_type | tokenizer | 
bleu_mean | bleu_std | chrf_mean | chrf_std | num_examples | 
seeds | n_valid | status | output_quality_flagged_seeds
```

**Current marianmt-tokenizer-comparison:**
```
Tokenizer | Seed 42 | Seed 43 | Seed 44 | Mean ± SD | CV%
(separate tables for BLEU and ChrF++)
```

**Issue:** Different tabular format; v2 is columnar (seeds aggregated), current is row-wise (seeds separated)

---

### 📋 STRUCTURE ALIGNMENT MATRIX

| Component | v2 MoVoC | Current Repo | Status |
|-----------|----------|--------------|--------|
| docs/ | ✅ | ✅ | Aligned |
| data/train/ | ✅ | ✅ | Aligned (corpus unclear) |
| data/test/ | ✅ | ✅ | Aligned |
| data/intrinsic/ | ✅ | ✅ | Aligned |
| data/extrinsic/ | ✅ | ✅ | Aligned |
| tokenizers/ | ✅ | ✅ | Aligned |
| Intrinsic_Evaluation/ | ✅ | ✅ (but JSON) | Format mismatch |
| Extrinsic_Evaluation/ | ✅ | ✅ | Aligned |
| scripts/ | ✅ | ✅ | Aligned |
| TABLE 2 (MorphScore) | ✅ CSV | ✅ JSON | Format mismatch |
| TABLE 3 (MarianMT) | ✅ CSV | ⚠️ MD (incomplete) | **MAJOR MISMATCH** |
| TABLE 4 (Precision) | ✅ CSV | ✅ JSON | Format mismatch |
| Zero-shot results | ✅ Included | ⚠️ Excluded | **Omitted from publication** |

---

## 🎯 RECOMMENDATIONS

### Priority 1: TABLE 3 Alignment

**Action Required:**
1. Obtain the authoritative Phase 2 **CONVERGED** models from v2 (or retrain to convergence)
2. Evaluate on FLORES200 + OPUS datasets (not custom datasets)
3. Include zero-shot results (EN→Tigre, EN→Ge'ez) in TABLE 3
4. Reformat TABLE 3 to match v2 CSV structure:
   ```csv
   direction,evaluation_dataset,evaluation_type,tokenizer,bleu_mean,bleu_std,chrf_mean,chrf_std,num_examples,seeds,n_valid,status
   ```

### Priority 2: Intrinsic Results Format

**Action Required:**
1. Export `Intrinsic_Evaluation/results/` JSON to CSV matching v2 format
2. Ensure field names match exactly: language, tokenization, precision, renyi_alpha2, morphscore, movoc_tok_mode, words

### Priority 3: Documentation

**Action Required:**
1. Add dataset lineage documentation:
   - Which experiments use OPUS vs. other corpora?
   - Clarify training data source (NLLB corpus reference)
2. Document why Phase 1/2 undertrained models differ from v2 converged results
3. Explain zero-shot omission from TABLE 3

### Priority 4: File Placement

**Action Required:**
1. Ensure intrinsic results CSV files at: `Intrinsic_Evaluation/results/table2_final.csv`, `table4_final.csv`
2. Ensure extrinsic results CSV at: `Extrinsic_Evaluation/results/table3_final.csv`
3. Update `results/final_summary/TABLE_3_FINAL.md` with complete TABLE 3 (including zero-shot)

---

## ✨ AUTHORITATIVE REFERENCE

**Source:** `https://github.com/hailaykidu/MoVoC/tree/main/v2`
- `v2/README.md` — Result selection policy
- `v2/table2/` — MorphScore reconstruction (AMSEG provenance)
- `v2/table3/` — MarianMT full results (FLORES200 + OPUS)
- `v2/table4/` — Intrinsic precision & entropy
- `v2/reports/` — Methodology, limitations, reconstruction summary

**Key Quote from v2 README:**
> "Main tables report the **final approved methodology, applied identically to every tokenizer**."
> - **Table 2** — final MorphScore result
> - **Table 3** — final MarianMT evaluation, mean ± std across seeds 42/43/44  
> - **Table 4** — official exact-match precision and normalized Rényi entropy

---

## 🔗 NEXT STEPS

Before pushing to GitHub:

1. **Verify dataset lineage** — confirm which experiments use FLORES200 vs. OPUS
2. **Reconcile zero-shot results** — decide: include in TABLE 3 or keep separate?
3. **Align TABLE 3 format** — match v2 CSV structure (direction, dataset, type, tokenizer, metrics)
4. **Export intrinsic results** — convert JSON to v2-compatible CSV format
5. **Document discrepancies** — if Phase 1/2 experiments are intentionally different from v2, explain why in README

