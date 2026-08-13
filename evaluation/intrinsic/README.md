# Intrinsic evaluation

Paper methodology (Sec. 3, Sec. 6)
&nbsp;&nbsp;&nbsp;&nbsp;↓
Intrinsic evaluation implementation (`movoc/metrics.py`, this directory)
&nbsp;&nbsp;&nbsp;&nbsp;↓
Verified rerun results (`evaluation/results/`)

The tables below follow the paper's structure, terminology, metric names,
language ordering and vocabulary-size notation. Only the values are replaced
with those from the verified rerun.

> The reported values correspond to the verified rerun of the intrinsic
> evaluation. Differences from the original paper values may occur due to
> differences in available resources, preprocessing, implementation details,
> and evaluation conditions.

---

## Table 2: Morphological dataset and MoVoC-Tok MorphScore

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---|---|
| Amharic (amh) | 80k | 41.6 |
| Tigrinya (tir) | 80k | 34.0 |
| Geʿez (gez) | 20k | 92.3 |
| Tigre (tig) | 32k | 45.0 |

The "No. Items" column reproduces the paper's own figures. The number of
items actually evaluated in this rerun is recorded in
[`docs/TABLE2_ITEM_COUNT_DISCREPANCY.md`](../../v2/audits/dataset_audit.md):
18,524 (amh), 70 (tir), 48 (gez) and 4,026 (tig) boundary-scorable held-out
items.

---

## Table 4: Morpheme boundary precision and Rényi entropy (α = 2, 32k vocabulary)

| Language | Tokenization | Precision ↑ | Rényi Entropy ↓ |
|---|---|---|---|
| Amharic | MoVoC-Tok | 29.1 | 0.67 |
| Amharic | BPE | 13.4 | 0.73 |
| Tigrinya | MoVoC-Tok | 29.8 | 0.91 |
| Tigrinya | BPE | 19.0 | 0.93 |
| Tigre | MoVoC-Tok | 46.3 | 0.76 |
| Tigre | BPE | 60.4 | 0.76 |
| Geʿez | MoVoC-Tok | 35.3 | 0.85 |
| Geʿez | BPE | 34.1 | 0.83 |

Rényi entropy is normalized to [0, 1]; lower values indicate a sharper, more
consistent segmentation distribution.

**On the Tigre row.** Tigre is the one language where BPE scores higher
precision than MoVoC-Tok (60.4 vs 46.3). The available Tigre resource is a
deduplicated lexical list in which every entry occurs exactly once, so
constrained merge learning ran without any corpus frequency distribution to
rank candidate merges (see the reproducibility conditions below). The Tigre
figures therefore reflect the evaluation conditions available for that
language rather than a property of the method, and are not comparable with
Amharic and Tigrinya, which were learned from running text with real
frequencies.

Geʿez BPE reached 3,076 of the 32k vocabulary setting because its corpus
contains 1,282 unique words; Amharic, Tigrinya and Tigre all reached 32,000.

---

## Reproducibility conditions

### Tigre

- The available corpus is a deduplicated lexical resource.
- No frequency distribution is available; every entry occurs exactly once.
- `min_freq=1` was required (the default `min_freq=2` discards the entire
  resource and yields zero merges).
- Annotation coverage limits the number of evaluated instances.

### Held-out evaluation

`movoc/annotation.py` draws the gold set and the vocabulary-construction set
from the same file for Amharic, Geʿez and Tigre. This rerun scores disjoint
held-out halves so no item used for vocabulary construction is also scored;
for Tigrinya, whose gold file is separate, overlapping words are removed.
Full detail in
[`docs/RECONSTRUCTED_EVALUATION.md`](../../v2/reports/reconstructed_evaluation.md).

---

## Contents

| File | Purpose |
|---|---|
| `paper_tables.py` | Computes Tables 2 and 4 for all four languages |
| `build_geez_tigre_arms.py` | Builds the Geʿez and Tigre BPE and MoVoC-Tok arms (Algorithm 1, Steps 3 and 6) |
| `score_tigre_movoc_tok.py` | Scores the Tigre MoVoC-Tok arm alone; refuses to report a partial merge table |

Metric implementations live in `movoc/metrics.py` and are unchanged.

## Reproducing

```bash
# Geʿez and Tigre tokenizer arms (Amharic and Tigrinya already ship)
python evaluation/intrinsic/build_geez_tigre_arms.py

# Tables 2 and 4
python evaluation/intrinsic/paper_tables.py
```

Outputs are written to `evaluation/results/`:

| File | Contents |
|---|---|
| `paper_tables.json` | MorphScore, boundary precision and Rényi entropy per language and tokenization, with provenance |
| `paper_tables_leaky.json` | Same metrics scored in-sample, kept for comparison against the held-out figures |
| `extended_arms_build.json` | Geʿez and Tigre build record: corpus sizes, vocabulary requested vs achieved, merge counts, constraint sources |

Intrinsic evaluation is independent of the MarianMT extrinsic pipeline; no
translation model is trained or evaluated here.
