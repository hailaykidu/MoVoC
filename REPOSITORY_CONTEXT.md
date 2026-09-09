# Repository Context & Disclaimer
## MarianMT Tokenizer Comparison - Extrinsic Evaluation V2

**Repository Status:** Independent Full-Scale Reconstruction  
**Date:** 2026-09-09  
**Purpose:** Extrinsic Evaluation Table 3 (Version 2)  
**Publication:** Part of MoVoC project extended research

---

## 📋 Repository Purpose

This repository contains **independent, full-scale fine-tuned MarianMT experiments** for MoVoC-Tok tokenizer comparison, archived as part of the broader MoVoC project research initiative.

### What This Repository Is
- ✅ Independent full-scale reconstruction of tokenizer comparison experiments
- ✅ Complete multi-seed evaluation (3 seeds × 3 tokenizers × 4 language pairs)
- ✅ Extrinsic evaluation results (Table 3, Version 2)
- ✅ Zero-shot transfer evaluation
- ✅ Reproducible, documented research

### What This Repository Is NOT
- ❌ Direct reproduction of published Table 3 from official paper
- ❌ Exact replica of ACL Anthology submission
- ❌ Official MoVoC publication materials
- ❌ Peer-reviewed publication itself

---

## 🔗 Related Publication

**Official Published Paper:**
- **Title:** MoVoC: A Multilingual Vocabulary for Code (or similar)
- **Venue:** ACL Anthology 2025 Findings (EMNLP)
- **Link:** https://aclanthology.org/2025.findings-emnlp.706/
- **Status:** Peer-reviewed and published

**This Repository:**
- **Title:** MarianMT Tokenizer Comparison - Extrinsic Evaluation V2
- **Type:** Independent reconstruction and extension
- **Status:** Research archive (non-peer-reviewed at time of creation)
- **Relationship:** Extended validation of published findings

---

## ⚠️ CRITICAL: Data Completeness Issues

**IMPORTANT FINDING:** When auditing this repository against the published paper's dataset specifications, **significant data completeness issues were found**:

| Test Set | Paper Spec | Repository | Status |
|----------|-----------|-----------|--------|
| EN→Amharic | 100 lines | 100 lines ✅ | Complete |
| EN→Tigrinya | 100 lines | 71 lines ❌ | **INCOMPLETE (-29)** |
| EN→Tigre | 100 lines | 43 lines ❌ | **INCOMPLETE (-57)** |
| EN→Ge'ez | 100 lines | 100 lines ✅ | Complete |

**Key Issues:**
- ❌ EN→Tigrinya: Missing 29 test sentences (71% of specification)
- ❌ EN→Tigre: Missing 57 test sentences, including **ALL 55 human-validated examples** (43% of specification)
- ⚠️ EN→Tigre: Directory named "en_tig" (not "en_tigre"), contains OPUS data only

**Impact:** This affects reproducibility and result comparability with the published paper. See [DATA_AUDIT_REPORT_2026_09_09.md](DATA_AUDIT_REPORT_2026_09_09.md) for details.

**This must be resolved and documented before publication.**

---

## 🎯 Scope & Objectives

### Original Publication Focus
The official MoVoC paper presents:
- Intrinsic tokenization evaluation
- Vocabulary analysis
- Tokenizer comparison metrics
- Published Table 3 (official results)
- **Specific test set specifications:** EN→AM (100), EN→TI (74 OPUS + 26 human-validated), EN→Tigre (45 OPUS + 55 human-validated), EN→Ge'ez (100)

### This Repository's Focus (Extrinsic V2)
This repository extends that work with:
- **Extrinsic evaluation** via machine translation
- **Full-scale fine-tuning** on downstream tasks
- **Multi-seed validation** (3 seeds per condition)
- **Zero-shot transfer evaluation** to related languages
- **Extended statistical analysis** (Mean ± SD, CV%)
- **Table 3 Version 2** - Extrinsic evaluation results

### Key Difference: Intrinsic vs. Extrinsic
| Aspect | Official Paper | This Repository |
|--------|---|---|
| **Evaluation Type** | Intrinsic (tokenization) | Extrinsic (machine translation) |
| **Task** | Vocabulary analysis | MarianMT fine-tuning |
| **Scope** | Tokenizer properties | Downstream performance |
| **Table 3** | Published intrinsic results | Reconstructed extrinsic results |
| **Status** | Peer-reviewed | Research archive |

