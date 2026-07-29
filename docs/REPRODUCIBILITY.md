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
| Ge'ez parallel corpus | **absent** |
| Ge'ez MT evaluation set | **absent** — `data/evaluation/` holds `amharic/`, `tigrinya/`, `tigre/` only |
| Manifest entry | `data/evaluation/manifest.json` records Ge'ez as `"source": "none -- no parallel data"`, `"note": "evaluated intrinsically only (paper Sec 5.1)"` |
| Ge'ez morpheme annotations | **present** — `data/annotations/geez/manual_morphemes.json` (193 entries), used for intrinsic evaluation |

One inconsistency exists inside the released code itself and is recorded
here rather than silently corrected: `evaluation/finetune_marianmt.py`
declares `EVAL_BENCHMARK = {..., "geez": "opus"}`, implying an OPUS
evaluation source for Ge'ez, while the manifest in the same repository
records that no such parallel data exists.

### Consequence

**The English→Ge'ez block of Table 3 cannot be reproduced from the
artifacts released here.** No Ge'ez parallel evaluation data is present,
and no procedure is described in the paper or implemented in this
repository that would produce translation scores for a language stated to
have no parallel data.

This is recorded as an open question, not as a claim that the reported
figures are wrong. Until it is resolved the block is marked
**unavailable**, and this repository reports no Ge'ez MT figures.

The Ge'ez *intrinsic* evaluation — MorphScore, boundary precision, Rényi
entropy over the annotated morpheme set — is unaffected and remains
reproducible.

### Provenance search (2026-07-28)

A search of the repository history and the local working environment
located material that bears on this block. It is recorded here because it
narrows the question, though it does not close it.

**A real English–Ge'ez parallel corpus exists and was used for a Ge'ez MT
training run outside this repository.**

| Evidence | Detail |
|---|---|
| Corpus | Mermru English–Ge'ez parallel corpus — **2,107** verse-aligned pairs, biblical text (Genesis creation narrative) |
| Origin | [Mermru](https://mermru.com/), a linguistic and computational resource platform providing Ge'ez resources, including English–Ge'ez parallel corpus resources |
| Accessed via | `datasets.load_dataset("Bedru/Eng-Geez")` (HuggingFace Hub) |
| Cached locally | 2026-07-17 |
| Training script | `mt_finetune/train_mt_gez.py`, which exports it to `data_gez/all.en` / `data_gez/all.gez` and describes it as "real parallel data, not a synthetic pairing" |
| Completed run | `mt_finetune/papermt_repro_train_gez.out` — 792 steps, 3 epochs, final training loss 3.36 |
| Checkpoints | `mt_finetune/mt_output_gez/{checkpoint-500, checkpoint-792, final}` |

The corpus originates from **Mermru** and is reached through the
`Bedru/Eng-Geez` dataset loader. The located artifacts record the loader
path; the Mermru attribution is supplied by the authors and is recorded
here so the corpus is credited to its source rather than to the
distribution channel alone.

`train_mt_gez.py` further notes that this corpus was already listed in
MoVoC_Tok's own `01_collection/corpus_raw/manifest.json` ("Eng-Geez", 2107
rows), but that only the **monolingual Ge'ez side** was kept there, for
tokenizer training — the Ge'ez MT script is the first place in this project
family to use it as an aligned pair.

So Ge'ez MT training was performed, on genuine parallel data, contrary to
what §4.2's "absence of parallel data" would suggest. That corpus is *not*
part of this repository and is not referenced by any released
configuration.

**This resolves the training-data question, not the evaluation
reproducibility question.** Knowing which corpus the model was trained on
does not identify the held-out set the Table 3 Ge'ez figures were scored
against, nor the metric implementation used.

**What is still missing is the scoring step.** The Ge'ez training
directory contains four Python files — `build_model.py`, `train_mt.py`,
`train_mt_am.py`, `train_mt_gez.py` — and none computes BLEU or chrF++.
No scoring script, no predictions file, and no BLEU/chrF log was found
anywhere in that environment. Its own README states the position
explicitly:

> "No held-out eval set is used, matching what the evidence says the
> original did — but this also means there's no independent BLEU/chrF
> signal produced by this run itself; that would need a separate
> evaluation step against a real, disjoint test set."

