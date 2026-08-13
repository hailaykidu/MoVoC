# Contribution material review

Pre-cleanup classification of appendix, audit, report and documentation
material. **Review only — no file was deleted, moved or modified, and neither
the README nor the manuscript was touched.**

41 files reviewed across `v2/appendix/`, `v2/audits/`, `v2/reports/` and `docs/`.

## Method

Inbound references were resolved mechanically: every markdown and LaTeX file in
the repository was parsed for links and backticked paths, and each target
matched against the file list. "Required for reproducibility" means the file
documents a decision, parameter or data source needed to regenerate a table —
not merely that it discusses one.

## Finding that shapes the whole review

**The manuscript references none of these files.** `v2/paper/manuscript/main.tex`
is self-contained and cites only published works, as a paper should. So
"referenced in paper" is `no` for all 41 entries and cannot discriminate between
them. Classification therefore rests on reproducibility and transparency value.

## Classification

**A** Core paper content · **B** Reproducibility requirement ·
**C** Supporting transparency · **D** Exploratory / historical

### `docs/`

| File | Class | In paper | In README | Repro. required | Recommendation |
|---|---|---|---|---|---|
| `methodology.md` | A | no | no | **yes** (all tables) | keep |
| `limitations.md` | A | no | no | no | keep |
| `overview.md` | C | no | no | no | keep |
| `REPRODUCIBILITY.md` | B | no | no | **yes** (artifact inventory) | keep |
| `dataset_release_report.md` | B | no | no | **yes** (Table 2 counts) | keep |
| `table_consistency_report.md` | B | no | no | **yes** (verifies all tables) | keep |
| `repository_validation_report.md` | C | no | no | no | keep |
| `contribution_alignment_report.md` | C | no | no | no | optional |
| `geez_data_consistency_review.md` | C | no | no | no | keep |
| `repository_restructure_report.md` | D | no | no | no | archive |

### `v2/reports/`

| File | Class | In paper | In README | Repro. required | Recommendation |
|---|---|---|---|---|---|
| `reconstruction_v2_summary.md` | A | no | **yes** | no | keep |
| `limitations.md` | A | no | **yes** | no | keep (duplicate — see below) |
| `methodology.md` | A | no | no | **yes** | keep (duplicate — see below) |
| `discussion.md` | C | no | no | no | keep |
| `publication_freeze_checklist.md` | C | no | no | no | keep |
| `reconstructed_evaluation.md` | D | no | no | no | optional |

### `v2/audits/`

