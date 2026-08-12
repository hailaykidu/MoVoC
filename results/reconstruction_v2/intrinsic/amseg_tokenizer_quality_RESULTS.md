# Intrinsic — tokenizer quality

How well each tokenizer's segmentation preserves gold morphological
boundaries. Independent of any downstream model: these numbers describe the
tokenizers themselves, and are unaffected by the MT training failure.

## Methodology

| Metric | Definition |
|---|---|
| Morpheme boundary precision | of all internal boundaries a tokenizer produces, the fraction coinciding with a gold morpheme boundary. Word start and end are not boundaries. |
| MorphScore (Arnett & Bergen, 2025) | recall of gold boundaries among words the tokenizer actually segmented; unsegmented words excluded rather than scored zero; extra boundaries not penalised. |
| Rényi entropy (α=2) | `H = 1/(1-α)·log(Σ pᵢ^α)` over the token distribution, normalized by `log(support)` — the scale the paper reports. |

**Denominator note.** MorphScore divides by *gold* boundaries, not predicted
ones. Dividing by predicted boundaries makes it algebraically identical to
precision, since unsegmented words contribute nothing to either sum; the two
metrics would then always agree, which is not the intent.

**Surface projection.** Gold morphemes are citation forms and usually do not
concatenate to the surface word (ሰላማዊ is annotated ሰላም + ኣዊ, fusing to ማ).
Boundaries are projected onto the surface by locating each morpheme in it;
words whose morphemes cannot be located are excluded and counted, never
segmented on a guess.

Evaluation data, sources and exclusion counts are in `../../data/manifest.json`.
Computed by `scripts/evaluate_intrinsic.py`. Raw values in `metrics.json`.

## Results

See `summary_table.md` for the in-language / cross-lingual split and
`table4_format.md` for the paper's Table 4 layout.

| Language | Tokenizer | Boundary Precision | MorphScore | Rényi α=2 (norm.) |
|---|---|---:|---:|---:|
| Amharic | BPE | 0.3170 | 0.4105 | 0.66 |
| Amharic | WordPiece | 0.3005 | 0.3842 | 0.63 |
| Amharic | **MoVoC-Tok** | **0.3208** | **0.4139** | 0.63 |
| Tigrinya | BPE | 0.3142 | 0.4200 | 0.77 |
| Tigrinya | WordPiece | 0.3167 | 0.4186 | 0.68 |
| Tigrinya | **MoVoC-Tok** | **0.3242** | **0.4366** | 0.76 |
| Tigre | BPE | 0.5380 | 0.5004 | 0.75 |
| Tigre | WordPiece | 0.5123 | 0.4778 | 0.69 |
| Tigre | **MoVoC-Tok\*** | **0.5629** | **0.5278** | 0.73 |
| Ge'ez | **BPE** | **0.4326** | **0.6667** | 0.81 |
| Ge'ez | WordPiece | 0.4201 | 0.6392 | 0.82 |
| Ge'ez | MoVoC-Tok\* | 0.4301 | 0.6561 | 0.82 |

`*` = cross-lingual: MoVoC-Tok was not trained on this language. Tigre and
Ge'ez were excluded from MoVoC-Tok training because no independent training
morpheme resources were available; their manual annotations were reserved
exclusively for intrinsic evaluation.

## Interpretation

MoVoC-Tok achieves the highest boundary precision and MorphScore in Amharic,
Tigrinya and Tigre. In Tigre this holds cross-lingually — the model was trained
on Tigrinya constraints and never saw Tigre morphemes — which is evidence of
genuine transfer between related Ethio-Semitic languages.

Ge'ez is the exception, with BPE ahead. Ge'ez is evaluated on 172 words, so
that gap should be treated as inconclusive rather than a ranking.

**Scale caveat.** These absolute values are well below the figures in the
published Table 4 (which reports 73.9–88.3 on a 0–100 precision scale against
32.1–56.3 here), while the *direction* of the MoVoC-Tok advantage reproduces.
The discrepancy is unresolved; the most likely candidates are a more permissive
boundary-matching criterion in the original work, and different test sets and
vocabularies. These numbers should not be presented as reproducing Table 4.

**Independent of the MT failure.** Nothing here depends on the collapsed
translation models. These are properties of the tokenizers measured against
gold annotations, and remain valid regardless of the downstream outcome.
