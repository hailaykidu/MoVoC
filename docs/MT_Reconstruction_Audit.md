# MT Reconstruction Audit

**Date:** 2026-07-31
**Scope:** multi-seed extrinsic (machine translation) evaluation
**Inner repository HEAD at scoring time:** `ebd5b8e3`

## Purpose

This is a **reproducibility and reconstruction report** for the Version 2
verification release. Its aim is to document what the current repository can
rebuild from the published methodology, and to record the behaviour observed
when that reconstruction is run end to end.

It is **not** a critique, correction, or re-evaluation of the published
paper. The MoVoC paper's scientific contribution — morphology-aware subword
construction for Ge'ez-script languages, together with the morpheme-annotated
datasets and the MoVoC-Tok segmentation method — stands on its published
evidence. Nothing in this document revises, disputes, or supersedes it.

## Summary

The published training configuration and experimental design were
reconstructed faithfully: 18 runs across 2 languages × 3 tokenizers × 3
seeds, all completing training and decoding without error. **The pipeline
reconstruction succeeded.**

The reconstructed models did not reach a converged translation regime, so
this rerun **cannot conclusively rank tokenizers**. That is a limitation of
what could be rebuilt from the available artifacts, not a finding about the
proposed method.

Numerical differences from the published values are **expected**. The
original checkpoints, logs, predictions and scoring pipeline were not
recovered, and the scale of the published BLEU column is unresolved. The
values reported here are **Version 2 verification results** — new
measurements from a reconstructed pipeline — and are not a replacement for,
or a reproduction of, the published Table 3.

---

## How to read this report

Three categories of material appear below, and they are kept separate
throughout.

