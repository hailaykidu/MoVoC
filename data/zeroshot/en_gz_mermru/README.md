# data/zeroshot/en_gz_mermru/

Zero-shot **English → Ge'ez** evaluation set. 100 held-out sentence pairs.

| | |
|---|---|
| `source.txt` | English source, one sentence per line (100 lines) |
| `target.txt` | Ge'ez reference, one sentence per line (100 lines) |
| `upstream_manifest.json` | verbatim provenance manifest (held-out indices, checksums) |

## Provenance

- **Language pair:** English → Ge'ez
- **Purpose:** additional zero-shot MT evaluation. **Not** a reproduction of any
  published Table 3 Ge'ez block — the paper (§4.2) evaluates Ge'ez only
  intrinsically, due to the absence of parallel data.
- **Source:** the **Mermru English–Ge'ez parallel corpus** (<https://mermru.com/>).
  This is the origin of the sentence pairs.
- **How the file was obtained:** read from the `Bedru/Eng-Geez` dataset on the
  Hugging Face Hub — a download channel, not the source. Do not attribute the
  corpus to Bedru.
- **Size:** 100 pairs, sampled with `random.Random(42).sample` over the cleaned
  2,107-pair corpus. Selected indices are in `upstream_manifest.json`.
- **Checksums** (SHA256): `source.txt` `2c9e40e0…79692`, `target.txt` `e41cd2f8…4d61c`.

## Canonical location

This is a **copy**. The script-facing original is
`data/evaluation/geez/test.en` / `data/evaluation/geez/test.gez`, with its
manifest at `data/evaluation/geez/manifest.json`.

## Usage

Evaluation only. No Ge'ez text enters MT training, tokenizer training, or
vocabulary construction.
