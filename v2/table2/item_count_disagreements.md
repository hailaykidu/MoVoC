# Why Tigre's item count differs across projects

Four different Tigre counts appear across related local projects. None are
errors — each reflects a different filtering rule applied to the same
underlying annotation set.

| Value | Source | Rule |
|---|---|---|
| **1,974** | `v2/table2/table2_final.csv`, `v2/table4/table4_final.csv` (this repository) | Surface-aligned, multi-morpheme words only |
| 2,149 | `movoc_table2_repro/results/TABLE2_FINAL.md` | Final MorphScore item count in that document (unsegmented excluded) |
| 2,457 | `movoc_table4_repro/results_intrinsic{,_official}/dataset_statistics.csv` | Words with ≥2 morphemes, before surface-alignment filtering |
| 5,666 | `marianmt-tokenizer-comparison/Paper_Artifacts/table2_final.md` | All words, unsegmented included (scored 1.0) |

The same pattern holds for Ge'ez: this repository's Table 2 and Table 4
both use **172**, while `marianmt-tokenizer-comparison/Paper_Artifacts/table2_final.md`
reports **77** under its own, differently-filtered set.

## What this repository uses

`table2_final.csv` and `table4_final.csv` in this repository use the same
1,974-word Tigre set and 172-word Ge'ez set — both produced by
`scripts/evaluate_intrinsic.py` reading `evaluation/data/{tigre,geez}_gold.tsv`.
MorphScore: 1 if a tokenizer boundary aligns with the gold morpheme
boundary, else 0; unsegmented (single-morpheme) words are excluded; the
final score is the mean over the evaluated set. See
[`Intrinsic_report.md`](../table4/Intrinsic_report.md) and
[`table4_final.csv`](../table4/table4_final.csv) for Table 4's boundary
precision, which is a different metric over this same evaluation set.
