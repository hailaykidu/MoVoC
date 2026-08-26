# Table 3 — notes

Source: `v2/table3/table3_final.csv`, `v2/table3/MarianMT_report.md`.

## Publication-ready table

**Table 3: English→X translation quality by tokenization strategy.**
FLORES-200 devtest (n = 1012), mean ± std over seeds 42/43/44.

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ |
|---|---|---:|---:|
| **English → Amharic** | BPE | **1.4937 ± 0.0866** | **21.5573 ± 0.2167** |
| | WordPiece | 0.0534 ± 0.0140 | 11.5990 ± 0.0295 |
| | MoVoC-Tok | 0.7907 ± 0.0363 | 18.3999 ± 0.1711 |
| **English → Tigrinya** | BPE | **1.2557 ± 0.2135** | **10.8757 ± 0.0708** |
| | WordPiece | 0.0439 ± 0.0037 | 6.7069 ± 0.1085 |
| | MoVoC-Tok | 0.2710 ± 0.0775 | 7.8489 ± 0.2845 |

LaTeX: `v2/table3/table3_final.tex`.

## Setup

- MarianMT: 6+6 layers, 8 heads, d_model 512, FFN 2048, tied embeddings.
- One multilingual model per tokenizer, trained on English→Amharic and
  English→Tigrinya.
- Three seeds (42/43/44); mean ± standard deviation reported.
- Scored with sacreBLEU — BLEU `tok:13a|smooth:exp`, chrF++ `nc:6|nw:2`.

## Additional cells in the CSV

`table3_final.csv` also holds OPUS/Tatoeba results and zero-shot Tigre and Ge'ez
evaluation (18 cells total). The main table reports the FLORES-200 block; the
remainder is available for an appendix.

### Note on the published manuscript's English→Ge'ez inconsistency

In the original manuscript, English→Ge'ez translation results were reported in
Table 3 while the text stated that Ge'ez lacked parallel data, creating an
inconsistency between the evaluation description and the reported results. In
Version 2, this inconsistency is clarified: the English→Ge'ez evaluation used
an available parallel resource (`amseg/data/evaluation/geez/test.{en,gez}`,
n=100) and is reported as part of the extrinsic evaluation, zero-shot
alongside Tigre — see the OPUS/Tatoeba block in `v2/table3/MarianMT_report.md`.

## Findings to report — read this before citing a ranking

BPE posts the highest BLEU and chrF++ on both supervised directions, with
MoVoC-Tok second and WordPiece a distant third (en→am: 0.7907 vs 0.0534 BLEU;
en→ti: 0.2710 vs 0.0439). It would be tempting to write that up as "BPE wins,"
but that's not a conclusion this table actually supports.

Table 3, as reconstructed, is inconclusive on tokenizer quality and should
not be used to rank BPE, WordPiece, or MoVoC-Tok. All nine runs stopped at
75,000 optimizer steps — about 5.5× fewer than a comparably-trained MarianMT
baseline (~416,000 steps) — and training loss never converged (final loss
3.00–3.59). BLEU sits below 2 in every one of the 18 cells as a direct result,
far below any regime where these differences are meaningful. MoVoC-Tok's nine
runs are additionally flagged for output-quality anomalies (token repetition,
token dominance), so its numbers are the least trustworthy of the three even
before accounting for the training-scale problem. BPE's apparent lead reflects
an artifact of undertrained models, not evidence that it's the better
tokenizer — that comparison would need training run to the full step budget
first.

chrF++ does separate the systems more cleanly than BLEU at this scale, which
makes sense for morphologically rich targets where character-level overlap
carries more signal than exact n-gram match — but a clearer separation between
undertrained numbers is still a separation between undertrained numbers.

This is why the paper doesn't rest its central claim on Table 3. Section 7
turns to qualitative analysis instead, precisely because BLEU and chrF++ don't
directly assess whether token boundaries align with the underlying
morphological structure — see the discussion in `v2/table3/MarianMT_report.md`.

## Caption draft

> **Table 3.** English→X translation quality by tokenization strategy on
> FLORES-200 devtest (n = 1012), mean ± standard deviation over three seeds. One
> multilingual MarianMT model per tokenizer.
