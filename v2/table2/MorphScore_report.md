# Table 2 — MorphScore

Two categories. Published values are the paper's claims; the AMSEG intrinsic
tokenizer evaluation below is the authoritative reproduction.

---

## A. Published Results

From the paper (arXiv:2509.08812), verbatim. Archived in
[`../../original/published_results/`](../../original/published_results/).

| Language (ISO 639-3) | No. Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 0.710 |
| Tigrinya (tir) | 80,000 | 0.731 |
| Ge'ez (gez) | 20,000 | 0.670 |
| Tigre (tig) | 32,000 | 0.654 |

---

## B. AMSEG Intrinsic Evaluation (authoritative)

Source: `amseg/evaluation/results/intrinsic_tokenizer_table.md` and
`table2_morphscore_movoc_tok.md`, released BPE-32K / WordPiece-32K /
MoVoC-Tok-32K artifacts (`amseg/scripts/evaluate_intrinsic.py`), run against
`data/annotations/`. Authoritative; see [`./`](./).

For all four languages, this is the annotated morpheme test set built
specifically to assess segmentation quality, not a generic text corpus — the
same set used for Table 4's boundary precision. This is why MoVoC-Tok tends
to perform better here than on extrinsic tasks: the test set directly rewards
alignment with morpheme boundaries.

| Language (ISO 639-3) | Tokenizer | No. Items | MorphScore ↑ | Mode |
|---|---|---:|---:|---|
| Amharic (amh) | BPE | 81,224 | 0.4105 | in-language |
| Amharic (amh) | WordPiece | 81,224 | 0.3842 | in-language |
| Amharic (amh) | MoVoC-Tok | 81,224 | **0.4139** | in-language |
| Tigrinya (tir) | BPE | 5,224 | 0.4200 | in-language |
| Tigrinya (tir) | WordPiece | 5,224 | 0.4186 | in-language |
| Tigrinya (tir) | MoVoC-Tok | 5,224 | **0.4366** | in-language |
| Tigre (tig) | BPE | 1,974 | 0.5004 | cross-lingual (Tigrinya model) |
| Tigre (tig) | WordPiece | 1,974 | 0.4778 | cross-lingual (Tigrinya model) |
| Tigre (tig) | MoVoC-Tok | 1,974 | **0.5278** | cross-lingual (Tigrinya model) |
| Ge'ez (gez) | BPE | 172 | **0.6667** | cross-lingual (Tigrinya model) |
| Ge'ez (gez) | WordPiece | 172 | 0.6392 | cross-lingual (Tigrinya model) |
| Ge'ez (gez) | MoVoC-Tok | 172 | 0.6561 | cross-lingual (Tigrinya model) |

MorphScore is boundary **recall**, micro-averaged, unsegmented words excluded.
Values are fractions in [0, 1] (multiply by 100 for a percentage reading).

Tigre and Ge'ez have no dedicated MoVoC-Tok artifact; both are scored with the
Tigrinya-trained MoVoC-Tok as a cross-lingual generalization measurement, not
language-specific training.

**MoVoC-Tok achieves the highest MorphScore among the evaluated tokenizers for
Amharic (0.4139), Tigrinya (0.4366), and Tigre (0.5278).** For Ge'ez —
evaluated exclusively in the cross-lingual setting because it was never a
MoVoC-Tok training language — BPE achieves a slightly higher MorphScore
(0.6667) than MoVoC-Tok (0.6561). Tigre and Ge'ez results measure cross-lingual
generalization; Amharic and Tigrinya results measure in-language performance.

**Both this table and Table 4 fall well below the published record's exact
values** (published MorphScore 0.654–0.731; here 0.38–0.67, over a different
evaluation set entirely — see Difference below). Neither reproduces the
paper's numbers. What holds is the direction consistent with the paper's
central intrinsic claim: MoVoC-Tok scores highest among the tokenizers
compared here in three of four languages, with BPE only narrowly ahead on
the fourth (Ge'ez).

### Tokenization quality — interpretive scope

The main clarification is that Tigre and Ge'ez were not training languages;
their results measure cross-lingual generalization, whereas Amharic and
Tigrinya measure in-language performance. The absolute MorphScore values in
this table should be interpreted only within this study. MorphScore is defined
relative to a specific tokenizer, gold-annotation convention, and evaluation
set, so these values are **not commensurable with those reported by Arnett and
Bergen (2025)**: their 22-language sample contains no Semitic or Ge'ez-script
language and their fusional subset is entirely Indo-European; their evaluation
sets range from 112 to 2,000 items with inconsistent inflectional versus
derivational boundary annotation, which they note "could introduce
uncontrolled variance"; and their scores were computed for a different suite
of monolingual tokenizers. We therefore make no claim of exceeding an external
MorphScore threshold.

While MoVoC-Tok does not score higher than all SentencePiece tokenizer
variants — WordPiece is never highest, but BPE leads on Ge'ez — this indicates
that our hybrid approach instills at least partial morpheme awareness into the
tokenization process. Our intrinsic evaluation results (Table 4) further
inform this: MoVoC-Tok leads on boundary precision in three of four languages
(Amharic, Tigrinya, Tigre), with a near-tie on Ge'ez (0.4301 vs. BPE's 0.4326).
The effect for Amharic and Tigrinya is comparatively modest; the larger,
more clearly separated gains appear on the less-represented, lower-resource
languages, Tigre and Ge'ez, where MoVoC-Tok's cross-lingual application of the
Tigrinya-trained tokenizer is closely competitive with or ahead of the
frequency-driven baselines.

### Difference from published

| Language | Items (published → AMSEG) | MorphScore, MoVoC-Tok (published → AMSEG) | Δ |
|---|---|---|---:|
| Amharic | 80,000 → 81,224 | 0.710 → 0.4139 | −0.296 |
| Tigrinya | 80,000 → 5,224 | 0.731 → 0.4366 | −0.294 |
| Ge'ez | 20,000 → 172 | 0.670 → 0.6561 | −0.014 |
| Tigre | 32,000 → 1,974 | 0.654 → 0.5278 | −0.126 |

Item counts differ from the published figures throughout; the published
Tigrinya/Amharic evaluation pools are far larger than the annotated,
surface-alignable set used here. See Caveats below.

---

## Caveats

- **Evaluation-set sizes differ substantially across languages**, reflecting
  available annotation coverage — this is unchanged from the published setup
  and is not an AMSEG-specific limitation.
- MorphScore is recall-oriented and does not penalise false positives; it is
  reported alongside boundary precision (Table 4) rather than in place of it.
- Tigre and Ge'ez are cross-lingual (Tigrinya-model) results, not
  language-specific training; do not read them as directly comparable to the
  in-language Amharic/Tigrinya rows without that caveat.

Historical detail on the earlier official+fallback pooling methodology (now
superseded by the AMSEG evaluation above) is retained in
[`REPRODUCTION_STATUS.md`](REPRODUCTION_STATUS.md) and
[`../audits/dataset_audit.md`](../audits/dataset_audit.md),
[`../audits/tigrinya_80k_attempt_report.md`](../audits/tigrinya_80k_attempt_report.md).
