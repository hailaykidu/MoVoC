# Revision notes for the corrected version

Two changes are required before the corrected version can go to the Anthology.
Both follow from checks against the repository, not from new experiments.

1. The intrinsic evaluation is rescored on held-out words, which changes one of
   the two headline claims.
2. The translation results (Tables 3 and 7) are withdrawn.

---

## 1. Intrinsic evaluation: rescore on held-out words

### What changes

| Claim | Published | Corrected |
|-------|-----------|-----------|
| Highest boundary precision | three of four languages | **two of four** (Amharic, Tigre) |
| Highest MorphScore | three of four languages | three of four (unchanged) |

Tables 2 and 4 are replaced by `tables/table2_heldout.tex` and
`tables/table4_heldout.tex`, regenerated with

    python scripts/evaluate_intrinsic.py --outdir evaluation/results \
        --exclude-training

Item counts in Table 2 change accordingly: Amharic 81,224 to 76,488, Tigrinya
5,224 to 2,438. Tigre (1,974) and Ge'ez (172) are unchanged.

Full detail, including why the manifest's own provenance labels undercount the
overlap, is in `evaluation/CONTAMINATION.md`.

### Abstract

Replace

> In intrinsic evaluation of morpheme boundary precision and MorphScore,
> MoVoC-Tok scores highest of the three tokenizers in three of four languages

with

> In intrinsic evaluation on words held out from the morpheme resource used to
> constrain its training, MoVoC-Tok scores highest MorphScore in three of four
> languages and highest morpheme boundary precision in two of four, including
> the largest gains on Tigre, a language it was not trained on.

Delete the sentence reporting that the translation results do not rank the
tokenizers (see section 2 below).

### Section 6 (Results), after the intrinsic tables

Add:

> MoVoC-Tok is a supervised tokenizer: it consumes morpheme annotations that
> BPE and WordPiece do not receive. Using that supervision is the method, and a
> gain from it is a result. It is only a result, however, on words the
> supervision was not given for. Part of each in-language evaluation set is
> drawn from the same morpheme resource that constrained MoVoC-Tok's training
> (4,736 of 81,224 Amharic words; 2,786 of 5,224 Tigrinya words), and on those
> words the tokenizer is reproducing a constraint it was given rather than
> generalizing from it. We therefore report every in-language number on held-out
> words only. Tigre and Ge'ez have no training morpheme resource and are scored
> cross-lingually with the Tigrinya tokenizer, so they are unaffected.
>
> On held-out words MoVoC-Tok improves MorphScore in three of four languages and
> boundary precision in two of four. Differences are assessed by a paired
> bootstrap over words (10,000 resamples, shared resampling index).
>
> The exception is Tigrinya boundary precision, where the advantage present over
> the whole set (0.3242 against 0.3142 for BPE) does not survive the exclusion.
> On held-out words the difference is −0.0016, with a 95% interval of
> [−0.0106, +0.0075]: the data do not separate the two tokenizers on this
> metric, and we claim no precision gain for Tigrinya. Tigrinya MorphScore is a
> genuine improvement (+0.0185 against BPE, p=0.017).
>
> We attribute the Tigrinya precision null to annotation coverage rather than to
> the method. The Tigrinya morpheme vocabulary realises 7,125 types against
> 50,978 for Amharic (Table 5), from 6,692 training records against 10,293, and
> the constraint reaches too few word types for the learned merges to transfer
> beyond the annotated words. That the recall-oriented metric still improves
> while the precision metric does not is consistent with this reading: the
> learned merges continue to recover gold boundaries where they fire, but do not
> fire on enough unseen forms to raise precision overall.
>
> The clearest evidence that morpheme supervision generalizes is Tigre, which
> has no training morpheme resource of its own and is tokenized cross-lingually
> with the Tigrinya model. It shows the largest gains in the table (+0.0250
> precision, p=0.009; +0.0274 MorphScore, p=0.003, both against BPE). Ge'ez, at
> 172 words, resolves nothing in either direction. Morpheme supervision helps
> where annotation coverage is sufficient, and transfers across closely related
> languages; our Tigrinya result marks where coverage falls short.

