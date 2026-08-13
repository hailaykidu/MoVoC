# Invalid MT evaluation run — 2026-07-28

> **The numbers in this directory are not results.**
>
> They were produced by a broken generation configuration and measure that
> misconfiguration, not the tokenizers under test. They must not be quoted,
> summarised, or copied into Table 3, the README, or any other document.
>
> They are kept only as debugging evidence for the defect described below.

## What was attempted

An extrinsic evaluation of the eight fine-tuned MarianMT checkpoints
(4 tokenizer strategies × 2 languages), scoring BLEU and chrF++ on the OPUS
test sets, to regenerate Table 3.

The run was stopped after 7 of 16 directions once the outputs were
identified as invalid.

## Why the run is invalid

`evaluation/finetune_marianmt.py` resized the model's embedding matrix to
each new tokenizer's vocabulary, and updated `pad_token_id`,
`eos_token_id` and `decoder_start_token_id` — but left the remaining
vocabulary-dependent fields carrying ids inherited from the base
checkpoint, `Helsinki-NLP/opus-mt-en-ti`.

The base model ships `bad_words_ids: [[63049]]`, its own pad id. After
resizing, that id refers to nothing meaningful:

| Checkpoint | vocab_size | inherited `bad_words_ids` | effect |
|---|---|---|---|
| `mt_*_marian` | 63,050 | `[[63049]]` | valid — vocabulary unchanged |
| `mt_*_bpe` | 32,000 | `[[63049]]` | **out of range — `generate()` raises** |
| `mt_*_wordpiece` | 32,000 | `[[63049]]` | **out of range — `generate()` raises** |
| `mt_*_movoc_tok` | 143,963 | `[[63049]]` | in range but denotes an unrelated token, silently suppressed |

`forced_eos_token_id` was likewise inherited as `0` while the resized
tokenizers use `2`.

So the BPE and WordPiece arms crashed outright:

```
ValueError: The model vocabulary size is 32000, but the following tokens
were being biased: [63049]
```

and the MoVoC-Tok arm ran to completion while suppressing an arbitrary
token — scoring ~0.01 BLEU. **That figure is an artifact of the
misconfiguration.** It says nothing about MoVoC-Tok.

## A second, independent problem

The reverse directions (`am-en`, `ti-en`) scored ≈0 across every arm. The
base checkpoint is `Helsinki-NLP/opus-mt-en-ti`, a single-direction
English→Tigrinya model with no English decoder. Those eight evaluations
cannot yield meaningful numbers from these checkpoints regardless of the
configuration defect, and the evaluation protocol needs revisiting before
they are attempted again.

## Fix

`align_special_tokens()` in `evaluation/finetune_marianmt.py` now resets
every vocabulary-dependent field in one place after resizing, clears ids
that have no equivalent under the new vocabulary, and asserts that each
remaining id is within range — failing at setup rather than at generation
time.

Verified: the configuration that previously raised the error above now
generates successfully, and reverting the fix reproduces the crash exactly.

## Status of the checkpoints

The eight existing checkpoints were **trained** with the flawed
`generation_config` baked in. Re-running evaluation against them is not
sufficient; they must be retrained with the corrected script before any
Table 3 figure can be regarded as a reproduction.

Until then **Table 3 remains pending reproduction, with no numbers.**

## Contents

| File | What it is |
|---|---|
| `logs/amharic_bpe.log`, `logs/amharic_wordpiece.log` | tracebacks of the `ValueError` |
| `logs/*_marian.log`, `logs/*_movoc_tok.log` | runs that completed under the broken config |
| `logs/run_table3.log` | full run output, stopped at 7/16 |
| `*.json` | scorer output — **invalid**, retained for traceability |
| `run_table3.sh` | the runner used, kept so the run is reconstructible |
