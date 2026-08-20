# data/

- `raw/opus_en_ti/`, `raw/opus_en_am/` — downloaded OPUS zip/moses files.
  Gitignored. Populated by `scripts/prepare_opus_data.py`.
- `processed/en_ti/{train,validation,test}/`, `processed/en_am/{...}` —
  cleaned, filtered, split parallel text files, one sentence per line,
  `src.txt` / `tgt.txt`. Gitignored. Same examples are used for every
  tokenizer within a language pair — tokenization happens after this split,
  never before it.
- `manifests/en_ti.json`, `manifests/en_am.json` — **committed**. Small JSON
  files recording corpus name, source URL, retrieval date, split sizes,
  preprocessing steps and thresholds, and SHA256 checksums of the processed
  split files. No raw text is stored in these manifests.

The test split is never used for tokenizer selection or model training of
any kind; it is touched exactly once, after tokenizer selection, for the
selected tokenizer's final evaluation.
