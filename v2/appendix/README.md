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
| 4 (precision) | Tigre | **63.3** | BPE 60.0 | +3.3 |
| 4 (Rényi ↓) | Amharic | **0.62** | BPE 0.66 | −0.04 |
| 4 (Rényi ↓) | Tigrinya | **0.92** | BPE 0.93 | −0.01 |
| 4 (Rényi ↓) | Tigre | **0.71** | BPE 0.73 | −0.02 |

Tigre is the only language where MoVoC-Tok leads on both official metrics under
the primary methodology, and its annotations are 100% surface-concatenative.

Recorded with it: the Tigre MoVoC-Tok row is cross-lingual (the Tigrinya 32k
model), and a second run disagrees on the winner. See
[`../audits/tokenizer_audit.md`](../audits/tokenizer_audit.md).

## B. Sensitivity analyses

[`../audits/precision_linguistic_sensitivity.md`](../audits/precision_linguistic_sensitivity.md)
— linguistically grounded precision variants for Amharic and Ge'ez.

Recorded outcome: no linguistically motivated variant reverses the primary
ranking. A blanket ±1 tolerance flips Ge'ez (64.34 vs 62.94); the
fusion-restricted variant does not (−1.92 vs −1.40 exact).

**These are sensitivity values. They never appear in Table 4, which reports
official exact-match precision.**

## C. Alternative evaluations

- **Held-out vs in-sample splits** — `../table2/paper_tables_released_pipeline*.json`
- **Three-arm intrinsic run** on different evaluation data (BPE / WordPiece /
  MoVoC-Tok), which **contradicts the primary run on Tigre's winner**. Unresolved;
  see [`../table4/Intrinsic_report.md`](../table4/Intrinsic_report.md).
- **Ge'ez MorphScore 88.7** — computed on 172 words (44 official) with a
  tokenizer built after publication. Not used in any headline claim.

## D. Audits

Full investigations in [`../audits/`](../audits/): entropy, projection,
precision, tokenizer, dataset, plus incident evidence from a documented failed
MT run.
