# marianmt-tokenizer-comparison

A controlled scientific comparison of three **already-trained** tokenizers — BPE,
WordPiece, and MoVoC-Tok — under a shared MarianMT architecture, for two
translation directions: English→Tigrinya (en_ti) and English→Amharic (en_am).

This repository is **independent**: it does not import from, depend on, or
modify `amseg`, `MoVoC`, or any thesis/publication repository. It reads three
tokenizer artifacts from those repositories as **read-only, absolute-path
external inputs** (see `tokenizers/*/README.md` for the exact source paths).
No tokenizer files are copied or committed here.

## Scientific question

Under identical MarianMT architecture, identical OPUS parallel data, identical
training configuration, and three random seeds (42, 43, 44), which of BPE,
WordPiece, or MoVoC-Tok gives the strongest en→ti and en→am translation
performance as measured by chrF++?

Selection uses **mean validation chrF++ across seeds only**. The held-out test
set is touched exactly once, after selection, for the selected tokenizer only.

## Design summary

- 2 language pairs × 3 tokenizers × 3 seeds = **18 full training runs**.
- Fixed learning rate **1.44e-7** for every run (see "Known caveats" below —
  this is an explicit, recorded experimental choice, not a default).
- Tokenizers are loaded strictly read-only; never retrained, resized, or
  modified. A machine-readable manifest is produced by
  `scripts/verify_tokenizers.py` before anything else runs.
- `en_ti` runs all three tokenizers at vocab size 63051.
- `en_am` runs BPE/WordPiece at vocab size 32000, but the MoVoC-Tok condition
  for en_am **reuses** the Tigrinya-trained 63050/63051 MoVoC-Tok tokenizer
  (no Amharic-trained 63k MoVoC-Tok exists). This is a deliberate,
  user-approved decision — see "Known caveats".
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
2. **en_am MoVoC-Tok is cross-lingual reuse of a Tigrinya-only tokenizer.**
   It was trained exclusively on Tigrinya text
   (`shared_vocab: false`, corpus = `NLLB.en-ti.ti`). Applying it to Amharic
   is out-of-domain and is expected to show elevated fertility and/or UNK
   rate on Amharic text. `scripts/verify_tokenizers.py` measures and prints
   this explicitly and the tokenizer manifest records
   `"cross_lingual_reuse": true` with a warning field. The pipeline does
   **not** block or fail because of this — it is a knowing, recorded
   tradeoff, not a defect.
3. **en_am vocab sizes are not uniform across tokenizers.** BPE/WordPiece use
   32000; MoVoC-Tok (reused) has native vocab 63050/63051. This is
   documented in `configs/en_am.yaml` and the tokenizer manifest, not hidden.

## Repository layout

```
configs/                   base.yaml + per-language-pair configs
data/                      manifests only committed; raw/processed data is gitignored
tokenizers/                pointer READMEs to external, read-only tokenizer artifacts
src/marianmt_comparison/   library code (config, data, tokenization, model, training, evaluation, selection, reproducibility)
scripts/                   CLI entry points run by SLURM (verify, prepare, train, evaluate, aggregate, select)
slurm/                     sbatch scripts, chained via afterok
experiments/               per-run working dirs (empty at commit time; .gitkeep only)
results/                   generated CSV/JSON/final report (not pre-filled)
docs/                      experimental protocol, SLURM protocol, results writeup
```

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
