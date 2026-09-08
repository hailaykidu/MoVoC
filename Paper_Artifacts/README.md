# Paper Artifacts & Results

This directory contains symbolic links to the main paper results and supporting documentation.

## 📊 Main Results Tables

### Table 2: Intrinsic Evaluation Results
**File:** [table2_final.md](../Intrinsic_Evaluation/reports/table2_final.md)

Intrinsic tokenization evaluation metrics:
- Morphological segmentation accuracy
- Coverage and vocabulary statistics
- Character error rate (CER)
- Performance across tokenizer types (BPE, WordPiece, MoVoC-Tok)

### Table 3: Extrinsic Evaluation (Machine Translation)
**File:** [table3_final.md](../results/TABLE_3_FINAL_CLEAN.md)

Main machine translation results:
- BLEU scores (SacreBLEU)
- ChrF++ character-level F-score
- Language pairs: EN→Amharic, EN→Tigrinya
- Cross-validation with 3 random seeds (42, 43, 44)
- **16/18 complete experiments** (2 archived as incomplete)

**Updated Clean Version:** [TABLE_3_FINAL_CLEAN.md](../results/TABLE_3_FINAL_CLEAN.md)
- Contains only complete, comparable experiments
- Documents archived incomplete runs

### Table 4: Zero-Shot Transfer Results
**File:** [table4_final.md](../Intrinsic_Evaluation/reports/table4_final.md)

Zero-shot evaluation on related languages:
- EN→Tigre
- EN→Ge'ez
- Transfer performance from tokenizers trained on EN→Amharic/Tigrinya

## 📚 Reproducibility Documentation

**Directory:** [reproducibility_docs](../docs/)

Complete documentation for reproducing results:
- [methodology.md](../docs/methodology.md) — Experimental setup and protocols
- [dataset_description.md](../docs/dataset_description.md) — Data sources and preparation
- [convergence_analysis.md](../docs/convergence_analysis.md) — Training convergence metrics

## 🗂️ Data & Models

### Training Data & Manifests
- [DATA_MANIFEST.md](../DATA_MANIFEST.md) — Data retrieval instructions and sources
- [MODEL_MANIFEST.md](../MODEL_MANIFEST.md) — Model metadata and storage locations

### Experiment Results
- **Intrinsic Evaluation:** [Intrinsic_Evaluation/](../Intrinsic_Evaluation/)
- **Extrinsic Evaluation:** [Extrinsic_Evaluation/](../Extrinsic_Evaluation/)
- **Experiments:** [experiments/](../experiments/)

### Archive
- **Incomplete Experiments:** [archive/ARCHIVE_README.md](../archive/ARCHIVE_README.md)
  - EN→AM BPE seed_42 (failed)
  - EN→AM MoVoC-Tok seed_44 (incomplete)

## 📖 Citation

If you use these results, please cite the paper:

```bibtex
@article{teklehaymanot2025movoc,
  title={MoVoC: Morpheme-aware Vocabulary Construction for Machine Translation},
  author={Teklehaymanot, Hailay Kidu and ...},
  year={2025}
}
```

See [CITATION.md](../CITATION.md) for full citation information.

## 🔍 Quick Navigation

| Resource | Link |
|----------|------|
| Main Results (Table 3 - Clean) | [TABLE_3_FINAL_CLEAN.md](../results/TABLE_3_FINAL_CLEAN.md) |
| Intrinsic Results (Table 2) | [Intrinsic_Evaluation/](../Intrinsic_Evaluation/) |
| Extrinsic Results (Table 3) | [Extrinsic_Evaluation/](../Extrinsic_Evaluation/) |
| Training Data | [data/](../data/) |
| Experiments | [experiments/](../experiments/) |
| Archive (Incomplete) | [archive/](../archive/) |
| Manifests | [DATA_MANIFEST.md](../DATA_MANIFEST.md) / [MODEL_MANIFEST.md](../MODEL_MANIFEST.md) |

## ℹ️ Note on Symbolic Links

This directory uses symbolic links to point to the actual results files elsewhere in the repository. GitHub's web interface may show these as symbolic links rather than navigable directories. Use the links above to access the files directly.

For local access:
```bash
# View symbolic links
ls -l Paper_Artifacts/

# Follow links to actual files
cat Paper_Artifacts/table3_final.md
```

---

**Repository:** https://github.com/hailaykidu/MoVoC  
**Branch:** v2/table3_extrinsic_mt  
**Last Updated:** 2026-09-09
