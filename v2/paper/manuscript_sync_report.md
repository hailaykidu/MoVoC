# Manuscript sync report

> **Out of date, re-verified.** This report documents a sync/build-verification
> pass done against the manuscript's earlier numbers (Amharic precision
> 24.0/24.3-style, Rényi 0.62/0.66-style). Tables 2 and 4's authoritative
> values changed since (AMSEG intrinsic evaluation, see
> [`table4_notes.md`](table4_notes.md)), and `main.tex`'s prose has been
> updated to match — the entropy discussion was dropped from the prose
> entirely rather than restated with new numbers. The build-process notes
> below (LaTeX blockers found and fixed, Ethiopic rendering caveat, how to
> push to Overleaf) are still accurate; the "Values in the prose" table below
> is not. `scripts/check_manuscript_values.py` needed a fix of its own — it
> checked for a `renyi_alpha2_normalized` column that no longer exists in
> `table4_final.csv` (now `renyi_alpha2`, since the current table reports raw
> entropy) and was silently skipping all entropy validation as a result. With
> that fixed and the Table 3 training-scale figures (75,000 / 416,000 / 5.5x /
> 3.00-3.59, sourced from `v2/table3/PROVENANCE.md`) added to its allowlist,
> it passes again against the current `main.tex`.

## Scope — what this report does and does not cover

**The Overleaf manuscript was not modified.** This environment has no network
access to the Overleaf host, no Overleaf credentials and no tool that
can read or write that project. I could not open the manuscript, so I cannot
report which of its values were outdated, which sections changed, or confirm its
current state.

What was produced instead: a **complete manuscript in the repository**, written
entirely from the frozen V2 sources, at
[`manuscript/main.tex`](manuscript/main.tex). Applying it to Overleaf makes the
manuscript match the repository by construction. **Applying it is a manual step
that has not been performed.**

## Deliverable

| File | Contents |
|---|---|
| `v2/paper/manuscript/main.tex` | full manuscript, 10 sections |
| `v2/paper/manuscript/tables/table2_final.tex` | copied verbatim from `v2/table2/` |
| `v2/paper/manuscript/tables/table3_final.tex` | copied verbatim from `v2/table3/` |
| `v2/paper/manuscript/tables/table4_final.tex` | copied verbatim from `v2/table4/` |

Sections: Abstract, Introduction, Related Work, Methodology, Datasets, Intrinsic
Evaluation, Extrinsic Evaluation, Discussion, Limitations, Conclusion.

## Tables

All three are pulled in with `\input`, so **no value is retyped in the
manuscript body**:

```latex
\input{tables/table2_final}
\input{tables/table3_final}
\input{tables/table4_final}
```

Editing a number would require editing the fragment, which the consistency check
would then catch against the CSV.

| Table | Source | Values |
|---|---|---|
| 2 | `v2/table2/table2_final.tex` | AMSEG intrinsic evaluation, 3 tokenizers x 4 languages, 12 cells |
| 3 | `v2/table3/table3_final.tex` | 6 FLORES-200 cells, mean ± std, seeds 42/43/44 |
| 4 | `v2/table4/table4_final.tex` | AMSEG intrinsic evaluation, 3 tokenizers x 4 languages, 12 cells, raw Rényi entropy |

## Values in the prose (current)

Every number stated in the text is drawn from the frozen tables or from
`v2/table3/PROVENANCE.md` for the training-scale caveat (see the checker's
`ALLOW` list):

