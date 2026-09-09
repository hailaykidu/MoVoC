# Repository Context

This repository contains **independent full-scale MarianMT fine-tuning experiments** to compare MoVoC-Tok tokenizer on low-resource African languages. Results should not be interpreted as direct reproduction of published Table 3, but anyone can reproduce the extrinsic evaluation part from here.

## ⚠️ Important

- **NOT** direct reproduction of published results
- **NOT** official MoVoC publication
- **Independent** extrinsic (machine translation) evaluation
- Anyone can **reproduce** these experiments from included materials

## 📊 What's Included

**Test Data:** 405 pairs (4 language pairs)
- EN→Amharic: 100 pairs
- EN→Tigrinya: 102 pairs
- EN→Ge'ez: 100 pairs (zero-shot)
- EN→Tigre: 103 pairs (zero-shot)

**Experiments:** 35/36 completed (97%)
- 3 tokenizers (BPE, WordPiece, MoVoC-Tok)
- 3 random seeds each (42, 43, 44)
- Multi-seed evaluation with Mean ± SD, CV%

**Reproducibility Materials:**
- Complete source code (12 scripts)
- Configuration files
- Pre-trained models (18 files)
- Evaluation scripts
- Training logs
- Results and metrics

## 🔍 Interpretation

**Valid:**
- "MoVoC-Tok shows strong performance on Amharic in this extrinsic evaluation"
- "These results demonstrate morphological transfer effectiveness"
- "Independent validation of tokenizer comparison"

**Invalid:**
- "This is the published Table 3"
- "This directly reproduces the official paper"
- "These are peer-reviewed results"

## 📝 Citation

If citing this repository:
```
This is independent extrinsic evaluation (downstream task evaluation) 
of tokenizer comparison. Distinguish from the official published paper 
when citing results.
```

## 📁 Repository Structure

```
PUBLICATION_PACKAGE/
├── 1_CODE/ - Training & evaluation scripts
├── 2_CONFIG/ - Configuration files
├── 4_MODELS/ - Pre-trained models
├── 5_RESULTS/ - Evaluation results
├── 6_SCRIPTS/ - SLURM scripts
└── 8_ARCHIVE/ - Archived development artifacts

data/ - 405 evaluation pairs
experiments/ - Model training results
```

## ✅ Reproducibility

- Complete experimental setup documented
- Random seeds: 42, 43, 44
- Hyperparameters in configs
- Training scripts available
- Statistical analysis reproducible

---

**Repository Purpose:** Independent extrinsic evaluation (machine translation) of MoVoC-Tok tokenizer comparison  
**Status:** Research archive, not peer-reviewed publication  
**Completion:** 35/36 experiments (97%)