**Consequence.** The training half of the English→Ge'ez block is
accounted for; the evaluation half is not. Reproducing the Table 3 Ge'ez
figures would still require knowing which held-out Ge'ez test set was
scored and with which metric implementation — neither of which is present
in this repository or in the located artifacts. The block therefore
remains **unavailable**.

The `EVAL_BENCHMARK["geez"] = "opus"` declaration in
`evaluation/finetune_marianmt.py` is **deliberately left in place**. It is
inconsistent with this repository's own manifest, but it is also the only
released trace pointing at a Ge'ez evaluation source, and removing it
would destroy evidence rather than resolve anything.

### Second provenance search (2026-07-28)

A wider search across the local project family — `MoVoC_Tok/`,
`MoVoC_MT/`, `EnTiMT/` — was run specifically for the missing Ge'ez
evaluation artifacts.

**The 100 validated Ge'ez sentence pairs were not found.** No file of that
size exists in any searched directory. The only Ge'ez corpus files located
are the Mermru corpus and its derivatives:

| File | Lines | What it is |
|---|---|---|
| `MoVoC_Tok/01_collection/corpus_raw/geez.txt` | 2,107 | monolingual Ge'ez side of the Mermru corpus |
| `MoVoC_Tok/02_cleaning/corpus_clean/geez.txt` | 2,387 | cleaned Ge'ez text |
| `mt_finetune/data_gez/all.en` / `all.gez` | 2,107 | the aligned pair, exported for MT training |

**No held-out Ge'ez split exists.** Every located Ge'ez file is either the
full 2,107-row corpus or a monolingual derivative of it. Nothing is
partitioned into train/dev/test.

**No Ge'ez evaluation was found.** `MoVoC_MT/05_evaluation/` — the only
directory in the project family containing scoring code — covers Amharic,
Tigrinya and Tigre only. It contains no Ge'ez path, no Ge'ez reference
file, and no Ge'ez entry in either stored report.

**No Table 3 predictions or references were found**, for Ge'ez or any
other language: no hypothesis files, no per-strategy outputs, and no
report containing the three-tokenizer comparison the table presents.

### Corpus-family trace

The requested trace connects cleanly:

```
Mermru (https://mermru.com/)
  └─ distributed as  Bedru/Eng-Geez  (HuggingFace Hub, 2,107 pairs)
       ├─ MoVoC_Tok/01_collection/corpus_raw/manifest.json
       │    records it under both "geez" (2,107 rows, 185,238 chars)
       │    and "english" (2,107 rows, 264,773 chars)
       │    -> only the monolingual Ge'ez side was carried forward,
       │       into corpus_raw/geez.txt, for tokenizer training
       └─ mt_finetune/train_mt_gez.py
            load_dataset("Bedru/Eng-Geez") -> data_gez/all.en + all.gez
            -> the first use of the corpus as an aligned MT pair
```

Both sides of the corpus were catalogued in the manifest from the start;
the tokenizer pipeline kept only the Ge'ez side, and the MT script later
re-fetched the pair from the Hub.

**What this means for the Table 3 Ge'ez block.** Two findings stand, and
both should be preserved:

1. **The 2,107 English–Ge'ez pairs appear to have been used for training.**
   `train_mt_gez.py` exports the full corpus to `data_gez/all.en` /
   `all.gez` and trains on it; a completed run and its checkpoints exist.

2. **No surviving artifact identifies a valid held-out Ge'ez evaluation
   set.** No 100-pair file, no train/dev/test split of the Ge'ez corpus, no
   Ge'ez reference or prediction file, and no Ge'ez entry in any scoring
   script or stored report.

Since the corpus was used in full for training with no held-out portion,
any Ge'ez Table 3 figure was either scored against that same training data
— which would not be a valid held-out evaluation — or against a set that
does not survive in any searched location. **The artifacts do not
distinguish these possibilities**, so the block remains **unavailable for
reproduction**, and this repository reports no Ge'ez MT figures.

---

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
[`incidents/2026-07-28-invalid-mt-evaluation/`](incidents/2026-07-28-invalid-mt-evaluation/)
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

