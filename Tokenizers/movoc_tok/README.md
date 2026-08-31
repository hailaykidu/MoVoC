# MoVoC-Tok tokenizer — external artifact pointer

This directory intentionally contains **no tokenizer files**. The MoVoC-Tok
tokenizer used by this comparison is a pre-trained artifact that lives in the
`amseg` repository and is loaded read-only by absolute path.

| Language pair | Source path | Native vocab | HF export vocab | Notes |
|---|---|---|---|---|
| en_ti | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_63050_tigrinya/` | 63050 | 63051 | Trained on Tigrinya (`NLLB.en-ti.ti`) |
| en_am | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_63050_tigrinya/` (**reused, same path**) | 63050 | 63051 | **Cross-lingual reuse — see warning below** |

## Cross-lingual reuse warning (en_am condition)

The MoVoC-Tok tokenizer used for the en_am condition is **the exact same
Tigrinya-trained tokenizer** used for en_ti. There is no Amharic-trained
MoVoC-Tok at 63k vocab. A 32k Amharic-only MoVoC-Tok variant does exist
(`amseg/tokenizers/hf/movoc_tok_32k_amharic/`) but was **rejected** in favor
of keeping vocab size uniform at 63051 across the en_ti/en_am MoVoC-Tok
conditions.

Per `amseg/tokenizers/tigrinya_movoc_tok_63050/training_config.json`, this
tokenizer's training corpus was exclusively
`NLLB.en-ti.ti` (`"shared_vocab": false` — no Amharic text was involved in
training). Applying it to Amharic text is genuinely out-of-domain: Amharic
uses the same Ge'ez script family as Tigrinya but a distinct vocabulary and
morphology, so expect **elevated fertility and/or UNK rate** relative to a
tokenizer actually trained on Amharic.

This is a **deliberate, user-approved experimental decision**, not an error.
It is recorded loudly and explicitly:

- The tokenizer manifest entry for `en_am/movoc_tok` includes
  `"cross_lingual_reuse": true` and a `"warning"` field with this exact text.
- `scripts/verify_tokenizers.py` computes and prints Amharic tokenization
  fertility and UNK rate for this tokenizer, and prints the warning — but
  does **not** fail or block the pipeline because of it.
- `configs/en_am.yaml` documents this in a comment next to the `movoc_tok`
  entry.

Do not "fix" this by silently substituting the 32k Amharic tokenizer, and do
not treat the resulting vocab-size non-uniformity in en_am as a bug requiring
correction — it is intentional and must remain visible in all generated
artifacts (manifest, configs, final report).
