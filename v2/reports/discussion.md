# Discussion

Scope: reconstruct, organize, reproduce, audit and document the original work.
V2 introduces no new claims, metrics, task definitions or evaluation protocols.

## Reproduction outcome

Using the released metric implementation without modification:

| Table | Metric | Reproduces? |
|---|---|---|
| 2 | MorphScore | Values do not match published |
| 3 | BLEU / chrF++ | Not reproducible — scoring pipeline not preserved |
| 4 | Boundary precision | Values do not match published |
| 4 | Rényi entropy | Direction reproduces in 3 of 4 languages |

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

Tigre is the strongest valid result: the only language where MoVoC-Tok leads on
both official metrics — precision 63.3 vs 60.0 and Rényi 0.71 vs 0.73 — and the
only language whose gold annotations are 100% surface-concatenative, so the
official projection is exact.

Two facts recorded with it: the Tigre MoVoC-Tok row is cross-lingual (the
Tigrinya 32k model), and a second run disagrees on the winner. See
[`../table4/Intrinsic_report.md`](../table4/Intrinsic_report.md).

## Evaluation data

Three of four languages cannot be evaluated at the paper's stated item counts
from the released annotations. Tigrinya reaches 5,224 scorable items against a
stated 80,000. The constraint is gold annotation coverage, not corpus size. See
[`../audits/dataset_audit.md`](../audits/dataset_audit.md).
