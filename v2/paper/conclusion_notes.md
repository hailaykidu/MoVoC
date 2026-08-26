# Conclusion — notes

## Points to make

1. **Method.** MoVoC constructs vocabularies that reserve half the budget for
   morpheme types; MoVoC-Tok segments under the constraint that no merge crosses
   a morpheme boundary.

2. **Resource.** Morpheme annotations for four Ge'ez-script languages — 169,806
   records, 129,261 with at least one boundary — released in a single documented
   schema, for three languages that had no public morpheme-annotated resource.

3. **Intrinsic result.** MoVoC-Tok attains the highest morpheme boundary
   precision and MorphScore against BPE and WordPiece in three of four
   languages (Amharic, Tigrinya, Tigre), with a near-tie against BPE on the
   fourth (Ge'ez, the one language with no dedicated MoVoC-Tok artifact).

4. **Extrinsic result — inconclusive, not a ranking.** The English→X
   translation runs stopped at 75,000 of a comparable baseline's ~416,000
   optimizer steps and never converged; BLEU sits below 2 in every cell, and
   all nine MoVoC-Tok runs are flagged for output-quality anomalies. BPE
   posts the highest BLEU/chrF++ under these conditions, with MoVoC-Tok
   second and substantially ahead of WordPiece, but this reflects the
   training budget, not tokenizer quality — it should not be cited as
   evidence for or against any of the three.

5. **Takeaway.** Constraining subword merges to morpheme boundaries measurably
   improves how well segmentation lines up with real morpheme structure in
   Ge'ez-script languages. Intrinsic segmentation quality and downstream
   translation quality are reported separately: the extrinsic runs here are
   too undertrained to say whether the intrinsic advantage transfers, not
   evidence that it doesn't.

## Future work

- In-language MoVoC-Tok for Tigre and Ge'ez, given sufficient training
  annotations.
- Extending supervised translation coverage beyond Amharic and Tigrinya.
- Larger-scale translation training to test whether the intrinsic advantage
  transfers downstream.

## Draft

> We presented MoVoC, a morphology-aware vocabulary construction method for
> Ge'ez-script languages, and MoVoC-Tok, its constrained-merge tokenizer, along
> with morpheme annotations for Amharic, Tigrinya, Tigre and Ge'ez. MoVoC-Tok
> attains the highest morpheme boundary precision and MorphScore in three of
> four languages, with a near-tie on the fourth, showing that constraining
> merges to morpheme boundaries produces segmentation that lines up more
> closely with true morpheme structure. The downstream translation runs,
> trained far short of the step budget a comparable baseline would need, do
> not converge and should not be read as a ranking of the three tokenizers.
> We release the annotations, vocabularies and evaluation code as a reference
> implementation.
