# Conclusion — notes

## Points to make

1. **Method.** MoVoC constructs vocabularies that reserve half the budget for
   morpheme types; MoVoC-Tok segments under the constraint that no merge crosses
   a morpheme boundary.

2. **Resource.** Morpheme annotations for four Ge'ez-script languages — 169,806
   records, 129,261 with at least one boundary — released in a single documented
   schema, for three languages that had no public morpheme-annotated resource.

3. **Intrinsic result.** MoVoC-Tok produces sharper subword distributions than
   BPE, with lower normalized Rényi entropy in three of four languages, and the
   highest morpheme boundary precision in Tigre (63.3 vs 60.0).

4. **Extrinsic result.** In English→X translation under identical training
   conditions, BPE leads on the two supervised directions, with MoVoC-Tok second
   and substantially ahead of WordPiece.

5. **Takeaway.** Constraining subword merges to morpheme boundaries measurably
   improves segmentation consistency in Ge'ez-script languages. Intrinsic
   segmentation quality and downstream translation quality are reported
   separately, as they do not move together at this training scale.

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
> yields lower Rényi entropy than BPE in three of four languages and the highest
> boundary precision in Tigre, showing that constraining merges to morpheme
> boundaries produces more consistent subword inventories. In downstream
> translation at this training scale, BPE remains ahead, with MoVoC-Tok second.
> We release the annotations, vocabularies and evaluation code as a reference
> implementation.
