# Reproducibility notes

This document records what can and cannot be reproduced from the artifacts
released in this repository, and where the paper and the released code
leave a question open.

It **does not revise, correct, or dispute any claim in the paper.** Where
the paper says two things that do not sit together, both are quoted and the
question is left open. The purpose is to make the reproduction scope
explicit, so that a reader knows exactly which figures this repository can
regenerate and which it cannot.

---

## Published MoVoC results

The paper reports intrinsic results in Table 2, translation results in
Table 3, and further analysis in Table 4. **Those are the published
results of the MoVoC paper.** They were produced by the authors under the
experimental conditions described in the paper, and this repository does
not restate, revise or supersede them.

The README cites Table 3 verbatim for reference. No number in this
repository replaces or updates any published value.

---

## Available artifacts

**Preserved in this repository:**

| Artifact | Location |
|---|---|
| Morpheme annotations, four languages | `data/annotations/{amharic,tigrinya,tigre,geez}/` |
| Pre-tokenization and morphological analysis (Sec. 3.1) | `movoc/preprocessing.py`, `movoc/hornmorph.py`, `movoc/annotation.py` |
| Vocabulary construction (Sec. 3.2) | `movoc/vocabulary.py`, `train.py` |
| MoVoC-Tok constrained merges (Sec. 3.3) | `movoc/tokenizer.py` |
| Intrinsic metrics (Sec. 5.2) | `movoc/metrics.py`, `evaluate.py` |
| Extrinsic evaluation code (Sec. 5.1) | `evaluation/finetune_marianmt.py`, `evaluation/translate_eval.py` |
| Baseline tokenizers | `data/vocabulary/` |
| Evaluation sets | `data/evaluation/` |

**Not preserved:**

| Artifact | Status |
|---|---|
| Trained model checkpoints from the publication period | not available |
| Generated predictions behind Tables 2–4 | not available |
| The scoring pipeline that produced Table 3 | not available |
| Training logs, SLURM records and seeds for the reported runs | not available |
| A held-out Ge'ez parallel evaluation set | not available |
| The repository state referenced by the paper | not available |

---

## Reconstruction effort

Because the original artifacts are not fully available, the methodology and
evaluation pipeline described in the paper were reconstructed, so that the
approach can be run and inspected.

**This is verification work, not historical reproduction.** Anything it
produces is a *reconstructed evaluation following the published
methodology, not the original reported results*. It does not recover the
original runs, does not produce replacement values for the published
tables, and makes no claim to reproduce them. Its purpose is to
confirm that the described method executes end to end and to make the
pipeline available to readers.

Outputs of the reconstructed pipeline are written under
`experiments/tokenizer_comparison/` and are deliberately **not published in
the README**, for the reasons documented in the sections below: the
original scoring pipeline is unavailable, the metric scale of the published
BLEU column is unresolved, and no held-out Ge'ez evaluation set survives.

The sections that follow are the detailed evidence inventory behind these
statements — what was searched, what was found, and what remains open. They
record limitations; they do not fill gaps with reconstructed values.

---

# Evidence inventory

What follows records, item by item, what was searched and what was found.

---

## 1. English→Ge'ez (Table 3) — not reproducible from released artifacts

### What the paper says

**Table 3** reports an English→Ge'ez block:

| Strategy | BLEU↑ | chrF++↑ |
|---|---|---|
| BPE | 0.0480 ± 0.0070 | 3.0500 ± 0.55 |
| WordPiece | 0.0550 ± 0.0065 | 3.2500 ± 0.60 |
| MoVoC-Tok | 0.0660 ± 0.0060 | 3.9500 ± 0.50 |

and its caption reads: *"Translation performance of BPE, WordPiece, and
MoVoC-Tok for English to Amharic, Tigrinya, Tigre, and Ge'ez."*

**Section 4.2** states, of the same language:

