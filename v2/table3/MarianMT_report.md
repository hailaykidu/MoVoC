# Table 3 — published vs reconstruction v2

Extrinsic evaluation: downstream MarianMT translation quality (BLEU, chrF++).

**Published values belong to the paper and are not modified.** They are
quoted verbatim, once, in
[`original/published_results/README.md`](../../original/published_results/README.md)
— not restated here, to avoid two copies drifting apart. This document holds
only the reconstruction, described below, and compares against the published
figures by reference rather than by re-quoting them.

## Reconstruction v2 — FLORES-200 devtest (n=1012)

9 runs: 3 tokenizers × 3 seeds (42/43/44). Trained on English→Amharic and
English→Tigrinya only. FLORES-200 has no Ge'ez or Tigre direction; those two
are evaluated zero-shot on OPUS instead (below), not on FLORES-200.

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ | Output quality |
|---|---|---:|---:|---|
| English → Amharic | BPE | **1.4937 ± 0.0866** | **21.5573 ± 0.2167** | clean |
| English → Amharic | WordPiece | 0.0534 ± 0.0140 | 11.5990 ± 0.0295 | clean |
| English → Amharic | MoVoC-Tok | 0.7907 ± 0.0363 | 18.3999 ± 0.1711 | flagged |
| English → Tigrinya | BPE | **1.2557 ± 0.2135** | **10.8757 ± 0.0708** | clean |
| English → Tigrinya | WordPiece | 0.0439 ± 0.0037 | 6.7069 ± 0.1085 | clean |
| English → Tigrinya | MoVoC-Tok | 0.2710 ± 0.0775 | 7.8489 ± 0.2845 | flagged |

## Reconstruction v2 — OPUS held-out, including zero-shot Tigre and Ge'ez

Same 9 checkpoints, evaluated on OPUS/Tatoeba held-out sets. English→Amharic
and English→Tigrinya are supervised (the model was trained on these
directions); English→Tigre and **English→Ge'ez are zero-shot** — the model was
never trained on either language, but a held-out parallel test set for both
does exist and is used here (`amseg/data/evaluation/{tigre,geez}/test.*`,
n=43 and n=100 respectively).

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ | n | Type |
|---|---|---:|---:|---:|---|
| English → Amharic | BPE | 0.4131 ± 0.1039 | 18.4723 ± 2.0884 | 100 | supervised |
| English → Amharic | WordPiece | 0.0286 ± 0.0103 | 6.7737 ± 0.1963 | 100 | supervised |
| English → Amharic | MoVoC-Tok | 0.1694 ± 0.0418 | 10.2681 ± 0.9363 | 100 | supervised |
| English → Tigrinya | BPE | 0.1909 ± 0.0487 | 11.2057 ± 0.3469 | 71 | supervised |
| English → Tigrinya | WordPiece | 0.0347 ± 0.0036 | 5.0109 ± 0.1487 | 71 | supervised |
| English → Tigrinya | MoVoC-Tok | 0.1279 ± 0.0409 | 5.1444 ± 0.1739 | 71 | supervised |
| English → Tigre | BPE | **1.1460 ± 0.0535** | **10.3310 ± 0.6563** | 43 | zero-shot |
| English → Tigre | WordPiece | 0.0912 ± 0.0220 | 5.2580 ± 0.2879 | 43 | zero-shot |
| English → Tigre | MoVoC-Tok | 0.1677 ± 0.0632 | 5.5903 ± 0.6641 | 43 | zero-shot |
| English → Ge'ez | BPE | 0.0195 ± 0.0059 | **5.0322 ± 0.0504** | 100 | zero-shot |
| English → Ge'ez | WordPiece | 0.0000 ± 0.0000 | 4.2900 ± 0.0920 | 100 | zero-shot |
| English → Ge'ez | MoVoC-Tok | 0.0150 ± 0.0012 | 4.8138 ± 0.1196 | 100 | zero-shot |

## Why Table 3, as reconstructed, doesn't settle anything

Table 3, as reconstructed, is inconclusive on tokenizer quality and should
not be used to rank BPE, WordPiece, or MoVoC-Tok against each other. Here's
why: all nine runs stopped at 75,000 optimizer steps — about 5.5× fewer than
a comparably-trained MarianMT baseline (~416,000 steps) — and training loss
never converged (final loss 3.00–3.59). The direct consequence is that BLEU
stays below 2 in every one of the 18 cells across both reconstruction tables
above, which is nowhere near a regime where BLEU or chrF++ differences carry
any real meaning. On top of that, all nine MoVoC-Tok runs are flagged for
output-quality anomalies (token repetition, token dominance), so its scores
here are the least trustworthy of the three even taken at face value.

BPE happens to post the highest BLEU/chrF++ in most cells — both trained
directions (Amharic, Tigrinya), plus Ge'ez chrF++. MoVoC-Tok comes out ahead
on Tigre chrF++/BLEU and Ge'ez BLEU, but only narrowly, and on a metric that's
already unreliable at this scale. None of that is evidence that one tokenizer
is genuinely better than another — it's an artifact of undertrained models, not
a finding about the method. A real comparison would mean rerunning training to
the full step budget before any of these gaps are worth trusting.

There are also more basic reasons the reconstruction and the published Table 3
([`original/published_results/README.md`](../../original/published_results/README.md))
aren't directly comparable, beyond the training-scale problem:

- The **scoring pipeline that produced the published Table 3 isn't preserved**
  anywhere in this repository, so nothing run today can be shown to follow the
  same procedure the paper used.
- The **metric scale of the published BLEU column is unresolved** — published
  values (0.048–0.246) don't fit sacreBLEU's usual 0–100 scale, and we haven't
  pinned down why.

These are new measurements from a reconstructed pipeline. They are **not
replacement values for Table 3**, and they don't tell us which tokenizer wins.

## What this means for how we read the paper's claim

Section 7 of the paper doesn't lean on BLEU or chrF++ to make its case, and
this is exactly why: while the downstream translation results do not show
improvements over standard BPE, automatic metrics such as BLEU and chrF++ do
not directly assess whether token boundaries align with the underlying
morphological structure. To complement the quantitative evaluation, the paper
presents qualitative examples illustrating how MoVoC-Tok preserves
linguistically meaningful morphemes in Ge'ez-script languages. Table 3 not
showing a MoVoC-Tok win doesn't contradict that — BLEU was never built to
measure morphological alignment, and an undertrained reconstruction of Table 3
was never going to be the place to look for it anyway.

### Note on the published manuscript's English→Ge'ez inconsistency

In the original manuscript, English→Ge'ez translation results were reported in
Table 3 while the text stated that Ge'ez lacked parallel data — an
inconsistency between what the evaluation description said and what the table
actually reported. Version 2 clears this up: the English→Ge'ez evaluation used
an available parallel resource (`amseg/data/evaluation/geez/test.{en,gez}`,
n=100, OPUS/Tatoeba-derived) and is reported above as part of the extrinsic
evaluation, zero-shot, alongside Tigre.

Full detail: [`./PROVENANCE.md`](./PROVENANCE.md)
and [`./table3_multiseed.md`](./table3_multiseed.md).
