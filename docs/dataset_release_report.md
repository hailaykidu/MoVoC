# Dataset release readiness report

Verification that the morpheme-annotated datasets are documented and releasable.

## Result

| Check | Status |
|---|---|
| All annotation files parse as valid JSON | **5/5** |
| Counts documented in `data/README.md` | **5/5 match measured values** |
| Annotation format documented | yes — worked JSON example |
| Field semantics documented | yes — per-field table, variant keys noted |
| Usage examples documented | yes — `movoc.annotation` + `boundaries_from_triple` |
| Per-language evaluation sets present | 4/4 (amharic, tigrinya, tigre, geez) |

**All dataset checks pass.**

## Measured contents

Counts were recomputed from the files, not copied from documentation.

| Language | File | Records | Multi-morpheme |
|---|---|---:|---:|
| Amharic | `data/annotations/amharic/postedited_morphemes.json` | 153,759 | 123,761 |
| Tigrinya | `data/annotations/tigrinya/gold_morphemes.json` | 206 | 205 |
| Tigrinya | `data/annotations/tigrinya/postedited_morphemes.json` | 7,531 | 2,665 |
| Tigre | `data/annotations/tigre/manual_morphemes.json` | 8,117 | 2,457 |
| Ge'ez | `data/annotations/geez/manual_morphemes.json` | 193 | 173 |

*Multi-morpheme* = entries carrying at least one morpheme boundary, i.e. the
scorable subset for boundary metrics. The distinction matters: single-morpheme
entries are valid annotations but contribute no boundary, and conflating the two
is what makes item counts hard to compare against the paper.

## Format

JSON array, one object per word; `-` marks an empty slot.

```json
{"no": 3, "word": "ዝወደቐ", "prefix": "ዝ-", "root": "ወደቐ", "suffix": "-"}
```

Two key conventions coexist and are both documented: Amharic uses capitalised
keys (`Word`, `Prefix`, …), the other languages lowercase. Amharic and Tigre
carry `clitic`; Tigrinya's gold set is prefix/root/suffix only.
`movoc/annotation.py` normalises all variants.

## Directory layout

`data/` is organised by purpose, with per-language subdirectories under each:

```
data/
├── README.md          format, counts, usage
├── annotations/       amharic/ tigrinya/ tigre/ geez/   <- the contribution
├── evaluation/        amharic/ tigrinya/ tigre/ geez/ + flores200.zip
├── raw/               source corpora (HornMT, extended word lists)
└── vocabulary/        built BPE / WordPiece / MoVoC vocabularies
```

The requested `data/{amharic,tigrinya,tigre,geez}` grouping is realised as
`data/annotations/{lang}/` and `data/evaluation/{lang}/`, keeping annotations
distinct from parallel test data. No files were moved.

## Release caveats — documented, not blocking

- **Coverage spans two orders of magnitude** (Ge'ez 193 records vs Amharic
  153,759).
- **Ge'ez and Tigre annotations are evaluation-only.** The paper (Sec. 4.1)
  states no separate training morpheme data was obtained for them.
- **Provenance differs by language**: Amharic and Tigrinya post-edited sets are
  HornMorpho output with human correction; Tigre and Ge'ez are manual; the
  Tigrinya gold set is held out from vocabulary construction.

All three are stated in `data/README.md`, with per-language detail in
`v2/audits/dataset_audit.md`.
