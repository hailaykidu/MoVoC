# Repository restructure — migration report

Reorganisation of the MoVoC repository around **Original** and **Reconstruction
Version 2**, with V2 as the primary research artifact.

**No numerical result was changed. No released artifact was modified. No audit
conclusion was rewritten.** This was a structural migration only.

## Status

Staged in the working tree, **not committed and not pushed**. Review the diff
before committing.

Local `main` was 4 commits behind the remote at the start and was fast-forwarded
to `ef9062d` first, so the restructure sits on top of current upstream.

## New tree

```
MoVoC/
├── README.md · CITATION.cff
├── original/          ARCHIVAL — never modified
│   ├── published_results/README.md   the paper's Tables 2/3/4, verbatim
│   ├── paper/ · released_artifacts/ · references/
├── v2/                PRIMARY CONTENT
│   ├── table2/  table2_final.{csv,tex} · MorphScore_report.md · status
│   ├── table3/  table3_final.{csv,tex} · MarianMT_report.md · provenance
│   ├── table4/  table4_final.{csv,tex} · Intrinsic_report.md · status
│   ├── tokenizers/ · marianmt/
│   ├── audits/  entropy · projection · precision · dataset · tokenizer
│   │            + incidents/ (failed-run evidence)
│   ├── appendix/ best runs · sensitivity · alternative evaluations
│   └── reports/ summary · methodology · limitations · discussion
├── docs/  overview.md · methodology.md · limitations.md · REPRODUCIBILITY.md
│          · repository_restructure_report.md
├── movoc/ · evaluation/ · scripts/ · configs/ · data/ · models/ · assets/
```

## Category separation

The four categories the repository must never conflate:

| # | Category | Location | Rule |
|---|---|---|---|
| 1 | Original project | `original/` | Archival; not modified |
| 2 | Published results | `original/published_results/` | Never overwritten |
| 3 | Reproduction | `v2/table{2,3,4}/*_final.*` | Authoritative; never replaced by sensitivity values |
| 4 | Reconstruction v2 findings | `v2/audits/`, `v2/appendix/` | Explain discrepancies; never replace 2 or 3 |

Every per-table report carries **Published**, **V2 Reconstruction** and
**Comparison** as separate sections.

## File migrations

All moves used `git mv` where the source was tracked, preserving history.

| From | To |
|---|---|
| `results/reconstruction_v2/intrinsic/paper_tables*.json` | `v2/table2/paper_tables_released_pipeline*.json` |
| `results/reconstruction_v2/intrinsic/amseg_tokenizer_quality_*` | `v2/table4/` |
| `results/reconstruction_v2/extrinsic/*`, `mt/*` | `v2/table3/` |
| `results/original_paper/README.md` | `original/paper/README.md` |
| `docs/TABLE2_ITEM_COUNT_DISCREPANCY.md` | `v2/audits/dataset_audit.md` |
| `docs/MT_Reconstruction_Audit.md` | `v2/audits/mt_reconstruction_audit.md` |
| `docs/HISTORICAL_INVESTIGATION.md` | `v2/audits/historical_investigation.md` |
| `docs/RECONSTRUCTED_EVALUATION.md` | `v2/reports/reconstructed_evaluation.md` |
| `docs/reconstruction_vs_original.md` | `v2/reports/reconstruction_v2_summary.md` |
| `docs/incidents/` | `v2/audits/incidents/` |

## Imported from external working directories

Table 2 and Table 4 reproduction artifacts were produced outside the repository
and are now vendored in, making the repo self-contained:

| Source | Destination |
|---|---|
| `movoc_table2_repro/results/` | `v2/table2/`, `v2/audits/tigrinya_*` |
| `movoc_table4_repro/results_intrinsic_official/` | `v2/table4/` |
| `movoc_table4_repro/results_precision_audit/` | `v2/audits/precision_audit.md` |
| `movoc_table4_repro/results_precision_linguistic/` | `v2/audits/precision_linguistic_sensitivity.md` |

## Files created

- `README.md` — rewritten: Motivation, Original MoVoC, Reconstruction V2,
  Reconstructed Results, Major Findings, Repository Structure
- `CITATION.cff`
- `original/published_results/README.md` — published Tables 2/3/4 verbatim
- `v2/README.md`, `v2/appendix/README.md`
- `v2/table{2,3,4}/{MorphScore,MarianMT,Intrinsic}_report.md`
- `v2/table3/table3_final.{csv,tex}` — generated from `table3_multiseed.json`
- `v2/audits/{entropy,projection,tokenizer}_audit.md` — extracted **verbatim**
  from `v2/table4/REPRODUCTION_STATUS.md` so each audit is separately citable;
  conclusions unchanged
- `v2/reports/discussion.md`, `docs/overview.md`

## Removed

- `results/` — superseded by `v2/` and `original/published_results/`. An earlier
  intermediate layout (`reconstruction_v2/`, `reproduction/`, `results/table*_final/`)
  was created and then folded into `v2/` when the v2-primary policy arrived; no
  content was lost.

## Verification

- **Broken internal links: 0** (23 introduced by the moves, all repaired).
- All published values cross-checked against
  `original/published_results/README.md`; all reproduction values against
  `v2/table*/[*_final.csv]`.
- `git status` shows renames as `R`, so history is preserved.

## Outstanding items — not resolved by this restructure

1. **No `LICENSE` file exists.** `CITATION.cff` declares MIT, but the repository
   ships no license text. Choosing a license is the author's decision, so none
   was invented. **This should be added before publication.**
2. **The Tigre contradiction is unresolved.** Two intrinsic runs disagree on the
   winner — the three-arm run has MoVoC-Tok ahead (56.3 vs 53.8 precision), the
   held-out run has BPE ahead (60.4 vs 46.3). Recorded in
   `docs/limitations.md` §5 and `v2/table4/Intrinsic_report.md`. **Must be
   settled before Tigre is cited as a MoVoC-Tok win.**
3. `original/released_artifacts/` and `original/references/` are created but
   empty — released code and data still sit at their historical top-level paths
   (`movoc/`, `data/`, `evaluation/`, `scripts/`) so import paths and the
   documented commands keep working. Moving them would break `train.py`,
   `evaluate.py` and every documented invocation.
