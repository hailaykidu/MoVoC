# Version 2 reconstruction — machine translation

`table3_reconstruction_v2.json` is a byte-identical copy of
`experiments/multiseed/results/table3_multiseed.json`.

**These results are not a direct reproduction of the published Table 3.**

## The run

| | |
|---|---|
| Experiments | **18** — 2 training languages × 3 tokenizers × 3 seeds |
| Training languages | Amharic, Tigrinya |
| Tokenizers | BPE, WordPiece, MoVoC-Tok |
| Seeds | **42, 43, 44** |
| Completion | all 18 runs completed, 4.5–7.2 h each |
| Evaluation | supervised direction + zero-shot Tigre and Ge'ez = **54 decode passes** |
| Test sets | Amharic n=100, Tigrinya n=71, Tigre n=43, Ge'ez n=100 |
| Decoding | greedy, `num_beams=1`, `max_length=128` |
| Metrics | sacreBLEU 2.6.0 — BLEU `tok:13a|smooth:exp`, chrF++ `nc:6|nw:2` |
| Scored | 18/18 usable, 0 excluded, 0 errors |
| Generated | 2026-07-31 |

The evaluation pipeline is a **reconstruction**: the scoring pipeline behind
the published Table 3 is not available in this repository, so no run
performed now can be shown to follow the same procedure.

## Observed behaviour

**The pipeline reconstruction succeeded**: all 18 runs completed their full
training schedule and all 18 checkpoints decoded without error across 54
passes.

The reconstructed models did not reach a converged translation regime. Final
training loss was 6.5–8.2 against roughly 1–3 for converged MT, and decoded
output is repetitive (mean hypothesis length 155 characters against 11.6 for
the references, with one character occupying about half the output and no
EOS emitted). All 54 scores fall in BLEU 0.0053–0.0411 and chrF++ 0.53–2.91.

**Because none of the systems reached a converged regime, this rerun cannot
rank the tokenizers.** No claim about MoVoC-Tok — superiority or
inferiority — is supported by this run in either direction, and nothing here
should be read as evidence for or against the paper's Table 3 findings.

Standard deviations are small (max 0.0013 BLEU), but this reflects three
seeds behaving consistently within the same unconverged regime —
reproducibility of the run, not resolving power of the measurement.

Full analysis, including training dynamics and the open learning-rate
question: [`../../../docs/MT_Reconstruction_Audit.md`](../audits/mt_reconstruction_audit.md).

## Comparison with the published Table 3

Not performed, and not currently possible. Beyond the unconverged models,
the original scoring pipeline is unavailable and the scale of the published
BLEU column is unresolved. The published values are quoted, with citation,
in [`README.md` §1](../../README.md#1-published-movoc-paper-results); they
are **not** reproduced here and must not be tabulated alongside these
figures.
