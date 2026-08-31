# Experimental protocol

## Scientific question

Under the same MarianMT architecture, OPUS parallel data, training
configuration, and three random seeds, which of BPE, WordPiece, or
MoVoC-Tok provides the strongest en->ti and en->am translation performance
by chrF++?

## Design

- 2 language pairs (en_ti, en_am) x 3 tokenizers (bpe, wordpiece,
  movoc_tok) x 3 seeds (42, 43, 44) = **18 full training runs**.
- Fixed learning rate **1.44e-7** for every run. This value has previously
  produced degenerate/near-zero results in a related experiment; it is
  used anyway here per an explicit, recorded decision -- if the 18 runs
  show flat/near-zero chrF++, that is an anticipated possible outcome of
  this specific hyperparameter choice, not necessarily evidence of a bug
  in this pipeline. See `README.md` "Known caveats" #1.
- All other hyperparameters (batch size, epochs, optimizer, scheduler,
  label smoothing, generation settings) are fixed across all 18 runs and
  come from `configs/base.yaml`.

## Tokenizer policy

All three tokenizers are pre-trained, external, read-only artifacts for the
MT pipeline's purposes (see `Tokenizers/*/README.md` for exact source paths
on this host). This repository:

- never retrains, resizes, truncates, or merges any tokenizer vocabulary;
- never changes normalization or special tokens;
- loads each tokenizer via `AutoTokenizer.from_pretrained(<absolute path>)`
  and records its exact configuration and vocabulary size as read from disk
  (`scripts/verify_tokenizers.py` -> `data/manifests/tokenizer_manifest.json`).

### Vocab sizes are not uniform across language pairs

- `en_ti`: all three tokenizers at vocab size 63051.
- `en_am`: bpe/wordpiece at vocab size 32000; movoc_tok at vocab size
  63051 (HF export; native 63050) because it **reuses** the Tigrinya-trained
  MoVoC-Tok tokenizer -- no Amharic-trained 63k MoVoC-Tok exists. This is a
  deliberate, user-approved decision, recorded loudly in
  `Tokenizers/movoc_tok/README.md`, `configs/en_am.yaml`, and the tokenizer
  manifest (`"cross_lingual_reuse": true`). Expect elevated fertility/UNK
  rate for this condition; `scripts/verify_tokenizers.py` measures and
  prints this but does not block the pipeline.

## MarianMT model and embedding adaptation

`Helsinki-NLP/opus-mt-en-ti` is the intended base checkpoint for en_ti.
`Helsinki-NLP/opus-mt-en-am` is attempted for en_am; if it does not resolve
on the HuggingFace Hub, a MarianMT model is constructed from scratch with
architecture hyperparameters matching `marian_original`'s setup (6+6
layers, 8 heads, d_model 512, ffn 2048, shared embeddings; see
`configs/base.yaml`'s `model:` block). This resolution is checked live
(network required) by `scripts/verify_models.py` and again by
`scripts/train.py` at the start of every run, and the outcome
(found/not_found/fallback_used) is recorded per run.

For every (tokenizer, base model) pair, `src/marianmt_comparison/model.py`'s
`build_model_for_tokenizer`:

1. Loads/constructs the base model.
2. Resizes input embeddings and output projection to `len(tokenizer)`,
   verifying the resulting shapes explicitly.
3. Re-initializes newly-added embedding rows using a normal distribution
   matching the existing checkpoint's embedding std (or, for from-scratch
   construction, all rows are initialized this way).
4. Verifies special token IDs (pad/unk/bos/eos) are in-range and do not
   collide with each other.
5. Raises `ModelAdaptationError` with the specific failing check and
   actual-vs-expected values if any of the above fails.
6. Writes `embedding_adaptation_report.json` into the run's experiment
   directory.

`scripts/verify_models.py` runs this logic in check mode for all 6
(tokenizer x language_pair) combinations before any training, and hard-fails
the pipeline (nonzero exit) if any combination fails.

## Data

OPUS NLLB parallel corpus (moses format), downloaded fresh at pipeline run
time by `scripts/prepare_opus_data.py` (plain `requests` + `zipfile`, no
`opustools` dependency). Same parallel examples are used across all three
tokenizer conditions within a language pair -- the train/validation/test
split happens once, before any tokenizer sees the data (`data_split_seed`
in `configs/base.yaml`, independent of the 3 training seeds). The test
split is never touched for tokenizer training or model selection.

Preprocessing: whitespace-strip each line; drop empty lines; drop any line
pair where either side exceeds `max_whitespace_tokens` (250)
whitespace-split tokens. Exact thresholds and resulting split sizes +
SHA256 checksums are recorded in `data/manifests/{en_ti,en_am}.json`.

## Evaluation

chrF++ via sacrebleu 2.6.0: `char_order=6, word_order=2, beta=2,
lowercase=False, whitespace=False`. BLEU (`sacrebleu.corpus_bleu`
defaults) as a secondary metric. Every run records `sacrebleu.__version__`
and the exact chrF signature string.

## Model-selection procedure (never select on test)

Per language pair:

1. Train all 9 runs (3 tokenizers x 3 seeds).
2. Evaluate all 9 on the validation set.
3. Compute mean + std validation chrF++ per tokenizer across its 3 seeds
   (`src/marianmt_comparison/selection.py`).
4. Select the tokenizer with the **highest mean validation chrF++**.
   A single best-performing seed is never used to select a tokenizer.
5. Only then evaluate the selected tokenizer's 3 checkpoints on the
   held-out test set (`scripts/evaluate.py --split test`, invoked only for
   the tokenizer named in `results/{language_pair}/best_tokenizer.json`).

`scripts/select_best_tokenizer.py` implements steps 3-4 and prints the
exact follow-up `scripts/evaluate.py` commands for step 5; it does not
itself run test-set evaluation.

## Metadata recorded per run

Every run (`experiments/<pair>/<tokenizer>/seed_<seed>/metadata.json`)
records: language_pair, tokenizer, seed, model_identifier, model_revision,
tokenizer_identifier, tokenizer_revision, tokenizer_vocab_size,
dataset_identifier, dataset_manifest, learning_rate, batch_size, epochs,
max_source_length, max_target_length, optimizer, scheduler,
sacrebleu_version, chrF++ signature, git_commit, timestamp. No credentials,
tokens, or unnecessary cluster identifiers are recorded.

## Smoke test

Before the 18 full runs: English->Tigrinya, BPE, seed 42, on a small data
subset (`configs/base.yaml`'s `smoke_test:` block: 200 train / 50 eval
examples, 1 epoch). Verifies dataset loading, tokenizer loading,
tokenizer/model integration, vocabulary mapping, forward pass, finite loss,
generation, chrF++ computation, output writing, and checkpoint writing. If
it fails, the 18 full training runs must not be submitted --
`slurm/pipeline.sbatch`'s default stage enforces this by stopping before
the full sweep is ever queued.
