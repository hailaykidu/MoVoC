# Filing checklist for the corrected version

The two technical conditions are met and verified (see
`evaluation/CONTAMINATION.md` and `RESPONSE_TO_REVIEW.md`). What remains is a
sequence of approvals and submissions, in this order.

## 1. Co-author agreement — before anything is filed

Dren Fazlija is a co-author and has to agree to the corrected version before it
is submitted anywhere. Send him:

- the built paper (`corrected_emnlp2025.zip`, or `main.pdf` from it);
- `RESPONSE_TO_REVIEW.md`, which explains what changed and why;
- a plain statement of the two substantive changes: the precision claim drops
  from three of four languages to two of four, and the translation results are
  withdrawn entirely.

Wolfgang Nejdl is also listed as an author and should receive the same.

**Status.** Done. Dren Fazlija agreed to the version at `f5d84dc` ("nothing to
add from my end, please proceed"), and Wolfgang Nejdl has agreed to the same
version. All three authors have agreed, so the revision may be filed.

## 2. Supervisor check

The reviewer asked to see the new version before it is filed. Both of his
acceptance checks pass on the current branch:

- `scripts/evaluate_intrinsic.py` with no flag still reproduces all 36 values
  of the published Tables 2 and 4 exactly, at the original word counts
  (81,224 / 5,224 / 1,974 / 172);
- `scripts/check_numbers.py` reports 0 numbers without a source, exit status 0.
  The count of distinct numbers moves as the text changes; it is 248 at
  `f5d84dc`, and only the zero matters.

The held-out numbers the corrected paper reports come from the same script with
`--exclude-training`, which scores 76,488 / 2,438 / 1,787 / 170 words — the
original counts above are those of the full sets, and the paper no longer
reports results on them. The three tables in the archive are byte-identical to
the repository files they are generated from.

**Status.** Both checks pass at `f5d84dc`. The reviewer confirmed the three
review points and the two follow-up points, and asked for no further check.

## 3. ACL Anthology revision

Submit through the form on the paper's Anthology page
(<https://aclanthology.org/2025.findings-emnlp.706/>), referring to the
programme chairs' advice. The Anthology keeps the original PDF alongside the
revision, which is why the correction notice stands on page 1 rather than in an
appendix.

`ANTHOLOGY_CHANGE_SUMMARY.txt` in the archive is written for this form.

## 4. arXiv

Post as a new version of arXiv:2509.08812 with the comment
`corrected version`. Same PDF and source as the Anthology revision.

## 5. Notify the programme chairs

Reply in the thread of the correction notice of 31 August, with the supervisor
in Cc, once the revision is filed.

## Note on one claim

The comparison with job 52623 (loss 3.13, 24.7 BLEU en-am) is not in the paper.
That job is not in this repository, so the figure cannot be traced from the
released artifacts, and `check_numbers.py` would flag it. The withdrawal rests
instead on the missing decode outputs and the recorded length ratios, both of
which are in `table3_multiseed.json`. If the comparison is wanted in the paper,
the job log needs to be committed first.