### Limitations

Add:

> Our in-language intrinsic results are reported on words held out from the
> morpheme resource that constrained MoVoC-Tok's training. On Tigrinya the
> boundary precision advantage does not survive that exclusion, so we do not
> claim a precision gain for Tigrinya. We did not re-derive the morpheme
> resources to enlarge the held-out sets, so the Tigrinya held-out set is small
> (2,438 words) and its intervals are correspondingly wide; the Ge'ez set, at
> 172 words, does not resolve differences between tokenizers at all. The Amharic
> gains over BPE, while statistically resolved on 76,488 words, are small in
> absolute terms (+0.0018 precision, +0.0021 MorphScore), and we do not claim
> they are of practical consequence on their own. Our strongest in-language
> comparison is against WordPiece, and our strongest result overall is the
> cross-lingual Tigre transfer.

---

## 2. Translation results: withdraw Tables 3 and 7

### Why

Three independent reasons, each sufficient on its own.

**The outputs are not in the repository.** All 54 runs listed in `per_run` of
`table3_multiseed.json` reference `experiments/multiseed_1M/.../hyp_*.txt` and
the corresponding `ref_*.txt`. That directory does not exist in the repository
or anywhere in its history. The BLEU and chrF values cannot be checked against
the translations they summarise.

**The outputs show a generation defect.** Hypothesis/reference length ratios
run 2.06 to 4.28 on FLORES and up to 15.10 on OPUS. Generation is reaching the
128-token cap instead of emitting end-of-sequence. This is not undertraining:
final training loss across the runs is 2.9967 to 3.5854, in the same range as a
comparable from-scratch MarianMT that reached 24.7 BLEU en-am at loss 3.13. A
similar loss with BLEU below 1.56 in every cell points to a fault in generation
or scoring, not to training length.

**The setup cannot be described.** `table3_multiseed.json` records
`num_beams: 5`; `v2/archive/table3_intrinsic_v1_original/README.md` records
greedy decoding with `num_beams=1`. Whether the models were initialised from a
pretrained MarianMT or trained from scratch is likewise unresolved. Both are
listed as open in `CORRECTION_INSTRUCTIONS.md` section 6.

`table3_multiseed.json` already states, in its own
`scientific_validity_caveat`, that the runs "do not reach a translation regime
comparable to a fully trained system, so the values support no ranking claim
about the tokenizers in either direction", and in `not_a_reproduction` that
they "must not be tabulated alongside" the published values.

### What replaces them

Delete Table 3, Table 7 and Section 7. Add to Section 6:

> The published version reported BLEU and chrF++ for English-to-X translation
> with each tokenizer. Those results are withdrawn. The decode outputs behind
> them are not available, so the scores cannot be verified against the
> translations; the recorded hypothesis/reference length ratios (2.1 to 15.1)
> indicate that generation did not terminate correctly, which makes the scores
> uninformative about the tokenizers; and the decoding configuration and model
> initialisation of those runs cannot be established from the surviving records.
> We therefore make no extrinsic claim. MoVoC's contribution is a tokenization
> method and an annotated dataset, and we evaluate it intrinsically. Whether
> morphology-aware tokenization improves downstream translation for these
> languages remains open.

Remove the corresponding sentences from the abstract and introduction, and
remove Table 3 and Table 7 from the correction summary in Appendix A, replacing
the entries with a note that the tables are withdrawn.

### Alternative, if the outputs are recoverable

If the 54 decode outputs can be located, if the EOS defect is diagnosed and
fixed, and if the decoding and initialisation settings are established from the
job logs, the extrinsic evaluation can be re-run and reinstated. That is a
larger piece of work than the Anthology correction, and it should not block the
intrinsic correction, which is ready now.
