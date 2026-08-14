# MoVoC

**Morphology-Aware Subword Construction for Ge'ez Script Languages**
Findings of EMNLP 2025 — [arXiv:2509.08812](https://arxiv.org/abs/2509.08812)

Subword vocabularies that respect morpheme boundaries in Ge'ez-script languages
— Amharic, Tigrinya, Tigre and Ge'ez — where standard BPE routinely splits
inside morphemes.

## Setup

```bash
pip install -r requirements.txt
```

Every command in this README assumes the dependencies in `requirements.txt`
are installed.

## MoVoC

A hybrid vocabulary. Half the budget is allocated to morpheme types recovered by
supervised morphological analysis, half to BPE merges:

```
s_lang = s / 2
s_morpheme = s_lang × r
s_BPE      = s_lang × (1 − r)
```

Morphemes enter the vocabulary as first-class units rather than being discovered
statistically, so frequent affixes and roots survive as whole tokens.

```bash
python train.py \
  --amharic-corpus PATH \
  --tigrinya-corpus PATH \
  -s 224000 \
  -r 0.7142857142857143
```

| Argument | Meaning |
|---|---|
| `--amharic-corpus` | Path to the Amharic monolingual corpus (required) |
| `--tigrinya-corpus` | Path to the Tigrinya monolingual corpus (required) |
| `-s`, `--vocab-size` | Total vocabulary size *s* (default 224,000) |
| `-r`, `--morpheme-ratio` | Proportion *r* of morpheme-aware tokens (default 5/7) |

Both corpora are required: vocabulary construction runs over Amharic and
Tigrinya together.

## MoVoC-Tok

A constrained-merge tokenizer: **a merge may never cross a morpheme boundary.**
Segmentation stays inside morphemes, so a token cannot straddle a prefix–root or
root–suffix join.

```bash
python segment.py amharic "ዝወደቐ"
```

The language is a **positional** argument and accepts `amharic` or `tigrinya`.
Text is also positional; omit it to read from stdin.

Merge tables are written to `models/`. The repository tracks
`movoc_tok_merges_geez.txt` and `movoc_tok_merges_tigre.txt`; the Amharic and
Tigrinya tokenizers are regenerated locally with `train.py` (build outputs are
untracked — see `.gitignore`).

The tracked Ge'ez and Tigre merge tables are not selectable through the
positional argument. Load them with `--merges`:

```bash
python segment.py tigrinya --merges models/movoc_tok_merges_tigre.txt "…"
python segment.py tigrinya --merges models/movoc_tok_merges_geez.txt "…"
```

The positional argument only selects the default merge-table path and is
overridden by `--merges`, so it does not affect which table is loaded here.

## Annotated datasets

Morpheme segmentations for four Ge'ez-script languages — a core contribution,
since three of them had no public morpheme-annotated resource.

| Language | ISO 639-3 | Records | Multi-morpheme | Source |
|---|---|---:|---:|---|
| Amharic | amh | 153,759 | 123,761 | HornMorpho + human post-editing |
| Tigrinya | tir | 7,737 | 2,870 | gold (206) + post-edited (7,531) |
| Tigre | tig | 8,117 | 2,457 | manual annotation |
| Ge'ez | gez | 193 | 173 | manual annotation |

Format, fields and usage: **[`data/README.md`](data/README.md)**.

```python
from movoc import annotation
entries = annotation.load("data/annotations/tigre/manual_morphemes.json")
```

## Intrinsic evaluation

Morpheme boundary precision, MorphScore and Rényi entropy over the annotated
morpheme sets (`movoc/metrics.py`, run by `evaluate.py`).

| Language | Tokenization | Precision ↑ | Rényi ↓ |
|---|---|---:|---:|
| Amharic | MoVoC-Tok | 24.0 | **0.62** |
| Amharic | BPE | 24.3 | 0.66 |
| Tigrinya | MoVoC-Tok | 26.6 | **0.92** |
| Tigrinya | BPE | 27.3 | 0.93 |
| Tigre | **MoVoC-Tok**\* | **63.3** | **0.71** |
| Tigre | BPE | 60.0 | 0.73 |
| Ge'ez | MoVoC-Tok\* | 35.4 | 0.82 |
| Ge'ez | BPE | 36.8 | **0.81** |

MoVoC-Tok yields lower (sharper) Rényi entropy in three of four languages, and
leads on precision in Tigre — the language whose annotations are 100%
surface-concatenative. `*` cross-lingual.

MorphScore over the same sets:

| Language | Items | MorphScore ↑ |
|---|---:|---:|
| Amharic (amh) | 80,000 | 41.3 |
| Tigrinya (tir) | 5,224 | 41.5 |
| Ge'ez (gez) | 172 | 88.7 |
| Tigre (tig) | 2,149 | 42.9 |

[`v2/table4/Intrinsic_report.md`](v2/table4/Intrinsic_report.md) ·
[`v2/table2/MorphScore_report.md`](v2/table2/MorphScore_report.md)

## Extrinsic evaluation

English→X MarianMT, FLORES-200 devtest, mean ± std over seeds 42/43/44.

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ |
|---|---|---:|---:|
| English → Amharic | BPE | 1.4937 ± 0.0866 | 21.5573 ± 0.2167 |
| English → Amharic | WordPiece | 0.0534 ± 0.0140 | 11.5990 ± 0.0295 |
| English → Amharic | MoVoC-Tok | 0.7907 ± 0.0363 | 18.3999 ± 0.1711 |
| English → Tigrinya | BPE | 1.2557 ± 0.2135 | 10.8757 ± 0.0708 |
| English → Tigrinya | WordPiece | 0.0439 ± 0.0037 | 6.7069 ± 0.1085 |
| English → Tigrinya | MoVoC-Tok | 0.2710 ± 0.0775 | 7.8489 ± 0.2845 |

[`v2/table3/MarianMT_report.md`](v2/table3/MarianMT_report.md)

## Paper (V2)

The Reconstruction Version 2 manuscript is written in Overleaf:
**<https://tex.cloud.uni-hannover.de/project/6a6c6667662fbc94aa2c5196>**

Writing materials — section notes, publication-ready tables and caption drafts —
are in [`v2/paper/`](v2/paper/). Results tables are generated in this repository
and copied into the manuscript verbatim; values are never edited in Overleaf.
See [`v2/paper/overleaf_integration.md`](v2/paper/overleaf_integration.md).

| Source of truth | Owns |
|---|---|
| This repository | datasets, tokenizers, experiments, tables, reports |
| Overleaf project | manuscript text, LaTeX, figures, bibliography |

## Reconstruction Version 2

V2 reconstructs, organizes, reproduces, audits and documents the work within the
original paper's scientific scope — same methodology, same task definitions,
same evaluation protocols. It is the basis of the V2 paper and the primary
content of [`v2/`](v2/). Published values are preserved verbatim in
[`original/published_results/`](original/published_results/) and are never
overwritten.

Main tables use the approved methodology applied identically to every tokenizer;
sensitivity analyses and best-run summaries sit in
[`v2/appendix/`](v2/appendix/) and never substitute for them.

### Supporting audits

Records behind the results, in [`v2/audits/`](v2/audits/): entropy, boundary
projection, precision, dataset coverage and tokenizer provenance. Audits are
supporting evidence; they do not replace the main tables.
Scope and caveats: [`v2/reports/limitations.md`](v2/reports/limitations.md).

Historical and exploratory material is retained for transparency in
[`v2/archive/`](v2/archive/) and is not part of the primary presentation.

## Repository structure

```
MoVoC/
├── data/          annotated datasets · evaluation sets · vocabularies
├── movoc/         library: vocabulary, tokenizer, metrics, annotation
├── models/        released MoVoC-Tok merge tables
├── train.py · segment.py · evaluate.py
├── v2/            Reconstruction Version 2
│   ├── table2/ · table3/ · table4/   results + per-table reports
│   ├── tokenizers/ · marianmt/       reconstruction records
│   ├── appendix/  best runs · sensitivity · alternative evaluations
│   ├── audits/    supporting records
│   ├── archive/   historical material, retained but not foregrounded
│   └── reports/   summary · methodology · limitations · discussion
├── original/      archival baseline + published_results/
└── docs/ · scripts/ · configs/ · evaluation/ · assets/
```

## Running the experiments

```bash
# Vocabulary construction and tokenizer training (Sec. 3.2, 3.3)
python train.py \
  --amharic-corpus PATH \
  --tigrinya-corpus PATH \
  -s 224000 \
  -r 0.7142857142857143

# Build the evaluation sets (Sec. 5.1)
python scripts/build_eval_sets.py --opus-dir PATH

# Intrinsic evaluation (Sec. 5.2)
python evaluate.py --alpha 2.0

# Downstream translation (Sec. 4.3, 5.1) -- Slurm batch job, requires a GPU
sbatch scripts/submit_marianmt.sh <strategy> <language> <src> <tgt>

# Regenerate result tables from run outputs
python scripts/make_tables.py
```

`--opus-dir` is the directory holding the Tatoeba.* files.

`submit_marianmt.sh` is a **Slurm batch script** — submit it with `sbatch`, not
`bash`, or the `#SBATCH` resource directives are ignored. Its four positional
arguments are:

| Argument | Meaning |
|---|---|
| `<strategy>` | Tokenizer arm: `marian`, `movoc_tok`, `bpe` or `wordpiece` |
| `<language>` | Target language, e.g. `amharic` or `tigrinya` |
| `<src>` | Source-side training file (English) |
| `<tgt>` | Target-side training file |

Two optional dev files and a max-samples cap may follow:
`sbatch submit_marianmt.sh <strategy> <language> <src> <tgt> [dev.en dev.xx] [max-samples]`.

### Optional arguments

| Script | Argument | Effect |
|---|---|---|
| `train.py` | `--max-lines` | Cap lines read per corpus; omit for the full corpus |
| | `--merge-lines` | Lines used for Step 6 merge learning |
| | `--skip-step6` | Stop after Step 5; no merge table is produced |
| | `--wordpiece` | Also train the WordPiece baseline (Sec. 4.3) |
| | `--skip-bpe` | Reuse the BPE tokenizers in `data/vocabulary/` instead of retraining |
| `segment.py` | `--merges` | Load an alternative merge table |
| `evaluate.py` | `--sentencepiece` | SentencePiece `.model` to score as an extra baseline |
| | `-o`, `--out` | Output path for the results JSON |
| `build_eval_sets.py` | `-o`, `--out-dir` | Output directory for the built sets |
| `make_tables.py` | `--results-dir` | Directory holding run outputs |
| | `-o`, `--out` | Output path for the regenerated tables |
| | `--multiseed` | Multi-seed results file to draw from |

---

## Citation

```bibtex
@inproceedings{teklehaymanot2025movoc,
  title     = {MoVoC: Morphology-Aware Subword Construction for
               Ge'ez Script Languages},
  author    = {Teklehaymanot, Hailay and Fazlija, Dren and Nejdl, Wolfgang},
  booktitle = {Findings of the Association for Computational Linguistics:
               EMNLP 2025},
  year      = {2025},
  eprint    = {2509.08812},
  archivePrefix = {arXiv}
}
```

## References

- Arnett & Bergen (2025). MorphScore.
- Costa-Jussà et al. (2022). No Language Left Behind.
- Goyal et al. (2022). FLORES-200.
- Junczys-Dowmunt et al. (2018). Marian.
- Kudo & Richardson (2018). SentencePiece.
- Nouri & Yangarber (2016). Morpheme boundary precision.
- Papineni et al. (2002). BLEU.
- Popović (2017). chrF++.
- Rényi (1961). Rényi entropy.
- Sennrich et al. (2016). Byte-Pair Encoding.
- Tiedemann (2012). OPUS.
