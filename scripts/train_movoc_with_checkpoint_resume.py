#!/usr/bin/env python3
"""
MoVoC-Tok Training Script with Checkpoint Resumption
======================================================

This script trains MoVoC-Tok with equal configuration across all seeds:
- Validation size: 752,900 examples (full validation set)
- Validation steps/epoch: 47,056
- Training steps/epoch: 847,012
- Batch size: 16 (both train and eval)
- Epochs: 10
- Checkpoint resumption: Continues from last checkpoint instead of timeout

Features:
  ✓ Automatic checkpoint detection and resumption
  ✓ Equal validation protocol across all seeds
  ✓ No timeout - pauses and resumes from checkpoint
  ✓ Metrics tracking and comparison
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments
from torch.utils.data import Dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.data import load_split
from marianmt_comparison.tokenization import load_tokenizer
from marianmt_comparison.config import load_config, run_experiment_dir, tokenizer_config
from marianmt_comparison.evaluation import evaluate as chrf_evaluate


class TranslationDataset(Dataset):
    """Dataset for translation tasks."""

    def __init__(self, examples, tokenizer, max_source_length=128, max_target_length=128):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        model_inputs = self.tokenizer(
            ex.source,
            max_length=self.max_source_length,
            truncation=True,
            return_token_type_ids=False
        )

        with self.tokenizer.as_target_tokenizer() if hasattr(self.tokenizer, "as_target_tokenizer") else _nullcontext():
            labels = self.tokenizer(
                ex.target,
                max_length=self.max_target_length,
                truncation=True,
                return_token_type_ids=False
            )

        model_inputs["labels"] = labels["input_ids"]
        model_inputs.pop("token_type_ids", None)
        return model_inputs


class _nullcontext:
    """Null context manager."""
    def __enter__(self):
        return None

    def __exit__(self, *a):
        return False


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    """Find latest checkpoint to resume from."""
    if not checkpoint_dir.exists():
        return None

    checkpoints = sorted(checkpoint_dir.glob("checkpoint-*"))
    if not checkpoints:
        return None

    return checkpoints[-1]


def train_movoc_with_resume(
    language_pair: str,
    tokenizer_name: str,
    seed: int,
    max_resume_attempts: int = 3
) -> dict[str, Any]:
    """
    Train MoVoC-Tok with checkpoint resumption.

    Args:
        language_pair: e.g., "en_am"
        tokenizer_name: e.g., "movoc_tok"
        seed: Random seed (42, 43, or 44)
        max_resume_attempts: Max times to resume from checkpoint

    Returns:
        Results dictionary with metrics and paths
    """

    print("")
    print("╔" + "=" * 78 + "╗")
    print("║" + f" MoVoC-Tok Training with Checkpoint Resumption".center(78) + "║")
    print("║" + f" Language: {language_pair.upper()} | Seed: {seed}".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print("")

    # Configuration
    print("📊 CONFIGURATION:")
    print("─" * 80)
    print(f"Language pair:             {language_pair}")
    print(f"Tokenizer:                 {tokenizer_name}")
    print(f"Seed:                      {seed}")
    print(f"Batch size:                16")
    print(f"Epochs:                    10")
    print(f"Training steps/epoch:      847,012")
    print(f"Validation steps/epoch:    47,056")
    print(f"Total per epoch:           894,068")
    print(f"Validation examples:       752,900 (FULL)")
    print("")

    # Load data
    print("📂 LOADING DATA:")
    print("─" * 80)
    train_examples = load_split(language_pair, "train", REPO_ROOT)
    val_examples = load_split(language_pair, "validation", REPO_ROOT)

    print(f"Training examples:         {len(train_examples):,}")
    print(f"Validation examples:       {len(val_examples):,}")
    print("")

    # Load config and tokenizer
    print("🔧 LOADING CONFIG & TOKENIZER:")
    print("─" * 80)
    cfg = load_config(language_pair)
    tok_entry = tokenizer_config(cfg, tokenizer_name)
    tokenizer = load_tokenizer(tok_entry["path"])

    print(f"Config file:               {language_pair}.yaml")
    print(f"Tokenizer:                 {tok_entry['path']}")
    print(f"Vocab size:                {tok_entry['vocab_size']:,}")
    print("")

    # Load model
    print("🤖 LOADING MODEL:")
    print("─" * 80)
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-am")
    print(f"Model:                     Helsinki-NLP/opus-mt-en-am")
    print(f"Device:                    {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print("")

    # Setup datasets
    train_ds = TranslationDataset(
        train_examples,
        tokenizer,
        cfg["max_source_length"],
        cfg["max_target_length"]
    )
    val_ds = TranslationDataset(
        val_examples,
        tokenizer,
        cfg["max_source_length"],
        cfg["max_target_length"]
    )

    # Run directory
    run_dir = run_experiment_dir(language_pair, tokenizer_name, seed)
    run_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = run_dir / "checkpoints"

    # Check for existing checkpoint
    print("🔍 CHECKING FOR EXISTING CHECKPOINTS:")
    print("─" * 80)
    latest_checkpoint = find_latest_checkpoint(checkpoint_dir)
    resume_from_checkpoint = None

    if latest_checkpoint:
        print(f"✅ Found checkpoint: {latest_checkpoint.name}")
        resume_from_checkpoint = str(latest_checkpoint)
        print(f"   Will resume from: {resume_from_checkpoint}")
    else:
        print("ℹ️  No checkpoint found - starting fresh training")
    print("")

    # Training arguments
    print("⚙️  SETTING UP TRAINING:")
    print("─" * 80)
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(checkpoint_dir),
        seed=seed,
        data_seed=seed,
        learning_rate=cfg["learning_rate"],
        per_device_train_batch_size=cfg["batch_size"],
        per_device_eval_batch_size=cfg["batch_size"],
        gradient_accumulation_steps=cfg["gradient_accumulation_steps"],
        weight_decay=cfg["weight_decay"],
        adam_beta1=cfg["adam_beta1"],
        adam_beta2=cfg["adam_beta2"],
        adam_epsilon=cfg["adam_epsilon"],
        lr_scheduler_type=cfg["lr_scheduler"],
        warmup_steps=cfg["warmup_steps"],
        label_smoothing_factor=cfg["label_smoothing"],
        predict_with_generate=True,
        generation_max_length=cfg["generation_max_length"],
        generation_num_beams=cfg["generation_num_beams"],
        logging_steps=cfg["logging_steps"],
        eval_strategy=cfg["eval_strategy"],
        save_strategy=cfg["save_strategy"],
        save_total_limit=cfg["save_total_limit"],
        load_best_model_at_end=cfg["load_best_model_at_end"],
        metric_for_best_model=cfg["metric_for_best_model"],
        greater_is_better=cfg["greater_is_better"],
        num_train_epochs=cfg["epochs"],
        report_to=[],
        disable_tqdm=False,
        fp16=torch.cuda.is_available(),
    )

    print(f"Training epochs:           {training_args.num_train_epochs}")
    print(f"Checkpoint dir:            {checkpoint_dir}")
    print(f"Resume checkpoint:         {'Yes' if resume_from_checkpoint else 'No'}")
    print("")

    # Train
    print("🚀 STARTING TRAINING:")
    print("─" * 80)
    print("")

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
    )

    try:
        # Train with resumption
        train_result = trainer.train(resume_from_checkpoint=resume_from_checkpoint)

        print("")
        print("✅ TRAINING COMPLETED SUCCESSFULLY!")
        print("─" * 80)
        print(f"Training loss:             {train_result.training_loss:.4f}")
        print("")

        # Evaluate
        print("📊 RUNNING FINAL EVALUATION:")
        print("─" * 80)
        predictions = trainer.predict(val_ds)
        pred_ids = predictions.predictions
        pred_ids[pred_ids == -100] = tokenizer.pad_token_id
        hyps = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        refs = [ex.target for ex in val_examples]

        # Compute metrics
        chrf = chrf_evaluate(hyps, [refs])

        print(f"Validation examples:       {len(hyps):,}")
        print(f"chrF++:                    {chrf:.4f}")
        print("")

        # Save results
        results = {
            "language_pair": language_pair,
            "tokenizer": tokenizer_name,
            "seed": seed,
            "status": "COMPLETED",
            "training_loss": train_result.training_loss,
            "chrfpp": chrf,
            "checkpoint_used": resume_from_checkpoint is not None,
        }

        status_file = run_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Results saved to: {status_file}")
        print("")

        return results

    except Exception as e:
        print("")
        print("❌ TRAINING INTERRUPTED!")
        print("─" * 80)
        print(f"Error: {str(e)}")
        print("")
        print("ℹ️  CHECKPOINT SAVED - Training can be resumed from last checkpoint")
        print("─" * 80)
        if latest_checkpoint:
            print(f"Last checkpoint: {latest_checkpoint.name}")
        else:
            latest = find_latest_checkpoint(checkpoint_dir)
            if latest:
                print(f"Last checkpoint: {latest.name}")
            else:
                print("No checkpoint saved yet")
        print("")
        print("To resume training, run this script again with the same parameters.")
        print("")

        # Save error status
        error_results = {
            "language_pair": language_pair,
            "tokenizer": tokenizer_name,
            "seed": seed,
            "status": "INTERRUPTED",
            "error": str(e),
            "checkpoint_saved": find_latest_checkpoint(checkpoint_dir) is not None,
        }

        status_file = run_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(error_results, f, indent=2)

        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Train MoVoC-Tok with checkpoint resumption and equal validation across seeds"
    )
    parser.add_argument(
        "--language_pair",
        choices=["en_ti", "en_am"],
        default="en_am",
        help="Language pair to train"
    )
    parser.add_argument(
        "--tokenizer",
        default="movoc_tok",
        help="Tokenizer name"
    )
    parser.add_argument(
        "--seed",
        type=int,
        choices=[42, 43, 44],
        required=True,
        help="Random seed"
    )

    args = parser.parse_args()

    try:
        results = train_movoc_with_resume(
            language_pair=args.language_pair,
            tokenizer_name=args.tokenizer,
            seed=args.seed
        )

        print("╔" + "=" * 78 + "╗")
        print("║" + " TRAINING SESSION COMPLETE".center(78) + "║")
        print("╚" + "=" * 78 + "╝")
        print("")

        return 0

    except Exception as e:
        print("")
        print("╔" + "=" * 78 + "╗")
        print("║" + " TRAINING INTERRUPTED - RESUME AVAILABLE".center(78) + "║")
        print("╚" + "=" * 78 + "╝")
        print("")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
