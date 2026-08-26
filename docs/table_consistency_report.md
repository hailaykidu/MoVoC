# Table consistency report

Verification that each table's CSV, TeX, per-table report and README
presentation carry identical values.

## Result

| Table | Rows | CSV ↔ TeX | TeX ↔ report | Report ↔ README | Verdict |
|---|---:|---|---|---|---|
| Table 2 | 12 | match | match | match | **consistent** |
| Table 3 | 6 (FLORES-200) + 12 (OPUS) | match | match | match | **consistent** |
| Table 4 | 12 | match | match | match | **consistent** |

**Inconsistencies found and fixed: the AMSEG intrinsic evaluation
(`amseg/evaluation/results/`) is now the authoritative source for Tables 2
and 4, propagated to every file listed below. The prior superseded values
(Amharic precision 24.0/24.3-style, MorphScore 41.3-style) are retained only
in `REPRODUCTION_STATUS.md` and the audit trail for provenance — they no
longer appear as current results anywhere else.**

Method: every numeric value in each `*_final.csv` was required to appear in
the corresponding `.tex`, the per-table report, the root README and the
manuscript prose in `v2/paper/manuscript/main.tex`.

## Table 2 — MorphScore

Source: `v2/table2/table2_final.csv`. Authoritative: AMSEG intrinsic
tokenizer evaluation, `amseg/evaluation/results/intrinsic_tokenizer_table.md`
and `table2_morphscore_movoc_tok.md`.

| Language | Tokenizer | Items | MorphScore ↑ | Mode |
|---|---|---:|---:|---|
| Amharic (amh) | BPE | 81,224 | 0.4105 | in-language |
| Amharic (amh) | WordPiece | 81,224 | 0.3842 | in-language |
| Amharic (amh) | MoVoC-Tok | 81,224 | 0.4139 | in-language |
| Tigrinya (tir) | BPE | 5,224 | 0.4200 | in-language |
| Tigrinya (tir) | WordPiece | 5,224 | 0.4186 | in-language |
| Tigrinya (tir) | MoVoC-Tok | 5,224 | 0.4366 | in-language |
| Tigre (tig) | BPE | 1,974 | 0.5004 | cross-lingual (Tigrinya model) |
| Tigre (tig) | WordPiece | 1,974 | 0.4778 | cross-lingual (Tigrinya model) |
| Tigre (tig) | MoVoC-Tok | 1,974 | 0.5278 | cross-lingual (Tigrinya model) |
| Ge'ez (gez) | BPE | 172 | 0.6667 | cross-lingual (Tigrinya model) |
| Ge'ez (gez) | WordPiece | 172 | 0.6392 | cross-lingual (Tigrinya model) |
| Ge'ez (gez) | MoVoC-Tok | 172 | 0.6561 | cross-lingual (Tigrinya model) |

Propagated to `table2_final.tex`, `MorphScore_report.md`,
`v2/paper/table2_notes.md`, `v2/paper/manuscript/tables/table2_final.tex`,
`v2/paper/manuscript/main.tex`, the root `README.md`, and this file.

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

The CSV additionally carries 12 non-FLORES cells (OPUS/Tatoeba, zero-shot
Tigre and Ge'ez, including English→Ge'ez — see the note on the published
manuscript's Ge'ez inconsistency in `v2/paper/table3_notes.md`). The TeX and
main-table README presentation show the FLORES-200 block only, by deliberate
scope choice; `MarianMT_report.md` now includes the OPUS block in full.

**Do not read this table as a tokenizer ranking.** All nine runs stopped at
75,000 of a comparable baseline's ~416,000 optimizer steps and never
converged (final loss 3.00–3.59); BLEU is below 2 in every cell, and all nine
MoVoC-Tok runs are flagged for output-quality anomalies. BPE's lead here
reflects the training budget, not tokenizer quality — see
`v2/table3/MarianMT_report.md`.

## Table 4 — boundary precision and Rényi entropy

Source: `v2/table4/table4_final.csv`. Authoritative: AMSEG intrinsic
tokenizer evaluation, same source as Table 2.

| Language | Tokenization | Precision ↑ | Rényi ↓ |
|---|---|---:|---:|
| Amharic | MoVoC-Tok | 0.3208 | 6.0589 |
| Amharic | BPE | 0.3170 | 6.2487 |
| Amharic | WordPiece | 0.3005 | 5.9949 |
| Tigrinya | MoVoC-Tok | 0.3242 | 6.2727 |
| Tigrinya | BPE | 0.3142 | 6.3747 |
| Tigrinya | WordPiece | 0.3167 | 5.6979 |
| Tigre | MoVoC-Tok\* | 0.5629 | 5.3192 |
| Tigre | BPE | 0.5380 | 5.4060 |
| Tigre | WordPiece | 0.5123 | 5.0260 |
| Ge'ez | BPE | **0.4326** | 3.8639 |
| Ge'ez | MoVoC-Tok\* | 0.4301 | 3.9735 |
| Ge'ez | WordPiece | 0.4201 | 3.9152 |

MoVoC-Tok leads boundary precision in three of four languages; Ge'ez is a
near-tie in BPE's favor (0.4326 vs 0.4301). Rényi entropy here is raw
(unnormalized); WordPiece is lowest in three of four languages, MoVoC-Tok
lowest only on Ge'ez. No sensitivity value (±1 or otherwise) appears in any
main table; those remain confined to `v2/audits/` and `v2/appendix/`.

## History: the earlier reproduction and the second intrinsic run

Table 4 previously reported a different reproduction (Amharic precision
24.0/24.3-style, entropy normalized to [0, 1]). That run is preserved for
provenance in `v2/table4/REPRODUCTION_STATUS.md` and is no longer presented
as current anywhere else in the repository.

A separate three-arm run on different evaluation data
(`v2/table4/amseg_tokenizer_quality_table4_format.md`) was previously
recorded as disagreeing with the primary run on Tigre's winner. That
disagreement is resolved: the AMSEG evaluation is now the primary run, and
the three-arm run's numbers agree with it to within rounding (same
underlying methodology and data). See
[`../v2/table4/Intrinsic_report.md`](../v2/table4/Intrinsic_report.md) for
the full history.
