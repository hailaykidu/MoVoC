# Table 2 — MorphScore

Three categories, kept separate. **Published values are the paper's claims;
reproduction values are new measurements; reconstruction findings explain the
difference.** None replaces another.

---

## A. Published Results

From the paper (arXiv:2509.08812), verbatim. Archived in
[`../../original/published_results/`](../../original/published_results/).

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 0.710 |
| Tigrinya (tir) | 80,000 | 0.731 |
| Ge'ez (gez) | 20,000 | 0.670 |
| Tigre (tig) | 32,000 | 0.654 |

---

## B. Reproduction Results

Released artifacts through the released pipeline
(`movoc/metrics.py::morphscore`), unmodified. Authoritative reproduction values;
see [`./`](./).

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 41.3 |
| Tigrinya (tir) | 5,224 | 41.5 |
| Ge'ez (gez) | 172 | 88.7 |
| Tigre (tig) | 2,149 | 42.9 |

MorphScore is boundary **recall**, micro-averaged, unsegmented words excluded,
over cumulative-length projection. Formula, aggregation, projection and
tokenizers unmodified; only the evaluation pool was expanded. Values are ×100.

### Difference

| Language | Items (published → reproduced) | MorphScore (published → reproduced) | Δ |
|---|---|---|---:|
| Amharic | 80,000 → **80,000** | 0.710 → 41.3 | −29.7 |
| Tigrinya | 80,000 → 5,224 | 0.731 → 41.5 | −31.6 |
| Ge'ez | 20,000 → 172 | 0.670 → 88.7 | +22.0 |
| Tigre | 32,000 → 2,149 | 0.654 → 42.9 | −22.6 |

Only **Amharic** reaches the published item count — the single like-for-like
comparison in the table.

---

## C. Reconstruction v2 Findings

Investigation of why B differs from A. These explain the discrepancy; they do
**not** replace either column.

**The binding constraint is surface alignment, not corpus size.** Gold boundaries
are character offsets into the surface word, so citation-form annotations that do
not concatenate back are unscorable.

| Language | Unique multi-morpheme | Surface-aligned | Excluded |
|---|---:|---:|---:|
| Amharic | 121,719 | 20,030 | 103,634 |
| Tigrinya | 2,838 | 2,369 | 496 |
| Ge'ez | 173 | 44 | 129 |
| Tigre | 1,974 | 1,974 | **0** |

Tigre loses nothing — its annotations are fully surface-concatenative.

**Evaluation data ceilings.** An exhaustive search established that three of four
languages cannot reach the published counts from any source in the environment.
Unannotated text is plentiful; gold annotation is what is missing
(`annotation_template_tigrinya.json` holds 20,000 words, all `pending`).

**Row caveats.** Ge'ez's 88.7 is not a win over 0.670 — 172 words, 44 official, a
tokenizer built after publication. Amharic is 75% AMSEG-derived and Tigrinya
48.1%; Tigre is the only 100% official row.

Detail: [`../audits/dataset_audit.md`](../audits/dataset_audit.md),
[`../audits/tigrinya_80k_attempt_report.md`](../audits/tigrinya_80k_attempt_report.md).
