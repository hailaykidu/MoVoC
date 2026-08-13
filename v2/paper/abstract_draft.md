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
5. **Result.** MoVoC-Tok yields lower Rényi entropy than BPE in three of four
   languages and higher boundary precision in Tigre.

## Draft

> Ge'ez-script languages are morphologically rich, and standard subword
> tokenizers routinely place boundaries inside morphemes. We present MoVoC, a
> morphology-aware vocabulary construction method that reserves half its budget
> for morpheme types recovered by supervised analysis and half for BPE merges,
> together with MoVoC-Tok, a constrained-merge tokenizer in which no merge may
> cross a morpheme boundary. We release morpheme annotations for Amharic,
> Tigrinya, Tigre and Ge'ez. Evaluated intrinsically with morpheme boundary
> precision, MorphScore and Rényi entropy, and extrinsically on English→X
> translation, MoVoC-Tok produces sharper subword distributions than BPE in
> three of four languages and higher boundary precision in Tigre.

## Numbers available for the abstract

- Rényi entropy: MoVoC-Tok lower in Amharic (0.62 vs 0.66), Tigrinya (0.92 vs
  0.93), Tigre (0.71 vs 0.73)
- Boundary precision, Tigre: 63.3 vs 60.0
- Datasets: 169,806 annotated records across four languages
