# Publication freeze checklist

Reconstruction Version 2 — reference repository for the V2 paper.

## Status: ready for paper writing

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Repository validated | **PASS** | [`../../docs/repository_validation_report.md`](../../docs/repository_validation_report.md) |
| 2 | Tables validated | **PASS** — 0 inconsistencies | [`../../docs/table_consistency_report.md`](../../docs/table_consistency_report.md) |
| 3 | Datasets documented | **PASS** — 5/5 files, counts verified | [`../../docs/dataset_release_report.md`](../../docs/dataset_release_report.md) |
| 4 | Links verified | **PASS** — 0 broken | repository validation report |
| 5 | Audits archived | **PASS** — 9 audits + incident evidence | [`../audits/`](../audits/) |
| 6 | Contribution alignment | **PASS** | [`../../docs/contribution_alignment_report.md`](../../docs/contribution_alignment_report.md) |
| 7 | LICENSE | **PASS** — MIT, matches `CITATION.cff` | `LICENSE` |
| 8 | Paper-writing ready | **YES** | this checklist |

## What is frozen

- **Structure** — `original/` (archival baseline) and `v2/` (primary content).
  No further restructuring or migration.
- **Results** — Tables 2, 3 and 4 as recorded. No experiment rerun, no value
  modified.
- **Audit outcomes** — preserved verbatim, including the two conflicting Tigre
  runs.
- **Methodology** — official metric implementations, unmodified.

## Main tables (frozen)

**Table 2 — MorphScore**

| Language | Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 41.3 |
| Tigrinya (tir) | 5,224 | 41.5 |
| Ge'ez (gez) | 172 | 88.7 |
| Tigre (tig) | 2,149 | 42.9 |

**Table 3 — MarianMT** (FLORES-200 devtest, mean ± std, seeds 42/43/44) — 6
cells, BPE leading both directions.

**Table 4 — boundary precision + Rényi entropy** — 8 cells, official exact-match
precision and normalized Rényi. MoVoC-Tok leads on precision in Tigre and on
entropy in three of four languages.

## Open items for the paper — not blockers

1. **Tigre winner unresolved.** Two runs disagree (three-arm: MoVoC-Tok 56.3 vs
   BPE 53.8; held-out: BPE 60.4 vs MoVoC-Tok 46.3). Both preserved. **A dedicated
   Tigre consistency audit is the prerequisite** before citing a single Tigre
   result.
2. **Amharic and Tigrinya merge tables are not in the repository.** Only `geez`
   and `tigre` are tracked; the other two are regenerated with `train.py`.
   Publishing them would improve reproducibility.
3. **Evaluation-set ceilings.** Tigrinya reaches 5,224 scorable items against a
   stated 80,000; Ge'ez 172 against 20,000. Recorded in
   [`limitations.md`](limitations.md).

## Reference paths

| Content | Path |
|---|---|
| Datasets | `data/annotations/`, `data/README.md` |
| Tokenizer | `movoc/tokenizer.py`, `models/` |
| Metrics | `movoc/metrics.py` |
| Tables | `v2/table{2,3,4}/*_final.{csv,tex}` |
| Per-table reports | `v2/table{2,3,4}/*_report.md` |
| Audits | `v2/audits/` |
| Published values | `original/published_results/` |
