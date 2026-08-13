# V2 paper — outline

Structure follows the original paper (arXiv:2509.08812). All values come from
the frozen V2 tables in `v2/table{2,3,4}/*_final.csv`.

| § | Section | Source |
|---|---|---|
| 1 | Introduction | `introduction_notes.md` |
| 2 | Related work | `related_work_notes.md` |
| 3 | Method — MoVoC, MoVoC-Tok | `methodology_notes.md` |
| 4 | Datasets and setup | `methodology_notes.md` §Datasets |
| 5.1 | Intrinsic evaluation — Tables 2, 4 | `table2_notes.md`, `table4_notes.md` |
| 5.2 | Extrinsic evaluation — Table 3 | `table3_notes.md` |
| 6 | Discussion | `discussion_notes.md` |
| 7 | Limitations | `limitations_notes.md` |
| 8 | Conclusion | `conclusion_notes.md` |

## Tables

| Table | Content | Source file |
|---|---|---|
| 2 | Morpheme datasets + MorphScore | `v2/table2/table2_final.csv` |
| 3 | MarianMT BLEU / chrF++ | `v2/table3/table3_final.csv` |
| 4 | Boundary precision + Rényi entropy | `v2/table4/table4_final.csv` |

## Contribution order

MoVoC → MoVoC-Tok → annotated datasets → intrinsic evaluation → extrinsic
evaluation.
