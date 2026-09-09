# MarianMT Tokenizer Comparison — Independent Full-Scale Experiments

## Status Statement

**This repository contains independent full-scale MarianMT tokenizer comparison experiments archived as part of the MoVoC project. The results should not be interpreted as a direct reproduction of the published Table 3 unless explicitly stated.**

---

## What This Repository Is

This repository documents independent, full-scale experiments comparing three tokenization strategies (BPE, WordPiece, MoVoC-Tok) applied to English-to-Amharic and English-to-Tigrinya machine translation tasks using the MarianMT framework.

**Key characteristics:**
- **Full-scale training:** 8,470,130 optimizer steps per model
- **Complete evaluation:** Supervised + zero-shot translation tasks
- **Three tokenizers:** BPE, WordPiece, MoVoC-Tok (32K vocab each)
- **Multiple seeds:** 42, 43, 44 for reproducibility
- **Quality control:** Convergence validation and cross-seed consistency analysis

---

## Relationship to Published Paper

### Published Paper (Authoritative)

**Title:** MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages  
**Publication:** Findings of EMNLP 2025  
**ArXiv:** https://arxiv.org/abs/2509.08812

The published paper reports original Table 3 results that are the authoritative scientific record. This repository **does not reproduce those values**.

### Key Differences

| Aspect | Published Paper | This Repository |
|--------|-----------------|-----------------|
| Training scale | ~416K optimizer steps (baseline reported) | 8,470,130 optimizer steps (full training) |
| Status | Original published results | Independent full-scale experiments |
| Claim | Definitive findings from original evaluation | Complementary analysis at different scale |

The published results should be cited when referencing the original research. This repository's results are independent and should be cited separately.

---

## Relationship to v2 Reconstruction

The MoVoC project includes a v2 reconstruction effort (`https://github.com/hailaykidu/MoVoC/tree/main/v2`) that attempts to reproduce parts of the published work at reduced scale (75,000 steps). This repository's experiments differ from v2:

- **v2 scale:** 75,000 optimizer steps (5.5× undertrained for methodological reasons)
- **This repo scale:** 8,470,130 optimizer steps (full training)
- **v2 status:** Reconstruction with known limitations; v2 explicitly states "not a direct reproduction"
- **This repo status:** Independent full-scale alternative evaluation

---

## Experimental Design

### Training Configuration

**Language Pairs:** 2
- English → Amharic
- English → Tigrinya

**Tokenizers:** 3 per language pair
- Byte-Pair Encoding (BPE)
- WordPiece
- MoVoC-Tok (morphology-aware)

**Training Setup:**
- Base model: Pre-trained MarianMT
- Vocabulary size: 32K tokens per tokenizer
- Optimizer steps: 8,470,130 per model
- Random seeds: 42, 43, 44
- Total Phase 1 models: 24 (2 languages × 3 tokenizers × 4 seeds)

**Validation:**
- Full convergence validation across all seeds
- Cross-seed consistency analysis (coefficient of variation)
- Loss stabilization verification

### Evaluation

**Supervised Tasks:**
- EN→Amharic: Evaluation on held-out test set
- EN→Tigrinya: Evaluation on held-out test set

**Zero-Shot Transfer (Supplementary):**
- EN→Tigre: Cross-lingual transfer using Tigrinya-trained models
- EN→Ge'ez: Cross-lingual transfer using Tigrinya-trained models

**Metrics:**
- BLEU (with sacrebleu 2.6.0+ implementation)
- ChrF++ (character n-gram F-score)
- Reported as mean ± standard deviation across seeds

---

## Results

### Supervised Results (Main Findings)

Results for English-to-Amharic and English-to-Tigrinya translation tasks, evaluated on standard test sets.

See: `results/TABLE_3_FINAL.md`

**Key Observations:**
- Cross-seed consistency: Coefficient of variation < 5% for most tokenizers
- All models achieve full convergence (loss stability confirmed)
- Tokenizer rankings differ from published paper due to full-scale training

### Zero-Shot Results (Supplementary)

