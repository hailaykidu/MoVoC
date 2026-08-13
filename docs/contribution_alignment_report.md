# Contribution alignment report

Verification that the repository presents MoVoC's research contributions first,
with audits as supporting material.

## Result

| Required prominence | Where | Status |
|---|---|---|
| 1. MoVoC vocabulary construction | README §1, `train.py`, `movoc/vocabulary.py` | **exposed** |
| 2. MoVoC-Tok | README §2, `segment.py`, `movoc/tokenizer.py` | **exposed** |
| 3. Annotated datasets | README §3, `data/README.md`, `data/annotations/` | **exposed** |
| 4. Intrinsic evaluation | README §4, `evaluate.py`, `movoc/metrics.py` | **exposed** |
| 5. Extrinsic evaluation | README §5, `evaluation/translate_eval.py` | **exposed** |
| Audits as supporting material | README §6 subsection, `v2/audits/` | **subordinate** |

## README section order

```
1. MoVoC                    <- vocabulary construction, with the budget formula
2. MoVoC-Tok                <- constrained-merge tokenization
3. Annotated datasets       <- counts table + link to data/README.md
4. Intrinsic evaluation     <- precision, Rényi, MorphScore
5. Extrinsic evaluation     <- MarianMT BLEU / chrF++
6. Reconstruction Version 2 <- with "Supporting audits" as a subsection
7. Repository structure
8. Running the experiments
```

The hierarchy communicates
**MoVoC → MoVoC-Tok → Datasets → Intrinsic → Extrinsic → Audits**.

Audits are never a top-level section. They appear only as a subsection of
Reconstruction Version 2, explicitly labelled supporting evidence.

## Method visibility

The vocabulary allocation is stated in the README body, not deferred to a
subdirectory:

```
s_lang = s / 2
s_morpheme = s_lang × r
s_BPE      = s_lang × (1 − r)
```

MoVoC-Tok's defining constraint — *a merge may never cross a morpheme boundary* —
appears in its own section with a runnable command.

## Dataset discoverability

Reachable from the repository root in one hop: a counts table in README §3 links
to `data/README.md`, which documents format, fields, usage and per-language
provenance. `data/` is the first entry in the repository-structure tree.

## Results visibility

Both evaluation tables appear in the README with their numbers inline, so a
reader sees the measurements without opening a subdirectory. Each links to its
per-table report for the published-vs-reconstruction comparison.

## Supporting material kept subordinate

| Material | Location | Not in |
|---|---|---|
| Audits | `v2/audits/` | README top level |
| Sensitivity analyses | `v2/appendix/` | any main table |
| Limitations | `v2/reports/limitations.md` | README body |
| Incident evidence | `v2/audits/incidents/` | results paths |

Sensitivity metrics (±1 tolerance, fusion-aware matching) appear **only** under
`v2/audits/` and `v2/appendix/`, never in Tables 2, 3 or 4.
