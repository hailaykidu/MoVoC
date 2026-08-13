# Reconstruction Version 2

The primary research artifact of this repository and the basis of the V2 paper.

V2 is an independent re-implementation, reproduction and audit of MoVoC
(Findings of EMNLP 2025, arXiv:2509.08812), built from the released artifacts.
Its purpose is to establish **what can be reproduced, what cannot, and why** —
not to restate the paper's claims.

## Result selection policy

Main tables report the **final approved methodology, applied identically to every
tokenizer**. Specifically:

- **Table 2** — the final MorphScore result. Not replaced by a higher score from
  an alternative dataset or metric.
- **Table 3** — the final MarianMT evaluation, mean ± std across seeds 42/43/44.
- **Table 4** — official exact-match precision and normalized Rényi entropy.
  **Never** ±1 or other sensitivity values.

Best-performing runs, sensitivity analyses and alternative evaluations live in
[`appendix/`](appendix/) and never substitute for the main tables.

> **Report the best fair comparison, not the best MoVoC-Tok score.**

## Structure

```
v2/
├── table2/      MorphScore    — table2_final.{csv,tex}, MorphScore_report.md
├── table3/      MarianMT      — table3_final.{csv,tex}, MarianMT_report.md
├── table4/      Intrinsic     — table4_final.{csv,tex}, Intrinsic_report.md
├── tokenizers/  tokenizer reconstruction records
├── marianmt/    MT reconstruction configuration
├── audits/      entropy · projection · precision · dataset · tokenizer
├── appendix/    best runs · sensitivity · alternative evaluations
└── reports/     summary · methodology · limitations · discussion
```

Each per-table report contains **Published Results**, **V2 Reconstruction** and
**Comparison** as separate sections. Categories are never merged into one table
without explicit labelling.

## Results at a glance

| Table | Metric | Published | V2 | Reproduces? |
|---|---|---|---|---|
| 2 | MorphScore (amh, n=80,000) | 0.710 | 41.3 | **No** |
| 3 | BLEU en→am | 0.2455 | 1.4937 (BPE leads) | **No** — pipeline absent |
| 4 | Precision (amh, MoVoC-Tok) | 85.5 | 24.0 | **No** |
| 4 | Rényi direction | MoVoC-Tok lower | MoVoC-Tok lower in 3/4 | **Yes** |

See [`reports/reconstruction_v2_summary.md`](reports/reconstruction_v2_summary.md)
and [`reports/limitations.md`](reports/limitations.md).
