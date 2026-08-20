# WordPiece tokenizer — external artifact pointer

This directory intentionally contains **no tokenizer files**. The WordPiece
tokenizers used by this comparison are pre-trained artifacts that live in the
`amseg` repository and are loaded read-only by absolute path.

| Language pair | Source path | Vocab size |
|---|---|---|
| en_ti | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/wordpiece_63051/` | 63051 |
| en_am | `/homes/neumann/teklehaymanot/amseg/tokenizers/hf/wordpiece_32k/` | 32000 |

Each source directory holds a standard HuggingFace `tokenizers`-format export
(`tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`).
Special tokens follow the same pattern as BPE: `<pad>`=0, `<unk>`=1,
`<s>`=2, `</s>`=3.

Do not copy these files into this repository. Loaded via
`AutoTokenizer.from_pretrained(<absolute path>)` at run time. See
`tokenizers/bpe/README.md` for the manifest-generation note.
