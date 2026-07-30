# Table 2 "No. Items" — discrepancy report

The paper's Table 2 states item counts of 80k (Amharic), 80k (Tigrinya),
20k (Ge'ez) and 32k (Tigre). This document records what the available
resources actually contain after preprocessing, and why the counts cannot be
reached. **No item is duplicated, padded, resampled or synthesised to close
the gap.**

## Measured counts

| Language | Paper "No. Items" | Annotation entries | Scorable after preprocessing | Held-out (scored) |
|---|---|---|---|---|
| Amharic (amh) | 80k | 153,759 | 37,048 | 18,524 |
| Tigrinya (tir) | 80k | **206** | 80 | 70 |
| Ge'ez (gez) | 20k | 193 | 97 | 48 |
| Tigre (tig) | 32k | 8,117 | 8,053 | 4,026 |

## Why entries drop out

Nothing is lost to malformed records — every entry in all four files has a
usable surface word (`no_word = 0` for all languages). Entries leave the
scorable set for one reason only: MorphScore and Boundary Precision are
defined over morpheme *boundaries*, so an entry annotated as a single
morpheme (no prefix and no suffix) contributes no boundary and cannot be
scored.

| Language | Entries | Single-morpheme (no boundary) | Distinct morphemes |
|---|---|---|---|
| Amharic | 153,759 | 33,688 | 50,978 |
| Tigrinya | 206 | 1 | 231 |
| Ge'ez | 193 | 20 | 69 |
| Tigre | 8,117 | 5,723 | 3,950 |

Amharic's reduction from 153,759 to 37,048 is dominated by entries whose
annotation carries no segmentable boundary.

## The corpora are not the limiting factor

The Ge'ez (Kibra Negest) and Tigre corpus sources supply *text*, which is
what the tokenizers are trained on. They carry **no morpheme
segmentations**, so they cannot enlarge the scorable set:

| Language | Corpus | Tokens | Unique words | Paper "No. Items" |
|---|---|---|---|---|
| Ge'ez | `Geez from Kibra negest 19.txt` | 2,040 | 1,282 | 20k |
| Tigre | `tigre-words-only.txt` | 419,627 | 419,627 | 32k |

Tigre is the decisive case: its corpus holds **419,627 words, far more than
the paper's stated 32k**, yet only 8,117 words carry gold annotations. The
binding constraint is therefore **annotation coverage, not corpus size**.
Adding corpus text cannot raise the evaluable item count.

Ge'ez runs the other way — 1,282 unique words against a stated 20k — so its
corpus is also too small to have produced 20k annotated items.

## Interpretation

Because Tigre's corpus exceeds its stated count while its annotations fall
far short, the paper's "No. Items" column cannot be the number of
gold-annotated, boundary-scorable words that the released annotation files
contain. It plausibly counts corpus tokens, vocabulary entries, or an
annotation set larger than the one released here. **The available artifacts
do not determine which**, and this repository does not guess.

## Consequence

Table 2 is reported with the **actual evaluated item counts**. The paper's
figures are shown alongside for reference and are not reproduced. The
difference is a limitation of the available annotation resources, recorded
here rather than absorbed into the table.
