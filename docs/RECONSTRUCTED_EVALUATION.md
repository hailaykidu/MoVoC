# Reconstructed evaluation following the MoVoC evaluation protocol

This document reports a **reconstructed evaluation following the MoVoC
evaluation protocol** (Findings of EMNLP 2025). It is **not a reproduction
of the paper's numbers**, and no value here should be compared against a
published one: the original scoring pipeline is unavailable and the scale of
the published BLEU column is unresolved.

Commit: `e5aed99` · alpha = 2.0 · sacreBLEU 2.6.0 · transformers 4.51.3 ·
torch 2.5.1+cu118

---

## 1. Evaluation-data leakage: found and fixed

`movoc/annotation.py:40-53` points `GOLD_SOURCES` at the **same file** as
`VOCAB_SOURCES` for three of four languages:

| Language | Vocabulary source | Gold source | Same file? |
|---|---|---|---|
| Amharic | `amharic/postedited_morphemes.json` | `amharic/postedited_morphemes.json` | **yes** |
| Tigrinya | `tigrinya/postedited_morphemes.json` | `tigrinya/gold_morphemes.json` | no (23-word overlap) |
| Ge'ez | `geez/manual_morphemes.json` | `geez/manual_morphemes.json` | **yes** |
| Tigre | `tigre/manual_morphemes.json` | `tigre/manual_morphemes.json` | **yes** |

