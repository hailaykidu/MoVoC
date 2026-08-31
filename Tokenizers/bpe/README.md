# BPE tokenizer — external artifact pointer

This directory intentionally contains **no tokenizer files**. The BPE
tokenizers used by this comparison are pre-trained artifacts that live in the
`amseg` repository and are loaded read-only by absolute path.

| Language pair | Source path | Vocab size |
|---|---|---|
| en_ti | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_63051/` | 63051 |
| en_am | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_32k/` | 32000 |

Each source directory holds a standard HuggingFace `tokenizers`-format export
(`tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`).
Special tokens: `<pad>`=0, `<unk>`=1, `<s>`=2, `</s>`=3.

Do not copy these files into this repository. `src/marianmt_comparison/config.py`
and `configs/*.yaml` reference these absolute paths directly; loading is done
via `AutoTokenizer.from_pretrained(<absolute path>)` at run time.

The full, verified manifest (vocab size, special-token IDs, tokenizer
config, and sample tokenizations, all read live from disk) is written by
`scripts/verify_tokenizers.py` to `data/manifests/tokenizer_manifest.json`
(not committed by default since it is a generated artifact — regenerate it
by running the script).
