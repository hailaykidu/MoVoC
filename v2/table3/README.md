# Version 2 reconstruction — machine translation

**These results are not a direct reproduction of the published Table 3.**

## Provenance

The frozen V2 Table 3 results are derived from `table3_multiseed.json` and
reported in `table3_final.csv`. Run-level records are summarised in
[`PROVENANCE.md`](./PROVENANCE.md).

The configuration in `evaluation/finetune_marianmt.py` corresponds to an older
fine-tuning workflow and is not the source of the V2 reconstruction results;
its learning rate (1.44e-07) is not a V2 Table 3 parameter.

## The run

| | |
|---|---|
| Runs | **9** — 3 tokenizers × 3 seeds, one multilingual model per run |
| Training languages | Amharic, Tigrinya |
| Tokenizers | BPE, WordPiece, MoVoC-Tok |
| Seeds | **42, 43, 44** |
| Completion | 9 launched, 9 completed, 9 valid, 0 excluded |
| Optimizer steps | 75,000 per run |
| Evaluation | supervised directions + zero-shot Tigre and Ge'ez = **54 decode passes** |
| Test sets | FLORES-200 n=1012; OPUS Amharic n=100, Tigrinya n=71, Tigre n=43, Ge'ez n=100 |
| Decoding | greedy, `num_beams=1`, `max_length=128` |
| Metrics | sacreBLEU 2.6.0 — BLEU `tok:13a|smooth:exp`, chrF++ `nc:6|nw:2` |
| Generated | 2026-07-31 |

The evaluation pipeline is a **reconstruction**: the scoring pipeline behind
the published Table 3 is not available in this repository, so no run
performed now can be shown to follow the same procedure.

## Observed behaviour

All 9 runs completed their full training schedule and every checkpoint decoded
without error across 54 passes.

Final training loss was 2.9967–3.5854. Reported BLEU spans 0.0000–1.4937 and
chrF++ spans 4.2900–21.5573 across all cells in `table3_final.csv`.

BLEU below 2 in every cell means none of these runs reached a translation
regime where a BLEU or chrF++ difference is trustworthy. All three tokenizers
were trained under identical conditions, but identical conditions on an
undertrained model don't add up to a fair ranking — see the discussion in
[`MarianMT_report.md`](./MarianMT_report.md) for why this table shouldn't be
read as settling which tokenizer is better.

Per-run records, output-quality flags and their causes:
[`PROVENANCE.md`](./PROVENANCE.md).

## Comparison with the published Table 3

Not performed, and not currently possible. The original scoring pipeline is
unavailable and the scale of the published BLEU column is unresolved. The
published values are quoted, with citation,
in [`README.md` §1](../../README.md#1-published-movoc-paper-results); they
are **not** reproduced here and must not be tabulated alongside these
figures.
