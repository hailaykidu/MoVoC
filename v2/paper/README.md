# Paper materials — MoVoC Reconstruction Version 2

**Title:** MoVoC: Morphology-Aware Subword Construction for Ge'ez Script
Languages — Reconstruction Version 2

**Overleaf project:**
<https://tex.cloud.uni-hannover.de/project/6a6c6667662fbc94aa2c5196>

## Purpose

The V2 paper presents MoVoC and MoVoC-Tok together with morpheme-annotated
datasets for four Ge'ez-script languages, evaluated intrinsically (morpheme
boundary precision, MorphScore, Rényi entropy) and extrinsically (English→X
MarianMT translation).

This directory holds the writing materials derived from the frozen repository
state. The manuscript itself lives in Overleaf.

## Contents

| File | Purpose |
|---|---|
| `paper_outline.md` | section structure and table mapping |
| `abstract_draft.md` | abstract elements and draft |
| `introduction_notes.md` | motivation, contributions |
| `related_work_notes.md` | tokenization, morphology, metrics |
| `methodology_notes.md` | MoVoC, MoVoC-Tok, datasets, both evaluations |
| `table2_notes.md` · `table3_notes.md` · `table4_notes.md` | publication-ready tables + caption drafts |
| `discussion_notes.md` | findings framed around the contributions |
| `limitations_notes.md` | scope limits from the final result set |
| `conclusion_notes.md` | summary and future work |
| `overleaf_integration.md` | repository ↔ Overleaf mapping and sync procedure |

## Updating tables

Tables are **generated in the repository, never edited in Overleaf.**

| Table | Source fragment |
|---|---|
| Table 2 | `v2/table2/table2_final.tex` |
| Table 3 | `v2/table3/table3_final.tex` |
| Table 4 | `v2/table4/table4_final.tex` |

To update:

1. Change the underlying result in the repository (requires rerunning the
   relevant evaluation — the repository is currently frozen).
2. Regenerate the `.tex` fragment alongside its `.csv`.
3. Re-run the consistency check so CSV, TeX, per-table report and README agree.
4. Copy the fragment into Overleaf.

**Never edit a number directly in the manuscript.** Doing so breaks agreement
with the CSV and the reports, which are validated together.

## Synchronizing with Overleaf

Full procedure and LaTeX requirements: [`overleaf_integration.md`](overleaf_integration.md).

Short form — copy the three `.tex` fragments into the Overleaf `tables/`
directory, recompile, and record the repository commit the manuscript was built
from.

## Source of truth

| Content | Owner |
|---|---|
| Datasets, tokenizers, experiments, tables, reports | this repository |
| Manuscript text, LaTeX, figures, bibliography | Overleaf project |

## Status

The repository is frozen for paper writing — see
[`../reports/publication_freeze_checklist.md`](../reports/publication_freeze_checklist.md).
All values in these notes trace to `v2/table{2,3,4}/*_final.csv`.
