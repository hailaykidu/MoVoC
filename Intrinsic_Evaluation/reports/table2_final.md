# Table 2: Intrinsic MorphScore Evaluation

Intrinsic MorphScore evaluation on annotated morpheme test sets across
four Ethio-Semitic languages, comparing MoVoC-Tok's predicted subword
boundaries against gold-standard morpheme boundaries.

| Language (ISO 639-3) | No. Words | MorphScore ↑ |
|-----------------------|----------:|--------------:|
| Amharic (amh)          |    33,322 |        0.6745 |
| Tigrinya (tir)         |     7,208 |        0.7531 |
| Ge'ez (gez)            |        77 |        0.7338 |
| Tigre (tig)            |     5,666 |        0.7583 |

## Methodology

MorphScore is computed as follows:

- Boundary score = 1 if a tokenizer boundary exactly matches a gold
  morpheme boundary; 0 otherwise.
- Recall-oriented scoring: matched boundaries / gold boundaries, per word.
- Macro-averaged across words (mean of each word's own ratio).
- Gold words are filtered by exact concatenation: a gold record is used
  only if `prefix + root + suffix` concatenates exactly to the surface
  word.
- Unsegmented (single-morpheme, zero-gold-boundary) words are included
  and scored 1.0.
- Exact boundary matching only (no tolerance window).

Model: each language's own 32k MoVoC-Tok (Amharic, Tigrinya); Tigrinya's
32k model applied cross-lingually for Ge'ez and Tigre, since no dedicated
model was ever trained for either at any vocabulary size.

## "No. Words"

"No. Words" is the number of words that contributed to the intrinsic
MorphScore evaluation. This is distinct from the resource counts
sometimes associated with the languages' tokenizer-construction data
(e.g. NLLB, HornMT, FLORES-200, OPUS, and other corpora used to build
vocabulary and train tokenizers): those resource counts describe
tokenizer-construction inputs, not the intrinsic evaluation set, and
should not be read as the evaluation dataset size. The values reported
here are the actual number of words used in the MorphScore computation
for each language.

Reproduce with:

```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/Intrinsic_Evaluation
python3 scripts/table2_final.py
```
