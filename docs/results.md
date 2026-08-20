# Results

This file is a pointer, not generated content. The authoritative,
auto-generated results live in:

- `results/en_ti/summary.csv`, `results/en_am/summary.csv` -- mean +/- std
  validation and test chrF++ per tokenizer.
- `results/en_ti/best_tokenizer.json`, `results/en_am/best_tokenizer.json`
  -- the tokenizer selected by mean validation chrF++ per language pair.
- `results/en_ti/validation_per_seed.csv`, `results/en_ti/test_per_seed.csv`
  (and the `en_am/` equivalents) -- every individual run's score.
- `results/final_report.md` -- the full auto-generated report (experimental
  configuration, dataset info, MarianMT checkpoint resolution, tokenizer
  info, per-seed and mean+-SD validation chrF++, selected tokenizer per
  language pair, held-out test chrF++, failed/missing runs, reproduction
  info), produced by `scripts/aggregate_results.py`.
- `results/job_manifest.json`, `results/failures.json`,
  `results/pipeline_status.json` -- machine-readable run/pipeline status.

None of the files under `results/` are pre-filled or hand-edited; they are
all produced by running the pipeline (`sbatch slurm/pipeline.sbatch`, then
`PIPELINE_STAGE=full sbatch slurm/pipeline.sbatch`) and are regenerated
in-place by `scripts/aggregate_results.py` every time it runs. Before the
pipeline has been run, `results/` is empty except for `.gitkeep` files.