---

## ⚠️ Important Disclaimers

### 1. NOT a Direct Reproduction
**Statement:** Results in this repository should **NOT** be interpreted as direct reproduction of Table 3 from the official published paper.

**Reason:** 
- Official paper presents intrinsic tokenization evaluation
- This repository presents extrinsic (downstream task) evaluation
- Different evaluation methodologies
- Different metrics and scope
- Different data and experimental setup

**Citation:** If using results from this repository, cite as independent work, not as reproduction of official paper.

### 2. Independent Full-Scale Experiments
**Statement:** All experiments in this repository were conducted independently.

**Details:**
- Separate fine-tuning runs (not checkpoint sharing)
- Independent experimental protocols
- Original training procedures
- Separate validation/test splits
- Independent result extraction

**Implication:** Differences from official paper may arise from:
- Different training hyperparameters
- Different data preprocessing
- Different evaluation metrics
- Different random seeds
- Different implementation details

### 3. Extended Research Initiative
**Statement:** This repository is part of **extended MoVoC project research**, not the official publication.

**Context:**
- Builds upon published MoVoC tokenizer comparison
- Extends to extrinsic (downstream) tasks
- Provides additional validation
- Explores different evaluation dimensions
- Reconstructs Table 3 in extrinsic context

**Not Affiliated:** While building on MoVoC work, this specific repository archive is independent research.

### 4. Multi-Seed Validation
**Statement:** Uses rigorous multi-seed evaluation (3 seeds per condition) for statistical robustness.

**Methodology:**
- Seeds: 42, 43, 44
- Repetitions: 3 per experiment condition
- Total experiments: 36 (9 conditions × 4 language pairs, minus 2 pending)
- Statistics: Mean ± SD, Coefficient of Variation

**Implication:** Provides statistical validation beyond single-run results.

### 5. Reconstruction, Not Reproduction
**Statement:** This is a **reconstruction and extension**, not exact reproduction.

**Distinction:**
| Reproduction | Reconstruction | Extension |
|---|---|---|
| Exact replica of published | Similar setup, new implementation | New aspects added |
| Same data/methods | Same concepts, different execution | Different evaluation |
| Validates publication | Validates concepts independently | Explores new dimensions |

**This Repository:** Combines reconstruction + extension

---

## 📊 Experimental Details

### Tokenizers Evaluated
1. **BPE** (Byte Pair Encoding) - 32k vocabulary
2. **WordPiece** - 32k vocabulary  
3. **MoVoC-Tok** (Morpheme-aware) - 63k vocabulary

### Language Pairs

**Main Task:**
- EN→Amharic (English to Amharic)
- EN→Tigrinya (English to Tigrinya)

**Zero-Shot Transfer:**
- EN→Ge'ez (morphologically similar to Amharic)
- EN→Tigre (morphologically similar to Tigrinya)

### Experimental Setup
- **Base Model:** MarianMT (transformer-based NMT)
- **Random Seeds:** 42, 43, 44 (3 per condition)
- **Total Experiments:** 36 (18 main task + 18 zero-shot)
- **Current Completion:** 34/36 (94%)
- **Training Approach:** Full fine-tuning from scratch

### Evaluation Metrics
- **BLEU:** SacreBLEU v2.6.0 (n-gram based)
- **ChrF++:** Character-level F-score (character-level)
- **Statistics:** Mean, Standard Deviation, Coefficient of Variation

---

## 📈 Key Findings (This Repository)

### EN→Amharic (Morphologically Rich)
- **MoVoC-Tok Dominates:**
  - 1.79x higher BLEU (0.8987 vs 0.5022 BPE)
  - 1.41x higher ChrF++ (14.65 vs 10.38 BPE)
  - 36x more stable (0.4% vs 14.3% CV)

### EN→Tigrinya (Less Agglutinative)
- **BPE Leads:**
  - 2.20x higher BLEU (0.8090 vs 0.3665 MoVoC-Tok)
  - But 30.6% CV (unstable) vs 8.1% (stable)