Results for unseen language pairs (Tigre, Ge'ez) evaluated using models trained on Amharic or Tigrinya data.

See: `results/ZERO_SHOT_SUPPLEMENTARY.md`

**Status:** These results are included for completeness but are supplementary to the main supervised evaluation.

---

## Repository Contents

```
marianmt-tokenizer-comparison/
│
├── README.md ........................... This file
├── MANIFEST.md ......................... Complete experiment manifest
├── CITATION.md ......................... Citation information
├── requirements.txt .................... Python dependencies
├── .gitignore .......................... Git configuration
│
├── docs/ ............................... Documentation
│   ├── convergence_analysis.md ......... Convergence validation report
│   ├── experiment_status.md ............ Complete experiment status
│   └── dataset_description.md .......... Dataset specifications
│
├── data/ ............................... Training and test data
│   ├── train/{en_am, en_ti}/ .......... Training data
│   ├── test/{en_am, en_ti}/ ........... Supervised test sets
│   └── extrinsic/{en_geez, en_tigre}/ . Zero-shot test data
│
├── tokenizers/ ......................... Pre-trained tokenizers
│   ├── en_am_{bpe, movoc, wordpiece}/ . Amharic tokenizers
│   └── en_ti_{bpe, movoc, wordpiece}/ . Tigrinya tokenizers
│
├── experiments/ ........................ Trained models (44 GB)
│   ├── en_am/{bpe, movoc_tok, wordpiece}/seed_{42,43,44}/
│   ├── en_ti/{bpe, movoc_tok, wordpiece}/seed_{42,43,44}/
│   ├── en_am_full_validation_correct_tok/movoc_tok/seed_{42,43}/
│   ├── en_ti_full_validation/{bpe, movoc_tok}/seed_{42,44}/
│   └── zero_shot_evaluation_seeds_focused/results.json
│
├── results/ ............................ Evaluation results
│   ├── TABLE_3_FINAL.md ................ Main supervised results
│   ├── table3_final.csv ................ Results in CSV format
│   ├── ZERO_SHOT_SUPPLEMENTARY.md ..... Zero-shot results (separate section)
│   ├── phase1_baseline/{en_am, en_ti}/ Phase 1 detailed results
│   ├── phase2_fullval/{en_am, en_ti}/ . Phase 2 convergence validation
│   └── phase3_zeroshot/ ............... Zero-shot evaluation
│
├── scripts/ ............................ Training and evaluation code
│   ├── train_en_ti_full_validation.py . Tigrinya Phase 2 training
│   ├── train_en_am_full_validation_correct_tok.py .. Amharic Phase 2
│   ├── zero_shot_evaluation_seeds_focused.py .... Zero-shot evaluation
│   ├── evaluate_checkpoint.py .......... Checkpoint evaluation
│   ├── verify_data.py .................. Data verification
│   ├── verify_models.py ................ Model verification
│   └── [other utility scripts]
│
├── src/ ............................... Source code package
│   └── marianmt_comparison/ ........... Main module
│       ├── config.py
│       ├── data.py
│       ├── tokenization.py
│       ├── training.py
│       ├── evaluation.py
│       └── reproducibility.py
│
├── slurm/ ............................. SLURM cluster templates
│   ├── submit_en_ti_full_validation.sbatch
│   ├── submit_en_am_full_validation_correct_tok.sbatch
│   ├── submit_zero_shot_seeds_focused.sbatch
│   └── [other job submission templates]
│
├── Extrinsic_Evaluation/ .............. Phase 3 evaluation pipeline
│   ├── scripts/
│   ├── configs/
│   └── results/
│
└── Intrinsic_Evaluation/ .............. Intrinsic evaluation artifacts
    ├── scripts/
    ├── results/
    └── [evaluation data files]
```

---

## Citation

To cite this repository, use:

```bibtex
@software{marianmt_tokenizer_comparison_2026,
  title={MarianMT Tokenizer Comparison — Independent Full-Scale Experiments},
  author={[Your Name]},
  year={2026},
  url={https://github.com/[your-username]/marianmt-tokenizer-comparison},
  note={Independent full-scale experiments; not a reproduction of published Table 3}
}
```

See `CITATION.md` for additional citation formats.

---

## Reproducibility

All trained models, tokenizers, and evaluation results are included in this repository. To reproduce the results:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Evaluate trained models:**
   ```bash
   python scripts/zero_shot_evaluation_seeds_focused.py --output-dir results/
   ```

3. **Generate results table:**
   ```bash
   # Results are pre-computed and available in results/TABLE_3_FINAL.md
   ```

For full training reproduction, see the training scripts in `scripts/` and SLURM templates in `slurm/`.

---

## Important Notes

### On Result Comparison

These results were obtained under different experimental conditions than the published paper and should **not be directly compared** to published Table 3 values without explicit acknowledgment of the differences:

- Different training scale (8.47M vs ~416K steps)
- Different optimization trajectory
- Potentially different underlying datasets

Any comparison should explicitly note these methodological differences.

### On Reproducibility Claims

This repository **does not claim** to reproduce the published paper's evaluation pipeline. The original scoring pipeline and exact training configuration are not preserved, making exact reproduction impossible.

### On Statistical Interpretation

All results are reported with means and standard deviations across seeds (42, 43, 44) to enable statistical analysis. Cross-seed consistency is validated in `docs/convergence_analysis.md`.

---

## Data and Code Availability

**Data:** Training data (tokenizers, test sets) are included or linked.  
**Code:** All training and evaluation scripts are included.  
**Models:** All trained checkpoints are included (44 GB total).  
**Results:** All evaluation results are included in `results/`.  

---

## License

This repository is released under [MIT/Apache 2.0]. See LICENSE file for details.

---

## Acknowledgments

This work builds on:
- **MoVoC:** Original morphological tokenizer framework
- **MarianMT:** Neural machine translation framework
- **HuggingFace Transformers:** ML infrastructure
- **MoVoC v2 Reconstruction:** Reference methodology for evaluation design

---

## Questions & Contact

For questions about this repository:
1. Check `MANIFEST.md` for complete experimental specifications
2. Check `docs/experiment_status.md` for detailed methodology
3. Check `docs/convergence_analysis.md` for quality control details

---

**Last Updated:** 2026-09-08  
**Status:** Ready for publication as independent experiment package  
**Push Approval:** Pending cleanup audit completion