> "To balance the data, we limited each language pair to 100 sentence
> pairs: Amharic (100 of 213 available), Tigrinya (74 from OPUS plus 26
> human-validated), Tigre (45 from OPUS plus 55 human-validated), and
> Ge'ez (100 newly created and validated). **Due to the absence of parallel
> data, Ge'ez was evaluated only intrinsically.**"

Section 5.1 likewise describes the MT model as trained "between English and
two low-resource Ge'ez script languages: Amharic and Tigrinya", with Tigre
added at evaluation for zero-shot assessment. Ge'ez is not named as an MT
evaluation language in that description.

### What this repository contains

| Artifact | Status |
|---|---|
| Ge'ez parallel corpus from the publication period | **absent** |
| Ge'ez MT evaluation set | **assembled for Reconstruction V2** — `data/evaluation/geez/` (Mermru English–Ge'ez corpus, 2,107 pairs, 100 held out at seed 42). Not a reproduction of the published Table 3 Ge'ez block. |
| Manifest entry | `data/evaluation/manifest.json` records the V2 source and split for Ge'ez; see also `data/evaluation/geez/manifest.json` |
| Ge'ez morpheme annotations | **present** — `data/annotations/geez/manual_morphemes.json` (193 entries), used for intrinsic evaluation |

One inconsistency exists inside the released code itself and is recorded
here rather than silently corrected: `evaluation/finetune_marianmt.py`
declares `EVAL_BENCHMARK = {..., "geez": "opus"}`, implying an OPUS
evaluation source for Ge'ez, while the paper's own Sec. 4.2 states that Ge'ez
was evaluated only intrinsically due to the absence of parallel data.

### Consequence

**The English→Ge'ez block of Table 3 cannot be reproduced from the
artifacts released here.** No Ge'ez parallel evaluation data from the
publication period was recovered, and no procedure is described in the paper
or implemented in this repository that would produce the published
translation scores for a language stated in Sec. 4.2 to have no parallel data.

Reconstruction V2 assembled its own Ge'ez parallel set for zero-shot
evaluation (`data/evaluation/geez/`, Mermru English–Ge'ez corpus, 2,107 pairs,
100 held out at seed 42). **It is a V2 resource, not a recovery of the
published one**, so it does not reproduce the published block.

This is recorded as an open question, not as a claim that the reported
figures are wrong.

The Ge'ez *intrinsic* evaluation — MorphScore, boundary precision, Rényi
entropy over the annotated morpheme set — is unaffected and remains
reproducible.

### What the repository contains

**Not available in the current MoVoC repository:** any English-Ge'ez
parallel corpus, any held-out Ge'ez evaluation split, and any Ge'ez
predictions or references from the published runs.

`data/annotations/geez/manual_morphemes.json` (193 entries) is present and
supports the intrinsic evaluation the paper describes for Ge'ez.

Investigation of Ge'ez corpus provenance carried out outside this
repository is recorded in
[`HISTORICAL_INVESTIGATION.md`](../v2/archive/historical_investigation.md). That
material is external evidence, not repository content.

## 2. Translation directions — three distinct scopes

The paper, the released training configuration, and Table 3 describe
overlapping but different sets of language pairs. Conflating them is the
main source of confusion, so they are separated here.

### 2a. Language pairs discussed in the paper

Section 5.1 describes the model as performing translation *"between English
and two low-resource Ge'ez script languages: Amharic and Tigrinya"*. The
word "between" is directionally ambiguous.

Section 6 contains one qualitative example framed as **Amharic → English**:

> "For example, in Amharic → English translation, the sentence ቤቱን አላየሁም was
> segmented more coherently by MoVoC, enabling the correct rendering as
> 'I did not see the house'."

This is an illustration of segmentation quality in the discussion. It is
not a Table 3 entry and no score is attached to it.

### 2b. Actual fine-tuning directions

The released configuration is unambiguous:

```python
# evaluation/finetune_marianmt.py
TRAINING_PAIRS   = ("en-am", "en-ti")
ZERO_SHOT_PAIRS  = ("en-tig",)
BASE_MODEL       = "Helsinki-NLP/opus-mt-en-ti"
```

