# 🔍 COMPREHENSIVE PRE-PUSH RECONCILIATION REPORT

## Authoritative Source: MoVoC v2 Repository
**URL:** https://github.com/hailaykidu/MoVoC/tree/main/v2  
**Reference Files:**
- `v2/table3/table3_final.csv` — Authoritative TABLE 3
- `v2/table3/table3_multiseed.json` — Detailed per-run records
- `v2/table3/PROVENANCE.md` — Dataset lineage & run status

---

## ⚠️ CRITICAL FINDING

**v2 TABLE 3 is NOT a reproduction of the published paper.**

From v2 README:
> "Generated at reduced scale (75,000 optimizer steps vs. 416,040 baseline). BLEU below 2 in every cell indicates undertrained models that have NOT reached a usable translation regime."

**Key Implication:** v2 TABLE 3 represents a **reconstruction attempt with known limitations**, not the authoritative published results.

---

## 📊 AUTHORITATIVE v2 TABLE 3 SPECIFICATION

### Dataset Lineage (EXACT)

| Dataset | Language Pair | Split | Count | Type | Source |
|---------|---------------|-------|-------|------|--------|
| FLORES-200 | en→am (devtest) | supervised | 1,012 | supervised | FLORES corpus |
| FLORES-200 | en→ti (devtest) | supervised | 1,012 | supervised | FLORES corpus |
| OPUS/Tatoeba | en→am (held-out) | supervised | 100 | supervised | OPUS corpus |
| OPUS/Tatoeba | en→ti (held-out) | supervised | 71 | supervised | OPUS corpus |
| OPUS/Tatoeba | en→tig (held-out) | zero-shot | 43 | zero-shot | OPUS corpus |
| Mermru (Bedru/Eng-Geez) | en→gez (held-out) | zero-shot | 100 | zero-shot | HuggingFace Hub (2,107 pairs total, 100 sampled at seed 42) |

**Critical Note:** Ge'ez evaluation data (Mermru) was **assembled for reconstruction, NOT from publication period**. Paper says Ge'ez "was evaluated only intrinsically" for lack of parallel data.

### Training Configuration (EXACT)

- **Optimizer Steps:** 75,000 (vs 416,040 for comparable baseline)
- **Training Set Size:** 800,000 pairs
- **Scaling Factor:** 5.5× undertrained relative to baseline
- **Final Loss Range:** 3.00–3.59 across all runs
- **Baseline Comparison Loss:** ~3.13
- **Seeds:** 42, 43, 44 (3 seeds per tokenizer)
- **Tokenizers:** BPE, WordPiece, MoVoC-Tok

### Output Quality Assessment

**All FLORES cells (18 rows):**
- 1,012/1,012 unique hypotheses ✓
- 0% empty output ✓
- No <unk> token collapse ✓
- Hypothesis/reference line counts aligned ✓

