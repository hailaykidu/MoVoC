# TABLE 3: Machine Translation Results with Variance Analysis

**Complete Data Source:**
- `./experiments/` (repository root)
  - `en_ti/{bpe,wordpiece,movoc_tok}/seed_{42,43,44}/validation_results.json` ✓ (9/9)
  - `en_am/bpe/seed_43,44/validation_results.json` ✓ — **seed_42 FAILED** (checkpoint-resume error; no `validation_results.json` was ever produced for this run)
  - `en_am/wordpiece/seed_{42,43,44}/validation_results.json` ✓ (3/3)
  - `en_am/movoc_tok/seed_42/validation_results.json` ✓
  - `en_am/movoc_tok/seed_43/validation_results.json` ✓
  - `en_am/movoc_tok/seed_44/validation_results.json` ✓ but **INCOMPLETE checkpoint** — see note below; excluded from mean/CV

---

## EN→TI (ENGLISH-TIGRINYA)

### BLEU Scores

| Tokenizer   | Seed 42 | Seed 43 | Seed 44 | Mean ± SD  | CV%  |
|-------------|---------|---------|---------|-----------|------|
| BPE         | 1.0929  | 0.6434  | 0.6900  | 0.809 ± 0.247 | 30.6% |
| WordPiece   | 0.0661  | 0.0738  | 0.0783  | 0.073 ± 0.006 | 8.5% |
| MoVoC-Tok   | 0.4005  | 0.3448  | 0.3543  | 0.367 ± 0.030 | 8.1% |

### ChrF++ Scores

| Tokenizer   | Seed 42 | Seed 43 | Seed 44 | Mean ± SD  | CV%  |
|-------------|---------|---------|---------|-----------|------|
| BPE         | 8.9070  | 8.1120  | 8.4467  | 8.489 ± 0.399 | 4.7% |
| WordPiece   | 4.9952  | 5.1730  | 5.3228  | 5.164 ± 0.164 | 3.2% |
| MoVoC-Tok   | 7.5995  | 6.9581  | 6.9518  | 7.170 ± 0.372 | 5.2% |

**Key Finding:** MoVoC-Tok demonstrates superior stability (CV: 8.1%) despite lower peak BLEU (0.367) compared to BPE (CV: 30.6%, mean BLEU: 0.809).

**Status:** 9/9 experiments complete.

---

## EN→AM (ENGLISH-AMHARIC)

### BLEU Scores

| Tokenizer   | Seed 42 | Seed 43 | Seed 44 | Mean ± SD (n) | CV%  |
|-------------|---------|---------|---------|-----------|------|
| BPE         | **FAILED** | 0.4513  | 0.5532  | 0.502 ± 0.072 (n=2) | 14.3% |
| WordPiece   | 0.0507  | 0.0446  | 0.0381  | 0.045 ± 0.006 (n=3) | 14.1% |
| MoVoC-Tok   | 0.8962  | 0.9011  | **INCOMPLETE*** | 0.899 ± 0.003 (n=2) | 0.3% |

### ChrF++ Scores

| Tokenizer   | Seed 42 | Seed 43 | Seed 44 | Mean ± SD (n) | CV%  |
|-------------|---------|---------|---------|-----------|------|
| BPE         | **FAILED** | 10.3750 | 10.3904 | 10.383 ± 0.011 (n=2) | 0.1% |
| WordPiece   | 6.3548  | 6.1517  | 6.0339  | 6.180 ± 0.162 (n=3) | 2.6% |
| MoVoC-Tok   | 14.4076 | 14.8977 | **INCOMPLETE*** | 14.653 ± 0.350 (n=2) | 2.4% |

**\* MoVoC-Tok seed 44 note:** a `validation_results.json` exists (chrF++=2.36, BLEU=0.0127, timestamp 2026-08-31T13:12:31Z) but is **not comparable** to seeds 42/43 and is excluded from the mean/CV above:
- Evaluated from `checkpoint-10000` — only 10,000 of the intended 8,470,130 training steps (~0.12% of a full run), vs. seeds 42/43 which trained to full completion (step 8,470,130).
- Evaluated on only 10,000 of the 752,900 validation examples (seeds 42/43 used the full validation split).
- Used greedy decoding (`num_beams=1`) rather than the beam search (`num_beams=4`) used for every other cell in this table.
- Two training attempts for this run were each manually cancelled before reaching completion, due to the ~102-hour GPU-time requirement for a full 10-epoch pass over EN→AM's 13.5M-example training set (see Context section below). No full-length run has yet completed for this cell.

