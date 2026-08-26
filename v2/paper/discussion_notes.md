# Discussion — notes

Scope: MoVoC, MoVoC-Tok, the annotated datasets, and the two evaluations.

## 1. Boundary precision — MoVoC-Tok does what it was built to do

The paper's central claim holds up: MoVoC-Tok segments more accurately at
morpheme boundaries than BPE, in three of the four languages we can measure —
Amharic (0.3208 vs 0.3170), Tigrinya (0.3242 vs 0.3142), and Tigre (0.5629 vs
0.5380). On Ge'ez it's essentially a coin flip (0.4301 vs 0.4326), which is
worth sitting with for a second: MoVoC-Tok was never trained on Ge'ez at all —
what's being applied there is the Tigrinya model, asked to do a job it wasn't
built for. That it still keeps pace with BPE on unseen territory says
something about how much of the constrained-merge idea generalizes, even
without language-specific training.

## 2. Boundary precision and morphological regularity

Precision is noticeably higher for Tigre (0.51–0.56) than for the more
fusional languages (0.30–0.32), and that gap isn't really about the
tokenizer — it's about how Tigre's morphology sits on the page. Its gold
annotations are fully surface-concatenative, so a morpheme boundary really is
just a character offset; there's no fusion or vowel-consonant blending to
trip up an exact-match metric. Amharic and Tigrinya don't get that luxury,
and all three tokenizers pay for it roughly equally.

## 3. Intrinsic and extrinsic behaviour tell different stories, and that's fine

MoVoC-Tok wins on intrinsic boundary precision; BPE comes out ahead on
downstream BLEU and chrF++ in the runs we have. It would be easy to read that
as MoVoC-Tok "losing" — but see the Table 3 note below before drawing that
conclusion. Segmentation quality, as measured by how well a tokenizer's
boundaries line up with real morphemes, doesn't automatically translate into
translation quality, and at this training scale we don't have a clean enough
downstream signal to say much either way. Both results are reported as what
they are, not as substitutes for one another.

## 4. Table 3 (extrinsic MT) is not a verdict on any tokenizer

Table 3, as reconstructed, is inconclusive on tokenizer quality and should
not be used to rank BPE, WordPiece, or MoVoC-Tok against each other. All nine
runs stopped at 75,000 optimizer steps — about 5.5× fewer than a
comparably-trained MarianMT baseline (~416,000 steps) — and training loss
never converged (final loss 3.00–3.59). As a direct result, BLEU stays below
2 in every one of the 18 cells, well below any regime where BLEU/chrF++
differences mean anything. On top of that, all nine MoVoC-Tok runs are
flagged for output-quality anomalies (token repetition, token dominance),
which makes its scores the least trustworthy of the three even taken at face
value.

BPE happens to post the highest BLEU/chrF++ in most cells, but that's an
artifact of undertrained models, not evidence that BPE is the better
tokenizer. A real comparison would need training run to the full step
budget before any of these gaps are worth trusting. Until then, Table 3
tells us the pipeline runs end-to-end and produces sane, decodable output —
not which tokenizer wins.

This is exactly why Section 7 of the paper turns to qualitative analysis
instead of leaning on BLEU/chrF++ alone: those automatic metrics don't
directly assess whether token boundaries align with the underlying
morphological structure. To complement the quantitative evaluation, the
paper presents qualitative examples illustrating how MoVoC-Tok preserves
linguistically meaningful morphemes in Ge'ez-script languages — the
downstream translation numbers not showing an improvement over BPE doesn't
undercut that; it's just a different question than the one BLEU is built to
answer.

## 5. Metric complementarity

Boundary precision penalises spurious boundaries; MorphScore is
recall-oriented and ignores false positives. Reporting them together gives a
fuller picture of segmentation behaviour than either alone would — a
tokenizer that under-segments looks good on precision, one that
over-segments looks good on recall, and neither number alone tells you
which failure mode you're looking at.

## 6. The datasets as a contribution

169,806 annotated records across four Ge'ez-script languages, of which
129,261 carry at least one morpheme boundary. Three of the four had no
public morpheme-annotated resource before this. The annotations support both
the vocabulary construction method and the intrinsic evaluation, and are
released in a single documented JSON schema.