Fine-tuning covers **English→Amharic** and **English→Tigrinya** only. Tigre
is excluded from training entirely and appears at evaluation to measure
zero-shot transfer, matching Sec 5.1.

The base checkpoint is a **single-direction** English→Tigrinya model. It
has no English decoder, so reverse directions cannot be produced by
fine-tuning it, irrespective of what evaluation data is supplied.

### 2c. Evaluation directions reported in Table 3

Table 3 reports **four blocks, all English→X**: Amharic, Tigrinya, Tigre,
Ge'ez. Three tokenizer strategies are compared in each: BPE, WordPiece,
MoVoC-Tok.

**Amharic→English and Tigrinya→English appear nowhere in Table 3.**

### Summary

| Scope | Directions |
|---|---|
| Discussed in the paper | English↔Amharic, English↔Tigrinya ("between"); one qualitative Amharic→English example |
| Fine-tuned (released config) | English→Amharic, English→Tigrinya |
| Evaluated in Table 3 | English→Amharic, English→Tigrinya, English→Tigre (zero-shot), English→Ge'ez |
| Reproducible here | English→Amharic, English→Tigrinya, English→Tigre (zero-shot) |

`evaluation/translate_eval.py` accepts `en-am`, `en-ti` and `en-tig`, and
rejects any other direction at argument-parse time rather than producing a
number that could be mistaken for a Table 3 result.

An earlier evaluation attempt in this repository did include `am-en` and
`ti-en`. Every such run scored ≈0 BLEU, including the arm whose vocabulary
was left untouched — the measurement reflected the single-direction base
model, not the tokenizers. Those runs are documented in
[`incidents/2026-07-28-invalid-mt-evaluation/`](../v2/archive/incidents/2026-07-28-invalid-mt-evaluation/)
and are not results.

---

## 3. Metric scale and implementation — unresolved

**Summary.** The released repository contains evaluation utilities based on
chrF scoring for individual model evaluation. However, the original Table 3
evaluation pipeline, including the tokenizer-wise BLEU and chrF++
computation, could not be recovered. The reconstructed evaluation therefore
uses a documented sacreBLEU-based implementation with fixed metric
signatures.

The paper cites BLEU (Papineni et al., 2002) and chrF++ (Popović, 2017) but
does not name an implementation, and the reported values do not sit on a
single consistent scale.

### What the repository contains

**Not available in the current MoVoC repository:** the scoring pipeline
that produced Table 3. No script in this repository computes BLEU and
chrF++ across three tokenizer arms over the paper's evaluation sets, and
no stored predictions, references or metric logs from the published runs
are present.

`evaluation/translate_eval.py` is the extrinsic evaluation code this
repository provides. It is part of the reconstruction, not an artifact of
the published runs.

Searches for the original pipeline outside this repository are recorded in
[`HISTORICAL_INVESTIGATION.md`](../v2/archive/historical_investigation.md).

### What this means for future runs

A corrected reproduction of the Amharic, Tigrinya and Tigre blocks is
possible from released artifacts: the corpora, tokenizers, training script
and evaluation sets are all present, and
`evaluation/translate_eval.py` scores BLEU and chrF++ (`word_order=2`) on
the paper's 100-pair OPUS sets.

**Such a run would be a modern, reproducible evaluation of the MoVoC
tokenizers. It would not be an exact reproduction of the published
Table 3**, and must not be presented as one. The original scoring pipeline
is unrecovered, so no run performed now can be shown to follow the same
procedure, and the scale of the published BLEU column is still unknown —
meaning a new result cannot be checked for agreement with the old one in
either direction.

Any figures produced in future should therefore be reported as a
**reconstructed evaluation following the MoVoC experimental methodology**,
with the protocol named alongside them, and kept visibly distinct from the
paper's reported values.

