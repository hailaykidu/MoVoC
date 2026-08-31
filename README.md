# MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages

Official companion and reproducibility repository for:

**Hailay Kidu Teklehaymanot, Dren Fazlija, and Wolfgang Nejdl. 2025.**
*MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages.*
Findings of the Association for Computational Linguistics: EMNLP 2025, pp. 13131–13144.

Paper: https://aclanthology.org/2025.findings-emnlp.706/

PDF: https://aclanthology.org/2025.findings-emnlp.706.pdf

## Overview

Many subword tokenization approaches such as BPE and WordPiece ignore
morphological structure and may split words in ways that conflict with
linguistic boundaries. This problem is particularly pronounced for
morphologically rich, low-resource languages written in the Ge'ez script.

MoVoC (Morpheme Vocabulary Construction) introduces a morphology-aware
approach to vocabulary construction that integrates supervised morphological
knowledge into constrained-BPE training. The resulting tokenizer, MoVoC-Tok,
prevents merge operations from crossing known morpheme boundaries while
retaining the efficiency of statistical subword tokenization.

The paper investigates four Ethio-Semitic languages:

- Amharic
- Tigrinya
- Tigre
- Ge'ez

and evaluates the approach through both intrinsic segmentation quality
measures and downstream MarianMT machine translation experiments.

## Main Contributions

- Introduction of the MoVoC vocabulary-construction framework.
- Development of the constrained-BPE MoVoC-Tok tokenizer.
- Release of morpheme-annotated evaluation resources.
- Intrinsic evaluation using MorphScore, Boundary Precision, and Rényi
  Entropy.
- Extrinsic evaluation through MarianMT translation experiments.

## Repository Overview

This repository contains the implementation, tokenizer assets,
vocabulary-construction resources, intrinsic evaluation artifacts,
extrinsic machine translation experiments, and reproducibility materials
associated with the MoVoC paper. It serves as the primary reference
implementation and companion repository for the published work.

Intrinsic evaluation (Table 2, Table 4) measures MoVoC-Tok's subword-boundary
alignment against gold morpheme annotations; extrinsic evaluation (Table 3)
measures downstream MarianMT translation quality under BPE, WordPiece, and
MoVoC-Tok tokenization for English→Tigrinya and English→Amharic.

The remainder of this document is repository-level organizational and
reproducibility information, not a quotation from the paper.

## Repository Structure

- `Intrinsic_Evaluation/`
  - Table 2 (MorphScore)
  - Table 4 (Boundary Precision and Rényi Entropy)
  - intrinsic evaluation datasets, scripts, and reports

- `Extrinsic_Evaluation/`
  - MarianMT fine-tuning and evaluation experiments: `configs/`, `scripts/`,
    `slurm/`, `src/`, `tests/` (source code and job definitions)
  - `experiments/`, `data/`, `results/` are symlinks to this repository's
    existing top-level directories of the same name, kept at their
    original paths since an actively running SLURM pipeline writes there

- `Tokenizers/`
  - `movoc_tok_32k/`: **canonical** constrained-BPE MoVoC-Tok tokenizers
    (Section 3.3 method) and HuggingFace exports
  - `movoc_tok_alternative/`: a historical, **non-canonical** tokenizer
    pipeline preserved for provenance only (frequency-selected vocabulary,
    greedy longest-match segmentation — does not implement Section 3.3's
    constrained-merge BPE; not used by any table or evaluation script)
  - `bpe/`, `wordpiece/`, `movoc_tok/` are pointer docs only: the MT
    pipeline's tokenizers, loaded read-only from `amseg/`, never copied
    locally

- `Vocabulary_Construction/`
  - MoVoC vocabulary-construction assets
  - constrained-BPE training implementation (Algorithm 3.3)
  - verification and export utilities

- `Paper_Artifacts/`
  - paper-related outputs and supporting materials: the three final tables
    (Table 2, Table 3, Table 4) and `docs/`

- `docs/`
  - experimental protocol, SLURM protocol, results writeup
    (`Extrinsic_Evaluation`/Table 3 specific)

Where a component above is a **symlink** (`Extrinsic_Evaluation/experiments`,
`Extrinsic_Evaluation/data`, `Extrinsic_Evaluation/results`, and everything
under `Vocabulary_Construction/` and `Paper_Artifacts/`), the real files
live at the target path shown; this keeps the running MT pipeline's
hardcoded relative paths (`experiments/...`, `data/...`) working unchanged
while giving the repository the structure above. The top-level `configs/`,
`scripts/`, `slurm/`, `src/`, `tests/` directories still exist on disk (the
running MT pipeline reads and writes them at those exact paths) but are no
longer tracked at the repository root — their tracked copies live under
`Extrinsic_Evaluation/`.

This repository does not import from, modify, or write to `amseg`, `MoVoC`,
or any other repository; everything under those paths is read read-only.
`Tokenizers/movoc_tok_32k/` is a deliberate, self-contained local copy of
the canonical constrained-BPE MoVoC-Tok checkpoints (verified
byte-identical to their `amseg/` originals — see
`Tokenizers/movoc_tok_32k/docs/verification_report.md`), kept here so
Table 2, Table 4, and future reproduction do not depend on `amseg/`
remaining available.

## Citation

If you use this repository, please cite:

```
Teklehaymanot, H. K., Fazlija, D., & Nejdl, W. (2025).
MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages.
Findings of the Association for Computational Linguistics: EMNLP 2025, pp. 13131–13144.
```

