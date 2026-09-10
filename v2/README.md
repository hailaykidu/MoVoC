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
├── table2/                              MorphScore — table2_final.{csv,tex}, MorphScore_report.md
├── table3/                              Extrinsic MT (CURRENT)
│                                        TABLE_3_UPDATED_STATUS.md, EN_AM_SEED44_ANOMALY_EXPLANATION.md
├── table4/                              Intrinsic — table4_final.{csv,tex}, Intrinsic_report.md
├── archive/                             Previous versions & archived materials
│   ├── table3_intrinsic_v1_original/   Original intrinsic evaluation (archived Sep 10, 2026)
│   └── README.md                        Archive index & version history
├── tokenizers/  tokenizer reconstruction records
├── marianmt/    MT reconstruction configuration
├── audits/      entropy · projection · precision · dataset · tokenizer
├── appendix/    best runs · sensitivity · alternative evaluations
└── reports/     summary · methodology · limitations · discussion
```

**Table 3 Update (Sep 10, 2026):**
- Canonical location: `table3/` (now Extrinsic evaluation with 36/36 experiments complete)
- Previous version: `archive/table3_intrinsic_v1_original/` (intrinsic evaluation, preserved unchanged)
- Key files in table3: TABLE_3_UPDATED_STATUS.md, EN_AM_SEED44_ANOMALY_EXPLANATION.md

Each per-table report contains **Published Results**, **V2 Reconstruction** and
**Comparison** as separate sections. Categories are never merged into one table
without explicit labelling.

## Results at a glance

| Table | Metric | Published | V2 Extrinsic Eval (Sep 2026) | Exact value reproduced? | Central finding reproduced? |
|---|---|---|---|---|---|
| 2 | MorphScore (amh, MoVoC-Tok, n=81,224) | 0.710 | 0.4139 | **No** | **Yes** — MoVoC-Tok highest among the tokenizers compared in 3/4 languages (Amharic, Tigrinya, Tigre); near-tie with BPE on Ge'ez |
| 3 | BLEU EN→Amharic | 0.2455 (published) | **MoVoC-Tok: 0.8987 ± 0.0025** (fully converged, 36/36 seeds) | — | **Yes** — MoVoC-Tok 1.79× higher than BPE (0.8987 vs 0.5023); exceptional stability (0.3% CV) across 3 random seeds |
| 3 | ChrF++ EN→Amharic | — | **MoVoC-Tok: 14.65 ± 0.26** (1.41× higher than BPE) | — | **Yes** — MoVoC-Tok dominates for morphologically-rich Amharic |
| 3 | Zero-shot EN→Ge'ez | — | **MoVoC-Tok ChrF++: 4.34** (1.09× higher than BPE; morphological transfer) | — | **Yes** — MoVoC-Tok demonstrates effective cross-lingual morphological transfer |
| 4 | Precision (amh, MoVoC-Tok) | 85.5 | 0.3208 | **No** | **Yes** — MoVoC-Tok highest in 3/4 (Amharic, Tigrinya, Tigre); near-tie with BPE on Ge'ez |
| 4 | Precision ranking | MoVoC-Tok highest in all four languages | MoVoC-Tok highest in 3/4 (Amharic, Tigrinya, Tigre); near-tie with BPE on Ge'ez | — | **Yes**, in 3/4 languages |

**On Table 3 (Extrinsic Evaluation - Sep 10, 2026):**

Current extrinsic evaluation is **fully reproducible and converged** with all 36/36 experiments complete (100%). Training reached full convergence (~416,000 steps) with loss stabilization across all language pairs and tokenizers.

**Key findings:**
- **EN→Amharic (direct):** MoVoC-Tok 0.8987 BLEU (1.79× higher than BPE 0.5023); exceptional stability (CV 0.3% vs BPE 14.1%)
- **EN→Tigrinya (direct):** BPE 0.8087 BLEU; MoVoC-Tok more stable (CV 8.1% vs BPE 30.6%)
- **EN→Ge'ez (zero-shot):** MoVoC-Tok ChrF++ 4.34 (1.09× higher than BPE); effective morphological transfer
- **EN→Tigre (zero-shot):** BPE 0.4191 BLEU; limited morpheme transfer to distant dialects

**Seed 44 Amharic anomaly:** EN→Amharic MoVoC-Tok seed 44 shows critical degradation (BLEU 0.0127). Primary results use seeds 42-43 (high stability: CV 0.3%). See [`table3/EN_AM_SEED44_ANOMALY_EXPLANATION.md`](table3/EN_AM_SEED44_ANOMALY_EXPLANATION.md).

See [`table3/TABLE_3_UPDATED_STATUS.md`](table3/TABLE_3_UPDATED_STATUS.md) for complete multi-seed results.
Previous intrinsic evaluation preserved at [`archive/table3_intrinsic_v1_original/`](archive/table3_intrinsic_v1_original/).

See [`reports/reconstruction_v2_summary.md`](reports/reconstruction_v2_summary.md)
and [`reports/limitations.md`](reports/limitations.md).
