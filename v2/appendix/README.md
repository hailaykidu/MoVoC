# Appendix — supporting analyses

**Nothing in this directory belongs in the main V2 tables.** These analyses may
show where MoVoC-Tok performed best, but they do not replace the primary results
in [`../table2/`](../table2/), [`../table3/`](../table3/) and
[`../table4/`](../table4/), which use the final approved methodology applied
identically to every tokenizer.

> **Guiding principle:** report the *best fair comparison*, not the *best
> MoVoC-Tok score*.

## A. Best MoVoC-Tok results

Where MoVoC-Tok leads under the primary methodology — reported here for
discussion, already present in the main tables.

| Table | Language | MoVoC-Tok | Best baseline | Margin |
|---|---|---:|---:|---:|
| 4 (precision) | Amharic | **0.3208** | BPE 0.3170 | +0.0038 |
| 4 (precision) | Tigrinya | **0.3242** | BPE 0.3142 | +0.0100 |
| 4 (precision) | Tigre | **0.5629** | BPE 0.5380 | +0.0249 |
| 2 (MorphScore) | Amharic | **0.4139** | BPE 0.4105 | +0.0034 |
| 2 (MorphScore) | Tigrinya | **0.4366** | BPE 0.4200 | +0.0166 |
| 2 (MorphScore) | Tigre | **0.5278** | BPE 0.5004 | +0.0274 |

MoVoC-Tok leads on boundary precision and MorphScore in three of the four
languages under the primary methodology; Ge'ez is a near-tie with BPE on both
(precision 0.4301 vs 0.4326; MorphScore 0.6561 vs 0.6667). Tigre and Ge'ez are
both cross-lingual rows — the Tigrinya 32k model applied to a language it was
never trained on — so Tigre's win there is a generalization result, not an
in-language one.

## B. Sensitivity analyses

[`../audits/precision_linguistic_sensitivity.md`](../audits/precision_linguistic_sensitivity.md)
— linguistically grounded precision variants for Amharic and Ge'ez.

Recorded outcome: no linguistically motivated variant reverses the ranking on
Amharic. A blanket ±1 tolerance flips Ge'ez (64.34 vs 62.94); the
fusion-restricted variant does not (−1.92 vs −1.40 exact). These deltas were
computed against the precision run that has since been superseded (see D
below) — they still support the qualitative finding (no linguistically
motivated fix reverses the ranking), but the exact figures predate the
current Table 4.

**These are sensitivity values. They never appear in Table 4, which reports
official exact-match precision.**

## C. Alternative evaluations

- **Held-out vs in-sample splits** — `../table2/paper_tables_released_pipeline*.json`
- **Ge'ez MorphScore 88.7** — an earlier, since-superseded computation on 172
  words (44 official) with a tokenizer built after publication. Table 2 now
  reports 0.6561 for the same language under the current methodology; the
  88.7 figure is not used in any headline claim.

## D. Audits

Full investigations in [`../audits/`](../audits/): entropy, projection,
precision, tokenizer, dataset, plus incident evidence from a documented failed
MT run.
