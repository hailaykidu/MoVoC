# Table 2 — final reproduction (superseded)

> **Status: superseded.** This was the accepted Table 2 reproduction until
> the AMSEG intrinsic tokenizer evaluation
> (`amseg/evaluation/results/`) replaced it as authoritative — see
> [`MorphScore_report.md`](MorphScore_report.md) and
> [`table2_final.csv`](table2_final.csv) for what's current. Kept here for
> provenance.

Reproduction of Table 2 of the MoVoC paper (Findings of EMNLP 2025,
arXiv:2509.08812), using the **official MorphScore implementation**, unmodified.

## Configuration

| Component | Setting |
|---|---|
| Metric | `movoc/metrics.py::morphscore` — boundary **recall**, micro-averaged |
| Unsegmented words | **Excluded**, not scored zero (`if not pred_b: continue`) |
| Gold projection | **Cumulative morpheme lengths** (`boundaries_from_triple`) |
| Tokenizers | Released `movoc_tok_merges_{lang}.txt`, 32k MoVoC-Tok |
| Data priority | Official MoVoC annotations → AMSEG evaluation data |
| Inclusion | Multi-morphemic **and** surface-aligned |

Formula, aggregation, projection and tokenizers were not modified. Only the
evaluation pool was expanded, as instructed. The repository's `metrics.py` is
byte-identical to the official release (`diff` clean).

## Result

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 41.3 |
| Tigrinya (tir) | 5,224 | 41.5 |
| Ge'ez (gez) | 172 | 88.7 |
| Tigre (tig) | 2,149 | 42.9 |

Scores are as computed. Nothing was adjusted toward the published values.

## Against the paper

| Language | Paper Items | Items reproduced | Paper MorphScore | Reproduced | Δ |
|---|---:|---:|---:|---:|---:|
| Amharic (amh) | 80,000 | **80,000** | 0.710 | 41.3 | **−29.7** |
| Tigrinya (tir) | 80,000 | 5,224 | 0.731 | 41.5 | −31.6 |
| Ge'ez (gez) | 20,000 | 172 | 0.670 | 88.7 | +22.0 |
| Tigre (tig) | 32,000 | 2,149 | 0.654 | 42.9 | −22.6 |

**Only Amharic reaches the published item count.** It is the one like-for-like
comparison in the table — same item count, same metric, same tokenizer — and it
falls **29.7 points short**.

## Source provenance

| Language | official_items | amseg_items | duplicates_removed | final_items | % official |
|---|---:|---:|---:|---:|---:|
| Amharic | 20,030 | 59,970 | 20,127 | 80,000 | 25.0% |
| Tigrinya | 2,713 | 2,511 | 2,723 | 5,224 | 51.9% |
| Ge'ez | 44 | 128 | 44 | 172 | 25.6% |
| Tigre | 2,149 | 0 | 2,457 | 2,149 | 100.0% |

Amharic and Ge'ez used the AMSEG directory only to fill the deficit after
official data was exhausted. Tigrinya and Tigre use the maximal union of both
sources. **Tigre is the only fully official row.**

## Findings

### 1. The binding constraint is surface alignment, not corpus size

MorphScore projects gold boundaries as cumulative morpheme lengths — character
offsets into the surface word. An annotation whose morphemes do not concatenate
back to the word produces offsets pointing at positions the word does not have,
and cannot be scored. The MoVoC annotations frequently store **citation forms**
(normalised roots) rather than surface allomorphs.

| Language | Unique multi-morpheme | Surface-aligned | Excluded |
|---|---:|---:|---:|
| Amharic | 121,719 | 20,030 | 103,634 |
| Tigrinya | 2,838 | 2,369 | 496 |
| Ge'ez | 173 | 44 | 129 |
| Tigre | 1,974 | 1,974 | **0** |

Amharic loses 85% of its entries this way, Ge'ez 75%. **Tigre loses none** — its
annotations are fully surface-concatenative, which is why it needed no
supplementation and why it also scored highest on boundary precision in the
Table 4 work.

### 2. Three of four languages cannot be evaluated at the paper's scale

Exhaustive search of the entire home directory — every repository, not just
MoVoC and AMSEG — established hard ceilings:

| Language | Maximum obtainable | Target | Gap |
|---|---:|---:|---:|
| Tigrinya | 5,224 | 80,000 | 74,776 |
| Ge'ez | 172 | 20,000 | 19,828 |
| Tigre | 2,149 | 32,000 | 29,851 |

For Tigrinya the search added **zero** new items over the previously known pool:
the large candidates were either placeholder/error files
(`NO_SEGMENTATION`, `ERROR: module 'hm' has no attribute 'anal'`), Amharic data
misfiled as Tigrinya (`Stem-processed.txt`, 187,517 rows — 39,888 of 40,062
aligned words overlap the Amharic annotations), or exact duplicates of
higher-priority files.

The decisive artifact is `annotation_template_tigrinya.json`: **20,000
frequency-ranked Tigrinya words, every one `annotation_status: pending` with zero
filled morpheme fields.** Unannotated Tigrinya text is plentiful; gold annotation
is what is missing. Reaching 80,000 would require roughly 75,000 words annotated
by a Tigrinya speaker.

### 3. The Amharic gap is not explained by item count

With Amharic at exactly 80,000 items, evaluation-set size is eliminated as an
explanation for the 29.7-point shortfall. The residual gap matches the Table 4
precision gap documented in
`../../movoc_table4_repro/results_intrinsic_official/REPRODUCTION_STATUS.md` §4
and shares its likely cause: exact character-offset matching under a projection
rule the paper does not describe.

**Tigre corroborates this independently.** It is the cleanest measurement in the
set — 100% official data, 100% surface-concatenative annotations, nothing lost to
filtering — and it still falls 22.6 points below its published value. Two
independent data paths producing the same shortfall points to the metric's
matching rule rather than to the evaluation data.

### 4. Ge'ez's 88.7 is not a result

It exceeds the published 0.670 by 22 points, but must not be read as a win:

- **172 words** — 0.9% of the stated 20,000, of which only 44 are official.
- The tokenizer `movoc_tok_merges_geez.txt` is a **9.3 KB artifact built Jul 30,
  after publication**. The paper (§4.1) states no training data was obtained for
  Ge'ez, so no original Ge'ez MoVoC-Tok exists.

### 5. Two rows are partly non-gold

Amharic is **75% AMSEG-derived** and Tigrinya **48.1%**, and part of that content
is HornMorpho-generated segmentation rather than gold annotation. Both are valid
measurements of the tokenizer against those segmentations, but neither is a pure
gold-annotation result and neither should be presented as one. Tigre alone is
100% official.

## Conclusion

**Table 2's published MorphScore values are not reproducible from the released
artifacts.** The metric is fully pinned and was executed without modification, so
the barrier is not the metric implementation. It is twofold: three of four
languages lack enough surface-aligned gold annotations to evaluate at the stated
scale, and the one language that reaches scale does so only with 75%
supplementation — and still falls ~30 points short.

## Artifacts

| File | Contents |
|---|---|
| `table2_final.csv` / `.tex` | the table above |
| `morphscore_scores.csv` | full provenance, exclusions, segmented-word counts |
| `final_report.md` | methodology and per-language detail |
| `tigrinya_80k_attempt_report.md` | exhaustive Tigrinya search and ceiling |
| `tigrinya_data_inventory.csv` | every Tigrinya source, usable and unusable |
| `tigrinya_source_breakdown.csv` | per-source contribution |

Regenerate with `python3 movoc_table2_repro/score_official_first.py` and
`python3 movoc_table2_repro/score_union_tir_tig.py`.