| | Category | Status |
|---|---|---|
| **1** | **Original published results** | The historical record. Reported in the paper (Table 2 intrinsic, Table 3 translation) and cited in [`README.md` §1](../README.md#1-published-movoc-paper-results). Not reproducible here, because the original checkpoints, predictions, logs and scoring pipeline were not recovered. Treated as citation, never edited or recomputed. |
| **2** | **Version 2 reconstruction results** | New measurements from the current reimplemented code and newly trained checkpoints, following the published methodology and experimental design. Verification evidence for this release. **Not a replacement for, correction to, or reproduction of the published values.** Differences are expected. |
| **3** | **Open questions** | Items that cannot be settled from within this repository because they depend on original execution artifacts. See §6. |

Full rationale for keeping categories 1 and 2 apart:
[`reconstruction_vs_original.md`](reconstruction_vs_original.md).

## 1. Repository state

Two files changed, both evaluation-only:

| File | Change |
|---|---|
| `scripts/score_multiseed.py` | `generation_ids_valid()` no longer rejects on `bad_words_ids` |
| `scripts/make_tables.py` | +91/−8: reader for the aggregate multi-seed schema |

**Generated artifacts (56):**

- `experiments/multiseed/results/table3_multiseed.json` — 53,478 B,
  md5 `fc12315d47761458847aca7c6e6abe40`, generated `2026-07-31T07:48:13Z`
- `experiments/multiseed/predictions/*.txt` — 54 files
- `evaluation/results/RESULTS.md` — regenerated

**Unchanged, verified:** all 18 checkpoints, every `generation_config.json`,
every `model.safetensors`, training code, scoring logic, metric computation,
and the intrinsic results (`paper_tables.json`, `intrinsic_eval.json`).

No commits were made and no training jobs were launched.

Note that `movoc/` is a nested git repository with independent history.
`score_multiseed.py` resolves `ROOT` to its own parent, so the commit
recorded in `table3_multiseed.json` is the inner repository's HEAD.

## 2. MT reconstruction

The experimental design follows the paper's Sec. 4.3: MarianMT fine-tuned on
the NLLB English–Amharic and English–Tigrinya parallel corpora, comparing
the MoVoC vocabulary against BPE and WordPiece baselines, with the reported
training configuration (3 epochs, batch size 8, max sequence length 128,
learning rate 1.44e-07, linear decay). The multi-seed extension — three
seeds per arm, so that each reported figure carries a standard deviation —
is an addition of this release, not a departure from the published design.

18 experiments: 2 training languages (Amharic, Tigrinya) × 3 tokenizers
(BPE, WordPiece, MoVoC-Tok) × 3 seeds (42, 43, 44). Slurm jobs 55314–55331,
all COMPLETED, 4.5–7.2 h each, finishing 2026-07-31 09:07.

Each checkpoint was evaluated on its supervised direction plus two zero-shot
languages (Tigre, Ge'ez), giving **54 decode passes**. Test sets: Amharic
n=100, Tigrinya n=71, Tigre n=43, Ge'ez n=100. Greedy decoding
(`num_beams=1`, `max_length=128`). sacreBLEU 2.6.0 — BLEU
`nrefs:1|case:mixed|eff:no|tok:13a|smooth:exp`, chrF++ `nc:6|nw:2`.

Final table: `experiments/multiseed/results/table3_multiseed.json`,
rendered into `evaluation/results/RESULTS.md`. 18 cells, all reported at
3 seeds, 0 excluded.

## 3. Evaluation validation

### The validator fix

`generation_ids_valid()` rejected any checkpoint whose serialized
`bad_words_ids` fell outside its vocabulary. Seven checkpoints carry the
base model's inherited `[[63049]]`; against a 32,000-token BPE or WordPiece
vocabulary that id is out of range, so **6 of 18 runs were excluded** before
decoding.

### Why the change is evaluation-only

`translate()` calls `align_special_tokens()` at load time, which sets
`bad_words_ids = None` before a single token is generated. The rejected
field never reaches `generate()`: it is a dead value in a saved config, not
a decoding fault. The validator was excluding runs whose weights are sound.

It could not catch the inverse case either. The two `movoc_tok` seed-42
checkpoints carry the same stale id, which passes validation silently
because 63049 < 144,417 while denoting an unrelated token. Clearing the
field at load time handles both directions; validating the serialized field
handles neither.

Retained checks: `pad_token_id`, `eos_token_id`, `decoder_start_token_id`,
`forced_eos_token_id`, `bos_token_id` — the ids that actually determine
correct decoding.

Result: 12/18 → **18/18 usable, 0 excluded**, 0 errors across 54 passes.

### Checkpoints untouched

Verified by modification time rather than assumed: zero
`generation_config.json` and zero `model.safetensors` files were modified
after scoring began. The newest checkpoint file is 09:07 (the final training
job); scoring ran 09:18–09:48.

## 4. Observed training and evaluation behaviour

Reported transparently, as the record of what this reconstruction produced.

### What the reconstruction established

The published methodology and experimental design were successfully
rebuilt. Vocabulary construction, MoVoC-Tok segmentation, MarianMT
fine-tuning, checkpoint serialization, and BLEU/chrF++ scoring all run end
to end. All 18 runs completed their full training schedule, and all 18
checkpoints decoded without error across 54 evaluation passes. The
experimental *design* — 2 languages × 3 tokenizers × 3 seeds, supervised
plus zero-shot directions — reproduces the structure described in the paper.

### Training dynamics

All 18 runs reached `global_step == max_steps` at 3.0/3.0 epochs —
structurally complete by every check the validator performs. All share
`peak_lr = 1.44e-07`, `warmup_steps: 0`, and linear decay to `4.67e-12`.

### Loss trajectory

Quartiles for `amharic_bpe_seed42`:

    13.35 → 8.27 → 8.20 → 8.15 → 8.16

Nearly all movement occurs in the first quartile; the final 75% of training
moves loss by 0.11. Final losses span 6.5–8.2 across all runs, against
roughly 1–3 for converged MT. Seed variance is ±0.02.

### Decoding behavior

Decoding is mechanically correct — valid Amharic and Tigrinya script,
plausible tokens, correct special-token wiring — but the output is
repetitive and characteristic of an unconverged model:

| Measure | Hypotheses | References |
|---|---|---|
| Mean length | 155.1 chars | 11.6 chars |
| Most-frequent character | ~50% of output | — |
| Unique-token ratio | ~4% | — |

Models run to `max_length` without emitting EOS. For example
`ይህ ነው ነው።።።።።።።።።።።።።` against the reference `ስሜ ጀክ ነው።`.

### Why this rerun cannot rank the tokenizers

All 54 passes fall in BLEU 0.0053–0.0411 and chrF++ 0.53–2.91 — the noise
floor. Standard deviations are small (max 0.0013 BLEU) and look clean, but
that tightness reflects three seeds behaving *consistently* within the same
unconverged regime: it indicates reproducibility of the run, not resolving
power of the measurement.

The decisive evidence is that `amharic_movoc_tok` seeds 42, 43 and 44 have
distinct weight checksums and distinct prediction files, yet produce BLEU
identical to four decimal places (0.0053). The metric has no signal left to
resolve. Between-arm separations reflect how repetitive output interacts
with n-gram matching, not translation quality.

Any tokenizer comparison requires models that first reach a converged
translation regime. Because these did not, **the rerun is inconclusive on
tokenizer ranking in either direction** — it neither supports nor
contradicts the paper's Table 3 findings, which rest on their own
experimental evidence.

## 5. MoVoC-Tok interpretation

**This MT rerun alone supports no claim about MoVoC-Tok in either
direction.**

Within the reconstructed run, no tokenizer separated measurably from the
others. Because none of the systems reached a converged translation regime,
the rerun **cannot isolate tokenizer effects on translation performance** —
the reconstruction never placed any system in a position to demonstrate one.
This is a limitation of the reconstruction, not an observation about the
proposed method.

Readers should not infer that BPE "outperformed" MoVoC-Tok from its higher
raw scores (0.0290 versus 0.0053 on supervised Amharic); those separations
are artifacts of unconverged output, per §4. Equally, nothing here should be
read as evidence against the paper's reported Table 3 results, which rest on
experimental artifacts this repository does not hold.

The paper's central claims about MoVoC-Tok remain supported by its own
published evidence, and by the intrinsic evaluation, which is unaffected by
this rerun (see the scope note below).

**Observation, offered without interpretation.** MoVoC-Tok checkpoints
reached lower final training loss (mean 6.654) than WordPiece (7.935) and
BPE (8.074), consistently across all six runs. Loss is not comparable across
different vocabularies — these tokenizers have different vocabulary sizes
(144k versus 32k) and therefore different per-token entropy baselines. This
is recorded as an observation only and should **not** be read as evidence of
tokenizer quality.

**Scope.** These conclusions concern extrinsic MT evaluation only. The
intrinsic results (Tables 2 and 4 — MorphScore, boundary precision, Rényi
entropy) come from a separate pipeline that does not involve these
checkpoints and are unaffected by this audit.

## 6. Open questions requiring additional original artifacts

Each item below is open because material from the original experimental run
is unavailable — not because anything in the published work is in doubt.
Access to the original artifacts would likely resolve all of them.

### Optimization schedule — a separate diagnostic experiment

The learning rate `1.44e-07` is transcribed faithfully from the paper's
Sec. 4.3, and `experiments/tokenizer_comparison/configs/learning_rate_verification.json`
records a deliberate check (2026-07-29) that confirmed the rate and declined
to change it. **This is not a repository implementation error**, and the
value is applied exactly as published.

The open question is what *surrounding* configuration accompanied it in the
original run. A fine-tuning rate of this magnitude behaves very differently
depending on schedule length, warmup, effective batch size, gradient
accumulation, and the state of the starting checkpoint — details that a
paper's experimental section would not normally enumerate in full. The
reconstruction supplies its own defaults for these (`warmup_steps: 0`,
linear decay, batch 8, no accumulation, 3 epochs), and those defaults are
almost certainly where the reconstruction and the original run diverge.

Distinguishing the possibilities requires the original training logs or
configuration files. This belongs to a separate diagnostic experiment and
was deliberately not undertaken here.

### Comparison with the published Table 3

Not currently possible, for reasons independent of either result set: the
original scoring pipeline is unavailable, so no run performed now can be
shown to follow the same procedure, and the scale of the published BLEU
column cannot be established from available material. Recovering the
original scoring code or predictions would be the prerequisite.

### A converged reconstruction

A reconstruction that reaches a converged translation regime would allow the
tokenizer comparison this rerun could not perform. That requires resolving
the optimization-schedule question above, and is future work rather than a
correction to anything.

---

## Reproducing this audit

```bash
python scripts/score_multiseed.py --dry-run   # 18/18 usable
python -u scripts/score_multiseed.py          # 54 passes → table3_multiseed.json
python scripts/make_tables.py                 # → evaluation/results/RESULTS.md
```