### Provenance search (2026-07-28)

An initial search of this repository and the `mt_finetune/` training
environment found no scoring code — those four scripts train only, and
that environment's README says so: *"there's no independent BLEU/chrF
signal produced by this run itself."*

**A scoring implementation was subsequently located in a separate project
directory**, `MoVoC_MT/05_evaluation/`. It uses **sacreBLEU**:

```python
# MoVoC_MT/05_evaluation/evaluate.py
import sacrebleu
bleu = sacrebleu.corpus_bleu(hyps, [tgt_lines])
chrf = sacrebleu.corpus_chrf(hyps, [tgt_lines])
```

> **The figures below are NOT MoVoC results and NOT the paper's setup.**
> They are the stored output of that separate script, reproduced here as
> evidence of what it computed — **plain chrF over 2,000 dev pairs**, where
> the paper reports **chrF++ over 100 OPUS pairs**. The mismatch is the
> point: it is why this script cannot be the Table 3 pipeline.

sacreBLEU emits **0–100** for both metrics, and the stored output confirms
that scale:

| Direction | BLEU | chrF *(not chrF++)* | n *(not 100)* |
|---|---|---|---|
| en→am | 11.699 | 33.655 | 2,000 |
| am→en | 20.485 | 45.554 | 2,000 |
| en→ti | 4.556 | 18.634 | 2,000 |
| ti→en | 10.571 | 31.945 | 2,000 |

(`MoVoC_MT/05_evaluation/eval_report.json`, SLURM job 53024.) A companion
script scored Tigre zero-shot: en→tig BLEU 2.713 / chrF 19.405 over 43
pairs.

**For reference, the paper's own evaluation setup is:** chrF++
(`word_order=2`), 100 OPUS sentence pairs per language, English→X
directions only, three tokenizers compared. None of those four properties
matches the script above.

#### Available evaluation tooling vs. the original Table 3 scoring pipeline

These are two different things, and the distinction is the point of this
subsection.

| | Available evaluation tooling | Original Table 3 scoring pipeline |
|---|---|---|
| Artifact | `MoVoC_MT/05_evaluation/evaluate.py` | **not located** |
| Metric library | sacreBLEU | unknown |
| Character metric | plain **chrF** (`word_order=0`) | **chrF++** per the paper |
| Test set | 2,000 held-out dev pairs | 100 OPUS pairs per language |
| Directions | en→am, am→en, en→ti, ti→en | English→X only |
| Systems compared | one model | three tokenizers (BPE, WordPiece, MoVoC-Tok) |
| Ge'ez | absent | reported |

**The located script is not the Table 3 pipeline**, and no evidence
connects its outputs to the published table. What it establishes is that
sacreBLEU was the metric library available in this project family — useful
for interpreting future runs, but not provenance for the published figures.

The companion project's own README is explicit about its relationship to
the paper. `MoVoC_MT/README.md` describes itself as *"the kind of
downstream MT validation the MoVoC paper's own Table 3 describes, but which
the MoVoC project itself never had until now"* — that is, an independent
validation effort, not a reproduction of the Table 3 run.

**Two discrepancies follow, and both remain open.**

*Metric.* The located script calls `corpus_chrf` with its default
`word_order=0`, which is plain **chrF**, not chrF++ (`word_order=2`). Its
own output labels the column `chrF`. The paper reports **chrF++**. So this
script cannot be the one that produced Table 3's chrF++ column, or it was
run with different arguments.

*Scale.* If Table 3's BLEU came from sacreBLEU it would be on 0–100, which
makes the reported 0.2455 an extremely low score rather than the ~24.6 a
0–1 reading would imply — while the accompanying chrF++ of 17.85 sits in
the range this tooling produces on 0–100. The two columns still do not sit
on a consistent scale, and the located artifacts do not resolve which
reading is correct.

So the question of **which** implementation produced Table 3 — sacreBLEU,
Moses multi-bleu, or a custom script — cannot be answered from available
artifacts, and neither can the scale that follows from it.

### Final targeted search (2026-07-28)

