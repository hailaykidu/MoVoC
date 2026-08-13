# Table 2 — notes

Source: `v2/table2/table2_final.csv`, `v2/table2/MorphScore_report.md`.

## Publication-ready table

**Table 2: Morpheme-annotated datasets and MorphScore for MoVoC-Tok.**

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 41.3 |
| Tigrinya (tir) | 5,224 | 41.5 |
| Ge'ez (gez) | 172 | 88.7 |
| Tigre (tig) | 2,149 | 42.9 |

LaTeX: `v2/table2/table2_final.tex`.

## Metric

MorphScore (Arnett & Bergen, 2025): recall of gold morpheme boundaries,
micro-averaged over the corpus, with unsegmented words excluded rather than
scored zero. Boundaries are cumulative morpheme lengths. Implementation:
`movoc/metrics.py::morphscore`. Values ×100.

## Evaluation sets

Items are multi-morphemic, surface-aligned words — those carrying at least one
gold boundary that can be located by character offset.

| Language | Items evaluated |
|---|---:|
| Amharic | 80,000 |
| Tigrinya | 5,224 |
| Ge'ez | 172 |
| Tigre | 2,149 |

## Caption draft

> **Table 2.** Morpheme-annotated evaluation sets and MorphScore for MoVoC-Tok.
> MorphScore is the micro-averaged recall of gold morpheme boundaries, excluding
> words the tokenizer left unsegmented. Higher is better.

## Points for the text

- MorphScore is recall-oriented and does not penalise false positives; it is
  reported alongside boundary precision (Table 4) rather than in place of it.
- Evaluation-set sizes differ substantially across languages, reflecting
  available annotation coverage.
