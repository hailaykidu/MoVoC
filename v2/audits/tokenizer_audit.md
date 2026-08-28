# Tokenizer audit

> **Extracted from archive.** This audit was originally extracted from `v2/table4/REPRODUCTION_STATUS.md (section 5)`.
> That file is now archived at `../archive/table4_reproduction_status_superseded.md`.
> See [`docs/duplicate_document_inventory.md`](../../docs/duplicate_document_inventory.md).

> Content is extracted verbatim from the archived `REPRODUCTION_STATUS.md`. Conclusions are
> unchanged; this file exists so each audit is separately citable.

## 5. Tigre and Ge'ez — documented cross-lingual assumption

**No MoVoC-Tok artifact exists for Tigre or Ge'ez at any vocabulary size.** The
repository contains MoVoC-Tok only for Amharic and Tigrinya (32k and 63k). This
follows from the paper itself (Sec. 4.1):

> "These annotations are applied for testing purposes only and are not part of
> the vocabulary since we did not get data for BPE training."

Table 4 nonetheless reports MoVoC-Tok rows for Tigre and Ge'ez, so those rows
must be produced by applying a tokenizer trained on another language. **The paper
does not state which.**

This reproduction applies the **32k Tigrinya MoVoC-Tok** (`movoc_tok_32k_tigrinya`)
cross-lingually to both, on the grounds that Tigrinya is the nearest trained
Ethio-Semitic relative and Ge'ez is the shared ancestor of both. This is an
assumption, not a documented method.

It is recorded as `cross-lingual (assumption)` in `table4_final.csv` and
`dataset_statistics.csv`, so the two affected rows are identifiable in the data
rather than only in prose. The Amharic and Tigrinya rows use in-language 32k
models and are unaffected by this assumption.
