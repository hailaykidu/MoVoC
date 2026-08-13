# Original paper results

**This directory contains no result files, and that is deliberate.**

## Where the published results are

The MoVoC paper's reported values are printed in the publication and cited
in this repository in exactly one place:

- [`README.md` §1 — "Published MoVoC paper results"](../../README.md#1-published-movoc-paper-results),
  which reproduces the paper's Table 3 as a cited quotation.
- The paper itself: Teklehaymanot, Fazlija & Nejdl, *"MoVoC:
  Morphology-Aware Subword Construction for Ge'ez Script Languages"*,
  Findings of EMNLP 2025, arXiv:[2509.08812](https://arxiv.org/abs/2509.08812).

The paper reports intrinsic results in Table 2 and translation results in
Table 3.

## Why there is no data file here

The original experimental artifacts were **not recovered**. The checkpoints,
generated predictions and scoring pipeline that produced the published
figures are not preserved in this repository. The metric scale of the
published BLEU column is also unresolved.

A `table3_original.json` was therefore **deliberately not created**. Any such
file could only be assembled by transcribing numbers out of the paper by
hand. A hand-copied JSON sitting beside genuine machine-generated output
invites exactly the confusion this directory exists to prevent: it would
look like recovered original experiment output when it is nothing of the
kind.

The published values remain where they belong — in the paper, and quoted
with citation in the top-level README.

## What this means in practice

- The published numbers represent the **historical publication record**.
  They are not reproducible from this repository.
- They must not be edited, "corrected", or replaced with reconstructed
  values.
- They must not be placed in the same table as reconstructed values.

See [`v2/reports/reconstruction_v2_summary.md`](../../v2/reports/reconstruction_v2_summary.md)
for the full rationale, and [`v2/`](../../v2/)
for what this repository *can* generate.
