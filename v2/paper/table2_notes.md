# Table 2 — notes

Source: `v2/table2/table2_final.csv`, `v2/table2/MorphScore_report.md`.
Authoritative values are the AMSEG intrinsic tokenizer evaluation
(`amseg/evaluation/results/intrinsic_tokenizer_table.md`,
`table2_morphscore_movoc_tok.md`).

## Publication-ready table

**Table 2: Morpheme-annotated evaluation sets and MorphScore for MoVoC-Tok.**

| Language (ISO 639-3) | Tokenizer | No. Items | MorphScore ↑ |
|---|---|---:|---:|
| Amharic (amh) | BPE | 81,224 | 0.4105 |
| Amharic (amh) | WordPiece | 81,224 | 0.3842 |
| Amharic (amh) | MoVoC-Tok | 81,224 | **0.4139** |
| Tigrinya (tir) | BPE | 5,224 | 0.4200 |
| Tigrinya (tir) | WordPiece | 5,224 | 0.4186 |
| Tigrinya (tir) | MoVoC-Tok | 5,224 | **0.4366** |
| Tigre (tig) | BPE | 1,974 | 0.5004 |
| Tigre (tig) | WordPiece | 1,974 | 0.4778 |
| Tigre (tig) | MoVoC-Tok | 1,974 | **0.5278** |
| Ge'ez (gez) | **BPE** | 172 | **0.6667** |
| Ge'ez (gez) | WordPiece | 172 | 0.6392 |
| Ge'ez (gez) | MoVoC-Tok | 172 | 0.6561 |

LaTeX: `v2/table2/table2_final.tex`.

## Metric

MorphScore (Arnett & Bergen, 2025): recall of gold morpheme boundaries,
micro-averaged over the corpus, with unsegmented words excluded rather than
scored zero. Boundaries are cumulative morpheme lengths. Implementation:
`scripts/evaluate_intrinsic.py` (migrated into this repository from the
separate `amseg` project); formula per `movoc/metrics.py`. Values are
fractions in [0, 1].

## Evaluation sets

Items are multi-morphemic, surface-aligned words — those carrying at least one
gold boundary that can be located by character offset. Tigre and Ge'ez have no
dedicated MoVoC-Tok artifact; both are scored with the Tigrinya-trained
MoVoC-Tok as a cross-lingual generalization measurement.

| Language | Items evaluated | Mode |
|---|---:|---|
| Amharic | 81,224 | in-language |
| Tigrinya | 5,224 | in-language |
| Tigre | 1,974 | cross-lingual (Tigrinya model) |
| Ge'ez | 172 | cross-lingual (Tigrinya model) |

## Caption draft

> **Table 2.** Morpheme-annotated evaluation sets and MorphScore for MoVoC-Tok.
> MorphScore is the micro-averaged recall of gold morpheme boundaries, excluding
> words the tokenizer left unsegmented. Higher is better.

## Points for the text

- MoVoC-Tok achieves the highest MorphScore among the evaluated tokenizers for
  Amharic (0.4139), Tigrinya (0.4366), and Tigre (0.5278). For Ge'ez, BPE is
  slightly ahead (0.6667 vs. 0.6561).
- Tigre and Ge'ez were not training languages for MoVoC-Tok; their results
  measure cross-lingual generalization, whereas Amharic and Tigrinya measure
  in-language performance.
- MorphScore is recall-oriented and does not penalise false positives; it is
  reported alongside boundary precision (Table 4) rather than in place of it.
- Evaluation-set sizes differ substantially across languages, reflecting
  available annotation coverage.

### Tokenization quality — interpretive scope for the text

The absolute MorphScore values here should be interpreted only within this
study. MorphScore is defined relative to a specific tokenizer,
gold-annotation convention, and evaluation set, so these values are **not
commensurable with those reported by Arnett and Bergen (2025)**: their
22-language sample contains no Semitic or Ge'ez-script language and their
fusional subset is entirely Indo-European; their evaluation sets range from
112 to 2,000 items with inconsistent inflectional versus derivational
boundary annotation, which they note "could introduce uncontrolled
variance"; and their scores were computed for a different suite of
monolingual tokenizers. No claim is made of exceeding an external MorphScore
threshold.

While MoVoC-Tok does not score higher than all SentencePiece tokenizer
variants (WordPiece is never highest here, but BPE leads on Ge'ez), this
indicates the hybrid approach instills at least partial morpheme awareness
into the tokenization process. Table 4 informs this further: MoVoC-Tok leads
boundary precision in three of four languages, with a near-tie on Ge'ez. The
effect is comparatively modest for Amharic and Tigrinya; the clearer
separation from the baselines appears on the lower-resource languages, Tigre
and Ge'ez.
