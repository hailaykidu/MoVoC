# Introduction — notes

## Motivation

Ge'ez-script languages (Amharic, Tigrinya, Tigre, Ge'ez) are morphologically
rich: a single orthographic word carries prefixes, a root, optional infixes,
suffixes and clitics. Standard subword tokenizers are trained on frequency
statistics alone and place boundaries inside morphemes, so a token can straddle
a prefix–root or root–suffix join.

These languages are also low-resource, with limited morphological annotation
available for supervised segmentation.

## Contributions

1. **MoVoC** — a hybrid vocabulary construction method allocating half the budget
   to morpheme types and half to BPE merges.
2. **MoVoC-Tok** — a constrained-merge tokenizer in which no merge crosses a
   morpheme boundary.
3. **Morpheme-annotated datasets** for four Ge'ez-script languages, 169,806
   records in total.
4. **Intrinsic and extrinsic evaluation** using boundary precision, MorphScore,
   Rényi entropy, and English→X MarianMT translation.

## Framing

The abugida writing system is central: one Ethiopic character encodes a
consonant–vowel pair, so morphological structure and orthographic units do not
align one-to-one. This motivates morphology-aware vocabulary construction rather
than purely statistical subword induction.

## Reference

Original paper: Teklehaymanot, Fazlija & Nejdl, *MoVoC: Morphology-Aware Subword
Construction for Ge'ez Script Languages*, Findings of EMNLP 2025,
arXiv:2509.08812.
