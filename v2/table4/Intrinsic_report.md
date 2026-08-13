# Table 4 — boundary precision and Rényi entropy

Three categories, kept separate. None replaces another.

---

## A. Published Results

From the paper (arXiv:2509.08812), verbatim. 32k vocabularies.

| Language | Tokenization | Precision ↑ | Rényi Entropy ↓ |
|---|---|---:|---:|
| Amharic | MoVoC-Tok | **85.5** | 0.40 |
| Amharic | BPE | 85.3 | 0.41 |
| Tigrinya | MoVoC-Tok | **88.3** | 0.39 |
| Tigrinya | BPE | 83.9 | 0.40 |
| Tigre | MoVoC-Tok | **83.9** | 0.44 |
| Tigre | BPE | 74.6 | 0.49 |
| Ge'ez | MoVoC-Tok | **85.6** | 0.40 |
| Ge'ez | BPE | 73.9 | 0.44 |

**Paper claim:** MoVoC-Tok outperforms BPE on precision in all four languages.

---

## B. Reproduction Results

Official exact-match precision and official normalized Rényi entropy, from the
released implementation unmodified. Authoritative; see
[`./`](./).

| Language | Tokenization | Precision ↑ | Rényi ↓ | Words |
|---|---|---:|---:|---:|
| Amharic | MoVoC-Tok | 24.0 | **0.62** | 123,761 |
| Amharic | BPE | 24.3 | 0.66 | 123,761 |
| Tigrinya | MoVoC-Tok | 26.6 | **0.92** | 205 |
| Tigrinya | BPE | 27.3 | 0.93 | 205 |
| Tigre | **MoVoC-Tok**\* | **63.3** | **0.71** | 2,457 |
| Tigre | BPE | 60.0 | 0.73 | 2,457 |
| Ge'ez | MoVoC-Tok\* | 35.4 | 0.82 | 173 |
| Ge'ez | BPE | 36.8 | **0.81** | 173 |

`*` cross-lingual: no MoVoC-Tok artifact exists for Tigre or Ge'ez, so the 32k
Tigrinya model is applied — a documented assumption, not a paper-stated method.

### Difference

| Language | Tokenization | Precision (published → reproduced) | Δ |
|---|---|---|---:|
| Amharic | MoVoC-Tok | 85.5 → 24.0 | −61.5 |
| Amharic | BPE | 85.3 → 24.3 | −61.0 |
| Tigrinya | MoVoC-Tok | 88.3 → 26.6 | −61.7 |
| Tigrinya | BPE | 83.9 → 27.3 | −56.6 |
| Tigre | MoVoC-Tok | 83.9 → 63.3 | −20.6 |
| Tigre | BPE | 74.6 → 60.0 | −14.6 |
| Ge'ez | MoVoC-Tok | 85.6 → 35.4 | −50.2 |
| Ge'ez | BPE | 73.9 → 36.8 | −37.1 |

**Ranking does not reproduce.** The paper reports MoVoC-Tok ahead in all four
languages; this reproduction finds it ahead on **Tigre only**.

**Entropy direction does reproduce** in 3 of 4 languages — MoVoC-Tok yields
lower (sharper) normalised entropy for Amharic, Tigrinya and Tigre. Ge'ez inverts
by 0.01.

---

## C. Reconstruction v2 Findings

Investigation of why B differs from A. **These do not replace the reproduction
values in section B.**

### Audited corrections (confirmed, applied, insufficient)

- **Entropy normalisation** — confirmed from released code as `H_α / log(support)`.
  Applied; entropy moved to the published order of magnitude.
  [`entropy_audit.md`](../audits/entropy_audit.md)
- **Cumulative-length projection** — confirmed as the official rule. Applied; the
  evaluable set grew substantially.
  [`projection_audit.md`](../audits/projection_audit.md)

Both were effective against their own targets, yet precision remained far below
published. The residual gap is **not** attributable to them.

### Most likely cause

An **undocumented boundary-matching rule**. Exact character-offset matching is
unusually strict for Ge'ez-script morphology, where one character fuses consonant
and vowel across morpheme joins.
[`precision_audit.md`](../audits/precision_audit.md)

### A second reconstruction run agrees

An earlier three-arm run on different evaluation data:

| Language | MoVoC-Tok | BPE | WordPiece |
|---|---:|---:|---:|
| Amharic | **32.1** | 31.7 | 30.1 |
| Tigrinya | **32.4** | 31.4 | 31.7 |
| Tigre\* | **56.3** | 53.8 | 51.2 |
| Ge'ez\* | 43.0 | **43.3** | 42.0 |

Both reconstructions land 30–60 points below published. Two independent runs
agreeing is stronger evidence than either alone.

**Unresolved contradiction:** this run has MoVoC-Tok ahead on Tigre (56.3 vs
53.8), while `paper_tables_released_pipeline.json` (held-out) has BPE ahead
(60.4 vs 46.3). Must be settled before Tigre is cited as a MoVoC-Tok win.

### Sensitivity analysis — does not change section B

A linguistically grounded precision analysis found that **no linguistically
motivated variant reverses the ranking**. Fusion-aware matching — crediting an
off-by-one only where the abugida actually fuses — leaves BPE ahead in both
Amharic and Ge'ez, and *widens* Ge'ez's gap (−1.92 vs −1.40 exact).

A ±1 blanket tolerance does flip Ge'ez (64.34 vs 62.94), but it is the least
constrained criterion tested and the fusion-restricted test rules out abugida
fusion as its cause. **±1 values never replace the official exact-match results.**
[`precision_linguistic_sensitivity.md`](../audits/precision_linguistic_sensitivity.md)
