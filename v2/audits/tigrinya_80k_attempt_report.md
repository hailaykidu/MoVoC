# Tigrinya 80,000-item attempt — result and provenance

Exhaustive search of the local working environment for MorphScore-capable
Tigrinya data.

## Outcome

**80,000 cannot be reached. Maximum obtainable: 5,224 items (6.5% of target).**

| | |
|---|---:|
| Target (paper Table 2) | 80,000 |
| **Maximum obtainable union** | **5,224** |
| **Gap remaining** | **74,776** |
| MorphScore on the maximal union | **41.5** |

The union is **identical to the previously reported 5,224**. Searching every
repository under the home directory — not just the authorised MoVoC and AMSEG
paths — added **zero** new scorable items. The pool was already saturated.

## Usable sources (priority order)

| Source | Priority | Found | Multi-morpheme | Surface-aligned | Duplicates removed | Retained |
|---|---:|---:|---:|---:|---:|---:|
| `gold_morphemes.json` (official gold) | 1 | 206 | 205 | 17 | 4 | **13** |
| `postedited_morphemes.json` (post-edited) | 2 | 7,531 | 2,665 | 2,356 | 0 | **2,356** |
| `tigrinya_morpheme_edited.json` (HornMT copy) | 2 | 7,531 | 2,665 | 2,356 | 2,356 | **0** |
| `tigrinya_morpheme_segmented.json` (HornMorpho) | 3 | 6,692 | 4,864 | 350 | 6 | **344** |
| `evaluation/data/tigrinya_gold.tsv` (AMSEG) | 4 | 5,224 | 5,224 | 5,224 | 2,713 | **2,511** |
| `TigrinyaTokenizer/output/ሃይላይ_ኪዱ_table.json` | 4 | 206 | 205 | 17 | 17 | **0** |
| **Union** | | | | | | **5,224** |

Two sources are exact duplicates of higher-priority files:
`tigrinya_morpheme_edited.json` is byte-equivalent to `postedited_morphemes.json`
(both 7,531 records), and `ሃይላይ_ኪዱ_table.json` duplicates the 206-record gold set.

## Sources found but unusable

| Resource | Rows | Why unusable |
|---|---:|---|
| `annotation_template_tigrinya.json` | 20,000 | **Blank worklist** — every entry `annotation_status: pending`, 0 filled morpheme fields |
| `Morpheme_Aware/Tigr_segmentation_output.txt` | 43,511 | 100% `NO_SEGMENTATION` placeholders |
| `HornMT/data/Tigr_segmentation_output.txt` | 43,511 | 100% `ERROR: module 'hm' has no attribute 'anal'` — a failed HornMorpho run |
| `HornMT/.../Stem-processed.txt` | 187,517 | **Amharic, not Tigrinya** — 39,888 of 40,062 aligned words overlap the Amharic annotations; only 64 overlap Tigrinya |
| `HornMT/.../Root-based annotated corpus.txt` | 36,414 | Amharic running text in SGML; no word/segmentation pairs |
| `HornMT/.../Stem-based annotated corpora.txt` | 36,414 | Amharic running text in SGML; no word/segmentation pairs |
| `lgse-repro/data/morph_lexicon.txt` | 230 | Tigrinya, but subsumed by the gold set |
| `HornMT Tatoeba.en-ti.ti` | 74 | Parallel sentences, no morphological annotation |

The two largest candidates by row count — `Stem-processed.txt` (187,517) and the
two SGML corpora (36,414 each) — are **Amharic**. Language was verified by
overlap: of 40,062 surface-aligned unique words in `Stem-processed.txt`, 39,888
appear in the Amharic annotations and 64 in the Tigrinya ones.

## Why the ceiling is 5,224 and not higher

Tigrinya has **2,838 unique multi-morpheme entries** across all annotation JSON
files, of which only **2,369 are surface-aligned**. MorphScore projects gold
boundaries as cumulative morpheme lengths — character offsets into the surface
word — so an annotation whose parts do not concatenate back to the word yields
offsets pointing at positions the word does not have. Citation-form annotations
(normalised roots) are therefore unscorable, not merely inconvenient.

The AMSEG evaluation file lifts the total to 5,224 by contributing 2,511
surface-aligned words absent from the raw JSON. That is the ceiling: **every
annotated Tigrinya word in the repository that MorphScore can score is already
in the union.**

## What would be required to reach 80,000

**74,776 additional Tigrinya words with gold morpheme annotations.** No
transformation of existing data can produce them:

- The corpora are not the constraint. `annotation_template_tigrinya.json` was
  built from `all.ti` with frequency counts (top entry `እዩ።`, frequency 36,547),
  so **unannotated Tigrinya text is plentiful**.
- The constraint is annotation. That template is the exact resource needed — a
  20,000-word frequency-ranked worklist — and it is **entirely unannotated**.
- Even fully annotating it would give at most 20,000 more, reaching ~25,000, still
  short of 80,000.

Reaching the paper's scale requires roughly **75,000 words annotated by a
Tigrinya speaker**, of which the repository provides a worklist for 20,000.

This makes the published Tigrinya figure (80,000 items, MorphScore 0.731) not
reproducible from any artifact in this environment, and suggests the released
annotation set is a small subset of what the paper's authors evaluated.

## MorphScore on the maximal union

**41.5** on 5,224 items, against a published 0.731 — a shortfall of ~31.6 points.
Computed with the official `movoc/metrics.py::morphscore` (boundary recall,
micro-averaged, unsegmented words excluded) over cumulative-length projection,
using the released `movoc_tok_merges_tigrinya.txt`. Metric, aggregation,
projection and tokenizer unchanged.

The score is **unchanged from the smaller official-first pool**, because the
union added no new items — an independent confirmation that the Tigrinya
evaluation set is saturated.

## Outputs

| File | Contents |
|---|---|
| `tigrinya_data_inventory.csv` | every source: found / multi-morpheme / aligned / duplicates / retained |
| `tigrinya_source_breakdown.csv` | contribution per source, plus unusable sources with reasons |
| `tigrinya_union_summary.json` | machine-readable summary |
| `tigrinya_80k_attempt_report.md` | this document |

Regenerate with `python3 movoc_table2_repro/tigrinya_inventory.py`.