A last search was run specifically for the Table 3 generation artifacts,
across this repository, `MoVoC_Tok/`, `MoVoC_MT/`, `EnTiMT/`,
`mt_finetune/` and the HuggingFace cache.

| Sought | Result |
|---|---|
| `word_order=2` / `chrF++` / `CHRF(` in any script | Only in code written for **this** repository during the 2026-07-28 work, and its copies. No pre-existing chrF++ implementation. |
| A tokenizer-loop evaluation (three strategies scored together) | **None.** No script anywhere iterates over BPE / WordPiece / MoVoC-Tok to score them. |
| The literal reported values (0.2455, 0.2150, 17.85, 0.0660 …) | **Not found** in any script, log, report or table. |
| The string "Table 3" | One occurrence, in `MoVoC_MT/README.md`, describing that project as validation the MoVoC project *"never had until now"*. |

**Conclusion of the provenance investigation.** No artifact producing the
published Table 3 figures survives in any searched location. The scoring
tooling that does exist computes plain chrF over 2,000 dev pairs for a
single model; nothing computes chrF++ over 100 OPUS pairs across three
tokenizer arms, which is what Table 3 reports.

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

Both are on a 0–100 scale. `word_order=2` is chrF++; the released
`MoVoC_MT/05_evaluation/evaluate.py` uses the default `word_order=0`, which
is plain chrF — one of the reasons it cannot be the Table 3 pipeline.

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

## 4. Current reproduction status

| Table 3 block | Status |
|---|---|
| English→Amharic | **pending** — requires retraining with the corrected `align_special_tokens()` |
| English→Tigrinya | **pending** — as above |
| English→Tigre (zero-shot) | **pending** — as above; evaluated from the Amharic/Tigrinya checkpoints |
| English→Ge'ez | **unavailable** — see §1 |

The checkpoints produced before `align_special_tokens()` existed carry a
`generation_config` inherited from the base model and cannot yield valid
figures; see
[`incidents/2026-07-28-invalid-mt-evaluation/`](incidents/2026-07-28-invalid-mt-evaluation/).

**No BLEU or chrF++ figures are reported in this repository.** Table 3 is
left without numbers rather than populated with uncertain ones.

### Summary after the provenance search

The provenance search of 2026-07-28 covered this repository's full git
history (all refs, deleted files, unreachable objects) and the local
training environment. Its outcome:

**Reproducible from released artifacts**

- English→Amharic, English→Tigrinya, and English→Tigre (zero-shot)
  fine-tuning and evaluation. The corpora, tokenizers, training script and
  evaluation sets are all present. These require retraining with the
  corrected `align_special_tokens()` before they yield valid figures, but
  nothing is missing.
- All intrinsic evaluation, for all four languages including Ge'ez.

**Unresolved**

- **English→Ge'ez extrinsic reproduction.** The training data is now
  identified — the Mermru English–Ge'ez parallel corpus (2,107 verse-aligned
  pairs, accessed via `load_dataset("Bedru/Eng-Geez")`), together with a
  completed training run located outside this repository. What remains
  missing is the **held-out evaluation set** the Table 3 Ge'ez figures were
  scored against, and the scoring step itself. Identifying the training
  corpus does not resolve this. See §1.
- **Exact comparison against Table 3's numbers.** A sacreBLEU-based
  scoring script was located in `MoVoC_MT/05_evaluation/`, establishing
  what tooling the project family used, but it is **not** the script that
  produced Table 3: it scores plain chrF rather than chrF++, uses 2,000
  held-out dev pairs rather than 100 OPUS pairs, and evaluates a single
  model rather than three tokenizer arms. The scale of Table 3's BLEU
  column remains unresolved. See §3.

Neither is settled by anything in the searched locations. What would settle
them: the held-out Ge'ez evaluation set, and the script that generated the
Table 3 figures themselves. Until those are available, this repository can
reproduce the Amharic/Tigrinya/Tigre experiments on their own terms but
cannot state whether the result agrees with the published table.

**Searched (2026-07-28):** this repository's full git history including all
refs, deleted files and unreachable objects; `mt_finetune/`; `MoVoC_Tok/`;
`MoVoC_MT/`; `EnTiMT/`; and the local HuggingFace cache.