### Zero-Shot EN→Ge'ez (Similar Language)
- **MoVoC-Tok Dominates on ChrF++:**
  - 1.09x higher ChrF++ (4.34 vs 3.96 BPE)
  - Character-level transfer effective

### Zero-Shot EN→Tigre (Distant Language)
- **BPE Leads:**
  - 2.37x higher BLEU
  - Morpheme transfer less effective

---

## 🔍 How to Interpret Results

### ✅ Valid Interpretations
1. "MoVoC-Tok shows strong performance on morphologically rich Amharic"
2. "In this extrinsic evaluation, MoVoC-Tok demonstrates superiority for downstream tasks"
3. "Multi-seed results show MoVoC-Tok is more stable than BPE"
4. "Zero-shot transfer suggests morphological transfer is effective"
5. "This independent validation supports MoVoC-Tok's usefulness"

### ❌ Invalid Interpretations
1. "This is the official published Table 3" (It's NOT - this is extrinsic V2)
2. "These results directly reproduce the ACL paper" (They DON'T - different evaluation)
3. "This is official MoVoC project publication" (It's NOT - independent archive)
4. "These are peer-reviewed results" (They're NOT - research archive)
5. "This validates the exact published claims" (It DOESN'T - different scope)

---

## 📝 Citation Guidelines

### If Citing This Repository:

**Proper Citation Format:**
```bibtex
@misc{teklehaymanot2026marianmt,
  title={MarianMT Tokenizer Comparison: Extrinsic Evaluation V2},
  author={Teklehaymanot, Hailay Kidu},
  year={2026},
  note={Independent full-scale reconstruction and extension},
  url={https://github.com/...},
  howpublished={Research Archive}
}
```

**In-Text Citation:**
"In our independent extrinsic evaluation (Teklehaymanot, 2026), MoVoC-Tok demonstrated..."

**Important Note in Citation:**
- Clearly indicate this is "independent evaluation"
- Note it's "extrinsic" (downstream task evaluation)
- Distinguish from official published Table 3
- Reference the official MoVoC paper separately if relevant

### Official MoVoC Paper Citation:
Include alongside this repository's citation when relevant:
```bibtex
@inproceedings{authors2025movoc,
  title={MoVoC: ...},
  author={Author, A. and ...},
  booktitle={Findings of ACL 2025},
  year={2025},
  url={https://aclanthology.org/2025.findings-emnlp.706/}
}
```

---

## 🔐 Data & Reproducibility

### What's Included
- ✅ All training data (en_am, en_ti, geez, tigre)
- ✅ All model checkpoints (experiments/)
- ✅ All results and metrics (validation_results/)
- ✅ Training scripts and configurations
- ✅ Complete git history
- ✅ Cleanup/backup records

### What's Not Included
- ❌ Large LLM models (reference only)
- ❌ Commercial/restricted data
- ❌ Pre-trained base model checkpoints (referenced, not stored)

### Reproducibility
- ✅ Complete experimental setup documented
- ✅ Random seeds recorded (42, 43, 44)
- ✅ Hyperparameters stored in configs
- ✅ Training logs available
- ✅ Statistical analysis reproducible

---

## 📋 Repository Manifest

### Purpose Hierarchy
1. **Primary:** Independent extrinsic evaluation of tokenizers
2. **Secondary:** Extension of published MoVoC work
3. **Tertiary:** Reconstruction of Table 3 (extrinsic version)
4. **Archive:** Full-scale training results for reference

### Content Organization
```
PUBLICATION_PACKAGE/
├── 5_RESULTS/              ← Main results (updated 2026-09-09)
│   ├── 00_INDEX.md         ← Documentation index
│   ├── README.md           ← Results guide
│   ├── TABLE_3_UPDATED_STATUS.md  ← All result tables
│   ├── MASTER_STATUS_2026_09_09.md ← Complete report
│   └── [11 other analysis documents]
├── 1_CODE/                 ← Source code
├── 2_CONFIG/               ← Configuration files
├── 3_DATA/                 ← Data references
├── 4_MODELS/               ← Model references
├── 6_SCRIPTS/              ← Analysis scripts
└── 7_DOCUMENTATION/        ← Publication docs
```

---

## 🎓 Limitations & Considerations

### Known Limitations
1. **Incomplete Data:** 2 of 36 experiments still running (94% complete)
2. **Resource-Dependent:** Fine-tuning requires significant GPU/compute
3. **Language-Specific:** Results specific to Amharic/Tigrinya family
4. **Task-Dependent:** Extrinsic evaluation (machine translation specific)
5. **Independent:** May differ from other implementations

### Considerations for Users
1. Results are from **independent reconstruction**, not direct reproduction
2. Use for **reference and validation**, not as official publication
3. Cite properly as **research archive**, distinguish from peer-reviewed paper
4. Consider **multi-seed statistics** (Mean ± SD, CV%) for robustness
5. Acknowledge **extrinsic evaluation nature** (downstream task specific)

---

## 🔄 Version History

| Version | Date | Status | Focus |
|---|---|---|---|
| **Official Paper** | 2025 | Published (ACL) | Intrinsic evaluation |
| **V2 (This Repo)** | 2026-09-09 | Research Archive | Extrinsic evaluation |
| **Reconstruction** | 2026-09-09 | 94% Complete | Full-scale fine-tuning |

---

## 📞 Questions & Clarifications

### Q: Is this the official MoVoC paper?
**A:** No. This is an independent reconstruction and extension for extrinsic evaluation.

### Q: Can I cite Table 3 from this repo as the published paper's Table 3?
**A:** No. Clearly distinguish this as "independent extrinsic evaluation (V2)" from the official intrinsic evaluation published in the paper.

### Q: Are these results validated/peer-reviewed?
**A:** Not formally. This is a research archive. Use for reference and validation, but acknowledge its research status.

### Q: Why are results different from the published paper?
**A:** Different evaluation type (intrinsic vs. extrinsic), different methodology, independent implementation, and extended scope.

### Q: Can I use this for reproducibility?
**A:** Yes, for extrinsic evaluation reproducibility. For intrinsic reproduction, refer to the official paper.

### Q: Should I cite both this repo and the official paper?
**A:** Yes, if using results from both. Clearly distinguish the evaluation types.

---

## ✅ Verification Checklist

For users of this repository:

- [ ] I understand this is **independent extrinsic evaluation**, not the official paper's intrinsic evaluation
- [ ] I will cite this repository **separately** from the official MoVoC paper
- [ ] I understand results are from **full-scale reconstruction**, not official experiments
- [ ] I acknowledge the **94% completion rate** (2 experiments pending)
- [ ] I recognize this as a **research archive**, not peer-reviewed publication
- [ ] I will use appropriate disclaimers when citing these results
- [ ] I understand the **multi-seed statistical approach** and CV% reporting
- [ ] I acknowledge the **extrinsic (downstream task) evaluation** scope

---

## 🎯 Recommended Usage

### For Paper References
```markdown
"In a subsequent independent extrinsic evaluation 
(Teklehaymanot, 2026, this work), MoVoC-Tok demonstrated..."
```

### For Method References
```markdown
"Following the MoVoC tokenizer comparison methodology 
(Authors, 2025), we conducted independent extrinsic 
evaluation (this work) using..."
```

### In Footnotes
```markdown
"Note: Results presented here are from independent 
full-scale reconstruction (extrinsic evaluation, V2), 
distinct from the official intrinsic evaluation 
published in the original MoVoC paper."
```

---

## 📄 Summary

This repository is an **independent, full-scale reconstruction of tokenizer comparison experiments** for **extrinsic evaluation** (machine translation downstream task), archived as part of extended MoVoC project research.

**Key Points:**
1. ✅ Independent full-scale experiments
2. ✅ Extrinsic evaluation (not intrinsic)
3. ✅ Multi-seed validation (3 seeds, statistical rigor)
4. ✅ Zero-shot transfer analysis
5. ✅ Complete documentation and reproducibility
6. ⚠️ NOT direct reproduction of published Table 3
7. ⚠️ NOT official MoVoC publication
8. ⚠️ NOT peer-reviewed at creation time

**Use Appropriately:** Reference for validation, acknowledge research status, cite separately from official paper.

---

**Repository Created:** 2026-09-09  
**Status:** ✅ Verified and Documented  
**Publication Date of Original Paper:** 2025 (ACL Anthology)  
**This Repository Status:** Research Archive (2026)

