Dear [Professor],

Thank you for both points. I have checked them against the repository and they
are correct. I have implemented the corrections on a branch,
`fix/eval-contamination`, and summarise below what changed, including one
respect in which the contamination is worse than your message states.

## 1. Tigrinya contamination

Your reading of the chain is right.
`tokenizers/tigrinya_movoc_tok_32k/training_config.json` names
`data/segmented/tigrinya_morpheme_segmented.json` as `morpheme_source`, and the
evaluation manifest attributes 2,412 of the 5,224 Tigrinya words to that file at
`"resource_tier": "training"`. I reproduced your three-way split exactly with
`scripts/evaluate_intrinsic.py`:

| Stratum | n | BPE | WordPiece | MoVoC-Tok |
|---|---|---|---|---|
| Training words | 2,412 | 0.3986 | 0.4059 | **0.4221** |
| Other post-edited | 2,812 | **0.2444** | 0.2432 | 0.2409 |
| Gold only | 160 | **0.4973** | 0.4696 | 0.4512 |

(boundary precision; the MorphScore column matches your figures too. These
strata follow the manifest's provenance labels, as in your message; the counts
change slightly once the overlap is computed properly, as set out next.)

### The overlap is larger than the manifest reports

The provenance file records only the *first* source each word was drawn from,
so filtering on the `resource_tier` label undercounts. Taking set membership
against the training file itself, the Tigrinya overlap is **2,786**, not 2,412:

| Provenance label | Also present in the training file |
|---|---|
| `tigrinya_morpheme_segmented.json` | 2,412 |
| `postedited_morphemes.json` | 356 |
| `gold_morphemes.json` | 18 |

The last row is the one that concerns me most. `gold_morphemes.json` is
described in the manifest as *"gold, held out from training and vocabulary
construction"*, but 18 of its 160 words (11.2%) are in the training resource.
That description was inaccurate, and I have corrected it. Had we filtered on the
label as the manifest invites, 374 contaminated words would have remained in the
evaluation set.

Exclusion is therefore done by set membership, via a new
`--exclude-training` flag. Default behaviour is unchanged and still reproduces
the published tables exactly. This leaves 2,438 held-out Tigrinya words rather
than the 2,812 that the label-based split gives, which is why the figures in the
next section differ slightly from the second row of the table above.

### Significance

Because the held-out margins are small, I added a paired bootstrap over words
(10,000 resamples, resampling index shared across tokenizers), reported against
BPE:

| Language | n | Metric | Δ | 95% CI | p |
|---|---|---|---|---|---|
| Amharic | 76,488 | Precision | +0.0018 | [+0.0004, +0.0033] | 0.012 |
| Amharic | 76,488 | MorphScore | +0.0021 | [+0.0001, +0.0042] | 0.045 |
| Tigrinya | 2,438 | Precision | −0.0016 | [−0.0106, +0.0075] | 0.744 |
| Tigrinya | 2,438 | MorphScore | +0.0185 | [+0.0031, +0.0345] | 0.017 |
| Tigre | 1,974 | Precision | +0.0250 | [+0.0060, +0.0446] | 0.009 |
| Tigre | 1,974 | MorphScore | +0.0274 | [+0.0096, +0.0458] | 0.003 |
| Ge'ez | 172 | Precision | −0.0025 | [−0.0260, +0.0195] | 0.839 |
| Ge'ez | 172 | MorphScore | −0.0105 | [−0.0383, +0.0157] | 0.442 |

This changes how I think the Tigrinya precision result should be stated. The
interval spans zero, so the held-out data do not separate MoVoC-Tok from BPE on
that metric. The supportable claim is that no difference is detected, rather
than that MoVoC-Tok is worse. Tigrinya MorphScore remains a genuine improvement.

### Amharic

You were right that the Amharic file was missing: `amharic_morpheme_segmented.json`
was absent from the repository and from its entire history. I have committed it
(10,293 records, matching `morpheme_records` in the training config). Scored on
the 76,488 words that are not in it, MoVoC-Tok still leads on both metrics,
though the margin over BPE is small in absolute terms. The overlap there is
4,736 of 81,224 words, 5.8%, against 53.3% for Tigrinya.