| Statement | Value | Source |
|---|---|---|
| Precision, Amharic | 0.3208 vs 0.3170 | `table4_final.csv` |
| Precision, Tigrinya | 0.3242 vs 0.3142 | `table4_final.csv` |
| Precision, Tigre | 0.5629 vs 0.5380 | `table4_final.csv` |
| Precision, Ge'ez (near-tie) | 0.4301 vs 0.4326 | `table4_final.csv` |
| MorphScore, Amharic/Tigrinya/Tigre/Ge'ez | 0.4139 / 0.4366 / 0.5278 / 0.6561 vs 0.6667 | `table2_final.csv` |
| BLEU, en→am MoVoC-Tok vs WordPiece | 0.7907 vs 0.0534 | `table3_final.csv` |
| BLEU, en→ti MoVoC-Tok vs WordPiece | 0.2710 vs 0.0439 | `table3_final.csv` |
| Table 3 training scale | 75,000 vs ~416,000 steps, 5.5x, loss 3.00–3.59 | `v2/table3/PROVENANCE.md` (checker allowlist) |
| Dataset totals | 169,806 records / 129,261 multi-morpheme | `data/README.md` rows |
| Amharic / Ge'ez record counts | 153,759 / 193 | `data/README.md` |

No published-paper value, superseded run, audit-only metric, sensitivity result
or appendix-only evaluation appears anywhere in the manuscript. The Rényi
entropy discussion (0.62/0.66-style normalized values) was removed from the
prose rather than restated with the current raw values.

## Local build verification

The manuscript was compiled locally with `pdflatex` + `bibtex` before handover,
so build failures are not discovered inside Overleaf.

```
pdflatex -> bibtex -> pdflatex -> pdflatex
errors: 0 | undefined references: 0 | undefined citations: 0
tables included: 3 | output: 9 pages
```

Three build blockers were found and fixed. **No numerical value was affected.**

| Issue | Fix |
|---|---|
| `\citep` undefined — `natbib` not loaded | added `\usepackage[numbers]{natbib}` |
| No bibliography — build aborted | added `references.bib` with the 8 cited works |
| Ethiopic example word dropped by pdfLaTeX | replaced with a transliteration; a comment documents how to restore native script under XeLaTeX/LuaLaTeX with an Ethiopic font |

The third is worth noting for a paper about Ge'ez script: **pdfLaTeX cannot
render Ethiopic characters at all.** If the Overleaf project should display the
native script, it must use XeLaTeX or LuaLaTeX with a font such as Abyssinica
SIL. As written, the manuscript compiles on any engine.

## One repository change

`v2/table3/table3_final.tex` contained literal `→` characters, which fail to
compile under pdfLaTeX with `inputenc`. Replaced with `$\rightarrow$`.
**Presentation only — no value changed**, and the CSV is untouched.

## Validation

```
$ python3 scripts/check_manuscript_values.py v2/paper/manuscript/main.tex
OK -- every numeric traces to v2/table{2,3,4}/*_final.csv
```

**Status: PASS**, re-run after the AMSEG intrinsic evaluation update and the
`renyi_alpha2` column-name fix described at the top of this report.

The checker was extended to read dataset counts from `data/README.md` and derive
its column totals, so the policy's named authority for dataset counts is
enforced rather than assumed.

Negative tests confirm it fails when it should: injecting the published values
`0.40`, `0.41`, `74.6`, `83.9` in place of frozen ones is detected, as is
substituting `85.5` for `24.0` in a table fragment.

## Note on dataset totals

`data/README.md` documents per-language counts but not the cross-language totals
169,806 and 129,261. I verified both by recomputing from
`data/annotations/*.json` and by summing the documented rows; the two agree.
Adding a totals row to `data/README.md` would make them directly citable rather
than derived.

## To apply this to Overleaf

1. Upload `tables/table2_final.tex`, `tables/table3_final.tex` and
   `tables/table4_final.tex` to the project's `tables/` directory, replacing any
   existing versions wholesale.
2. Ensure the preamble has `\usepackage{booktabs}` — Tables 2 and 3 require it.
   Table 4 uses plain `\hline`.
3. Take the prose for whichever sections you are updating from `main.tex`.
4. Recompile and record the repository commit the manuscript was built from.

Procedure and LaTeX requirements: [`overleaf_integration.md`](overleaf_integration.md).
