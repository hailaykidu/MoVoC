# Discussion — notes

Scope: MoVoC, MoVoC-Tok, the annotated datasets, and the two evaluations.

## 1. Morphology-aware segmentation yields sharper subword distributions

The clearest and most consistent intrinsic result. MoVoC-Tok attains lower
normalized Rényi entropy than BPE in three of four languages (Amharic 0.62 vs
0.66; Tigrinya 0.92 vs 0.93; Tigre 0.71 vs 0.73).

Lower entropy means a more concentrated token distribution: constraining merges
to morpheme boundaries yields a vocabulary whose units recur more consistently
across the corpus, rather than a long tail of near-duplicate fragments differing
only in where a morpheme was cut.

## 2. Boundary precision and morphological regularity

MoVoC-Tok attains the highest boundary precision in Tigre (63.3 vs 60.0). Tigre's
gold annotations are fully surface-concatenative — morphemes concatenate exactly
to the surface word — so morpheme boundaries coincide with character offsets.

Across both tokenizers, precision is markedly higher for Tigre (60–63) than for
the more fusional languages (24–37). This is a property of how morphological
structure maps onto the abugida orthography, and it affects both arms equally.

## 3. Intrinsic and extrinsic behaviour differ

MoVoC-Tok leads on intrinsic entropy but BPE leads on downstream BLEU and chrF++
in the supervised directions. MoVoC-Tok ranks second on both directions,
substantially ahead of WordPiece.

Segmentation quality as measured by morpheme alignment does not translate
directly into translation quality at this training scale. Both are reported
rather than one being taken as a proxy for the other.

## 4. Metric complementarity

Boundary precision penalises spurious boundaries; MorphScore is recall-oriented
and ignores false positives. Reporting them together characterises segmentation
behaviour more completely than either alone — a tokenizer that under-segments
scores well on precision, one that over-segments scores well on recall.

## 5. The datasets as a contribution

169,806 annotated records across four Ge'ez-script languages, of which 129,261
carry at least one morpheme boundary. Three of the four had no public
morpheme-annotated resource. The annotations support both the vocabulary
construction method and the intrinsic evaluation, and are released in a single
documented JSON schema.
