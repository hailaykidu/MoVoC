# Corrected version: MoVoC (Findings of EMNLP 2025)

Corrected version of Teklehaymanot, Fazlija and Nejdl (2025),
*MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages*,
Findings of EMNLP 2025, pp. 13131–13144,
<https://aclanthology.org/2025.findings-emnlp.706/>.

The results in the published version could not be reproduced. Following the
EMNLP 2025 programme chairs' advice, every result in this version is taken from
the reconstructed results in this repository. The correction notice after the
abstract summarises the changes, and Appendix D lists all of them.

Two changes since the first corrected draft:

- **Held-out evaluation.** Part of each in-language evaluation set consisted of
  words whose morpheme boundaries had constrained MoVoC-Tok's own training,
  which BPE and WordPiece never saw. All in-language results are now scored on
  held-out words only (76,488 Amharic, 2,438 Tigrinya), with bootstrap
  confidence intervals. MoVoC-Tok leads on MorphScore in three of four
  languages and on boundary precision in two of four. See
  `evaluation/CONTAMINATION.md` in the repository.
- **Translation results withdrawn.** Tables 3 and 7 are removed. The decode
  outputs are absent from the repository, the recorded length ratios show
  generation failing to terminate, and the decoding and initialisation settings
  of those runs cannot be established.

| File | Content |
|---|---|
| `main.pdf` | The corrected paper |
| `main.tex`, `custom.bib` | LaTeX source (ACL format, XeLaTeX) |
| `tables/` | The paper's tables, generated from this repository; `provenance.json` records the source of each. `table2_heldout.tex`, `table4_heldout.tex` and `table_significance_heldout.tex` are the ones the paper now inputs; `table3_final.tex` and `table7_opus.tex` are retained for reference but no longer used |
| `scripts/make_correction_tables.py` | Regenerates `tables/` from the repository |
| `scripts/check_numbers.py` | Checks that every number in the paper traces to a repository file |
| `CORRECTION_INSTRUCTIONS.md` | Full procedure, sources and acceptance checks |
| `ANTHOLOGY_CHANGE_SUMMARY.txt` | Change summary for the ACL Anthology revision |
| `acl.sty`, `acl_natbib.bst` | ACL style files (github.com/acl-org/acl-style-files) |
| `fonts/` | Noto Serif Ethiopic, SIL Open Font License 1.1 (`fonts/OFL.txt`) |

## Rebuild

From the repository root:

```bash
python v2/paper/corrected_emnlp2025/scripts/make_correction_tables.py \
       --repo . --out v2/paper/corrected_emnlp2025/tables
cd v2/paper/corrected_emnlp2025
latexmk -xelatex main.tex
python scripts/check_numbers.py --repo ../../.. --paper .
```

The intrinsic tables are copied verbatim from `v2/paper/manuscript/tables/`.
Regenerate them from the repository root with

```bash
python scripts/evaluate_intrinsic.py --outdir evaluation/results \
       --exclude-training
python scripts/bootstrap_significance.py . \
       evaluation/results/significance_heldout.json
```

No translation table is used: those results are withdrawn.

`main.tex` loads `fontspec` for the Ethiopic script, so it needs XeLaTeX or
LuaLaTeX; it will not build with pdfLaTeX.
