# Evaluation contamination: scope, cause and correction

## Summary

Part of the Amharic and Tigrinya intrinsic evaluation sets consists of words
whose morpheme boundaries constrained MoVoC-Tok's own training. On those words
MoVoC-Tok is not generalizing morpheme supervision to unseen forms; it is
recovering a constraint it was given. BPE and WordPiece never received that
information, so a comparison on those words is asymmetric.

This file documents the extent, the effect on the published tables, and how to
reproduce the corrected numbers.

## The chain

`tokenizers/{amharic,tigrinya}_movoc_tok_32k/training_config.json` names

    "morpheme_source": ".../data/segmented/{language}_morpheme_segmented.json"

Those two files (10,293 Amharic and 6,692 Tigrinya records) are now committed
under `data/segmented/`. Previously only the Tigrinya file was reachable, and
the Amharic file was absent from the repository entirely, which made the
Amharic overlap impossible for a reader to check.

The training objective forbids merges that cross a morpheme boundary of these
words. Boundary precision then measures, for the overlapping words, how well
the tokenizer reproduces boundaries it was trained not to cross.

## Extent

Membership is computed on surface word forms, against the full training file
of the tokenizer that scores the language — not against a file named after the
evaluation language.

| Language | Evaluation words | Training resource applied | Also in it | Held out |
|----------|-----------------:|---------------------------|-----------:|---------:|
| Amharic  | 81,224 | `amharic_morpheme_segmented.json`  | 4,736 (5.8%)  | 76,488 |
| Tigrinya | 5,224  | `tigrinya_morpheme_segmented.json` | 2,786 (53.3%) | 2,438 |
| Tigre    | 1,974  | `tigrinya_morpheme_segmented.json` | 187 (9.5%)    | 1,787 |
| Ge'ez    | 172    | `tigrinya_morpheme_segmented.json` | 2 (1.2%)      | 170 |

Tigre and Ge'ez have no training morpheme resource of their own, but the
tokenizer that scores them does: they are evaluated cross-lingually with the
Tigrinya MoVoC-Tok, which was trained on `tigrinya_morpheme_segmented.json`.
Tigre, Tigrinya and Ge'ez are Ethio-Semitic and share surface forms, so the
same exclusion applies to them. An earlier version of this file recorded their
overlap as zero. That was wrong: `training_words()` selected the resource by
the name of the *evaluation* language, so for Tigre it looked for
`data/segmented/tigre_morpheme_segmented.json`, which does not exist — no
Tigre resource constrained any tokenizer — and returned an empty set, silently
excluding nothing. The rule is now applied by scoring tokenizer
(`SCORING_TOKENIZER_LANGUAGE` in `scripts/evaluate_intrinsic.py`), and a
missing resource raises instead of returning an empty set, so the same failure
cannot pass unnoticed again.

### The provenance labels undercount the overlap

`evaluation/data/manifest.json` attributes 2,412 Tigrinya words to
`tigrinya_morpheme_segmented.json` at `"resource_tier": "training"`. The true
overlap is 2,786, because `tigrinya_provenance.tsv` records the *first* source
a word was drawn from, not every source containing it:

| Provenance label | Words also in the training file |
|------------------|-------------------------------:|
| `tigrinya_morpheme_segmented.json` | 2,412 |
| `postedited_morphemes.json` | 356 |
| `gold_morphemes.json` | 18 |

The last row matters most. `gold_morphemes.json` is described in the manifest as
`"gold, held out from training and vocabulary construction"` and tiered
`"evaluation_only"`, but 18 of its 160 words (11.2%) appear in the training
resource. That description is inaccurate as written.

Correcting the evaluation therefore requires set membership against the
training file itself. Filtering on the provenance label alone leaves 374
contaminated words in the set.

## Effect on the published tables

Boundary precision (Table 4) and MorphScore (Table 2), all words versus
held-out words only:

| Language | Tokenizer | Precision (all) | Precision (held-out) | MorphScore (all) | MorphScore (held-out) |
|----------|-----------|----------------:|---------------------:|-----------------:|----------------------:|
| Amharic  | BPE       | 0.3170 | 0.3156 | 0.4105 | 0.4127 |
| Amharic  | WordPiece | 0.3005 | 0.2998 | 0.3842 | 0.3872 |
| Amharic  | MoVoC-Tok | **0.3208** | **0.3174** | **0.4139** | **0.4148** |
| Tigrinya | BPE       | 0.3142 | **0.2401** | 0.4200 | 0.3648 |
| Tigrinya | WordPiece | 0.3167 | **0.2401** | 0.4186 | 0.3613 |
| Tigrinya | MoVoC-Tok | **0.3242** | 0.2385 | **0.4366** | **0.3833** |
| Tigre    | BPE       | 0.5380 | 0.5356 | 0.5004 | 0.4987 |
| Tigre    | WordPiece | 0.5123 | 0.5116 | 0.4778 | 0.4776 |
| Tigre    | MoVoC-Tok | **0.5629** | **0.5642** | **0.5278** | **0.5302** |
| Ge'ez    | BPE       | **0.4326** | **0.4308** | **0.6667** | **0.6640** |
| Ge'ez    | WordPiece | 0.4201 | 0.4182 | 0.6392 | 0.6364 |
| Ge'ez    | MoVoC-Tok | 0.4301 | 0.4282 | 0.6561 | 0.6534 |

