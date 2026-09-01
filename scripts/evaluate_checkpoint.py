#!/usr/bin/env python3
"""Evaluate a trained checkpoint on the validation set.

Usage:
    python3 scripts/evaluate_checkpoint.py --language_pair en_am --tokenizer movoc_tok --seed 44
    python3 scripts/evaluate_checkpoint.py --language_pair en_am --tokenizer movoc_tok --seed 44 --num_beams 2
"""
from __future__ import annotations

import argparse
import json
import sys
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
from marianmt_comparison.reproducibility import utc_timestamp  # noqa: E402
from marianmt_comparison.evaluation import evaluate as chrf_evaluate  # noqa: E402
import torch  # noqa: E402
import numpy as np  # noqa: E402
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments  # noqa: E402
from marianmt_comparison.training import TranslationDataset, DataCollatorForSeq2Seq  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--language_pair", choices=["en_ti", "en_am"], required=True)
    p.add_argument("--tokenizer", choices=list(VALID_TOKENIZERS), required=True)
    p.add_argument("--seed", type=int, choices=list(VALID_SEEDS), required=True)
    p.add_argument("--num_beams", type=int, default=2, help="Number of beams for beam search")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    language_pair = args.language_pair
    tokenizer_name = args.tokenizer
    seed = args.seed
    num_beams = args.num_beams

    run_label = f"{language_pair}/{tokenizer_name}/seed_{seed}"
    print(f"=== Evaluating checkpoint: {run_label} ===")

    cfg = load_config(language_pair)
    tok_entry = tokenizer_config(cfg, tokenizer_name)
    tokenizer = load_tokenizer(tok_entry["path"])

    val_examples = load_split(language_pair, "validation", REPO_ROOT)
    print(f"Validation examples: {len(val_examples)}")

    run_dir = run_experiment_dir(language_pair, tokenizer_name, seed)
    checkpoint_dir = run_dir / "checkpoints" / "checkpoint-10000"

    if not checkpoint_dir.exists():
        print(f"ERROR: Checkpoint not found at {checkpoint_dir}", file=sys.stderr)
        return 1

    print(f"Loading model from {checkpoint_dir}")
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_dir)

    # Create validation dataset
    val_ds = TranslationDataset(
        val_examples,
        tokenizer,
        cfg["max_source_length"],
        cfg["max_target_length"],
    )

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(run_dir / "checkpoints"),
        per_device_eval_batch_size=cfg["batch_size"],
        generation_max_length=cfg["generation_max_length"],
        generation_num_beams=num_beams,
        predict_with_generate=True,
        report_to=[],
        disable_tqdm=True,
        fp16=torch.cuda.is_available(),
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        eval_dataset=val_ds,
        data_collator=collator,
        tokenizer=tokenizer,
    )

    print(f"Running prediction with num_beams={num_beams}...")
    predictions = trainer.predict(
        val_ds,
        max_length=cfg["generation_max_length"],
        num_beams=num_beams,
    )

    pred_ids = predictions.predictions
    pred_ids[pred_ids == -100] = tokenizer.pad_token_id
    hyps = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    refs = [ex.target for ex in val_examples]

    print("Computing CHRF++ and BLEU...")
    eval_result = chrf_evaluate(hyps, refs)

    validation_results = {
        "language_pair": language_pair,
        "tokenizer": tokenizer_name,
        "seed": seed,
        "split": "validation",
        "num_beams_used": num_beams,
        **eval_result.to_dict(),
        "timestamp": utc_timestamp(),
    }

    results_path = run_dir / "validation_results.json"
    results_path.write_text(json.dumps(validation_results, indent=2), encoding="utf-8")
    print(f"\nValidation results written to {results_path}")
    print(f"chrF++: {validation_results['chrf_plus_plus']:.4f}")
    print(f"BLEU:   {validation_results['bleu']:.4f}")

    # Mark as complete
    status = {
        "language_pair": language_pair,
        "tokenizer": tokenizer_name,
        "seed": seed,
        "status": "COMPLETED",
        "stage": "evaluate",
        "validation_chrfpp": validation_results["chrf_plus_plus"],
        "run_dir": str(run_dir),
        "num_beams": num_beams,
    }
    status_path = run_dir / "status.json"
    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"Status written to {status_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
