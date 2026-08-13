# Reconstruction versus original: how to read the results in this repository

This repository contains two kinds of numbers. They look alike — both are
BLEU, chrF++, MorphScore, boundary precision over the same four languages —
and they are **not comparable**. This document explains what each is, where
it lives, and why they must be kept apart.

---

## 1. Original paper results

**What they are.** The values reported in *"MoVoC: Morphology-Aware Subword
Construction for Ge'ez Script Languages"* (Teklehaymanot, Fazlija & Nejdl),
Findings of EMNLP 2025, arXiv:[2509.08812](https://arxiv.org/abs/2509.08812)
— Table 2 (intrinsic) and Table 3 (translation).

**Where they are.** Quoted with citation in
[`README.md` §1](../README.md#1-published-movoc-paper-results), and in the
paper. There is **no original result file in this repository**; see
[`results/original_paper/README.md`](../../original/published_results/README.md).

**Their status.** They represent the **historical publication record**.

**What is missing.** The original checkpoints, the generated predictions,
and the scoring pipeline that produced these figures were **not recovered**.
The metric scale of the published BLEU column is also unresolved. Nothing in
this repository can regenerate them, and no run performed today can be shown
to follow the same procedure.

Because the artifacts are unavailable, the published values are treated as
**citations, not data**. They are never edited, never recomputed, and never
replaced with newer numbers.

## 2. Version 2 reconstruction results

**What they are.** New measurements produced by the current repository:
reimplemented code, the released vocabularies and tokenizers, newly trained
checkpoints, and a reconstructed evaluation pipeline.

Vocabularies were **not** rebuilt for Amharic or Tigrinya; those measurements
use the released artifacts. The only vocabularies constructed here are the
Ge'ez and Tigre verification arms, built from user-supplied corpora that are
not part of the MoVoC repository — see
[`../tokenizers/extended_arms_build_reconstruction_v2.json`](../tokenizers/extended_arms_build_reconstruction_v2.json).

**Where they are.** Working paths `evaluation/results/` and
`experiments/multiseed/results/`, with archival copies under
[`results/reconstruction_v2/`](../).

**Their status.** Internal validation evidence. They demonstrate that the
described method runs end to end — vocabulary construction, MoVoC-Tok
segmentation, MarianMT fine-tuning, BLEU/chrF++ scoring. They are **not**
corrected, updated, or verified versions of the published results, and they
**may differ from the original reported values**.

Every reconstructed file carries this in its own metadata: the intrinsic
tables include a `not_a_reproduction` field, and the multi-seed MT results
state *"Not a reproduction of the published Table 3."*

## 3. Why the two must not be merged

Four independent reasons. Any one would be sufficient.

**The scoring script is unavailable.** The decoding and metric-computation
procedure that produced Table 3 is not in this repository, nor are the
checkpoints and predictions it was run on. Two BLEU numbers computed by different pipelines
are not comparable even when both are labelled "BLEU" — tokenization,
smoothing and effective-order choices all move the figure.

**The BLEU scale is unresolved.** The published BLEU column's scale cannot
be established from available material. Reconstructed values use sacreBLEU
2.6.0 on a 0–100 scale with a recorded signature. A ratio between the two is
not meaningful.

**The MT reconstruction did not reach a converged regime.** The 18
multi-seed runs completed and decoded cleanly, but final training loss was
6.5–8.2 against roughly 1–3 for converged MT, output ran to `max_length`
without emitting EOS, and all 54 scores fell in the 0.005–0.041 BLEU noise
floor. These numbers characterise the reconstructed training setup rather
than tokenizer quality, and cannot be set against figures from a converged
run. See [`MT_Reconstruction_Audit.md`](../audits/mt_reconstruction_audit.md).

**The evaluation protocols differ.** The reconstructed intrinsic evaluation
scores a held-out half of each annotation set, because the original
`GOLD_SOURCES` pointed at the same files used to build the vocabularies for
Amharic, Ge'ez and Tigre. Held-out and in-sample scoring are different
measurements; the `_leaky` variant is retained precisely to show the gap.

## 4. Practical rules

- **Never place original and reconstructed values in the same table.**
  Report them in separate, explicitly labelled tables.
- **Never describe a reconstructed value as reproducing, confirming, or
  contradicting a published one.** The comparison is not available.
- **Never edit the published values** to match reconstructed output.
- **Always carry the provenance label** when quoting a number — either
  "published (arXiv:2509.08812)" or "reconstruction v2".
- **Do not read the MT reconstruction as evidence about MoVoC-Tok.** Because
  the reconstructed models did not converge, the rerun cannot isolate
  tokenizer effects in either direction — it neither supports nor
  contradicts the paper's findings.

## 5. Scope note

The MT reconstruction's limitations concern **extrinsic evaluation only**.
The intrinsic results (Tables 2 and 4 — MorphScore, boundary precision,
Rényi entropy) come from a separate pipeline that does not involve the MT
checkpoints, and stand or fall on their own evidence.

---

## See also

- [`results/README.md`](../README.md) — the archival layer and source-path mapping
- [`results/original_paper/README.md`](../../original/published_results/README.md) — why no original data file exists
- [`results/reconstruction_v2/README.md`](../README.md) — what the reconstruction produced
- [`MT_Reconstruction_Audit.md`](../audits/mt_reconstruction_audit.md) — full MT audit
- [`REPRODUCIBILITY.md`](../../docs/REPRODUCIBILITY.md) — what is and is not reproducible