So Amharic, Ge'ez and Tigre were scored on the very words that built their
vocabularies. `evaluate.py:216` acknowledges this ("those scores are
optimistic") but does not correct it.

**Fix** (`scripts/paper_tables.py`): where gold and vocabulary share a file,
the set is partitioned with `random.Random(42)` into disjoint halves and only
the held-out half is scored. Where the gold file is separate (Tigrinya), any
word also present in the vocabulary source is removed. `--leaky` reproduces
the old behaviour for comparison.

**Measured effect** — leakage inflates every figure:

| Language | Metric | In-sample | Held-out | Δ |
|---|---|---|---|---|
| Amharic | MorphScore | 41.7 | **41.6** | −0.1 |
| Tigrinya | MorphScore | 39.3 | **34.0** | **−5.3** |
| Amharic | Boundary precision | 29.2 | **29.1** | −0.1 |
| Tigrinya | Boundary precision | 33.3 | **29.8** | **−3.5** |

Amharic barely moves (37,048 items — the vocabulary is not memorising
individual words); Tigrinya moves materially on 80 items. All tables below
use the **held-out** figures.

---

## 2. Table 2 — Morphological dataset and MoVoC-Tok MorphScore

Held-out, MoVoC-Tok only, as the paper's Table 2 is laid out.

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---|---|
| Amharic (amh) | 18,524 | 41.6 |
| Tigrinya (tir) | 70 | 34.0 |
| Ge'ez (gez) | 48 | not available |
| Tigre (tig) | 4,026 | not available |

**Ge'ez and Tigre are "not available", not zero.** MoVoC-Tok merge tables
exist only for Amharic and Tigrinya (`models/movoc_tok_merges_{amharic,
tigrinya}.txt`); `train.py` was never run for the other two languages, so
there is no MoVoC-Tok tokenizer to score. Reporting a number for them would
require training those tokenizers first.

**Dataset-size difference from the paper.** Item counts here are held-out
halves of the released annotations (Amharic 18,524 of 37,048 scorable;
Ge'ez 48 of 97; Tigre 4,026 of 8,053; Tigrinya 70 of 80 after overlap
removal). The paper's Table 2 item counts describe its own annotation sets
and are not reproduced.

MorphScore is computed **exactly once per tokenizer per language**, in a
single pass in `score_arm()`.

---

## 3. Table 4 — Boundary precision and Rényi entropy (α = 2)

| Language | Tokenization | Precision ↑ | Rényi Entropy ↓ |
|---|---|---|---|
| Amharic | MoVoC-Tok | **29.1** | **0.67** |
| Amharic | BPE | 1.6 | 0.76 |
| Tigrinya | MoVoC-Tok | **29.8** | **0.91** |
| Tigrinya | BPE | 1.7 | 0.93 |
| Ge'ez | — | not available | not available |
| Tigre | — | not available | not available |

Lower Rényi entropy indicates a **sharper, more consistent** segmentation
distribution — the tokenizer concentrates mass on fewer, more consistent
subwords (`movoc/metrics.py:109-119`, normalised to [0,1] by log support).
MoVoC-Tok is lower than BPE for both available languages.

BPE vocabulary size is 32,000 for both languages (verified), matching the
paper's comparison scale. MoVoC-Tok is a merge table over V_MoVoC, not a
fixed-size vocabulary.

---

## 4. Table 3 — extrinsic, multi-seed: PENDING

**No MT numbers are reported here.** Table 3 requires 18 independent
training runs (3 tokenizers × 2 trainable languages × 3 seeds) at ~4–7 GPU-h
each. The campaign is submitted (Slurm 55314–55331, partition `ampere`);
until it completes there is nothing to report, and no value is estimated,
interpolated or carried over from the paper.

**All 8 pre-existing checkpoints are excluded** from Table 3. They are
seed-42 only, and all six resized arms carry `forced_eos_token_id=0` while
their tokenizers use eos=2 — the defect recorded in
`docs/incidents/2026-07-28-invalid-mt-evaluation/`. A single seed cannot
carry a standard deviation in any case.

Scoring (`scripts/score_multiseed.py`) enforces, before any figure is
printed:

1. `global_step == max_steps` and `should_training_stop` true, else excluded;
2. every generation id in range for the checkpoint's vocabulary, else excluded;
3. at least 2 surviving seeds per cell, else the cell is withheld;
4. one metric implementation for every arm — a single `BLEU()` and
   `CHRF(word_order=2)` instance scores all of them.

Excluded runs are listed explicitly in `results/table3_multiseed.json`.

Ge'ez and Tigre are **zero-shot** — neither receives training. Tigre matches
the paper's own Sec 5.1 setup; Ge'ez is an **additional** zero-shot
evaluation on the seeded 100-pair Mermru split
(`data/evaluation/geez/manifest.json`, sha256-verified), and is **not** a
reproduction of the published Table 3 Ge'ez block.

---

## 5. Provenance

Every reported intrinsic value traces to:

| Field | Value |
|---|---|
| Commit | `e5aed99` |
| Split seed | 42 (`SPLIT_SEED`, `paper_tables.py`) |
| Metric implementation | `movoc/metrics.py` |
| Evaluation command | `python scripts/paper_tables.py` |
| Output file | `evaluation/results/paper_tables.json` |
| Leaky contrast | `evaluation/results/paper_tables_leaky.json` |

Per-language artifacts:

| Language | Gold file | MoVoC-Tok artifact | BPE artifact |
|---|---|---|---|
| Amharic | `data/annotations/amharic/postedited_morphemes.json` | `models/movoc_tok_merges_amharic.txt` | `data/vocabulary/bpe_amharic.json` (32,000) |
| Tigrinya | `data/annotations/tigrinya/gold_morphemes.json` | `models/movoc_tok_merges_tigrinya.txt` | `data/vocabulary/bpe_tigrinya.json` (32,000) |
| Ge'ez | `data/annotations/geez/manual_morphemes.json` | absent | — |
| Tigre | `data/annotations/tigre/manual_morphemes.json` | absent | — |

For Table 3, `score_multiseed.py` records per cell: seed list, per-seed BLEU
and chrF++, checkpoint path, predictions path, both sacreBLEU signatures, and
the commit hash.

---

## 6. Remaining methodological differences from the paper

1. **Metric scale unresolved.** The paper's chrF++ is 40–75× its BLEU; both
   metrics here are 0–100. No comparison against Table 3 is possible in
   either direction.
2. **Scoring pipeline unrecovered.** The paper names BLEU and chrF++ but no
   implementation; this uses sacreBLEU 2.6.0 with recorded signatures.
3. **Seed count and values.** The paper says "multiple runs" without stating
   how many or which seeds; this uses exactly 42/43/44.
4. **Test-set sizes.** Released files hold Tigrinya 71 and Tigre 43 pairs
   against the paper's described 100; the human-validated top-ups are not in
   the repository.
5. **Ge'ez MT.** The paper's §4.2 states Ge'ez lacked parallel data yet
   Table 3 reports an En→Ge'ez block. Reconstructed here only as an
   additional zero-shot evaluation on a newly built split.
6. **Ge'ez/Tigre intrinsic arms missing.** No MoVoC-Tok tokenizer was
   trained for them.
7. **Held-out evaluation.** The paper's Table 2/4 item counts suggest
   full-set scoring; this scores held-out halves to remove leakage, so item
   counts are roughly half the released annotation sizes.
8. **Decoding parameters.** The paper states none; greedy (`num_beams=1`,
   `max_length=128`) is this repository's choice, held identical across arms.

---

## 7. Reproducibility statement

**Directly comparable to the paper:** nothing. No value in this document
should be compared numerically against a published MoVoC figure.

**Reconstructed but not identical:** Table 2 MorphScore (Amharic,
Tigrinya); Table 4 boundary precision and Rényi entropy (Amharic, Tigrinya).
Computed fresh from released annotations and reconstructed tokenizers, on
held-out data, with full provenance.

**Impossible to verify from available artifacts:** the published Table 3
figures and their ± values (scoring pipeline, predictions, checkpoints,
seeds and logs from the publication period are all absent); the published
En→Ge'ez block (no held-out Ge'ez set survives); the scale of the published
BLEU column; and Table 2/4 entries for Ge'ez and Tigre under MoVoC-Tok
(tokenizers never trained).
