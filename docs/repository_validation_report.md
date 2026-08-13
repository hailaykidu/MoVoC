# Repository validation report

Consistency check of links, paths and references. **No experiment was rerun and
no result modified.**

## Summary

| Check | Result |
|---|---|
| Markdown links | **0 broken** (all relative paths resolve) |
| Entry-point scripts | 6/6 present |
| Dataset references | 5/5 annotation files valid and documented |
| Tokenizer references | Corrected — see below |
| Citations | `CITATION.cff` present, consistent with `LICENSE` (MIT) |

## Links

All markdown link references across every markdown file resolve to an existing
file. Four stale references were repaired, all caused by renames during the
restructure:

| File | Was | Now |
|---|---|---|
| `v2/table4/Intrinsic_report.md` | `boundary_projection_audit.md` | `projection_audit.md` |
| `v2/table2/REPRODUCTION_STATUS.md` | `table2_reproduction.csv` | `table2_final.csv` |
| `v2/table2/final_report.md` | `table2_reproduction.tex` | `table2_final.tex` |
| `v2/audits/tokenizer_audit.md` | `table4_reproduction.csv` | `table4_final.csv` |

`docs/overview.md` was updated: its reading order pointed at three
`docs/table*_summary.md` files that now live as per-table reports under `v2/`.

## Scripts

| Script | Status |
|---|---|
| `train.py`, `segment.py`, `evaluate.py` | present |
| `scripts/build_eval_sets.py`, `scripts/submit_marianmt.sh`, `scripts/make_tables.py` | present |

Every command in the README's "Running the experiments" block references an
existing file.

## Tokenizer references — one correction

The README stated that released merge tables live in
`models/movoc_tok_merges_{lang}.txt`. **Only `geez` and `tigre` are tracked**;
Amharic and Tigrinya merge tables are not in the repository, and `models/` is
gitignored except for those two files.

The README now states this accurately: Amharic and Tigrinya tokenizers are
regenerated locally with `train.py`. **No files were moved and no ignore rule
changed** — only the claim was corrected to match reality.

## Unresolved backticked references — expected, not breakage

76 backticked filenames do not resolve. These were reviewed individually and
fall into three legitimate categories:

1. **External working directories** cited as provenance in audits
   (`movoc_table*_repro/`, `MoVoC_Tok/`, `HornMT/`, `lgse-repro/`). These record
   *where a measurement came from* and are outside this repository by design.
2. **Historical filenames** in `historical_investigation.md` and
   `mt_reconstruction_audit.md`, naming files as they existed at the time of the
   investigation. Rewriting them would falsify the audit record.
3. **Sibling-file references inside audit reports** (e.g.
   `precision_variants_linguistic.csv`), naming outputs that live in the external
   analysis directories the audits describe.

None affects navigation of the repository.
