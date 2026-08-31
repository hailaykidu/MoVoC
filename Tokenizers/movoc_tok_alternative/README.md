# MoVoC-Tok (alternative pipeline) — NOT the paper's Section 3.3 tokenizer

**Status: historical / not canonical.** This directory is preserved for
provenance only. It is **not** used by Table 2, Table 4, Table 3, or any
evaluation script in this repository. The canonical MoVoC-Tok tokenizer is
[`../movoc_tok_32k/`](../movoc_tok_32k/README.md).

## What this is

A second, earlier tokenizer-construction pipeline exists in `amseg/`, under
the same base directory name (`tokenizers/movoc_tok_32k`) as the canonical
checkpoints, but built by different code:

| | This (alternative) pipeline | Canonical pipeline (`../movoc_tok_32k/`) |
|---|---|---|
| Script | `train_movoc_tok.py` | `train_movoc_tok_bpe.py` |
| Algorithm | Selects tokens from a pre-built shared vocabulary pool by frequency; segments by greedy longest-match against the fixed result | Learns BPE merges directly, rejecting any merge that would cross a morpheme boundary |
| Vocabulary source | `shared_vocabulary_construction/movoc_vocab.json` — a combined Amharic+Tigrinya pool (105,310 entries: BPE pieces + morphemes from both languages, deduplicated) | Independent, per-language: each language's own corpus + own morpheme file, no cross-language pooling |
| `amseg/` build order | Built first (00:31) | Built ~40 minutes later the same day (00:31 Amharic / 01:09–01:11) |

## Why this is not Section 3.3's MoVoC-Tok

The paper's Section 3.3 describes MoVoC-Tok as:

> "a constrained-merge BPE: a merge may never cross a morpheme boundary...
> Within each morpheme, merges proceed by the usual BPE ranking, so the
> tokenizer remains a deterministic, greedy, linear-time segmenter."

This is a description of constrained **merge learning** — BPE's iterative
pair-merging procedure, restricted by a per-word boundary constraint at
every step. `train_movoc_tok.py`'s algorithm does not learn merges at all:
it picks whole tokens (already-formed BPE pieces and morphemes) out of a
fixed candidate pool by descending frequency, then tokenizes new text by
greedy longest-match against that fixed selection. No merge operations are
performed or restricted during this process — it is vocabulary
*selection*, not constrained BPE training.

`build_movoc_vocab.py`'s own `vocabulary_report.md` (copied here under
`shared_vocabulary_construction/`) describes its allocation procedure as
implementing "MoVoC Algorithm 1 (paper Sec. 3.2)" with `N = 2` (Amharic,
Tigrinya) sharing one combined budget. The paper's actual Section 3.2 text
(`s_lang = s / 2`, `s_morpheme = s_lang × r`, `s_BPE = s_lang × (1 − r)`)
describes a per-language morpheme/BPE split ratio, not a formula for
pooling two languages' vocabularies into one shared budget — that
cross-language framing in the report is this pipeline's own interpretation,
not a reading directly supported by the paper's Section 3.2 formula.

## Contents

```
config.json                          the alternative movoc_tok_32k's own metadata
                                      (segmentation: "greedy longest-match",
                                      selection_policy: frequency-ranked)
vocab.json, vocab.txt                the selected 32,000-token vocabulary
shared_vocabulary_construction/
  movoc_vocab.json                   the shared Amharic+Tigrinya candidate
                                      pool this vocabulary was selected from
                                      (105,310 entries)
  vocabulary_report.md               that pool's own composition report
  build_movoc_vocab.py               the script that built movoc_vocab.json
  train_movoc_tok.py                 the script that selected vocab.json/
                                      vocab.txt from movoc_vocab.json
```

All files copied unmodified from `amseg/`, checksummed byte-identical to
source at copy time. Nothing here was retrained, regenerated, or altered,
and this directory is not read by any script elsewhere in this repository.

Do not present this pipeline as equivalent to, or a variant of, the
canonical MoVoC-Tok in `../movoc_tok_32k/` — it implements a different
algorithm and is not what the paper's Section 3.3 describes.
