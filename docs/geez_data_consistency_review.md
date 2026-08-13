# Ge'ez parallel data — consistency review

Documentation review of how Ge'ez parallel data is described across the
repository. **No numerical result, evaluation methodology or table was
modified.** Wording only.

## 1. Published statement

The paper states that Ge'ez was evaluated **only intrinsically** because
parallel data was not available:

> "To balance the data, we limited each language pair to 100 sentence pairs:
> Amharic (100 of 213 available), Tigrinya (74 from OPUS plus 26
> human-validated), Tigre (45 from OPUS plus 55 human-validated), and Ge'ez
> (100 newly created and validated). **Due to the absence of parallel data,
> Ge'ez was evaluated only intrinsically.**"

Located in the paper's Sec. 4.2, quoted in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). Sec. 5.1 likewise describes the MT
model as trained between English and Amharic and Tigrinya only, with Tigre added
at evaluation for zero-shot assessment; Ge'ez is not named as an MT evaluation
language there.

## 2. Table 3 statement

The published Table 3 nonetheless reports an **English→Ge'ez block** (BPE
0.0480, WordPiece 0.0550, MoVoC-Tok 0.0660 BLEU). Recorded verbatim in
[`../original/published_results/README.md`](../original/published_results/README.md).

**These two statements are in tension within the published paper.** This
repository records the tension rather than resolving it, and makes no claim that
the reported figures are wrong.

## 3. Reconstruction V2 Ge'ez data source

V2 assembled its own Ge'ez parallel set for the V2 evaluation workflow:

| Property | Value |
|---|---|
| Corpus | Mermru English–Ge'ez parallel corpus |
| Origin | <https://mermru.com/>, distributed via `Bedru/Eng-Geez` on the HuggingFace Hub |
| Total pairs | 2,107 (after dropping empty sides and exact duplicates) |
| Held out | 100, `random.Random(42).sample` |
| Location | `data/evaluation/geez/` |

Provenance is recorded in `data/evaluation/geez/manifest.json`, whose stated
purpose is *"additional zero-shot English→Ge'ez evaluation; NOT a reproduction of
the published Table 3 Ge'ez score."*

**This is a V2 resource, not a recovery of the publication-period data.** It does
not reproduce the published Ge'ez block, and V2 did not change the methodology,
introduce a new task, or introduce a new evaluation metric — the Ge'ez set is
evaluated zero-shot with the same BLEU/chrF++ protocol used for the other
languages.

## 4. Repository updates made

| File | Change |
|---|---|
| `data/evaluation/manifest.json` | Ge'ez entry read `"source": "none -- no parallel data"`, contradicting the 2,107 pairs present in `data/evaluation/geez/`. Now records the Mermru source, pair counts, split seed, and that it is a V2 resource. |
| `docs/REPRODUCIBILITY.md` | Artifact table said the Ge'ez MT evaluation set was **absent** and that `data/evaluation/` held only three languages. Now states the set was assembled for V2, with source and split, and marks it as not a reproduction. |
| `docs/REPRODUCIBILITY.md` | "Consequence" section said no Ge'ez parallel data is present. Now distinguishes publication-period data (not recovered) from the V2 set (assembled), preserving the finding that the published block cannot be reproduced. |
| `v2/reports/limitations.md`, `docs/limitations.md` | "No held-out Ge'ez evaluation set exists" now reads that none from the publication period was recovered, and notes the V2 set explicitly. |

Files reviewed but **not changed**, because their Ge'ez wording was already
accurate: `README.md`, `data/README.md`, `v2/README.md`,
`v2/table3/MarianMT_report.md`, `v2/table3/README.md`,
`v2/paper/manuscript/main.tex`, `v2/paper/*_notes.md`,
`original/published_results/README.md`, `v2/audits/*`.

The manuscript required no change: it does not claim Ge'ez MT results, and its
limitations section already scopes Ge'ez to intrinsic evaluation with a
cross-lingual tokenizer.

## 5. Consistency status

| Check | Status |
|---|---|
| Published statement (Sec. 4.2) recorded verbatim | consistent |
| Published Table 3 Ge'ez block recorded verbatim | consistent |
| V2 Ge'ez source documented with provenance and split | consistent |
| Published vs V2 Ge'ez data distinguished everywhere | consistent |
| Manifest matches the files on disk | consistent (was contradictory) |
| Manuscript makes no Ge'ez MT claim | consistent |

**Status: consistent.** Every location that discusses Ge'ez parallel data now
distinguishes (A) what the published paper states from (B) what Reconstruction
V2 assembled, and no document asserts that Ge'ez parallel data is absent from
the repository while the V2 set is present in it.
