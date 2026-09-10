# V2 Archive

This directory contains previous versions and archived materials from the V2 reconstruction.

## `table3_intrinsic_v1_original/`

**Original Table 3 - Intrinsic Evaluation (Sep 10, 2026)**

- Contains original Table 3 files from the main branch
- Intrinsic evaluation metrics (morpheme boundary precision, MorphScore, Rényi entropy)
- Based on annotated morpheme sets
- Original files:
  - `MarianMT_report.md` - Original report
  - `PROVENANCE.md` - Original provenance documentation
  - `table3_multiseed.json`, `table3_final.csv`, `table3_final.tex` - Original data

**Why archived:**
- Replaced with extrinsic evaluation results (machine translation experiments)
- New Table 3 focuses on downstream tasks with MarianMT fine-tuning
- Original intrinsic evaluation results remain in git history and tags

**How to access original:**
```bash
git log --all --oneline | grep -i "table3\|intrinsic"
git show v2-paper-baseline:v2/table3/
```

---

## Version History

| Date | Component | Status | Notes |
|------|-----------|--------|-------|
| 2026-09-10 | Table 3 Extrinsic | Active | New extrinsic evaluation (EN→Amharic, EN→Tigrinya, zero-shot) |
| 2026-09-10 | Table 3 Intrinsic | Archived | Original intrinsic evaluation (boundary precision, MorphScore) |

