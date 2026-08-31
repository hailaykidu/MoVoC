# amharic_movoc_tok_63050 — post-publication checkpoint

**A post-publication Amharic 63,050 MoVoC-Tok checkpoint generated using the
same Section 3.3 constrained-BPE methodology and training settings as the
existing `tigrinya_movoc_tok_63050` checkpoint.**

This is **not part of the original published experiments** (Tables 2, 3, and
4 are unaffected and unchanged by this artifact). It was created afterward
to give the en_am condition a genuine in-language 63k tokenizer, alongside
the existing cross-lingual-reuse setup documented in
`../../movoc_tok/README.md`.

## Provenance

- **Creation date**: 2026-09-01
- **Corpus**: `NLLB.am-en.am` (400,000 lines read, 158,504 word types, min_freq=2)
- **Morpheme source**: `amseg/data/segmented/amharic_morpheme_segmented.json`
  (10,293 records; 4,439 words with projected boundaries; same file used for
  the existing `amharic_movoc_tok_32k` checkpoint)
- **Vocab size**: 63,050 native / 63,051 HF export
- **Training procedure**: Section 3.3 constrained-BPE merge learning
  (`amseg/scripts/train_movoc_tok_bpe.py`), objective
  `max_V Σ log P(BPE(w_i; V, M_i)) s.t. no s_j crosses M_i`; 62,005 merges
  learned, 365,830 boundary-crossing merge candidates rejected;
  `shared_vocab: false` (per-language, matching the paper's per-language
  design — see `training_config.json`)
- **Training time**: 38.4 minutes, CPU-only, single process

## Verification performed

- `scripts/verify_movoc_tok.py` (run against the native checkpoint in
  `amseg/`): vocabulary size exactly 63,050 (PASS); 0% boundary violations,
  4,439/4,439 constrained words respected (PASS); lossless round-trip
  decoding, 2,000/2,000 (PASS)
- Structural field comparison against `tigrinya_movoc_tok_63050`'s
  `config.json`/`training_config.json`: identical field sets
- HF export (`../hf_exports/amharic_63050/`) loads via
  `AutoTokenizer.from_pretrained` and produces identical segmentation to the
  native checkpoint on held-out test words

## Files

```
config.json             method/vocab-size/special-token metadata
tokenizer.model          learned merges, boundary-constrained
tokenizer.vocab
training_config.json    full training provenance
provenance.json         checksums, comparison notes, this checkpoint's
                        distinction from the original published experiments
```

HF-format export: `../hf_exports/amharic_63050/`.

Do not retrain or modify. Do not use to regenerate Table 2, Table 3, or
Table 4 without an explicit, separate decision to do so.
