# Table 2 reproduction — MorphScore (superseded)

> **Status: superseded.** This official-first-plus-fallback methodology and
> its results (Amharic 41.3 over an 80,000-item pooled set, etc.) were the
> accepted Table 2 reproduction until the AMSEG intrinsic tokenizer
> evaluation (`amseg/evaluation/results/`) replaced it as authoritative — see
> [`MorphScore_report.md`](MorphScore_report.md) and
> [`table2_final.csv`](table2_final.csv) for the current result, which uses
> AMSEG's own evaluation set directly rather than a pooled
> official-plus-fallback set. This file's investigation into surface
> alignment remains accurate background; the specific numbers below (and in
> `table2_final.csv`/`.tex` as they stood at the time) are no longer current.
>
> **The 80,000/20,000/32,000 "published item counts" this document treats as
> the target were themselves mislabeled in the paper.** They are an
> estimated combined total across every dataset used anywhere in the project
> for that language -- MoVoC vocabulary-construction data (BPE-training and
> morphological-analysis) plus the Machine Translation training and
> evaluation datasets, pooled together -- not the intrinsic MorphScore
> evaluation set size. Chasing those counts as an evaluation-scale target --
> which is what "official-first + fallback" and "union (maximal)" below were
> built to do -- was solving the wrong problem. See
> [`../../docs/limitations.md`](../../docs/limitations.md) §2.

Official MoVoC evaluation data first; a local AMSEG evaluation directory
used **only** to fill deficits. MorphScore computed with the official
implementation, unmodified.

## Result

| Language (ISO 639-3) | No. Items | MorphScore ↑ | Paper Items | Paper MorphScore | Pool |
|---|---:|---:|---:|---:|---|
| Amharic (amh) | **80,000** | 41.3 | 80,000 | 0.710 | official-first + fallback |
| Tigrinya (tir) | 5,224 | 41.5 | 80,000 | 0.731 | union (maximal) |
| Ge'ez (gez) | 172 | 88.7 | 20,000 | 0.670 | official-first + fallback |
| Tigre (tig) | 2,149 | 42.9 | 32,000 | 0.654 | union (maximal) |

Amharic reaches the published count. The other three cannot: no authorised source
contains enough evaluable items.

**Tigrinya and Tigre use the maximal union** of official MoVoC data and AMSEG
evaluation data, deduplicated — every scorable item in either source, with no cap.

## Source accounting

| Language | official_items_used | amseg_items_used | duplicates_removed | final_items_evaluated | % official |
|---|---:|---:|---:|---:|---:|
| Amharic | 20,030 | 59,970 | 2,042 | 80,000 | 25.0% |
| Tigrinya | 2,713 | 2,511 | 2,723 | 5,224 | 51.9% |
| Ge'ez | 44 | 128 | 0 | 172 | 25.6% |
| Tigre | **2,149** | 0 | 2,457 | 2,149 | 100.0% |

For Amharic and Ge'ez the AMSEG directory was used only to fill the deficit after
official data was exhausted. For Tigrinya and Tigre the two sources were unioned.

### Effect of the union (Tigrinya, Tigre)

| Language | Before (official-first) | After (union) | Δ items | MorphScore before → after |
|---|---:|---:|---:|---|
| Tigrinya | 5,224 | 5,224 | 0 | 41.5 → 41.5 |
| Tigre | 1,974 | **2,149** | **+175** | 44.6 → **42.9** |

**Tigre gained 175 items** from `tigre_morpheme_segmented.json` — surface-aligned,
multi-morpheme words that the AMSEG evaluation file had filtered out upstream.
Adding them lowered MorphScore by 1.7 points, so the AMSEG file's exclusions were
removing words the tokenizer handles comparatively poorly. Tigre remains 100%
official-sourced: the union simply reaches deeper into the official annotations
than the pre-built AMSEG file does.

**Tigrinya gained nothing.** The union confirms the AMSEG evaluation file already
contains every scorable Tigrinya word available in any source; the 2,511 items it
contributes are ones absent from the raw JSON annotations after alignment
filtering. The score is unchanged at 41.5.

## The binding constraint is surface alignment, not item count

MorphScore's gold boundaries are **character offsets into the surface word**
(cumulative morpheme lengths). An annotation whose morphemes do not concatenate
back to the word produces offsets that point at positions the word does not have,
so it cannot be scored meaningfully. The MoVoC annotations frequently store
**citation forms** — normalised roots — rather than surface allomorphs.

Official multi-morpheme entries, before and after the alignment requirement:

