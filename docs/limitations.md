# Limitations

> **Canonical version.** A synchronized copy exists at `v2/reports/limitations.md`.
> Edit here first, then mirror the change. See
> [`docs/duplicate_document_inventory.md`](duplicate_document_inventory.md).

What this repository could not establish, stated plainly.

## 1. Absolute intrinsic values differ from the published results, while the central claim is preserved

Both Table 2 (MorphScore) and Table 4 (boundary precision) produce absolute values 
below their published counterparts, using the **official metric implementation without 
modification**. Two independent reconstruction runs on different evaluation data reach 
the same shortfall. However, the central claim of the paper — that MoVoC-Tok outperforms 
BPE on boundary precision — is preserved across three of four languages.

The metric is fully pinned — formula, aggregation, projection and tokenizers are
all taken from the released code. The audited corrections (entropy normalisation,
boundary projection) were each confirmed effective against their own
target, and the gap persisted through them.

Part of this gap has a specific, now-identified cause (see item 2): the
published Table 2's "No. Items" column was not the intrinsic evaluation set
size at all, so the earlier framing of this as an item-count shortfall
measured against the paper's own evaluation scale was itself based on a
miscaptioned column, not a genuine reproduction failure of that scale.

## 2. Table 2's "No. Items" column named the wrong dataset

The published Table 2 caption reads "Languages for which we created
morphological datasets with the corresponding MoVoC-Tok tokenizer's
MorphScore." Its "No. Items" column (80,000 / 80,000 / 20,000 / 32,000) was,
on the author's review after revisiting the paper, an estimated **combined
total across every dataset used anywhere in the project for that
language** — MoVoC vocabulary-construction data (both the BPE-training half
and the morphological-analysis half) *and* the Machine Translation training
and evaluation datasets, all pooled together — not the size of the intrinsic
MorphScore evaluation set.

For all four languages, intrinsic evaluation actually relied on the annotated
morpheme test set built specifically to assess segmentation quality. The
current (AMSEG) evaluation set sizes are:

| Language | AMSEG evaluation set (intrinsic MorphScore/precision) |
|---|---:|
| Amharic | 81,224 |
| Tigrinya | 5,224 |
| Ge'ez | 172 |
| Tigre | 1,974 |

These are not shortfalls against the published "No. Items" column — that
column described a different dataset entirely, and comparing the two is not
meaningful. `v2/table2/final_report.md` documents an earlier investigation
that treated the published counts as an evaluation-scale target and searched
for surface-aligned annotations to reach it; that investigation's mechanics
(surface-alignment as the binding constraint on how much of the annotated set
is scorable) remain accurate, but its framing of the published counts as the
correct target does not.

Separately and still true: unannotated text is plentiful —
`annotation_template_tigrinya.json` holds 20,000 frequency-ranked Tigrinya
words, every one `annotation_status: pending`, none with morpheme fields
filled — so gold annotation, not corpus availability, remains the actual
constraint on how large any language's evaluation set could grow.

## 3. No MoVoC-Tok artifact exists for Tigre or Ge'ez

The paper (Sec. 4.1) states no training data was obtained for these languages,
yet Table 4 reports MoVoC-Tok rows for both. A cross-lingual substitute is
therefore required and **the paper does not say which**. This reproduction applies
the 32k Tigrinya model and marks the two affected rows as an assumption.

The `models/movoc_tok_merges_{geez,tigre}.txt` artifacts in this repository are
**reconstructions built after publication**, not original released artifacts.

## 4. Table 3 MT evaluation — inconsistency clarified

The original paper contains an internal inconsistency regarding Geʿez:
- §4.2 claims "no parallel data was obtained" for Geʿez
- Table 3 reports Geʿez MT evaluation results
- These were based on zero-shot evaluation using Mermru.com data (Biblical Christian textbooks)

Version 2 of the paper clarifies this inconsistency by explicitly documenting Mermru.com as a Geʿez parallel data source.

**What limits Table 3 reproduction:**
- The scoring script that produced the published Table 3 is not preserved,
  along with the trained checkpoints and decoded predictions behind it.
- The metric scale of the published BLEU column is unresolved (0.048–0.246 is
  inconsistent with sacreBLEU's 0–100 scale).
- For Geʿez zero-shot evaluation: the exact training seeds and scoring pipeline are unavailable, so the exact published numbers cannot be reproduced. However, Mermru.com data (the original source) and zero-shot methodology are available for reconstruction.
- **Undertraining and non-convergence:** As reconstructed, all nine runs stopped at 
  75,000 optimizer steps—approximately 5.5× fewer than a comparably trained MarianMT 
  baseline (~416,000 steps). Training loss did not converge, remaining between 3.00 
  and 3.59. BLEU remained below 2 across all 18 cells, far below a regime where 
  differences in BLEU or chrF++ can be meaningfully interpreted. Observed differences 
  are more likely to reflect training conditions than genuine tokenizer quality differences. 
  A meaningful comparison would require rerunning with full training budget and convergence.
- MoVoC-Tok reconstruction runs produce degenerate output and are flagged.

## 5. An internal contradiction — resolved

Two earlier intrinsic runs in this repository disagreed on Tigre's winner: a
three-arm run had MoVoC-Tok ahead (56.3 vs 53.8 precision), a held-out run had
BPE ahead (60.4 vs 46.3). This is now resolved: the AMSEG intrinsic evaluation
(`amseg/evaluation/results/`), now authoritative for Tables 2 and 4, agrees
with the three-arm run to within rounding — MoVoC-Tok leads Tigre precision
(0.5629 vs 0.5380). The held-out run's contrary result is treated as
superseded, not as an open contradiction. See
[`../v2/table4/Intrinsic_report.md`](../v2/table4/Intrinsic_report.md).

## 6. Scope

These are statements about artifact availability in this repository. V2
reconstructs, reproduces, audits and documents the original work within its
published scope.
