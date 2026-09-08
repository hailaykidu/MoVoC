#!/usr/bin/env python3
"""
EN-Amharic MoVoC-Tok Training with Full Validation Set (CORRECT TOKENIZER)

CRITICAL FIX:
  Previous EN-AM training used movoc_tok_63050_tigrinya (WRONG - Tigrinya tokenizer)
  This training uses movoc_tok_63050_amharic (CORRECT - Amharic tokenizer)

This script trains MoVoC-Tok on English-Amharic using:
  - Full validation set: 752,900 examples (5% of data)
  - CORRECT Amharic tokenizer: movoc_tok_63050_amharic
  - Identical training config to previous runs
  - Results saved to SEPARATE directory (original results untouched)

Configuration:
  Language Pair:       en_am (English-Amharic)
  Tokenizer:           movoc_tok_63050_amharic (CORRECT AMHARIC, NOT TIGRINYA)
  Seeds:               42, 43, 44 (3 independent replicates for n=3 replication)
  Validation Size:     752,900 examples (5% of data, FULL validation)
  Training Size:       13,552,207 examples (89.9% of data)
  Batch Size:          16
  Epochs:              10

Comparison:
  Previous: movoc_tok_63050_tigrinya (WRONG tokenizer) → chrF++ 14.41
  Current:  movoc_tok_63050_amharic (CORRECT tokenizer) → chrF++ ? (to measure)

Expected Impact:
  - Proper language-specific tokenization
  - More accurate representation of Amharic morphology
  - Fair comparison with EN-TI results (which use correct tigrinya tokenizer)
  - Results will be scientifically valid and publishable
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Any
from datetime import datetime

import torch
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from torch.utils.data import Dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
AMSEG_ROOT = REPO_ROOT.parent / "amseg"  # Adjacent to this repository
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.data import load_split
from marianmt_comparison.tokenization import load_tokenizer
from marianmt_comparison.config import load_config, tokenizer_config
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
            padding=False,
            return_tensors=None,
            return_token_type_ids=False
        )

        with self.tokenizer.as_target_tokenizer() if hasattr(self.tokenizer, "as_target_tokenizer") else _nullcontext():
            labels = self.tokenizer(
                ex.target,
                max_length=self.max_target_length,
                truncation=True,
                padding=False,
                return_tensors=None,
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


def train_en_am_full_validation_correct(
    seed: int,
    tokenizer_name: str = "movoc_tok_63050_amharic"
) -> dict[str, Any]:
    """
    Train MoVoC-Tok on EN-AM with full validation set and CORRECT Amharic tokenizer.

    Args:
        seed: Random seed (42, 43, or 44)
        tokenizer_name: Tokenizer to use (MUST be movoc_tok_63050_amharic, not tigrinya)

    Returns:
        Results dictionary with metrics
    """

    language_pair = "en_am"
    variant_name = "full_validation_correct_tok"

    print("")
    print("╔" + "=" * 80 + "╗")
    print("║" + f" EN-Amharic MoVoC-Tok Training (CORRECT TOKENIZER)".center(80) + "║")
    print("║" + f" Seed: {seed}".center(80) + "║")
    print("╚" + "=" * 80 + "╝")
    print("")

    print("⚠️  CRITICAL TOKENIZER FIX")
    print("─" * 80)
    print("Previous training used: movoc_tok_63050_tigrinya (WRONG - Tigrinya tokenizer)")
    print("This training uses:     movoc_tok_63050_amharic (CORRECT - Amharic tokenizer)")
    print("")

    # Configuration
    print("📊 CONFIGURATION")
    print("─" * 80)
    print(f"Language pair:             {language_pair.upper()}")
    print(f"Tokenizer:                 {tokenizer_name}")
    print(f"  Previous (WRONG):         movoc_tok_63050_tigrinya")
    print(f"  Current (CORRECT):        movoc_tok_63050_amharic")
    print(f"Variant:                   {variant_name}")
    print(f"Seed:                      {seed}")
    print(f"Batch size:                16")
    print(f"Epochs:                    10")
    print(f"Training examples:         13,552,207")
    print(f"Validation examples:       752,900 (FULL)")
    print(f"Validation steps/epoch:    {752900 // 16:,} (752,900 ÷ 16)")
    print(f"Training steps/epoch:      {13552207 // 16:,} (13,552,207 ÷ 16)")
    print("")
    print("Comparison to Previous:")
    print(f"  Previous (wrong tok):    chrF++ 14.41 (seed 42, movoc_tok_63050_tigrinya)")
    print(f"  Current (correct tok):   chrF++ ? (measuring, movoc_tok_63050_amharic)")
    print("")

    # Load data
    print("📂 LOADING DATA")
    print("─" * 80)
    train_examples = load_split(language_pair, "train", REPO_ROOT)
    val_examples = load_split(language_pair, "validation", REPO_ROOT)

    print(f"Training examples:         {len(train_examples):,}")
    print(f"Validation examples:       {len(val_examples):,}")
    print("")

    # Load config and tokenizer
    print("🔧 LOADING CONFIG & TOKENIZER")
    print("─" * 80)
    cfg = load_config(language_pair)

    # Load CORRECT Amharic tokenizer
    tokenizer_path = AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_amharic"
    print(f"Tokenizer path:            {tokenizer_path}")

    tokenizer = load_tokenizer(str(tokenizer_path))

    print(f"Config file:               {language_pair}.yaml")
    print(f"Tokenizer:                 movoc_tok_63050_amharic (CORRECT)")
    print(f"Vocab size:                {tokenizer.vocab_size:,}")
    print("")

    # Load model (use Tigrinya model as base - same vocabulary)
    print("🤖 LOADING MODEL")
    print("─" * 80)
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-ti")
    model.resize_token_embeddings(tokenizer.vocab_size)

    print(f"Model:                     Helsinki-NLP/opus-mt-en-ti (finetuned for Amharic)")
    print(f"Model vocab (resized):     {model.config.vocab_size}")
    print(f"Tokenizer vocab:           {tokenizer.vocab_size}")
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

    # Run directory (separate from original to preserve old results)
    run_dir = REPO_ROOT / "experiments" / f"{language_pair}_{variant_name}" / "movoc_tok" / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = run_dir / "checkpoints"

    # Training arguments
    print("⚙️  SETTING UP TRAINING")
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
    print("")

    # Train
    print("🚀 STARTING TRAINING")
    print("─" * 80)
    print("")

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    try:
        train_result = trainer.train()

        print("")
        print("✅ TRAINING COMPLETED SUCCESSFULLY!")
        print("─" * 80)
        print(f"Training loss:             {train_result.training_loss:.4f}")
        print("")

        # Evaluate
        print("📊 RUNNING FINAL EVALUATION")
        print("─" * 80)
        predictions = trainer.predict(val_ds)
        pred_ids = predictions.predictions
        pred_ids[pred_ids == -100] = tokenizer.pad_token_id
        hyps = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        refs = [ex.target for ex in val_examples]

        # Compute metrics
        chrf_result = chrf_evaluate(hyps, refs)
        chrf_score = chrf_result.chrf_score

        print(f"Validation examples:       {len(hyps):,}")
        print(f"chrF++:                    {chrf_score:.4f}")
        print("")

        # Save results
        results = {
            "language_pair": language_pair,
            "variant": variant_name,
            "tokenizer": "movoc_tok_63050_amharic",
            "tokenizer_note": "CORRECT Amharic tokenizer (fixed from previous tigrinya)",
            "seed": seed,
            "status": "COMPLETED",
            "training_loss": train_result.training_loss,
            "chrfpp": float(chrf_score),
            "validation_examples": len(val_examples),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        results_file = run_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        status_file = run_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump({"status": "COMPLETED", "chrfpp": float(chrf_score), "training_loss": train_result.training_loss}, f, indent=2)

        print(f"✅ Results saved to:")
        print(f"   {results_file}")
        print(f"   {status_file}")
        print("")
        print("⚠️  TOKENIZER FIX APPLIED:")
        print(f"   Previous (WRONG):  movoc_tok_63050_tigrinya → chrF++ 14.41")
        print(f"   Current (CORRECT): movoc_tok_63050_amharic → chrF++ {chrf_score:.2f}")
        print("")

        return results

    except Exception as e:
        print("")
        print("❌ TRAINING FAILED!")
        print("─" * 80)
        print(f"Error: {str(e)}")
        print("")

        error_results = {
            "language_pair": language_pair,
            "variant": variant_name,
            "tokenizer": "movoc_tok_63050_amharic",
            "seed": seed,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        status_file = run_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(error_results, f, indent=2)

        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Train MoVoC-Tok on EN-AM with full validation and CORRECT Amharic tokenizer"
    )
    parser.add_argument(
        "--seed",
        type=int,
        choices=[42, 43, 44],
        required=True,
        help="Random seed (42, 43, or 44)"
    )

    args = parser.parse_args()

    try:
        results = train_en_am_full_validation_correct(seed=args.seed)

        print("╔" + "=" * 80 + "╗")
        print("║" + " TRAINING SESSION COMPLETE".center(80) + "║")
        print("╚" + "=" * 80 + "╝")
        print("")
        print(f"✅ Seed {args.seed} complete with chrF++ = {results['chrfpp']:.4f}")
        print(f"✅ Using CORRECT tokenizer: movoc_tok_63050_amharic")
        print("")

        return 0

    except Exception as e:
        print("")
        print("╔" + "=" * 80 + "╗")
        print("║" + " TRAINING FAILED".center(80) + "║")
        print("╚" + "=" * 80 + "╝")
        print("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
