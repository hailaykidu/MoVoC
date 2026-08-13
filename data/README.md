# Morpheme-annotated datasets for Ge'ez-script languages

A core contribution of MoVoC: morpheme segmentations for four Ge'ez-script
languages, three of which had no public morpheme-annotated resource.

## Contents

| Language | ISO 639-3 | File | Records | Multi-morpheme | Source |
|---|---|---|---:|---:|---|
| Amharic | amh | `annotations/amharic/postedited_morphemes.json` | 153,759 | 123,761 | HornMorpho + human post-editing |
| Tigrinya | tir | `annotations/tigrinya/gold_morphemes.json` | 206 | 205 | manual gold, held out from vocabulary construction |
| Tigrinya | tir | `annotations/tigrinya/postedited_morphemes.json` | 7,531 | 2,665 | HornMorpho + human post-editing |
| Tigre | tig | `annotations/tigre/manual_morphemes.json` | 8,117 | 2,457 | manual annotation |
| Ge'ez | gez | `annotations/geez/manual_morphemes.json` | 193 | 173 | manual annotation |

*Multi-morpheme* counts entries carrying at least one morpheme boundary — the
scorable subset for boundary metrics. Single-morpheme entries are valid
annotations but contribute no boundary.

## Annotation format

JSON array, one object per word. Morphemes are given as separate fields; `-`
marks an empty slot.

```json
{"no": 3, "word": "ዝወደቐ", "prefix": "ዝ-", "root": "ወደቐ", "suffix": "-"}
```

| Field | Meaning |
|---|---|
| `word` / `Word` | surface form |
| `prefix`, `root`, `infix`, `suffix`, `clitic` | morpheme slots; `-` if absent |

Amharic uses capitalised keys (`Word`, `Prefix`, …); the other languages use
lowercase. Tigre and Amharic carry `clitic`; Tigrinya's gold set is
prefix/root/suffix only. `movoc/annotation.py` normalises all variants.

## Usage

```python
from movoc import annotation

entries = annotation.load("data/annotations/tigre/manual_morphemes.json")
word, prefix, root, suffix = annotation.triple_of(entries[0])
```

Boundary positions are derived as cumulative morpheme lengths:

```python
from movoc.metrics import boundaries_from_triple
boundaries_from_triple("ዝ", "ወደቐ", "")     # -> {1}
```

## Other data

| Directory | Contents |
|---|---|
| `evaluation/` | parallel test sets per language (`test.en` + `test.{am,ti,tig,gez}`), FLORES-200 |
| `raw/` | source corpora: HornMT (amh/eng/tir), extended Ge'ez and Tigre word lists |
| `vocabulary/` | built vocabularies: BPE, WordPiece and MoVoC per language |

## Coverage note

Annotation coverage varies by two orders of magnitude across languages, and the
Ge'ez and Tigre sets are reserved for evaluation only — the paper (Sec. 4.1)
states no separate training morpheme data was obtained for them. Per-language
counts and their effect on evaluation are recorded in
[`../v2/audits/dataset_audit.md`](../v2/audits/dataset_audit.md).