### Metric implementation used by the reconstructed pipeline

Because the original could not be recovered, the reconstructed evaluation
fixes its own and records the signatures, so every figure it produces is
traceable to an exact metric configuration:

| Metric | Call | Signature |
|---|---|---|
| BLEU | `sacrebleu.metrics.BLEU().corpus_score(hyps, [refs])` | `nrefs:1\|case:mixed\|eff:no\|tok:13a\|smooth:exp\|version:2.6.0` |
| chrF++ | `sacrebleu.metrics.CHRF(word_order=2).corpus_score(hyps, [refs])` | `nrefs:1\|case:mixed\|eff:yes\|nc:6\|nw:2\|space:no\|version:2.6.0` |

Both are on a 0–100 scale. `word_order=2` is chrF++, matching the metric
the paper reports; sacreBLEU's default `word_order=0` would be plain chrF.

The signatures are asserted at run time: `run_evaluation.py --verify` fails
if the installed sacreBLEU produces anything other than the values recorded
in `configs/tokenizer_comparison.yaml`, so a library upgrade cannot silently
change what the reported numbers mean.

In every Table 3 row, chrF++ is 40–75× BLEU:

| Block | Strategy | BLEU | chrF++ | ratio |
|---|---|---|---|---|
| En→Am | MoVoC-Tok | 0.2455 | 17.85 | 72.7× |
| En→Ti | MoVoC-Tok | 0.2050 | 8.10 | 39.5× |

Read on a common 0–100 scale, that ratio is atypical — published MT results
usually place chrF++ within roughly 2–4× BLEU. Read with BLEU on 0–1 and
chrF++ on 0–100, En→Am MoVoC-Tok becomes 24.55 BLEU against 17.85 chrF++,
which inverts the relationship normally seen for morphologically rich
targets.

`evaluation/translate_eval.py` scores with sacrebleu, which emits 0–100 for
both metrics.

**Consequence for reproduction:** until the scale of the reported figures is
confirmed, a reproduction cannot be compared against Table 3 in either
direction. A faithful run could appear to differ by two orders of magnitude,
and a failed run could appear to agree. No comparison against the published
numbers is made in this repository, and none should be inferred from a
generated table.

---

## 4. Limitations summary

These are recorded as limitations of the available artifacts. **None is
filled with a reconstructed value.**

| Limitation | Consequence |
|---|---|
| The Table 3 scoring pipeline is not available in the current MoVoC repository | No run performed now can be shown to follow the published procedure |
| The metric scale of the published BLEU column is unresolved | Reconstructed figures cannot be checked against Table 3 in either direction |
| No held-out Ge'ez parallel evaluation set is available in the current MoVoC repository | The English→Ge'ez block cannot be regenerated at all (§1) |
| No checkpoints, predictions, logs, seeds or job records from the publication period are available in the current MoVoC repository | The reported runs cannot be inspected or re-scored |
| The repository state referenced by the paper is not available in the current MoVoC repository | The implementation as it stood at publication cannot be examined |

**No BLEU or chrF++ figures are reported in this repository**, and the
published Table 3 is neither restated as reconstructed output nor
supplemented with reconstructed values.

A separate defect, found and fixed during the reconstruction, is recorded
in [`incidents/2026-07-28-invalid-mt-evaluation/`](../v2/archive/incidents/2026-07-28-invalid-mt-evaluation/):
checkpoints produced before `align_special_tokens()` existed carried a
`generation_config` inherited from the base model and could not yield valid
figures. That record is kept as debugging evidence, and its numbers are not
results.

### Summary

The MoVoC repository contains the method implementation and the data
resources. It contains no experimental record for Tables 2, 3 or 4: no
checkpoints, no predictions, no scoring pipeline, no training logs, no
job records and no seeds.

Searches conducted outside this repository are recorded separately in
[`HISTORICAL_INVESTIGATION.md`](../v2/archive/historical_investigation.md). Nothing
found there is MoVoC repository content.

