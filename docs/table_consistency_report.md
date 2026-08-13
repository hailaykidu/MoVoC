# Table consistency report

Verification that each table's CSV, TeX, per-table report and README
presentation carry identical values. **Programmatic check; no table was
regenerated.**

## Result

| Table | Rows | CSV ↔ TeX | TeX ↔ report | Report ↔ README | Verdict |
|---|---:|---|---|---|---|
| Table 2 | 4 | match | match | match | **consistent** |
| Table 3 | 6 (FLORES-200) | match | match | match | **consistent** |
| Table 4 | 8 | match | match | match | **consistent** |

**Inconsistencies found: 0.**

Method: every numeric value in each `*_final.csv` was required to appear in the
corresponding `.tex`, the per-table report and the root README.

## Table 2 — MorphScore

Source: `v2/table2/table2_final.csv`

| Language | Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 41.3 |
| Tigrinya (tir) | 5,224 | 41.5 |
| Ge'ez (gez) | 172 | 88.7 |
| Tigre (tig) | 2,149 | 42.9 |

Propagated to `table2_final.tex`, `MorphScore_report.md`, `README.md`.

## Table 3 — MarianMT (FLORES-200 devtest, mean ± std, seeds 42/43/44)

Source: `v2/table3/table3_final.csv`

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ |
|---|---|---:|---:|
| English → Amharic | BPE | 1.4937 ± 0.0866 | 21.5573 ± 0.2167 |
| English → Amharic | WordPiece | 0.0534 ± 0.0140 | 11.5990 ± 0.0295 |
| English → Amharic | MoVoC-Tok | 0.7907 ± 0.0363 | 18.3999 ± 0.1711 |
| English → Tigrinya | BPE | 1.2557 ± 0.2135 | 10.8757 ± 0.0708 |
| English → Tigrinya | WordPiece | 0.0439 ± 0.0037 | 6.7069 ± 0.1085 |
| English → Tigrinya | MoVoC-Tok | 0.2710 ± 0.0775 | 7.8489 ± 0.2845 |

The CSV additionally carries 12 non-FLORES cells (OPUS/Tatoeba, zero-shot Tigre
and Ge'ez). The TeX and README present the FLORES-200 block only; this is a
deliberate scope choice, not an inconsistency.

## Table 4 — boundary precision and Rényi entropy

Source: `v2/table4/table4_final.csv`

| Language | Tokenization | Precision ↑ | Rényi ↓ |
|---|---|---:|---:|
| Amharic | MoVoC-Tok | 24.0 | 0.62 |
| Amharic | BPE | 24.3 | 0.66 |
| Tigrinya | MoVoC-Tok | 26.6 | 0.92 |
| Tigrinya | BPE | 27.3 | 0.93 |
| Tigre | MoVoC-Tok* | 63.3 | 0.71 |
| Tigre | BPE | 60.0 | 0.73 |
| Ge'ez | MoVoC-Tok* | 35.4 | 0.82 |
| Ge'ez | BPE | 36.8 | 0.81 |

Official exact-match precision and normalized Rényi entropy. No sensitivity
value (±1 or otherwise) appears in any main table; those remain confined to
`v2/audits/` and `v2/appendix/`.

## Second intrinsic run — preserved, not merged

`v2/table4/amseg_tokenizer_quality_table4_format.md` records a separate
three-arm run (BPE / WordPiece / MoVoC-Tok) on different evaluation data. It is
**not merged into Table 4** and its values are not propagated to the README.

The two runs disagree on Tigre's winner (three-arm: MoVoC-Tok 56.3 vs BPE 53.8;
held-out: BPE 60.4 vs MoVoC-Tok 46.3). Both are preserved exactly, per the
freeze policy. A dedicated Tigre consistency audit is the prerequisite for
selecting one.