### Resulting claims

Highest MorphScore in three of four languages, unchanged. Highest boundary
precision in **two of four**, down from three. The manuscript now states this,
and attributes the Tigrinya result to annotation coverage: the Tigrinya morpheme
vocabulary realises 7,125 types against 50,978 for Amharic, so the constraint
reaches too few word types for the merges to transfer beyond the annotated
words. That the recall-oriented metric still improves while precision does not
is consistent with that reading.

I have reorganised the discussion to lead with Tigre, which has no training
morpheme resource of its own and is tokenized cross-lingually. It carries the
largest and most clearly resolved gains in the paper, and it is the one result
that contamination cannot explain, so it is now where the generalization claim
rests.

## 2. Translation results

I agree, and I have withdrawn Tables 3 and 7 rather than attempting to repair
them before the Anthology deadline. All three of your objections hold:

- None of the 54 hypothesis or reference files referenced in `per_run` exists in
  the repository or its history, so the scores cannot be checked against the
  translations.
- Length ratios run 2.06–4.28 on FLORES and up to 15.10 on OPUS, which is
  generation reaching the 128-token cap rather than emitting end-of-sequence.
  Your 13 September point stands: final training loss of 2.9967–3.5854 is in the
  same range as job 52623 at 3.13, which reached 24.7 BLEU en→am, so a similar
  loss with BLEU below 1.56 in every cell indicates a generation or scoring
  fault, not training length.
- The records contradict each other on decoding (`table3_multiseed.json` gives
  5 beams; the archive README gives greedy with `num_beams=1`), and model
  initialisation is unresolved. Both are listed as open in
  `CORRECTION_INSTRUCTIONS.md`.

I would add a fourth, from our own artifacts: `table3_multiseed.json` already
states in its `scientific_validity_caveat` that the runs "support no ranking
claim about the tokenizers in either direction", and in `not_a_reproduction`
that they "must not be tabulated alongside" the published values. Publishing
them would contradict the repository's own record.

Section 6 now records the withdrawal and its grounds, and the claims that rested
on those numbers are removed from the abstract, introduction, discussion,
limitations and conclusion. The paper is presented as a tokenization method and
an annotated dataset, evaluated intrinsically, with the downstream question left
open.

If the decode outputs can be recovered and the generation defect diagnosed, the
extrinsic evaluation can be re-run and reinstated later. I did not want that to
block the intrinsic correction, which is ready now.

## What is on the branch

Eight commits on `fix/eval-contamination`:

1. The two `*_morpheme_segmented.json` training resources
2. `--exclude-training` in `scripts/evaluate_intrinsic.py`
3. Manifest corrections, including the gold-set description
4. Held-out Tables 2 and 4, plus revision notes
5. `scripts/bootstrap_significance.py` and its results
6. The significance results file (tracked explicitly; `evaluation/results/` is
   gitignored)
7. The manuscript edits
8. This response
9. The Anthology package (`corrected_emnlp2025.zip`), rebuilt so that the paper
   it contains states the same results as the repository. Its unpacked source
   is now tracked under `v2/paper/corrected_emnlp2025/` so it can be reviewed
   without unzipping.

One claim I dropped rather than carried into the package: the comparison with
job 52623 at 24.7 BLEU and loss 3.13. That job is not in the repository, so the
figure cannot be traced from the released artifacts, and I did not want an
unverifiable number in a corrected paper. The withdrawal argument in the
package rests on the length ratios and the missing outputs, both of which are
in the per-run records. The point still holds and I have kept it in this
response; if you would like it in the paper as well, it would need the job log
committed alongside.

Two documents may be the most useful starting points:
`evaluation/CONTAMINATION.md` for the extent and effect, and
`v2/paper/REVISION_NOTES.md` for the text changes.

Verified from a clean clone: the default evaluation path still reproduces all
twelve published boundary precision values to four decimal places, and the
manuscript compiles with no errors and no undefined references or citations.

I have not pushed the branch yet, and would welcome your view first, in
particular on whether the withdrawal of the translation tables is the right call
or whether you would prefer we attempt to recover the outputs.

Best regards,
Hailay
