# Discussion — notes

Scope: MoVoC, MoVoC-Tok, the annotated datasets, and the two evaluations.

## 1. Boundary precision vs. Rényi entropy — the central tradeoff

The paper's central claim still holds: **MoVoC-Tok segments more accurately at
morpheme boundaries**, leading BPE on boundary precision in three of four
languages (Amharic 0.3208 vs 0.3170; Tigrinya 0.3242 vs 0.3142; Tigre 0.5629 vs
0.5380), with a near-tie on Ge'ez (0.4301 vs 0.4326).

This comes **at a small cost to how evenly-distributed its token frequencies
are**: WordPiece, not MoVoC-Tok, attains the lowest Rényi entropy in three of
four languages (Amharic, Tigrinya, Tigre); MoVoC-Tok is lowest only on Ge'ez.
MoVoC-Tok optimizes for linguistic correctness — segmenting at true morpheme
boundaries — rather than for pure statistical compression, which is the
expected tradeoff for a morphology-aware tokenizer versus a frequency-driven
one like BPE or WordPiece. This is also supported qualitatively in Sec. 7
(Qualitative Analysis) of the published paper.

## 2. Boundary precision and morphological regularity

Precision is markedly higher for Tigre (0.51–0.56) than for the more fusional
languages (0.30–0.32). This is a property of how morphological structure maps
onto the abugida orthography, and it affects all three tokenizers similarly.

## 3. Intrinsic and extrinsic behaviour differ

MoVoC-Tok leads on intrinsic boundary precision but BPE leads on downstream
BLEU and chrF++ in the supervised directions. MoVoC-Tok ranks second on both
directions, substantially ahead of WordPiece.

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
