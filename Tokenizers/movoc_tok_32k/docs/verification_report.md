# Verification report — MoVoC-Tok 32k self-contained copy

Verification performed at copy time, 2026-08-31.

## 1. Checkpoint identity confirmed as constrained-BPE (Section 3.3)

`amharic/config.json` and `tigrinya/config.json`:
`"method": "morpheme-aware BPE (boundary-constrained merges)"`.

`amharic/training_config.json` and `tigrinya/training_config.json`:
`"objective": "max_V sum_i log P(BPE(w_i; V, M_i)) s.t. no s_j crosses M_i"`.

Confirmed against `docs/movoc_tok_report.md`, whose "Artifacts" section
names exactly these two checkpoints. Confirmed distinct from the
frequency-selected greedy longest-match design (`amseg/tokenizers/movoc_tok_32k`),
which uses a different `config.json` schema (`"segmentation": "greedy
longest-match"`, `"selection_policy": ...`) and is not part of this copy.

## 2. File integrity — checksum comparison, copy vs. source

All 22 copied files verified byte-identical (MD5) against their `amseg/`
source:

- `amharic/{config.json, tokenizer.model, tokenizer.vocab, training_config.json}` (4)
- `tigrinya/{config.json, tokenizer.model, tokenizer.vocab, training_config.json}` (4)
- `hf_exports/amharic/{tokenizer.json, tokenizer_config.json, special_tokens_map.json}` (3)
- `hf_exports/tigrinya/{tokenizer.json, tokenizer_config.json, special_tokens_map.json}` (3)
- `vocabulary_construction/{amharic,tigrinya}_morpheme_segmented.json` (2)
- `constrained_bpe/{train_movoc_tok_bpe.py, verify_movoc_tok.py, export_hf_tokenizers.py}` (3)
- `docs/movoc_tok_report.md` (1)

Result: **all checksums matched**, no mismatches.

## 3. Tokenizer load and segmentation verification

Both `hf_exports/amharic` and `hf_exports/tigrinya` load successfully via
`transformers.AutoTokenizer.from_pretrained` (vocab_size=32001 each,
including the 4 special tokens). Segmentation compared word-for-word
against the original `amseg/tokenizers/hf/movoc_tok_32k_{amharic,tigrinya}`
sources on 4 held-out test words per language:

| Language | Word | Source segmentation | Copy segmentation | Match |
|---|---|---|---|---|
| Amharic | የኦነግ | `▁የኦ`, `ነግ` | `▁የኦ`, `ነግ` | Yes |
| Amharic | አክራሪነት | `▁አክ`, `ራሪ`, `ነት` | `▁አክ`, `ራሪ`, `ነት` | Yes |
| Amharic | ኢትዮጵያ | `▁ኢትዮጵያ` | `▁ኢትዮጵያ` | Yes |
| Amharic | መንግስት | `▁መንግስት` | `▁መንግስት` | Yes |
| Tigrinya | ሰላማዊ | `▁ሰላማዊ` | `▁ሰላማዊ` | Yes |
| Tigrinya | ኣይናቱን | `▁ኣይና`, `ቱን` | `▁ኣይና`, `ቱን` | Yes |
| Tigrinya | ኣይመፀን | `▁ኣይመ`, `ፀን` | `▁ኣይመ`, `ፀን` | Yes |
| Tigrinya | ጉቦኛ | `▁ጉቦ`, `ኛ` | `▁ጉቦ`, `ኛ` | Yes |

Result: **all 8 test words segment identically**, copy loads and behaves
identically to source.

## 4. Vocabulary and merge-rule preservation

Vocabulary and merge rules are embedded in `tokenizer.model`/`tokenizer.vocab`
(native) and `tokenizer.json` (HF export); checksummed identical to source
(item 2) and confirmed to produce identical output (item 3) — no separate
merge-rule extraction was necessary or performed.

## Conclusion

The copied assets in `movoc_tok_32k/` are confirmed to correspond to the
constrained-BPE MoVoC-Tok implementation described in Section 3.3 of the
published paper, are byte-identical to their `amseg/` sources, and are
functionally verified to load and segment identically. Nothing was
retrained, regenerated, or modified.
