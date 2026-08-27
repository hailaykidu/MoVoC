# Overleaf integration

Mapping between this repository and the V2 manuscript
([`../paper/manuscript/main.tex`](manuscript/main.tex)).

## Division of authority

| Source of truth | Owns |
|---|---|
| **This repository** | datasets, tokenizers, experiments, tables, reports |
| **Overleaf project** | manuscript text, LaTeX, figures, bibliography |

Numbers flow **repository → Overleaf**, never the reverse.

## Authoritative sources

Every value in the manuscript comes from one of these files. The repository is
authoritative: on any discrepancy, the repository value wins and the manuscript
is corrected to match.

| Manuscript content | Authoritative source |
|---|---|
| Table 2 — datasets + MorphScore | `v2/table2/table2_final.{csv,tex}` |
| Table 3 — MarianMT BLEU / chrF++ | `v2/table3/table3_final.{csv,tex}` |
| Table 4 — precision + Rényi entropy | `v2/table4/table4_final.{csv,tex}` |
| Dataset counts | `data/README.md` — **and nowhere else** |
| Method description | `v2/reports/methodology.md` (finalized V2 version) |
| Overall summary | `v2/reports/reconstruction_v2_summary.md` |

```
repository value  ──►  Overleaf value
```

The `.tex` fragment is what gets copied; the `.csv` is the machine-readable
counterpart carrying the same values, for checking.

**No manual editing of values inside Overleaf.** A value that appears wrong in
the manuscript is corrected in the repository and the fragment re-copied. Editing
a number in Overleaf silently breaks agreement with the CSV, the per-table
report and the README, all of which are consistency-checked here.

## Supporting documentation

| Manuscript section | Repository source |
|---|---|
| Intrinsic evaluation prose | `v2/table4/Intrinsic_report.md`, `v2/table2/MorphScore_report.md` |
| Extrinsic evaluation prose | `v2/table3/MarianMT_report.md` |
| Limitations | `v2/reports/limitations.md` |
| Section notes and caption drafts | `v2/paper/*_notes.md` |

## What must not enter the manuscript

The repository retains records beyond the final result set. These are **not**
manuscript sources:

| Excluded | Where it lives | Why |
|---|---|---|
| Audit-only metrics | `v2/audits/` | sensitivity variants, not official metrics |
| Best-run and alternative evaluations | `v2/appendix/` | supporting material only |
| Intermediate and superseded runs | `v2/audits/`, `v2/table*/` non-final files | superseded by the final tables |
| Diagnostic values | e.g. training-loss ranges in `reconstruction_v2_summary.md` | run diagnostics, not results |

`reconstruction_v2_summary.md` is authoritative for the **narrative summary**;
its Table 2/3/4 numbers are the frozen ones. Diagnostic figures it cites
(training-loss ranges, BLEU noise floors from superseded runs) are not manuscript
values.

Results in the manuscript come only from `table{2,3,4}_final.*`.

## LaTeX requirements

The fragments are bare `tabular` environments — no `\begin{table}` wrapper, no
caption, no label. Wrap them in the manuscript:

```latex
\begin{table}[t]
  \centering
  \input{tables/table4_final}
  \caption{Morpheme boundary precision and normalized Rényi entropy (alpha = 2)
           for 32k vocabularies.}
  \label{tab:intrinsic}
\end{table}
```

Preamble packages required by the current fragments:

| Fragment | Needs |
|---|---|
| `table2_final.tex` | `\usepackage{booktabs}` (`\toprule`, `\midrule`, `\bottomrule`) |
| `table3_final.tex` | `\usepackage{booktabs}` |
| `table4_final.tex` | none — plain `\hline` |

Caption drafts for all three tables are in `v2/paper/table{2,3,4}_notes.md`.

## Sync procedure

1. Confirm the repository is clean and the tables validated
   (`docs/table_consistency_report.md`).
2. Copy the three `.tex` fragments into the Overleaf project's `tables/`
   directory, replacing the previous versions **wholesale** — do not merge by
   hand, and do not keep an older row.
3. Recompile; check no `booktabs` command is undefined.
4. Check the dataset section against `data/README.md` and the method section
   against `v2/reports/methodology.md`.
5. Record the repository commit used, so the manuscript is traceable to an exact
   repository state.

### Verifying a synced manuscript

Every numeric in the manuscript's results tables must appear in the frozen CSVs.
Run `scripts/check_manuscript_values.py` against a copy of the manuscript source:

```bash
python3 scripts/check_manuscript_values.py path/to/main.tex
```

It collects every value from `table{2,3,4}_final.csv` (tolerating padded
decimals such as `0.014` vs `0.0140`) and reports any number in the manuscript
that the repository does not produce.

A non-empty result means the manuscript carries a value the repository does not
produce. **Correct the manuscript, not the repository.**

## Verification before submission

| Check | Where |
|---|---|
| Tables match CSV / report / README | `docs/table_consistency_report.md` |
| Dataset counts match the files | `docs/dataset_release_report.md` |
| Links and paths resolve | `docs/repository_validation_report.md` |
| Freeze status | `v2/reports/publication_freeze_checklist.md` |

## Citation

`CITATION.cff` at the repository root holds the canonical entry. Repository
license: MIT (`LICENSE`).
