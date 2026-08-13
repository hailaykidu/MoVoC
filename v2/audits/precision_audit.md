# Precision audit — Table 4

Audits **only** the precision computation. Tokenizers, datasets and entropy were
not changed, and Table 4 was not regenerated.

## CHECK 1 & 3 — the official implementation

Every precision-like function in the official repository was located:

| File | Function |
|---|---|
| `movoc/metrics.py:42` | `boundary_precision` |
| `movoc/metrics.py:70` | `morphscore` (recall) |
| `evaluate.py:27` | `precision_from_cuts` |
| `evaluation/intrinsic/paper_tables.py:72` | `precision_from_cuts` (Table-4 generator) |

All implement the same thing:

```python
tp += len(p & g)      # exact set intersection
fp += len(p - g)
return tp / (tp + fp)  # micro-average
```

A repository-wide search for `toleran|fuzzy|window|within|approx|off.?by|abs(..)<=`
returned **no matches**. There is no boundary tolerance, no offset window, no
grapheme-level matching, and no fuzzy comparison anywhere in the official code.

**CHECK 1 answer:** exact position matching, character offsets, strict set
intersection.

**CHECK 3 answer:** the metric is `Correct / Predicted` — plain precision.
Not F1, not accuracy. `morphscore` is a separate *recall* metric reported in
Table 2, not Table 4.

Our implementation already matches the official one exactly.

## CHECK 4 — macro vs micro averaging

| Language | Tokenizer | Micro | Macro | Δ |
|---|---|---:|---:|---:|
| Amharic | MoVoC-Tok | 24.01 | 25.91 | +1.90 |
| Amharic | BPE | 24.29 | 25.74 | +1.45 |
| Tigrinya | MoVoC-Tok | 26.63 | 26.47 | -0.16 |
| Tigrinya | BPE | 27.27 | 27.67 | +0.40 |
| Tigre | MoVoC-Tok | 63.32 | 63.47 | +0.15 |
| Tigre | BPE | 60.05 | 60.13 | +0.08 |
| Ge'ez | MoVoC-Tok | 35.40 | 35.31 | -0.09 |
| Ge'ez | BPE | 36.80 | 36.54 | -0.26 |

**Not the explanation.** The two differ by at most 1.9 points and never
approach the published range. The official code uses micro; we use micro.

## CHECK 5 — Unicode normalization

Raw, NFC and NFKC give **identical precision to 2 decimals in all 8 cells**, and
identical word counts. Ge'ez-script codepoints are already composed, so
normalisation is a no-op here.

**Not the explanation.**

## CHECK 2 — boundary tolerance (the finding)

| Language | Tokenizer | Strict | ±1 | ±2 | Published |
|---|---|---:|---:|---:|---:|
| Amharic | MoVoC-Tok | 24.0 | 59.8 | 68.8 | 85.5 |
| Amharic | BPE | 24.3 | 61.0 | 69.7 | 85.3 |
| Tigrinya | MoVoC-Tok | 26.6 | 66.3 | 74.9 | 88.3 |
| Tigrinya | BPE | 27.3 | 66.7 | 74.5 | 83.9 |
| Tigre | MoVoC-Tok | 63.3 | 98.3 | 98.3 | 83.9 |
| Tigre | BPE | 60.0 | 98.5 | 98.5 | 74.6 |
| Ge'ez | MoVoC-Tok | 35.4 | 64.3 | 64.9 | 85.6 |
| Ge'ez | BPE | 36.8 | 62.9 | 64.2 | 73.9 |

**±1 tolerance moves precision into the published range for three of four
languages.** Amharic 24.0 → 59.8, Tigrinya 26.6 → 66.3, Ge'ez 35.4 → 64.3, and
Tigre overshoots to 98.3 (published 83.9).

### Why off-by-one dominates

Ge'ez script is an abugida: each character encodes a consonant *and* its vowel.
At a morpheme join the boundary frequently falls inside a fused character, so a
tokenizer cutting one position either side of the gold offset is linguistically
reasonable but scores zero under exact matching. Examples from
`precision_error_analysis.csv`:

```
የሚያገባትን   gold 2|6   pred 3|5   -> exact 0, ±1 = 2   (የሚያ|ገባ|ትን)
ማበልፀግም    gold 1|5   pred 1|3|4 -> exact 1, ±1 = 2   (ማ|በል|ፀ|ግም)
ተረጂነት     gold 1|3   pred 2|3   -> exact 1, ±1 = 2   (ተረ|ጂ|ነት)
```

## Verdict on the five candidate explanations

| # | Candidate | Verdict |
|---|---|---|
| 1 | Boundary tolerance | **Most likely.** ±1 lifts 3 of 4 languages into the published range |
| 2 | Macro vs micro | Ruled out — ≤1.9 point difference |
| 3 | Unicode normalization | Ruled out — identical to 2 dp across raw/NFC/NFKC |
| 4 | Hidden matching rule | Not in the official code; ±1 tolerance is the plausible form it would take |
| 5 | Different metric (F1/accuracy) | Ruled out — official code is precision; F1 is 23–44, further from published |

## Important caveat

**±1 tolerance is not documented in the paper and does not appear in the official
repository.** This audit shows it *would* reconcile the magnitudes; it is not
evidence that the paper used it. Tigre overshooting to 98.3 against a published
83.9 argues against a simple ±1 rule being the whole story.

The ranking also does not resolve: under ±1, MoVoC-Tok still trails BPE on
Amharic (59.8 vs 61.0), Tigrinya (66.3 vs 66.7) and Tigre (98.3 vs 98.5), and
leads only on Ge'ez (64.3 vs 62.9). The paper reports MoVoC-Tok ahead in all
four. **Tolerance explains the magnitude gap, not the ranking gap.**

## Artifacts

| File | Contents |
|---|---|
| `precision_variants.csv` | 72 rows: 4 languages × 2 tokenizers × 3 Unicode × 3 tolerances |
| `precision_error_analysis.csv` | 2,756 per-word records with gold/predicted boundaries, missed and spurious cuts |

No tokenizer, dataset or entropy setting was changed. Table 4 in
`../results_intrinsic_official/` remains the accepted reproduction and was not
modified.