| Language | Unique multi-morpheme | Surface-aligned | Excluded as unaligned |
|---|---:|---:|---:|
| Amharic | 121,719 | **20,030** | 103,634 |
| Tigrinya | 2,838 | 2,369 | 496 |
| Ge'ez | 173 | 44 | 129 |
| Tigre | 1,974 | 1,974 | 0 |

Amharic loses 85% of its entries this way, and Ge'ez 75%. **Tigre loses none** —
its annotations are fully surface-concatenative, which is why it needs no
fallback and why it scored highest on boundary precision in the Table 4 work.

The AMSEG evaluation data is usable precisely because it is already
surface-aligned (verified independently: 1 malformed row in 81,224 for Amharic,
0 elsewhere).

### Correction to an earlier figure

An earlier count in this project reported Amharic at 37,048 evaluable items. That
came from the official `annotation.triple_of`, which reads only `prefix`, `root`
and `suffix` and **silently drops `Infix` and `Clitic`**. Amharic clitics are
often a word's only morpheme boundary, so those words collapsed to
single-morpheme and were dropped. Preserving all fields yields 121,719 before
alignment filtering, 20,030 after.

## MorphScore — official implementation, unmodified

`movoc/metrics.py::morphscore`, via the official `movoc.tokenizer`. The
repository copy is byte-identical to the official one (`diff` clean).

```
MorphScore = Σ |gold_b ∩ pred_b| / Σ |gold_b|     over words where pred_b ≠ ∅
```

Recall of gold boundaries — **not** precision or F1, and a different metric from
Table 4's `boundary_precision` in the same file. Micro-averaged corpus-level, so
words with more boundaries carry more weight; not a mean of per-word scores.
Unsegmented words are **excluded rather than scored zero** (`if not pred_b:
continue`), per the paper's definition. Cumulative-length projection.

Formula, aggregation, projection and tokenizers are unchanged. Only the
evaluation pool was expanded. Tokenizers: released `movoc_tok_merges_*.txt`.

## Deduplication

One canonical entry per surface word. Official sources are consumed in priority
order (for Tigrinya: `gold_morphemes.json` before `postedited_morphemes.json`),
first occurrence wins, and AMSEG candidates already present in the official pool
are skipped. Amharic was capped from its available pool to exactly 80,000 by
seeded shuffle (`random.Random(42)`) so as not to exceed the published count. No
word is duplicated; nothing was synthesised.

## Interpretation

**Amharic (41.3 vs 0.710) is a like-for-like comparison** — 80,000 items, official
metric, released tokenizer — and falls **29.7 points short**. Item count is now
eliminated as an explanation. The residual gap matches the Table 4 precision gap
documented in
`../archive/table4_reproduction_status_superseded.md` §4
and shares its likely cause: exact character-offset matching under a projection
the paper does not describe.

The Amharic row is **75% AMSEG-derived**, and part of that is HornMorpho-generated
segmentation rather than gold annotation. It is a valid measurement of the
tokenizer against those segmentations, but it is not a pure gold-annotation
result and should not be presented as one.

**Ge'ez (88.7) must not be read as beating 0.670.** It rests on 172 words — 0.9%
of the stated 20,000 — with only 44 from official data, and uses
`movoc_tok_merges_geez.txt`, a 9.3 KB artifact built on Jul 30, **after
publication**. Both facts inflate it.

**Tigrinya (41.5)** is 48.1% AMSEG-derived. **Tigre (42.9)** is the only fully
official row, at 6.7% of its stated count — and the only language whose
annotations are 100% surface-concatenative, so nothing is lost to alignment
filtering. It is the cleanest measurement in the set, and it too falls 22.6
points below its published 0.654.

**Table 2's published values are not reproducible from the released artifacts.**
The metric is fully pinned and was executed without modification, so the barrier
is the evaluation data: three of four languages lack enough surface-aligned gold
annotations to evaluate at the paper's stated scale, and the one language that
reaches scale does so only with 75% supplementation.

## Outputs

| File | Contents |
|---|---|
| `table2_final.csv` | final table with per-source counts |
| `table2_final.tex` | LaTeX table |
| `morphscore_scores.csv` | scores with full provenance and exclusion counts |
| `final_report.md` | this document |

The script that produced this superseded run (`score_official_first.py`)
targeted the mislabeled 80,000/20,000/32,000 item counts (see the status
note above) and is not present in this repository. It does not regenerate
the current, authoritative Table 2 — for that, all four languages'
intrinsic evaluation relies on the annotated morpheme test set at
`evaluation/data/{amharic,tigrinya,tigre,geez}_gold.tsv`, run with
[`scripts/evaluate_intrinsic.py`](../../scripts/evaluate_intrinsic.py); see
[`table2_final.csv`](table2_final.csv) and
[`MorphScore_report.md`](MorphScore_report.md).
