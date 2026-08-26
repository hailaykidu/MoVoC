# Discussion

Scope: reconstruct, organize, reproduce, audit and document the original work.
V2 introduces no new claims, metrics, task definitions or evaluation protocols.

## Reproduction outcome

Using the released metric implementation without modification:

| Table | Metric | Reproduces? |
|---|---|---|
| 2 | MorphScore | Values do not match published; ranking (MoVoC-Tok highest) holds in 3 of 4 languages |
| 3 | BLEU / chrF++ | Not reproducible — the checkpoints, decoded predictions and scoring script behind the published values are not preserved, and the reconstruction is undertrained regardless (see Table 3 caveat) |
| 4 | Boundary precision | Values do not match published; ranking (MoVoC-Tok highest) holds in 3 of 4 languages |
| 4 | Rényi entropy | Values do not match published; entropy is not part of this reconstruction's headline claim (see `v2/table4/Intrinsic_report.md`) |

## Audit record

Three candidate explanations for the intrinsic gap were audited and settled from
the released code:

| Candidate | Verdict | Effect |
|---|---|---|
| Entropy normalisation | Confirmed: `H_α / log(support)` | Entropy moved to the published order of magnitude |
| Boundary projection | Confirmed: cumulative morpheme lengths | Evaluable set grew substantially |
| Item counts | Corrected: Amharic reaches 80,000 | Set size eliminated as a factor |

Each correction was effective against its own target; the precision gap persisted
through all three. The residual is therefore attributable to none of them.

The audits further record that off-by-one dominates the error profile (42%
Amharic, 54% Ge'ez of predicted boundaries), and that MoVoC-Tok and BPE show
near-identical error profiles (≤0.8pp on every category) — the effect applies
equally to both arms. See [`../audits/precision_audit.md`](../audits/precision_audit.md).

## Result under the approved methodology

The AMSEG intrinsic evaluation (`amseg/evaluation/results/`) superseded the
run summarised above and is now the authoritative Table 2/4 result. Under it,
MoVoC-Tok leads boundary precision and MorphScore in three of four languages
— Amharic, Tigrinya and Tigre — with a near-tie against BPE on the fourth,
Ge'ez (precision 0.4301 vs 0.4326; MorphScore 0.6561 vs 0.6667). Tigre and
Ge'ez are both cross-lingual rows: no dedicated MoVoC-Tok artifact exists for
either, so the Tigrinya-trained model is applied to both.

The disagreement previously recorded between this run and a separate
three-arm run is resolved — the two agree to within rounding, since they use
the same underlying methodology and data. See
[`../table4/Intrinsic_report.md`](../table4/Intrinsic_report.md) for the full
history, including the entropy-normalisation and boundary-projection audits
above, which still explain why none of these numbers match the published
values.

## Evaluation data

Three of four languages cannot be evaluated at the paper's stated item counts
from the released annotations. Tigrinya reaches 5,224 scorable items against a
stated 80,000. The constraint is gold annotation coverage, not corpus size. See
[`../audits/dataset_audit.md`](../audits/dataset_audit.md).
