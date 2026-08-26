# Abstract — draft notes

## Elements

1. **Problem.** Ge'ez-script languages are morphologically rich; standard subword
   methods split inside morphemes.
2. **Method.** MoVoC allocates half the vocabulary budget to morpheme types and
   half to BPE merges; MoVoC-Tok segments under the constraint that no merge
   crosses a morpheme boundary.
3. **Resource.** Morpheme annotations for four Ge'ez-script languages —
   Amharic, Tigrinya, Tigre, Ge'ez.
4. **Evaluation.** Intrinsic (boundary precision, MorphScore, Rényi entropy) and
   extrinsic (English→X MarianMT).
5. **Result.** MoVoC-Tok attains the highest morpheme boundary precision and
   MorphScore in three of four languages, with a near-tie against BPE on the
   fourth (Ge'ez).

## Draft

> Ge'ez-script languages are morphologically rich, and standard subword
> tokenizers routinely place boundaries inside morphemes. We present MoVoC, a
> morphology-aware vocabulary construction method that reserves half its budget
> for morpheme types recovered by supervised analysis and half for BPE merges,
> together with MoVoC-Tok, a constrained-merge tokenizer in which no merge may
> cross a morpheme boundary. We release morpheme annotations for Amharic,
> Tigrinya, Tigre and Ge'ez. Evaluated intrinsically with morpheme boundary
> precision, MorphScore and Rényi entropy, and extrinsically on English→X
> translation, MoVoC-Tok attains the highest morpheme boundary precision and
> MorphScore in three of four languages, with a near-tie against BPE on the
> fourth.

## Numbers available for the abstract

- Boundary precision: MoVoC-Tok higher in Amharic (0.3208 vs 0.3170), Tigrinya
  (0.3242 vs 0.3142), Tigre (0.5629 vs 0.5380); near-tie on Ge'ez (0.4301 vs
  0.4326, BPE ahead)
- MorphScore: MoVoC-Tok higher in Amharic (0.4139), Tigrinya (0.4366), Tigre
  (0.5278); BPE narrowly ahead on Ge'ez (0.6667 vs 0.6561)
- Datasets: 169,806 annotated records across four languages
- Rényi entropy is no longer part of the headline claim — WordPiece, not
  MoVoC-Tok, has the lowest entropy in three of four languages under the
  current evaluation. Leave it out of the abstract.
