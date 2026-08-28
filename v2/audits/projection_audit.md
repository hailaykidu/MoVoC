# Boundary projection audit

> **Extracted from archive.** This audit was originally extracted from `v2/table4/REPRODUCTION_STATUS.md (section 2)`.
> That file is now archived at `../archive/table4_reproduction_status_superseded.md`.
> See [`docs/duplicate_document_inventory.md`](../../docs/duplicate_document_inventory.md).

> Content is extracted verbatim from the archived `REPRODUCTION_STATUS.md`. Conclusions are
> unchanged; this file exists so each audit is separately citable.

## 2. Paper-style cumulative-length projection — implemented

The official rule (`movoc/metrics.py::boundaries_from_triple`) derives gold
boundaries from **cumulative morpheme lengths** and never consults the surface
string:

```python
pos = 0
for part in parts[:-1]:
    pos += len(part)
    boundaries.add(pos)
```

This replaces the surface-locating rule used previously, which required each
morpheme to be found inside the surface word and excluded the word otherwise.

**Accepted and implemented.** The effect on the evaluation set is large, because
the gold annotations store citation forms that frequently do not concatenate to
the surface:

| Language | Words (surface-locating) | Words (cumulative-length) |
|---|---:|---:|
| Amharic | 22,907 | **123,761** |
| Tigrinya | 18 | **205** |
| Tigre | 2,457 | 2,457 |
| Ge'ez | 45 | **173** |

The full annotated datasets are now evaluated. Only monomorphemic words — which
carry no gold boundary — are skipped, matching the official
`segmentable_only=True` behaviour. Aggregation likewise follows the official
micro-average (Σmatched / Σpredicted).