| File | Class | In paper | In README | Repro. required | Recommendation |
|---|---|---|---|---|---|
| `dataset_audit.md` | B | no | no | **yes** (Table 2 item counts) | keep |
| `entropy_audit.md` | B | no | no | **yes** (Table 4 entropy normalisation) | keep (duplicate) |
| `projection_audit.md` | B | no | no | **yes** (Table 4 boundary projection) | keep (duplicate) |
| `tokenizer_audit.md` | B | no | no | **yes** (Tigre/Ge'ez cross-lingual assumption) | keep (duplicate) |
| `precision_audit.md` | C | no | no | no | keep |
| `tigrinya_80k_attempt_report.md` | C | no | no | no | keep |
| `tigrinya_data_inventory.csv` | C | no | no | no | keep |
| `tigrinya_source_breakdown.csv` | C | no | no | no | keep |
| `mt_reconstruction_audit.md` | D | no | no | no | archive |
| `historical_investigation.md` | D | no | no | no | archive |
| `precision_linguistic_sensitivity.md` | D | no | no | no | **see special check** |

### `v2/audits/incidents/2026-07-28-invalid-mt-evaluation/` (13 files)

| File | Class | In paper | In README | Repro. required | Recommendation |
|---|---|---|---|---|---|
| `README.md` | C | no | no | no | keep |
| `run_table3.sh` | C | no | no | no | keep |
| 4 × `*.json` (invalid-run outputs) | D | no | no | no | archive |
| 7 × `logs/*.log` | D | no | no | no | archive |

Evidence for a documented failed MT run. The `.gitignore` tracks these
deliberately, with a comment stating they are **not results**. They support
transparency about a discarded run; none is needed to regenerate a table.

### `v2/appendix/`

| File | Class | In paper | In README | Repro. required | Recommendation |
|---|---|---|---|---|---|
| `README.md` | C | no | no | no | keep — **see special check** |

## Duplicate content — five files are verbatim copies

Line-by-line comparison found complete duplication:

| File | Duplicates | Overlap |
|---|---|---|
| `v2/audits/entropy_audit.md` | `v2/table4/REPRODUCTION_STATUS.md` | 18/18 lines |
| `v2/audits/projection_audit.md` | `v2/table4/REPRODUCTION_STATUS.md` | 24/24 lines |
| `v2/audits/tokenizer_audit.md` | `v2/table4/REPRODUCTION_STATUS.md` | 14/14 lines |
| `v2/reports/methodology.md` | `docs/methodology.md` | 98/98 lines |
| `v2/reports/limitations.md` | `docs/limitations.md` | 44/44 lines |

These were created deliberately, so each audit is separately citable, and each
carries a header saying so. **The risk is divergence:** an edit to one copy that
misses the other produces two documents disagreeing on an audit conclusion. The
Ge'ez consistency review had to update `limitations.md` in both locations for
exactly this reason.

Recommendation: keep, but treat the `v2/table4/REPRODUCTION_STATUS.md` and
`docs/` versions as canonical, and consider replacing the copies with links if
the duplication ever causes a discrepancy.

## Special check — material outside the final V2 result set

Not for removal, only listed as instructed.

### 1. `v2/audits/precision_linguistic_sensitivity.md`

- Not referenced by the paper; not required for reproducibility.
- Presents precision under ±1 tolerance and fusion-aware matching — **metrics
  outside the final V2 result set**.
- Contains the only place in the repository where Ge'ez MoVoC-Tok leads BPE
  (64.34 vs 62.94 under ±1), which **inverts the Table 4 ranking**.

Its own conclusion is that no linguistically motivated variant reverses the
official ranking, so it argues *against* the alternative narrative rather than
for it. It is the documented basis for excluding ±1 from Table 4. **Transparency
value is high precisely because it records a negative result.**

Recommendation: **keep**, remain in `v2/audits/`, never cited as a result.

### 2. `v2/appendix/README.md`

- Aggregates best-run and sensitivity material, including the ±1 Ge'ez figure.
- States its own subordinate status and that ±1 never enters Table 4.

Recommendation: **keep** — it is the guard rail that keeps this material
labelled, not the thing that needs guarding.

### 3. `v2/audits/precision_audit.md`

- Cites published values (85.5, 88.3) for comparison and audit-only variants.
- Required to explain why Table 4 uses exact-match precision.

Recommendation: **keep** as transparency material.

### 4. `v2/audits/historical_investigation.md`, `mt_reconstruction_audit.md`

- Narrate repository history and a superseded MT reconstruction.
- Reference external paths outside this repository and pre-restructure filenames.
- Not required for any table.

Recommendation: **archive** — historical value only; the least navigable
material in the repository.

## Summary

| Class | Files | Recommendation |
|---|---:|---|
| A — core paper content | 5 | keep |
| B — reproducibility requirement | 7 | keep |
| C — supporting transparency | 12 | keep (1 optional) |
| D — exploratory / historical | 17 | archive (13 are incident evidence) |

**No file is recommended for deletion.** The only material recommended for
archival is repository-history narrative and failed-run evidence, none of which
is needed to regenerate Table 2, 3 or 4.

**Nothing in the repository emphasises results outside the final V2 set as
findings.** The one file presenting alternative metrics concludes that they do
not change the official ranking, and the appendix that collects them states
their subordinate status explicitly.

## Next step

This review is advisory. No cleanup or archival action should follow until its
recommendations are approved.