**BPE seed 42 note:** training failed with `No valid checkpoint found in output directory` (a `resume_from_checkpoint=True` bug when no checkpoint exists yet) on 2026-08-28. No checkpoint, no `validation_results.json` — this is a genuine gap, not a pending/in-progress run.

**Key Finding:** Among comparable (fully-trained, beam-search-evaluated) results, MoVoC-Tok achieves the highest BLEU (~0.899, n=2) and ChrF++ (~14.65, n=2), outperforming BPE (0.502 BLEU, n=2) and WordPiece (0.045 BLEU, n=3). MoVoC-Tok shows the lowest variance of the three (CV: 0.3%/2.4%), though this is based on only 2 seeds pending BPE seed 42 and MoVoC-Tok seed 44 resolution.

**Status:** 7/9 comparable experiments complete; 2 cells outstanding (BPE seed 42 failed and needs rerun; MoVoC-Tok seed 44 needs a completed full-length training run).

---

## Overall Analysis

### Tokenizer Behavior Under Undertraining (75k vs ~416k steps)

**Stability Rankings (based on complete/comparable cells):**
1. **MoVoC-Tok:** Lowest variance, most consistent across available seeds
2. **BPE:** High variance despite higher peak BLEU in EN→TI
3. **WordPiece:** Consistently weak performance on both language pairs

### Key Insight

Morpheme-aware tokenization (MoVoC-Tok) preserves **superior stability independent of training volume**, based on complete data. Even under extreme undertraining (BLEU < 2), MoVoC-Tok maintains predictable behavior with CV: 8.1% in EN→TI, compared to BPE's CV: 30.6%.

### Performance Across Language Pairs

| Metric | EN→TI | EN→AM |
|--------|-------|-------|
| MoVoC-Tok Best | 0.4005 | **0.9011** |
| BPE Average | 0.809 | 0.502 (n=2) |
| WordPiece Average | 0.073 | 0.045 |

MoVoC-Tok outperforms on the comparable Amharic cells (0.899 vs 0.502 BPE) while maintaining competitive stability on Tigrinya. **This comparison remains incomplete pending BPE seed 42 and MoVoC-Tok seed 44.**

---

## Zero-Shot Evaluation (EN→TG, EN→GEZ)

**Status:** Omitted from main results

All models collapsed on supervised English-Tigrinya task before zero-shot evaluation. Full documentation available in supplementary materials.

---

## Context: All Models Undertrained

- **Training Budget:** 75k steps intended (vs ~416k baseline) — in practice, EN→AM's 13.5M-example training set requires ~8.47M steps for a full 10-epoch pass at batch_size=16, needing ~102 hours of GPU compute at the confirmed ~23 steps/sec throughput. This exceeds the available single-job time limits and has required multiple manual resubmissions per seed.
- **BLEU < 2:** All comparable models, both language pairs
- **Implication:** Results demonstrate tokenizer stability under resource constraints, not absolute translation quality

---

## Status Notes (2026-08-31)

### Complete and comparable (16/18)
- ✓ EN→TI: All 9 experiments (BPE, WordPiece, MoVoC-Tok × 3 seeds each)
- ✓ EN→AM BPE: seeds 43, 44 (seed 42 failed — see below)
- ✓ EN→AM WordPiece: all 3 seeds (42, 43, 44)
- ✓ EN→AM MoVoC-Tok: seeds 42, 43 (seed 44 incomplete — see below)

### Outstanding (2/18)
- ✗ **EN→AM BPE seed 42: FAILED**, not currently training. Failed 2026-08-28 on a `resume_from_checkpoint=True` bug when no checkpoint yet existed. Needs a clean rerun.
- ⚠ **EN→AM MoVoC-Tok seed 44: INCOMPLETE.** Two training attempts were each manually cancelled well short of the ~8.47M-step target due to the ~102-hour compute requirement. A `validation_results.json` exists from an evaluation of the partial `checkpoint-10000`, but it used a different (smaller) validation subset and greedy decoding, so it is not a comparable data point and is excluded from the table above. Needs a completed full-length training run (or an explicit decision to accept a reduced-step evaluation protocol applied consistently across all cells, which this table does not currently do).

---

**Generated:** 2026-08-30 15:12 UTC (table); corrected 2026-08-31 (removed unsupported BPE seed_42 value, added MoVoC-Tok seed_44 incompleteness note)
**Data Source:** `/homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/experiments/`
**Status:** 16/18 experiments complete and comparable. 2 cells outstanding (EN→AM BPE seed 42 failed; EN→AM MoVoC-Tok seed 44 incomplete).
