# Duplicate document inventory

Five documents exist in two locations. **No document is removed** — the
duplication is deliberate, so that each audit and report is separately citable.
This inventory records which copy is canonical, so an edit to one is never left
unmatched in the other.

## Why this matters

The copies can diverge. During the Ge'ez consistency review, a limitation
statement had to be updated in **both** `docs/limitations.md` and
`v2/reports/limitations.md`; had one been missed, the repository would have
contained two documents disagreeing on a stated limitation.

## Inventory

### Identical bodies, differing sync headers

Both copies carry the same content below the sync header. Verified line-by-line
from line 6 onward.

| Source document (canonical) | Duplicate document (synchronized copy) | Scope | Status |
|---|---|---|---|
| `docs/methodology.md` | `v2/reports/methodology.md` | body, 98 lines | identical below header |
| `docs/limitations.md` | `v2/reports/limitations.md` | body, 44 lines | identical below header |

**Canonical:** the `docs/` copy. `docs/` is the repository-wide documentation
root and is where both files were first written; the `v2/reports/` copies exist
so the V2 section is self-contained.

### Section extracts

The audit file reproduces one section of a larger status document, verbatim,
under its own title. The extract is a strict subset, not an equal copy.

| Source document (canonical) | Duplicate document (synchronized copy) | Scope | Status |
|---|---|---|---|
| `v2/table4/REPRODUCTION_STATUS.md` §1 | `v2/audits/entropy_audit.md` | 18/18 lines | verbatim extract |
| `v2/table4/REPRODUCTION_STATUS.md` §2 | `v2/audits/projection_audit.md` | 24/24 lines | verbatim extract |
| `v2/table4/REPRODUCTION_STATUS.md` §5 | `v2/audits/tokenizer_audit.md` | 14/14 lines | verbatim extract |

**Canonical:** `v2/table4/REPRODUCTION_STATUS.md`. It is the complete record of
the Table 4 reproduction and the document the audits were extracted from; each
extract already carries a header naming it as its source.

## Rule

| Role | Meaning |
|---|---|
| **Canonical** | The authoritative copy. Edit here first. |
| **Synchronized copy** | Mirrors the canonical version. Never edit alone. |

When a change is needed:

1. Edit the canonical document.
2. Apply the identical change to the synchronized copy.
3. Confirm agreement before committing.

For the section extracts, only the extracted section is mirrored; the rest of
`REPRODUCTION_STATUS.md` has no counterpart.

## Verification

Each copy carries its own sync header — the canonical file names its copy, the
copy names its canonical — so the first five lines are **expected to differ**.
Compare the bodies, which start at line 6:

```bash
diff <(tail -n +6 docs/methodology.md) <(tail -n +6 v2/reports/methodology.md)
diff <(tail -n +6 docs/limitations.md) <(tail -n +6 v2/reports/limitations.md)
```

Both should produce no output. For the section extracts, each audit file's body
lines should all appear in `v2/table4/REPRODUCTION_STATUS.md`.

## Status

| Pair | Canonical | Copy | In agreement |
|---|---|---|---|
| methodology | `docs/` | `v2/reports/` | yes |
| limitations | `docs/` | `v2/reports/` | yes |
| entropy audit | `v2/table4/REPRODUCTION_STATUS.md` §1 | `v2/audits/` | yes |
| projection audit | `v2/table4/REPRODUCTION_STATUS.md` §2 | `v2/audits/` | yes |
| tokenizer audit | `v2/table4/REPRODUCTION_STATUS.md` §5 | `v2/audits/` | yes |

All five pairs verified in agreement at the time of writing.
