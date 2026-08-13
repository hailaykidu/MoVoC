# Related work — notes

## Subword tokenization

- **BPE** (Sennrich et al., 2016) — frequency-driven merges; the baseline
  MoVoC-Tok is compared against.
- **WordPiece** (Schuster & Nakajima, 2012) — likelihood-driven; the second
  baseline in the extrinsic comparison.
- **SentencePiece / Unigram** (Kudo & Richardson, 2018) — language-independent
  segmentation without pre-tokenization.

Common property: boundaries are induced from corpus statistics, with no
morphological constraint.

## Morphology-aware segmentation

- **Morfessor** (Creutz & Lagus, 2007) — unsupervised morphological segmentation.
- **HornMorpho** (Gasser, 2011) — supervised morphological analysis for Ethiopian
  Semitic languages; the analyzer behind the annotation pipeline.

## Evaluation metrics

- **Morpheme boundary precision** (Nouri & Yangarber, 2016) — predicted
  boundaries against gold morpheme boundaries.
- **MorphScore** (Arnett & Bergen, 2025) — recall-oriented boundary alignment;
  unsegmented words excluded.
- **Rényi entropy** (Rényi, 1961) — subword distribution diversity; lower
  indicates sharper, more consistent segmentation.

## Ge'ez-script NLP

Low-resource setting across all four languages, with Tigre and Ge'ez having
substantially less annotated data than Amharic and Tigrinya.
