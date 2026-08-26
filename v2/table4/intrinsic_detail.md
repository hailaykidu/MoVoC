# Table 4 — regenerated under the official MoVoC methodology (superseded)

> **Status: superseded.** This was the accepted Table 4 reproduction until the
> AMSEG intrinsic evaluation (`amseg/evaluation/results/`) replaced it as
> authoritative — see [`Intrinsic_report.md`](Intrinsic_report.md) and
> [`table4_final.csv`](table4_final.csv) for the current result. This file is
> kept for its audit history (the entropy-normalisation and
> cumulative-length-projection corrections below are still accurate and still
> apply); the specific precision/entropy values in the tables below are no
> longer current.
>
> Corrections 1 (normalized Rényi) and 2 (cumulative-length projection) are
> confirmed and incorporated. Precision values and rankings do not fully
> reproduce the publication; see `REPRODUCTION_STATUS.md` for the full
> statement, including the Tigre/Ge'ez cross-lingual assumption.

Supersedes `results_intrinsic/`, which the audits found invalid as a strict
reproduction. Intrinsic evaluation only: no MarianMT, no BLEU, no chrF++.

## Corrections applied

| # | Audit finding | Correction |
|---|---|---|
| 1 | Raw Rényi used | **Normalised** `H_alpha / log(support)`, matching `movoc/metrics.py` |
| 2 | Surface-locating projection | **Cumulative-length** rule, matching `boundaries_from_triple` |
| 3 | 63,051 MoVoC-Tok | **32k** per-language MoVoC-Tok, matching Table 4's caption |

Aggregation also switched to the official micro-average (Σmatched / Σpredicted)
over words carrying ≥1 gold boundary.

## Table 4 (reproduction)

| Language | Tokenization | Precision ↑ | Rényi ↓ |
|---|---|---:|---:|
| Amharic | MoVoC-Tok | 24.0 | 0.62 |
| Amharic | BPE | 24.3 | 0.66 |
| Tigrinya | MoVoC-Tok | 26.6 | 0.92 |
| Tigrinya | BPE | 27.3 | 0.93 |
| Tigre | MoVoC-Tok | 63.3 | 0.71 |
| Tigre | BPE | 60.0 | 0.73 |
| Ge'ez | MoVoC-Tok | 35.4 | 0.82 |
| Ge'ez | BPE | 36.8 | 0.81 |

## Evaluation set (after correction 2)

| Language | Records | Words evaluated | Gold boundaries | MoVoC-Tok model | Mode |
|---|---:|---:|---:|---|---|
| Amharic | 153,759 | 123,761 | 220,108 | `movoc_tok_32k_amharic` | in-language |
| Tigrinya | 206 | 205 | 259 | `movoc_tok_32k_tigrinya` | in-language |
| Tigre | 8,117 | 2,457 | 2,623 | `movoc_tok_32k_tigrinya` | cross-lingual (assumption) |
| Ge'ez | 193 | 173 | 258 | `movoc_tok_32k_tigrinya` | cross-lingual (assumption) |

The cumulative-length rule excludes no word for non-concatenation, so the
Amharic set grows from 22,907 to **123,761** words and Tigrinya from 18 to **205**.
Only monomorphemic words (no gold boundary) are skipped.

## Comparison with published Table 4

| Language | Tokenization | Prec (pub) | Prec (repro) | Δ | Rényi (pub) | Rényi (repro) | Δ |
|---|---|---:|---:|---:|---:|---:|---:|
| Amharic | MoVoC-Tok | 85.5 | 24.0 | -61.5 | 0.40 | 0.62 | +0.22 |
| Amharic | BPE | 85.3 | 24.3 | -61.0 | 0.41 | 0.66 | +0.25 |
| Tigrinya | MoVoC-Tok | 88.3 | 26.6 | -61.7 | 0.39 | 0.92 | +0.53 |
| Tigrinya | BPE | 83.9 | 27.3 | -56.6 | 0.40 | 0.93 | +0.53 |
| Tigre | MoVoC-Tok | 83.9 | 63.3 | -20.6 | 0.44 | 0.71 | +0.27 |
| Tigre | BPE | 74.6 | 60.0 | -14.6 | 0.49 | 0.73 | +0.24 |
| Ge'ez | MoVoC-Tok | 85.6 | 35.4 | -50.2 | 0.40 | 0.82 | +0.42 |
| Ge'ez | BPE | 73.9 | 36.8 | -37.1 | 0.44 | 0.81 | +0.37 |

### What the corrections fixed

**Rényi entropy is now on the paper's scale.** Reproduced 0.62–0.92 against a
published 0.39–0.49 — same order of magnitude, whereas the previous run gave
4.53–8.15. Correction 1 is confirmed effective.

**The full annotated datasets are now evaluated**, not a concatenative subset.

### What remains unreproduced

**Precision is still ~22–61 points below published**, and the direction now
differs from before: MoVoC-Tok leads BPE only for **Tigre** (63.3 vs 60.0).
Amharic (24.0 vs 24.3), Tigrinya (26.6 vs 27.3) and Ge'ez (35.4 vs 36.8) are
near-ties favouring BPE by <1.5 points. The paper reports MoVoC-Tok ahead in
all four.

Entropy direction *does* reproduce in 3 of 4 languages: MoVoC-Tok has lower
(better) normalised entropy for Amharic, Tigrinya and Tigre, matching the
paper. Only Ge'ez inverts (0.82 vs 0.81).

### Remaining candidate causes

1. **Predicted-boundary rule.** Both gold and predicted boundaries here use
   cumulative lengths over their own segmentations. If the paper compares
   tokenizer boundaries against gold in a more permissive way (for example
   allowing off-by-one at fusion points), all precision values would rise.
2. **Tigre and Ge'ez MoVoC-Tok is an assumption.** No in-language model exists
   at any size — the paper states no BPE training data was obtained for those
   languages. The Tigrinya 32k model was applied cross-lingually. The paper
   does not specify what it used, so those two rows rest on a documented guess.
3. **Amharic annotation source.** `postedited_morphemes.json` (153,759 records)
   was used; the paper's Table 2 reports 80k items for Amharic, so the exact
   subset may differ.
4. **Vocabulary +1.** MoVoC-Tok is 32,001 vs BPE 32,000 (Marian `<pad>`
   convention); not trimmed.

No data, formula, vocabulary or tokenizer output was adjusted to move these
values toward the published ones.

## Hardware

CPU. HuggingFace `tokenizers` is a Rust/CPU library with no CUDA path; the
workload is tokenizer-bound and completes in seconds. An A100 is available on
the `ampere` partition but would sit idle. See `performance_log.csv`.
