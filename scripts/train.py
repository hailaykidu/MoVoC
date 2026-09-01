#!/usr/bin/env python3
"""Train one (language_pair, tokenizer, seed) run, or the smoke test.

Usage:
    python3 scripts/train.py --language_pair en_ti --tokenizer bpe --seed 42
    python3 scripts/train.py --smoke_test

The smoke test uses configs/base.yaml's `smoke_test:` block (en_ti, bpe,
seed 42, small subset, 1 epoch) -- never changes learning rate or any other
recorded hyperparameter other than data size/epochs, which are explicitly
tagged as a smoke-test override in the written metadata.

Never silently retries with different settings. If a retry is desired, rerun
this exact command with the exact same arguments -- SLURM scripts (see
slurm/train_one.sbatch) do this by construction (array index -> fixed
(language_pair, tokenizer, seed) triple).
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import (  # noqa: E402
    VALID_SEEDS,
    VALID_TOKENIZERS,
    load_config,
    run_experiment_dir,
    tokenizer_config,
)
from marianmt_comparison.data import load_split  # noqa: E402
from marianmt_comparison.tokenization import load_tokenizer  # noqa: E402
from marianmt_comparison.training import run_training  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--language_pair", choices=["en_ti", "en_am"])
    p.add_argument("--tokenizer", choices=list(VALID_TOKENIZERS))
    p.add_argument("--seed", type=int, choices=list(VALID_SEEDS))
    p.add_argument("--smoke_test", action="store_true")
    p.add_argument("--max_steps", type=int, default=None, help="Max training steps (overrides num_train_epochs)")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.smoke_test:
        base_cfg_only = load_config("en_ti")
        smoke = base_cfg_only["smoke_test"]
        language_pair, tokenizer_name, seed = smoke["language_pair"], smoke["tokenizer"], smoke["seed"]
        max_train, max_eval = smoke["max_train_examples"], smoke["max_eval_examples"]
        epochs_override, batch_override = smoke["epochs"], smoke["batch_size"]
        run_label = "smoke_test"
    else:
        if not (args.language_pair and args.tokenizer and args.seed):
            print("Must pass --language_pair --tokenizer --seed, or --smoke_test", file=sys.stderr)
            return 2
        language_pair, tokenizer_name, seed = args.language_pair, args.tokenizer, args.seed
        max_train, max_eval = None, None
        epochs_override, batch_override = None, None
        run_label = f"{language_pair}/{tokenizer_name}/seed_{seed}"

    print(f"=== Training run: {run_label} ===")
    cfg = load_config(language_pair)
    if epochs_override is not None:
        cfg["epochs"] = epochs_override
    if batch_override is not None:
        cfg["batch_size"] = batch_override

    tok_entry = tokenizer_config(cfg, tokenizer_name)
    tokenizer = load_tokenizer(tok_entry["path"])

    train_examples = load_split(language_pair, "train", REPO_ROOT, max_examples=max_train)
    val_examples = load_split(language_pair, "validation", REPO_ROOT, max_examples=max_eval)
    print(f"train examples: {len(train_examples)}, validation examples: {len(val_examples)}")

    if args.smoke_test:
        run_dir = REPO_ROOT / "experiments" / "_smoke_test"
    else:
        run_dir = run_experiment_dir(language_pair, tokenizer_name, seed)

    manifest_path = REPO_ROOT / "data" / "manifests" / f"{language_pair}.json"
    dataset_identifier = f"OPUS-NLLB-{language_pair}"

    status_path = run_dir / "status.json"
    try:
        result = run_training(
            language_pair=language_pair,
            tokenizer_name=tokenizer_name,
            seed=seed,
            tokenizer=tokenizer,
            tokenizer_identifier=str(tok_entry["path"]),
            tokenizer_vocab_size=tok_entry["vocab_size"],
            train_examples=train_examples,
            val_examples=val_examples,
            cfg=cfg,
            run_dir=run_dir,
            dataset_identifier=dataset_identifier,
            dataset_manifest_path=str(manifest_path),
            max_steps=args.max_steps,
        )
    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        status = {
            "language_pair": language_pair,
            "tokenizer": tokenizer_name,
            "seed": seed,
            "status": "FAILED",
            "stage": "train",
            "error": str(exc),
            "traceback": tb,
        }
        run_dir.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print(f"TRAINING FAILED: {exc}", file=sys.stderr)
        print(tb, file=sys.stderr)
        return 1

    if not result["finite_loss"]:
        status = {
            "language_pair": language_pair,
            "tokenizer": tokenizer_name,
            "seed": seed,
            "status": "FAILED",
            "stage": "train",
            "error": "Non-finite training loss detected.",
        }
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
        print("TRAINING FAILED: non-finite loss.", file=sys.stderr)
        return 1

    status = {
        "language_pair": language_pair,
        "tokenizer": tokenizer_name,
        "seed": seed,
        "status": "COMPLETED",
        "stage": "train",
        "validation_chrfpp": result["validation_results"]["chrf_plus_plus"],
        "run_dir": result["run_dir"],
    }
    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"\nTRAINING COMPLETED: validation chrF++ = {result['validation_results']['chrf_plus_plus']:.4f}")
    print(f"Run directory: {result['run_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