Amharic, Tigre and Ge'ez are unchanged in ranking. **Tigrinya boundary
precision changes**: MoVoC-Tok leads on all words and is last on held-out
words. Tigrinya MorphScore is unaffected in ranking.

Tigre moves slightly *up* on exclusion, because MoVoC-Tok does worse on the
187 excluded words than on the rest (see below).

The claim "highest boundary precision in three of four languages" becomes
**two of four** (Amharic, Tigre). The MorphScore claim is unchanged at three of
four.

## Significance of the held-out differences

Paired bootstrap over words, 10,000 resamples, shared index across tokenizers
(`scripts/bootstrap_significance.py`, results in
`evaluation/results/significance_heldout.json`). Differences are MoVoC-Tok
minus the baseline.

| Language | n | Metric | vs BPE | vs WordPiece |
|----------|--:|--------|--------|--------------|
| Amharic  | 76,488 | Precision  | +0.0018 [+0.0004,+0.0033] p=0.012 | +0.0176 [+0.0157,+0.0194] p<0.001 |
| Amharic  | 76,488 | MorphScore | +0.0021 [+0.0001,+0.0042] p=0.045 | +0.0276 [+0.0251,+0.0300] p<0.001 |
| Tigrinya | 2,438  | Precision  | −0.0016 [−0.0106,+0.0075] p=0.744 | −0.0016 [−0.0129,+0.0102] p=0.805 |
| Tigrinya | 2,438  | MorphScore | +0.0185 [+0.0031,+0.0345] p=0.017 | +0.0220 [+0.0037,+0.0411] p=0.018 |
| Tigre    | 1,787  | Precision  | +0.0286 [+0.0096,+0.0476] p=0.004 | +0.0526 [+0.0253,+0.0805] p<0.001 |
| Tigre    | 1,787  | MorphScore | +0.0314 [+0.0133,+0.0494] p=0.001 | +0.0526 [+0.0267,+0.0787] p<0.001 |
| Ge'ez    | 170    | Precision  | −0.0026 [−0.0258,+0.0196] p=0.829 | +0.0100 [−0.0151,+0.0351] p=0.457 |
| Ge'ez    | 170    | MorphScore | −0.0106 [−0.0381,+0.0163] p=0.457 | +0.0170 [−0.0143,+0.0484] p=0.309 |

Three points follow.

**The Amharic margins over BPE are small but resolved.** +0.0018 precision and
+0.0021 MorphScore both exclude zero, on 76,488 words. They are real and they
are slight; the gain over WordPiece is an order of magnitude larger.

**Tigrinya precision is not a loss, it is a null.** The interval
[−0.0106, +0.0075] spans zero, so the held-out data do not separate MoVoC-Tok
from BPE on precision. The correct statement is that no difference is detected,
not that MoVoC-Tok is worse. Tigrinya MorphScore is a genuine gain
(+0.0185, p=0.017).

**Tigre is the strongest result in the paper.** It is the largest effect
(+0.0286 precision, +0.0314 MorphScore against BPE, both significant) and it is
cross-lingual: the Tigrinya tokenizer applied to a language with no training
morpheme data of its own. Ge'ez, at n=170, resolves nothing in either direction.

On the 187 excluded Tigre words the ordering reverses: MoVoC-Tok scores 0.5000
precision against 0.8000 for BPE (−0.3000, p=0.021). The constraint is applied
to Tigrinya surface forms, so where a Tigre word coincides with one, the
segmentation it enforces need not be the Tigre analysis the gold annotation
records. The cross-lingual gain is therefore a gain on words the constraint
did *not* reach — which is what makes it evidence of generalization rather
than of recall, and why excluding these words raises the Tigre margin instead
of lowering it. At n=187 this reading is tentative.

## Why Tigrinya and not Amharic

The two languages differ in annotation coverage, not in method. The Tigrinya
morpheme vocabulary realises 7,125 types against 50,978 for Amharic
(`tables/table5_vocab.tex`), from 6,692 training records against 10,293. On
Tigrinya the constraint reaches too few word types for the learned merges to
transfer; the advantage is confined to the annotated words themselves.

This is a statement about resource sufficiency and is the more useful finding
for a reader deciding whether to apply the method to another language.

## Reproducing

    # published tables, all words (unchanged)
    python scripts/evaluate_intrinsic.py --outdir evaluation/results

    # corrected tables, held-out words only
    python scripts/evaluate_intrinsic.py --outdir evaluation/results \
        --exclude-training

The flag excludes, per language, every evaluation word present in
`data/segmented/{language}_morpheme_segmented.json`, and records the count
removed under `reproducibility.languages.<lang>.excluded_movoc_training_words`.
Outputs are written with a `_heldout` suffix so both sets of numbers coexist.
