# Manuscript sync report

## Scope — what this report does and does not cover

**The Overleaf manuscript was not modified.** This environment has no network
access to `tex.cloud.uni-hannover.de`, no Overleaf credentials and no tool that
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
| 2 | `v2/table2/table2_final.tex` | Amharic 80,000 / 41.3 · Tigrinya 5,224 / 41.5 · Ge'ez 172 / 88.7 · Tigre 2,149 / 42.9 |
| 3 | `v2/table3/table3_final.tex` | 6 FLORES-200 cells, mean ± std, seeds 42/43/44 |
| 4 | `v2/table4/table4_final.tex` | 8 cells, official exact-match precision + normalized Rényi |

## Values in the prose

Every number stated in the text is drawn from the frozen tables:

| Statement | Value | Source |
|---|---|---|
| Entropy, Amharic | 0.62 vs 0.66 | `table4_final.csv` |
| Entropy, Tigrinya | 0.92 vs 0.93 | `table4_final.csv` |
| Entropy, Tigre | 0.71 vs 0.73 | `table4_final.csv` |
| Precision, Tigre | 63.3 vs 60.0 | `table4_final.csv` |
| Precision range, Tigre | 60.0–63.3 | `table4_final.csv` |
| Precision range, fusional | 24.0–36.8 | `table4_final.csv` |
| BLEU, en→am MoVoC-Tok vs WordPiece | 0.7907 vs 0.0534 | `table3_final.csv` |
| BLEU, en→ti MoVoC-Tok vs WordPiece | 0.2710 vs 0.0439 | `table3_final.csv` |
| Dataset totals | 169,806 records / 129,261 multi-morpheme | `data/README.md` rows |
| Amharic / Ge'ez record counts | 153,759 / 193 | `data/README.md` |

No published-paper value, superseded run, audit-only metric, sensitivity result
or appendix-only evaluation appears anywhere in the manuscript.

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

**Status: PASS.**

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