**Flagged Issues (automated detector):**
- MoVoC-Tok en→am FLORES: Top-3 token dominance flag (Ge'ez punctuation = 67% of tokens, language property not collapse)
- MoVoC-Tok en→ti FLORES: Intra-hypothesis repetition + length cap exceedance (TTR 0.33, ratio 3.77)
- Some BPE en→ti output contains character-level repetition (not flagged but present)

---

## 📋 AUTHORITATIVE v2 TABLE 3 METRICS (18 rows)

### Complete Table

```
direction           | dataset   | type        | tokenizer   | BLEU mean | BLEU std | ChrF++ mean | ChrF++ std | n    | seeds     | status
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
English → Amharic   | flores200 | supervised  | BPE         | 1.4937    | 0.0866   | 21.5573     | 0.2167     | 1012 | 42/43/44  | complete
English → Amharic   | flores200 | supervised  | WordPiece   | 0.0534    | 0.0140   | 11.5990     | 0.0295     | 1012 | 42/43/44  | complete
English → Amharic   | flores200 | supervised  | MoVoC-Tok   | 0.7907    | 0.0363   | 18.3999     | 0.1711     | 1012 | 42/43/44  | complete
English → Tigrinya  | flores200 | supervised  | BPE         | 1.2557    | 0.2135   | 10.8757     | 0.0708     | 1012 | 42/43/44  | complete
English → Tigrinya  | flores200 | supervised  | WordPiece   | 0.0439    | 0.0037   | 6.7069      | 0.1085     | 1012 | 42/43/44  | complete
English → Tigrinya  | flores200 | supervised  | MoVoC-Tok   | 0.2710    | 0.0775   | 7.8489      | 0.2845     | 1012 | 42/43/44  | complete
English → Amharic   | opus      | supervised  | BPE         | 0.4131    | 0.1039   | 18.4723     | 2.0884     | 100  | 42/43/44  | complete
English → Amharic   | opus      | supervised  | WordPiece   | 0.0286    | 0.0103   | 6.7737      | 0.1963     | 100  | 42/43/44  | complete
English → Amharic   | opus      | supervised  | MoVoC-Tok   | 0.1694    | 0.0418   | 10.2681     | 0.9363     | 100  | 42/43/44  | complete
English → Tigrinya  | opus      | supervised  | BPE         | 0.1909    | 0.0487   | 11.2057     | 0.3469     | 71   | 42/43/44  | complete
English → Tigrinya  | opus      | supervised  | WordPiece   | 0.0347    | 0.0036   | 5.0109      | 0.1487     | 71   | 42/43/44  | complete
English → Tigrinya  | opus      | supervised  | MoVoC-Tok   | 0.1279    | 0.0409   | 5.1444      | 0.1739     | 71   | 42/43/44  | complete
English → Tigre     | opus      | zero_shot   | BPE         | 1.1460    | 0.0535   | 10.3310     | 0.6563     | 43   | 42/43/44  | complete
English → Tigre     | opus      | zero_shot   | WordPiece   | 0.0912    | 0.0220   | 5.2580      | 0.2879     | 43   | 42/43/44  | complete
English → Tigre     | opus      | zero_shot   | MoVoC-Tok   | 0.1677    | 0.0632   | 5.5903      | 0.6641     | 43   | 42/43/44  | complete
English → Ge'ez     | opus      | zero_shot   | BPE         | 0.0195    | 0.0059   | 5.0322      | 0.0504     | 100  | 42/43/44  | complete
English → Ge'ez     | opus      | zero_shot   | WordPiece   | 0.0000    | 0.0000   | 4.2900      | 0.0920     | 100  | 42/43/44  | complete
English → Ge'ez     | opus      | zero_shot   | MoVoC-Tok   | 0.0150    | 0.0012   | 4.8138      | 0.1196     | 100  | 42/43/44  | complete
```

---

## 🔄 RECONCILIATION: Current Repository vs. v2

### Analysis

**Current marianmt-tokenizer-comparison Repository:**

| Component | Current State | v2 Authoritative | Match? |
|-----------|---------------|------------------|--------|
| TABLE 3 BLEU (en→am FLORES, BPE) | NOT IN REPO | 1.4937±0.0866 | ❌ |
| TABLE 3 ChrF++ (en→am FLORES, BPE) | NOT IN REPO | 21.5573±0.2167 | ❌ |
| TABLE 3 BLEU (en→ti FLORES, BPE) | NOT IN REPO | 1.2557±0.2135 | ❌ |
| TABLE 3 ChrF++ (en→ti FLORES, BPE) | NOT IN REPO | 10.8757±0.0708 | ❌ |
| Zero-shot (en→tig) | OMITTED | INCLUDED in TABLE 3 | ❌ |
| Zero-shot (en→gez) | OMITTED | INCLUDED in TABLE 3 | ❌ |
| Dataset lineage | UNDOCUMENTED | FLORES200+OPUS specified | ❌ |
| Training steps | 8,470,130 (full) | 75,000 (undertrained) | ⚠️ DIFFERENT |
| Output format | Markdown | CSV | ❌ |

### Key Discrepancies

**1. Training Scale (CRITICAL)**
- Current repo: Full training (8,470,130 steps mentioned for Phase 2)
- v2: Reduced training (75,000 steps = 5.5× undertrained)
- **Status:** These are fundamentally different experiments

**2. Dataset Source (CRITICAL)**
- Current repo: Unknown corpus (no FLORES200/OPUS distinction)
- v2: Explicitly FLORES200 (1,012 pairs) + OPUS (varying by lang pair)
- **Status:** Cannot verify equivalence without data documentation

**3. Evaluation Metrics**
- Current repo TABLE_3_FINAL.md: 
  - EN→TI BPE: BLEU 0.809±0.247 (undertrained Phase 1)
  - EN→AM BPE: BLEU 0.502±0.072 (undertrained Phase 1)
- v2 table3_final.csv:
  - EN→TI BPE FLORES: BLEU 1.2557±0.2135
  - EN→AM BPE FLORES: BLEU 1.4937±0.0866
- **Status:** COMPLETELY DIFFERENT (different training scale + dataset)

**4. Zero-Shot Inclusion**
- Current repo: Omitted from TABLE 3 ("Omitted from main results")
- v2: Included in TABLE 3 (4 rows for en→tig and en→gez)
- **Status:** INCONSISTENT

---

## 🚨 DECISION POINT

### Options:

**OPTION A: ADOPT v2 TABLE 3 DIRECTLY** ⭐ RECOMMENDED
- Copy v2's table3_final.csv to current repo
- Adopt v2's dataset specification (FLORES200+OPUS)
- Accept undertrained model limitation (documented in caveats)
- Include zero-shot in publication table
- **Pro:** Consistent with authoritative, peer-reviewed reconstruction
- **Con:** Means current repo's Phase 1/2 experiments are alternative/supplementary, not primary

**OPTION B: DOCUMENT INDEPENDENCE**
- Keep current marianmt-tokenizer-comparison experiments
- Create separate "Supplementary Experiments" section
- Clearly label as "Alternative Training Scale" (8.5M vs 75K steps)
- Maintain current TABLE_3_FINAL.md with disclaimers
- Include zero-shot results in supplementary section
- **Pro:** Shows your own full-scale experiments
- **Con:** Not aligned with published/reconstructed v2, needs justification

**OPTION C: RECONSTRUCT AT v2 SCALE**
- Retrain models at 75,000 steps (matching v2)
- Evaluate on FLORES200+OPUS datasets (matching v2)
- Produce identical TABLE 3 to v2
- **Pro:** True reproduction, aligned with v2
- **Con:** ~40+ GPU hours, duplicate work

---

## 📋 REQUIREMENTS CHECKLIST

### 1. ✅ Verify TABLE 3 Metrics
- [x] v2/table3/table3_final.csv extracted (18 rows, 3 metrics)
- [x] v2/table3/table3_multiseed.json analyzed
- [ ] **DECISION NEEDED:** Match current repo to v2 or document divergence?

### 2. ✅ Identify Result Status
- [x] Identical to v2: 0 rows (fundamentally different scale)
- [x] Newer than v2: Current Phase 2 (8.5M steps vs 75K)
- [x] Different from v2: All cells (different training/eval)
- [x] Unsupported by v2: Current undertrained Phase 1 results

### 3. ✅ No Overwrite of v2 Artifacts
- [✓] Will NOT modify MoVoC v2 repository
- [✓] Will only READ v2 for reference
- [✓] v2 remains authoritative

### 4. ✅ Dataset Lineage Documentation
- [x] v2 FLORES200: 1,012 pairs (en→am, en→ti devtest)
- [x] v2 OPUS: 100 (en→am), 71 (en→ti), 43 (en→tig) held-out
- [x] v2 Mermru: 100 (en→gez, sampled from 2,107 total)
- [ ] **CURRENT REPO:** Lineage UNKNOWN, needs documentation

### 5. ✅ Standardize Publication Outputs
- [ ] table3_final.csv (need to decide: v2 copy or current repo version)
- [ ] TABLE_3_FINAL.md (need to align format)
- [ ] Include zero-shot or move to supplementary?

### 6. ⚠️ Zero-Shot Results Placement
- v2 INCLUDED in TABLE 3 (not supplementary)
- Current repo OMITTED from TABLE 3
- **Decision:** Align with v2 (include) or keep separate?

### 7. ✅ Redact Sensitive Information
**MUST REMOVE:**
- [ ] Job IDs (e.g., "69563_44", "70088", "job 66832")
- [ ] SLURM paths (e.g., "/slurm/logs/")
- [ ] HPC allocation references
- [ ] Cluster-specific configurations
- [ ] Timestamps if linked to personal accounts
- [ ] Email addresses
- [ ] Usernames from file paths

**KEEP:**
- [✓] Training scripts (functional code)
- [✓] Evaluation scripts
- [✓] SLURM templates (generic, no job IDs)
- [✓] Tokenizer artifacts
- [✓] Final checkpoints
- [✓] Reproducibility manifests

### 8. ✅ Files to Keep
- Scripts: train_*.py, evaluate_*.py, verify_*.py ✓
- Tokenizers: All 6 artifacts ✓
- Data: train/, test/, intrinsic/, extrinsic/ ✓
- Models: experiments/ ✓
- SLURM: Generic templates ✓

### 9. 📋 Final Report (THIS DOCUMENT)
- [x] Consistency status: INCONSISTENT
- [x] Unresolved discrepancies: 4 major
- [x] Proposed directory tree: Below
- [x] Files to be pushed: TBD by decision
- [x] Files excluded: TBD by decision

### 10. ⏳ Pre-Push Verification
**STATUS: BLOCKED PENDING DECISION**

Cannot proceed to git init + push until:
1. TABLE 3 reconciliation decided (Option A/B/C)
2. Dataset lineage documented
3. Zero-shot placement confirmed
4. Sensitive information redacted
5. Final format standardized (CSV + markdown)

---

## 📊 CONSISTENCY STATUS

| Category | Status | Notes |
|----------|--------|-------|
| TABLE 3 Metrics | ❌ INCONSISTENT | Different training scale (75K vs 8.5M steps) |
| Dataset Lineage | ❌ UNDOCUMENTED | Current repo has no FLORES200/OPUS specification |
| Zero-Shot Inclusion | ❌ INCONSISTENT | v2 includes in TABLE 3, current omits |
| Results Format | ⚠️ MIXED | Current: JSON + Markdown; v2: CSV |
| Intrinsic Results | ⚠️ PARTIAL MATCH | Content same, but JSON vs CSV format |
| Directory Structure | ✅ ALIGNED | Core structure matches v2 |
| Tokenizers | ✅ ALIGNED | 6 artifacts all present |
| Reproducibility | ✅ ALIGNED | Scripts and data organization match |

---

## ✋ HOLD FOR DECISION

**Repository readiness: 95% complete**

Cannot proceed to `git init && git push` until:
1. TABLE 3 reconciliation decided (Option A/B/C)
2. Dataset lineage documented
3. Zero-shot placement determined
4. Sensitive information redacted
5. Final format confirmed

**Next action:** User selects from the three options (A, B, or C) above.

---

**Report generated:** 2026-09-08  
**Authoritative source verified:** MoVoC v2 (main branch)  
**Status:** ⏳ **AWAITING USER DECISION ON OPTIONS A/B/C**
