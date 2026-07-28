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
figures are wrong. Resolving it requires either the Ge'ez evaluation data
used for Table 3, or a description of the procedure that generated those
numbers. Until then the block is marked **unavailable**, and this
repository reports no Ge'ez MT figures.

The Ge'ez *intrinsic* evaluation — MorphScore, boundary precision, Rényi
entropy over the annotated morpheme set — is unaffected and remains
reproducible.

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

## 3. Metric scale — unconfirmed

The paper cites BLEU (Papineni et al., 2002) and chrF++ (Popović, 2017) but
does not name an implementation, and the reported values do not sit on a
single consistent scale.

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