## Scientific question

Under identical MarianMT architecture, identical OPUS parallel data, identical
training configuration, and three random seeds (42, 43, 44), which of BPE,
WordPiece, or MoVoC-Tok gives the strongest en→ti and en→am translation
performance as measured by chrF++?

Selection uses **mean validation chrF++ across seeds only**. The held-out test
set is touched exactly once, after selection, for the selected tokenizer only.

## Design summary

- 2 language pairs × 3 tokenizers × 3 seeds = **18 full fine-tuning runs**.
- Fixed learning rate **1.44e-7** for every run (see "Known caveats" below —
  this is an explicit, recorded experimental choice, not a default).
- Tokenizers are loaded strictly read-only; never retrained, resized, or
  modified. A machine-readable manifest is produced by
  `scripts/verify_tokenizers.py` before anything else runs.
- `en_ti` runs all three tokenizers at vocab size 63051.
- `en_am` runs BPE/WordPiece at vocab size 32000, but the MoVoC-Tok condition
  for en_am, **as actually run for the published results**, reuses the
  Tigrinya-trained 63050/63051 MoVoC-Tok tokenizer (at the time, no
  Amharic-trained 63k MoVoC-Tok existed). This is a deliberate, user-approved
  decision — see "Known caveats". A native Amharic 63k MoVoC-Tok checkpoint
  (`amharic_movoc_tok_63050`) now exists, built post-publication, but has not
  been used to rerun en_am or regenerate Table 3.
- Data: OPUS NLLB parallel corpus, downloaded fresh at pipeline run time
  (not committed). Fixed, deterministic train/validation/test splits.
- Evaluation: chrF++ via sacrebleu 2.6.0 (`char_order=6, word_order=2,
  beta=2, lowercase=False, whitespace=False`), BLEU as secondary metric.
- Orchestration: SLURM job-dependency chain (`afterok`) via
  `slurm/pipeline.sbatch`. First run is scoped to verification + a single
  smoke test only (see "Running the pipeline").

## Known caveats (recorded deliberately, not hidden)

1. **Learning rate 1.44e-7** is used for all 18 runs. This value has
   historically produced degenerate/near-zero results in a related
   experiment. It is being kept anyway per explicit instruction, so that this
   comparison is run under the same nominal configuration end-to-end. Do not
   "fix" this value without a new explicit decision — if results look
   degenerate, that is an expected and already-anticipated possible outcome,
   not necessarily a bug in this repository.
2. **en_am MoVoC-Tok, as published, is cross-lingual reuse of a
   Tigrinya-only tokenizer.** It was trained exclusively on Tigrinya text
   (`shared_vocab: false`, corpus = `NLLB.en-ti.ti`). Applying it to Amharic
   is out-of-domain and is expected to show elevated fertility and/or UNK
   rate on Amharic text. `scripts/verify_tokenizers.py` measures and prints
   this explicitly and the tokenizer manifest records
   `"cross_lingual_reuse": true` with a warning field. The pipeline does
   **not** block or fail because of this — it is a knowing, recorded
   tradeoff, not a defect. A native Amharic 63k MoVoC-Tok now exists
   (`Tokenizers/movoc_tok_32k/amharic_63050/`, post-publication) for a
   future en_am run, but the results in this repository still reflect the
   cross-lingual-reuse tokenizer described above.
3. **en_am vocab sizes are not uniform across tokenizers.** BPE/WordPiece use
   32000; MoVoC-Tok (reused) has native vocab 63050/63051. This is
   documented in `configs/en_am.yaml` and the tokenizer manifest, not hidden.

## Extrinsic_Evaluation/ (Table 3) internals

```
configs/                   base.yaml + per-language-pair configs
data/                      manifests only committed; raw/processed data is gitignored
src/marianmt_comparison/   library code (config, data, tokenization, model, training, evaluation, selection, reproducibility)
scripts/                   CLI entry points run by SLURM (verify, prepare, train, evaluate, aggregate, select)
slurm/                     sbatch scripts, chained via afterok
experiments/               per-run working dirs (empty at commit time; .gitkeep only)
results/                   generated CSV/JSON/final report (not pre-filled)
```

All paths above are reachable both directly (repo root) and via
`Extrinsic_Evaluation/<name>` (symlink) -- SLURM jobs run from and write to
the repo-root paths.

## Running the pipeline

```bash
sbatch slurm/pipeline.sbatch
```

By default (`PIPELINE_STAGE=verify_and_smoke`), the **first** invocation only
runs: environment/tokenizer/model/data verification, data preparation, and a
single smoke test (en→ti, BPE, seed 42, small data subset). It then **stops**
and writes a status report — it does **not** cascade into the 18 full
training runs automatically.

Once verification + smoke test are confirmed green, launch the full sweep as
a deliberate second step:

```bash
PIPELINE_STAGE=full sbatch slurm/pipeline.sbatch
```

See `docs/slurm_protocol.md` for environment setup (venv/conda activation,
partitions, resource requests) and `docs/experimental_protocol.md` for the
full experimental design and model-selection procedure.

## Reproduction

Every run's metadata records: language pair, tokenizer, seed, exact model and
tokenizer identifiers, dataset manifest, learning rate, batch size, epochs,
sacrebleu version, chrF++ signature, git commit, and timestamp. See
`docs/experimental_protocol.md` §"Metadata" and `results/final_report.md`
(generated after the pipeline runs).
