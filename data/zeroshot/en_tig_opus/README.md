# data/zeroshot/en_tig_opus/

Zero-shot **English → Tigre** evaluation set. 43 sentence pairs.

| | |
|---|---|
| `source.txt` | English source, one sentence per line (43 lines) |
| `target.txt` | Tigre reference, one sentence per line (43 lines) |

## Provenance

- **Language pair:** English → Tigre
- **Purpose:** zero-shot MT evaluation — Tigre is not in MoVoC vocabulary
  construction, MT fine-tuning, or MoVoC-Tok training.
- **Source:** OPUS / Tatoeba (Tiedemann, 2012).
- **Size:** 43 usable parallel pairs, from 45 raw English–Tigre lines.

### On the count

The MoVoC evaluation manifest (`data/evaluation/manifest.json`) records
`raw_lines: 45`, `usable_opus_pairs: 43`, `target_pairs: 100` (an unmet goal),
`human_validated_needed: 57`. The 100-pair target was never reached for Tigre;
43 is the full set present and used for the reported numbers. Any "60"-pair
figure in earlier drafts corresponds to no released file.

## Canonical location

This is a **copy**. The script-facing original is
`data/evaluation/tigre/test.en` / `data/evaluation/tigre/test.tig`.

## Usage

Evaluation only. No Tigre text enters MT training, tokenizer training, or
vocabulary construction. The Table 3 MarianMT models are fine-tuned on the
OPUS NLLB English–Amharic / English–Tigrinya corpus only (Costa-Jussà et al.,
2022); Tigre is a zero-shot direction.
