# MoVoC-Tok 32k — canonical constrained-BPE assets (self-contained copy)

This directory is a **complete, self-contained local copy** of the canonical
MoVoC-Tok tokenizer assets (Section 3.3 method: BPE merge learning restricted
so no merge crosses a morpheme boundary), for use by Table 2, Table 4, and
future intrinsic/extrinsic reproduction work. It supersedes the earlier
read-only pointer-only convention: the actual files now live here.

All files were **copied unmodified** from `amseg/` and verified byte-identical
by checksum; nothing was retrained, regenerated, or altered. See
[`docs/verification_report.md`](docs/verification_report.md) for the full
verification record.

## Verified identity

`amharic/config.json` and `tigrinya/config.json` each state
`"method": "morpheme-aware BPE (boundary-constrained merges)"`, and
`training_config.json` in both states the exact constrained objective:

```
max_V  sum_i log P(BPE(w_i; V, M_i))
subject to: no subword s_j crosses a morpheme boundary in M_i
```

This is the constrained-BPE MoVoC-Tok methodology (Section 3.3), confirmed
against `docs/movoc_tok_report.md` (the original training report). It is
**not** the earlier frequency-selected greedy longest-match design
(`amseg/tokenizers/movoc_tok_32k`, a superseded iteration built earlier the
same day) — that variant is deliberately excluded from this copy.

## Directory structure

```
movoc_tok_32k/
├── amharic/                  native constrained-BPE checkpoint (Amharic)
│   ├── tokenizer.model       learned merges, boundary-constrained
│   ├── tokenizer.vocab
│   ├── config.json           method/vocab-size/special-token metadata
│   └── training_config.json  full training provenance (objective, corpus,
│                              constraint counts, timing)
├── tigrinya/                 native constrained-BPE checkpoint (Tigrinya)
│   └── (same file set as amharic/)
├── hf_exports/
│   ├── amharic/               movoc_tok_32k_amharic, HuggingFace format
│   │   └── tokenizer.json, tokenizer_config.json, special_tokens_map.json
│   └── tigrinya/               movoc_tok_32k_tigrinya, HuggingFace format
│       └── (same file set)
├── vocabulary_construction/   morpheme-analysis inputs that produced the
│                              boundary constraints used during training
│   ├── amharic_morpheme_segmented.json
│   └── tigrinya_morpheme_segmented.json
├── constrained_bpe/            the implementation itself
│   ├── train_movoc_tok_bpe.py  constrained-BPE training (self-contained;
│   │                           constraint loading, corpus reading, the
│   │                           constrained merge-learner class, training
│   │                           loop, boundary projection via difflib)
│   ├── verify_movoc_tok.py     boundary-compliance / round-trip verification
│   └── export_hf_tokenizers.py native-checkpoint -> HuggingFace export
└── docs/
    ├── movoc_tok_report.md          original training report (both languages)
    └── verification_report.md       this copy's integrity/load verification
```

There is no separate `merges/` directory: the constrained-BPE model's merge
rules are embedded directly in `tokenizer.model`/`tokenizer.vocab` (native
format) and `tokenizer.json` (HF format) — there is no standalone
`merges.txt`, unlike a plain BPE tokenizer.

## Scope: what is and is not included

**Included** (everything needed to load, verify, and understand how these
two tokenizers were built):
- both native checkpoints and both HF exports, in full
- the morpheme-annotation files that supplied boundary constraints during
  training
- the complete constrained-BPE training/verification/export implementation
- the original training report

**Not included** (out of scope — large, generic, or not MoVoC-specific):
- the raw training corpora (`NLLB.am-en.am`, `NLLB.en-ti.ti`, 400,000 lines
  each) — see `training_config.json` in each checkpoint dir for their exact
  source paths; these are large, general-purpose parallel-data files, not
  tokenizer-specific artifacts
- checkpoints, logs, or caches from unrelated experiments
- the superseded frequency-selected tokenizer design

## Scope of use

Canonical for:
- Table 2 (`Intrinsic_Evaluation/reports/table2_final.md`)
- Table 4 (`Intrinsic_Evaluation/reports/table4_final.md`)
- MarianMT extrinsic evaluation
- future intrinsic/extrinsic reproduction experiments

Distinct from the separate 63,051-vocabulary MoVoC-Tok checkpoint used by
this repository's own MT pipeline (`en_am`/`en_ti` conditions — see
`../movoc_tok/README.md`), which is a larger, Tigrinya-only tokenizer reused
cross-lingually for Amharic by deliberate experimental decision. Do not
conflate the two.

Do not retrain or modify any of these files.
