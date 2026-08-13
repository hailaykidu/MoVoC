# Provenance — reconstruction-v2 extrinsic MT

Every aggregate in `table3_multiseed.json` traces to the run-level records
in its `per_run` array. This file summarises run status and validity.

## Runs

| Run ID | Tokenizer | Seed | Steps | Final loss | Status |
|---|---|---:|---:|---:|---|
| bpe_seed42 | BPE | 42 | 75000 | 3.579 | complete |
| bpe_seed43 | BPE | 43 | 75000 | 3.533 | complete |
| bpe_seed44 | BPE | 44 | 75000 | 3.585 | complete |
| movoctok_seed42 | MoVoC-Tok | 42 | 75000 | 3.079 | complete |
| movoctok_seed43 | MoVoC-Tok | 43 | 75000 | 2.997 | complete |
| movoctok_seed44 | MoVoC-Tok | 44 | 75000 | 3.020 | complete |
| wordpiece_seed42 | WordPiece | 42 | 75000 | 3.544 | complete |
| wordpiece_seed43 | WordPiece | 43 | 75000 | 3.483 | complete |
| wordpiece_seed44 | WordPiece | 44 | 75000 | 3.541 | complete |

**9 launched, 9 completed, 9 valid, 0 excluded.** No seed failed and no
run was dropped.

## Evaluation datasets

| Dataset | Split | Directions | n | Type |
|---|---|---|---:|---|
| FLORES-200 | devtest | en-am, en-ti | 1012 | supervised |
| OPUS/Tatoeba | held-out | en-am | 100 | supervised |
| OPUS/Tatoeba | held-out | en-ti | 71 | supervised |
| OPUS/Tatoeba | held-out | en-tig | 43 | zero-shot |
| OPUS/Tatoeba | held-out | en-gez | 100 | zero-shot |

FLORES-200 and OPUS are reported in separate blocks and never merged.

## Output-quality flags

An automated detector flags a cell on empty output, intra-hypothesis
repetition, top-3 token dominance, or length-ratio overrun. Inspection of
the decoded text shows the flags have two distinct causes:

1. **Ge'ez punctuation frequency (not collapse).** MoVoC-Tok en-am FLORES
   trips *top-3 token dominance* only, because the Ge'ez sentence-final
   marker accounts for ~67% of tokens. Those runs produce 1012/1012 unique
   hypotheses with intra-hypothesis TTR 0.58. The threshold is calibrated
   for Latin-script output and is not reliable here.
2. **Genuine repetition.** MoVoC-Tok en-ti FLORES trips *intra-hyp
   repetition* and *runs to length cap* (TTR 0.33, length ratio 3.77).
   Some BPE en-ti output also contains character-level repetition that the
   detector did not flag, so the flag is not reliable in either direction.

Flags are reported as computed. Neither the flags nor the scores are
adjusted.

## Known upstream limitation

Training used 75,000 optimizer steps on 800,000 pairs. A comparable
from-scratch MarianMT (same architecture) used 416,040 steps — 5.5× more.
Final loss here is 3.00–3.59 versus ~3.13 there. BLEU below 2 in every cell
is consistent with a model that has not reached a usable translation regime.
This is recorded, not hidden: the numbers are reported so the reconstruction
is auditable, not because they demonstrate translation quality.
