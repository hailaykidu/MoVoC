# Table 3 — published vs reconstruction v2

Extrinsic evaluation: downstream MarianMT translation quality (BLEU, chrF++).

**Published values belong to the paper and are not modified.**

## Published Table 3

| Strategy | BLEU ↑ | chrF++ ↑ |
|---|---|---|
| **English → Amharic** | | |
| BPE | 0.2150 ± 0.0120 | 16.2000 ± 1.05 |
| WordPiece | 0.2340 ± 0.0155 | 16.5000 ± 1.00 |
| MoVoC-Tok | **0.2455 ± 0.0108** | **17.8500 ± 0.95** |
| **English → Tigrinya** | | |
| BPE | 0.1720 ± 0.0095 | 7.2000 ± 0.85 |
| WordPiece | 0.1880 ± 0.0088 | 7.5000 ± 0.80 |
| MoVoC-Tok | **0.2050 ± 0.0080** | **8.1000 ± 0.75** |
| **English → Tigre** | | |
| BPE | 0.0950 ± 0.0080 | 4.0000 ± 0.70 |
| WordPiece | 0.1025 ± 0.0075 | 4.3000 ± 0.65 |
| MoVoC-Tok | **0.1175 ± 0.0068** | **5.1500 ± 0.60** |
| **English → Ge'ez** | | |
| BPE | 0.0480 ± 0.0070 | 3.0500 ± 0.55 |
| WordPiece | 0.0550 ± 0.0065 | 3.2500 ± 0.60 |
| MoVoC-Tok | **0.0660 ± 0.0060** | **3.9500 ± 0.50** |

Cited from arXiv:2509.08812.

## Reconstruction v2 — FLORES-200 devtest (n=1012)

9 runs: 3 tokenizers × 3 seeds (42/43/44). Trained on English→Amharic and
English→Tigrinya only; Tigre and Ge'ez are zero-shot.

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ | Output quality |
|---|---|---:|---:|---|
| English → Amharic | BPE | **1.4937 ± 0.0866** | **21.5573 ± 0.2167** | clean |
| English → Amharic | WordPiece | 0.0534 ± 0.0140 | 11.5990 ± 0.0295 | clean |
| English → Amharic | MoVoC-Tok | 0.7907 ± 0.0363 | 18.3999 ± 0.1711 | flagged |
| English → Tigrinya | BPE | **1.2557 ± 0.2135** | **10.8757 ± 0.0708** | clean |
| English → Tigrinya | WordPiece | 0.0439 ± 0.0037 | 6.7069 ± 0.1085 | clean |
| English → Tigrinya | MoVoC-Tok | 0.2710 ± 0.0775 | 7.8489 ± 0.2845 | flagged |

## Difference — and why the two are not directly comparable

The reconstruction **does not reproduce the published ranking**: BPE leads on
both directions, where the paper reports MoVoC-Tok ahead.

The two columns are not comparable measurements, for reasons documented rather
than worked around:

- The **scoring pipeline that produced Table 3 is not preserved** in this
  repository, so no run performed now can be shown to follow the same procedure.
- The **metric scale of the published BLEU column is unresolved** — published
  values (0.048–0.246) are inconsistent with sacreBLEU's 0–100 scale.
- **No held-out Ge'ez evaluation set** is available, so the Ge'ez block cannot be
  regenerated at all.
- MoVoC-Tok runs are **flagged for degenerate output**, so their scores measure a
  partly-failed training run, not the method.

These are new measurements from a reconstructed pipeline, **not replacement
values for Table 3**.

Full detail: [`./PROVENANCE.md`](./PROVENANCE.md)
and [`./results/table3_multiseed.md`](./table3_multiseed.md).
