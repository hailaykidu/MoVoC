# MoVoC-Tok tokenizer — external artifact pointer

This directory intentionally contains **no tokenizer files**. The MoVoC-Tok
tokenizer used by this comparison is a pre-trained artifact that lives in the
`amseg` repository and is loaded read-only by absolute path.

| Language pair | Source path | Native vocab | HF export vocab | Notes |
|---|---|---|---|---|
| en_ti | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_63050_tigrinya/` | 63050 | 63051 | Trained on Tigrinya (`NLLB.en-ti.ti`) |
| en_am | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_63050_tigrinya/` (**reused, same path**) | 63050 | 63051 | **Cross-lingual reuse in the published results — see warning below** |

## Cross-lingual reuse warning (en_am condition, as actually run)

The MoVoC-Tok tokenizer used for the en_am condition **in this repository's
existing results (Table 3 as published)** is **the exact same
Tigrinya-trained tokenizer** used for en_ti. At the time those experiments
were run, there was no Amharic-trained MoVoC-Tok at 63k vocab. A 32k
Amharic-only MoVoC-Tok variant existed
(`amseg/tokenizers/hf/movoc_tok_32k_amharic/`) but was **rejected** in favor
of keeping vocab size uniform at 63051 across the en_ti/en_am MoVoC-Tok
conditions.

**Update:** a native Amharic 63,050 MoVoC-Tok checkpoint now exists —
`amseg/tokenizers/hf/movoc_tok_63050_amharic/`, preserved in this repository
at [`../movoc_tok_32k/amharic_63050/`](../movoc_tok_32k/amharic_63050/NOTE.md).
It was built **post-publication**, using the same Section 3.3 constrained-BPE
procedure as `tigrinya_movoc_tok_63050`, specifically to remove this
asymmetry going forward. It has **not** been used to rerun the en_am MT
experiments or regenerate Table 3 — doing so would require a new MarianMT
fine-tuning pass, which has not been done. Everything below in this warning
describes the tokenizer actually used to produce the **existing, published**
Table 3 numbers, which remains the Tigrinya-reused checkpoint.

`amharic_movoc_tok_63050` and `tigrinya_movoc_tok_63050` are closely
related: same paper method (Section 3.3 constrained-BPE), same script
(`train_movoc_tok_bpe.py`), same target vocabulary size (63,050), same
training settings otherwise, and a meaningful vocabulary overlap (8,583 of
63,050 tokens, 13.6%) from the two languages' shared Ge'ez script and
loanwords. They are two independently-trained instances of the same family
of tokenizer, one per language — not two unrelated artifacts. The only
factual point below is narrower: Table 3's *existing, published* numbers
were produced with the Tigrinya checkpoint applied to Amharic text, not
with `amharic_movoc_tok_63050` (which postdates those runs).

Per `amseg/tokenizers/tigrinya_movoc_tok_63050/training_config.json`, this
tokenizer's training corpus was exclusively
`NLLB.en-ti.ti` (`"shared_vocab": false` — no Amharic text was involved in
training). Applying it to Amharic text is genuinely out-of-domain: Amharic
uses the same Ge'ez script family as Tigrinya but a distinct vocabulary and
morphology, so expect **elevated fertility and/or UNK rate** relative to a
tokenizer actually trained on Amharic.

**A separate, genuinely shared Amharic+Tigrinya MoVoC vocabulary does
exist** in `amseg/` (`movoc/movoc_vocab.json`, 105,310 entries) — but it was
never built at 63k vocabulary size, and it does not feed this tokenizer or
any tokenizer used anywhere in this repository's Table 2/Table 3/Table 4
results. It belongs to a different, non-canonical pipeline
(`train_movoc_tok.py`: frequency-selection + greedy longest-match, not
constrained-BPE merge learning) that does not implement the paper's Section
3.3 MoVoC-Tok. See
[`../movoc_tok_alternative/README.md`](../movoc_tok_alternative/README.md)
for that pipeline's own provenance. Do not read "a shared MoVoC vocabulary
exists" as evidence that *this* 63k checkpoint is anything other than
Tigrinya-only — the two are unrelated artifacts that happen to share the
"MoVoC" name.

This is a **deliberate, user-approved experimental decision**, not an error.
It is recorded loudly and explicitly:

- The tokenizer manifest entry for `en_am/movoc_tok` includes
  `"cross_lingual_reuse": true` and a `"warning"` field with this exact text.
- `scripts/verify_tokenizers.py` computes and prints Amharic tokenization
  fertility and UNK rate for this tokenizer, and prints the warning — but
  does **not** fail or block the pipeline because of it.
- `configs/en_am.yaml` documents this in a comment next to the `movoc_tok`
  entry.

Do not "fix" the **existing, published** Table 3 by silently substituting
the 32k or the new post-publication 63k Amharic tokenizer into the recorded
results, and do not treat the resulting vocab-size non-uniformity in en_am
as a bug requiring correction — it is intentional and must remain visible in
all generated artifacts (manifest, configs, final report). Using the new
`amharic_movoc_tok_63050` checkpoint for a *new* en_am run is fine and is in
fact why it was built — just don't conflate that hypothetical future run
with the numbers already published here.
