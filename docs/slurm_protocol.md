# SLURM protocol

## Cluster facts assumed by these scripts

- `sbatch`/`squeue` confirmed available on this host.
- Partitions: `blackwell` (gpunode08, RTX Pro 6000), `hopper` (gpunode07,
  H100 x8), `ampere` (gpunode02-06, A100), `standby` (overflow onto the
  same nodes as blackwell/hopper/ampere at lower priority).
- These scripts default to `--partition=ampere --gres=gpu:1`. Adjust for
  your allocation/queue times -- `standby` may get you a slot faster if
  `ampere` is busy, at the cost of possible preemption.
- **Account**: every sbatch script has a commented-out
  `# --account=<YOUR_ACCOUNT>` line. Uncomment and fill in your actual
  account if your site enforces one (`sacctmgr show associations
  user=$USER` lists yours). No account value is hardcoded here since it is
  allocation-specific and not something this repository should guess.

## Environment activation (required setup step, not automatic)

`module load conda` (or `module load mamba`) is required before `conda`
is on `PATH` on this host. Rather than depend on a specific named conda
environment (the existing `tigrinya_mt` env was checked and is missing
`transformers`/`pyyaml` -- unsuitable), every sbatch script sources
`slurm/env_setup.sh`, which:

1. Creates `.venv/` at the repo root (once, idempotently) via
   `python3 -m venv --system-site-packages`, inheriting the host's
   already-confirmed `transformers==4.51.3`, `torch==2.5.1+cu118`,
   `sacrebleu==2.6.0`, `sentencepiece==0.2.1`.
2. Activates it and `pip install -r requirements.txt` (idempotent; pins
   the remaining pure-Python deps: pyyaml, pandas, numpy, huggingface_hub,
   requests).
3. Sets `PYTHONPATH` to include `src/` so `marianmt_comparison` imports
   resolve without an editable install.

This is an explicit, visible step in every job script -- nothing here
silently relies on whatever module happens to be loaded in the submitting
shell.

## Job graph

```
sbatch slurm/pipeline.sbatch                      (default: PIPELINE_STAGE=verify_and_smoke)
    -> verify_tokenizers.py
    -> prepare_opus_data.py
    -> verify_data.py
    -> verify_models.py           (6 combinations; hard-fails on any failure)
    -> train.py --smoke_test
    -> STOPS. Writes results/pipeline_status.json.

PIPELINE_STAGE=full sbatch slurm/pipeline.sbatch  (deliberate second step)
    -> checks results/pipeline_status.json shows smoke_test PASSED
    -> slurm/run_all_experiments.sbatch:
         sbatch slurm/train_one.sbatch          (array 0-17, 1 GPU each)
           |  afterok
           v
         sbatch slurm/evaluate_all.sbatch       (array 0-17, validation split only)
           |  afterok
           v
         sbatch slurm/aggregate.sbatch          (CPU-only: aggregate_results.py + select_best_tokenizer.py)
```

Test-set evaluation for the selected tokenizer (spec section 8, step 5) is
a manual follow-up after inspecting `results/{language_pair}/best_tokenizer.json`
-- `scripts/select_best_tokenizer.py` prints the exact 3
`scripts/evaluate.py --split test` commands to run per language pair. This
is intentionally not auto-chained, since it must only run for the tokenizer
that was actually selected, and a human should confirm the selection first.

## Array index -> configuration mapping

`slurm/train_one.sbatch` and `slurm/evaluate_all.sbatch` both use the same
deterministic mapping from `SLURM_ARRAY_TASK_ID` (0-17) to
`(language_pair, tokenizer, seed)`:

```
language_pairs = [en_ti, en_am]
tokenizers     = [bpe, wordpiece, movoc_tok]
seeds          = [42, 43, 44]

lp_idx   = idx // 9
rem      = idx % 9
tok_idx  = rem // 3
seed_idx = rem % 3
```

## Retry policy

If a run fails, retry by resubmitting the **exact same array index** (same
`(language_pair, tokenizer, seed)`, hence the exact same learning rate,
batch size, data, and eval settings). Never change any hyperparameter
automatically on retry. `scripts/train.py` and `scripts/evaluate.py` take
no hidden environment-dependent branches that would make a retry produce a
different configuration.

## Status / failure artifacts

- `results/pipeline_status.json` -- per-stage PASS/FAIL for the
  verify_and_smoke stage, plus full-stage submission record.
- `results/job_manifest.json` -- COMPLETED/FAILED/MISSING for every one of
  the 18 expected runs, with SLURM job ID and run directory.
- `results/failures.json` -- diagnostic detail (stage, error message, log
  path) for every FAILED run.
- Each run's own `experiments/<pair>/<tokenizer>/seed_<seed>/status.json`.

None of these files contain full hostnames, usernames beyond what SLURM
itself assigns as a job ID, or absolute paths outside this repository --
`results/final_report.md` in particular only ever references paths
relative to the repo root.
