#!/usr/bin/env python3
"""
Boundary Test: Determine if trainer.predict() returns

This script is IDENTICAL to train_en_ti_full_validation.py with two changes ONLY:
1. Uses ultra-small validation subset (1000 examples instead of 136,601)
2. Adds boundary markers immediately before and after trainer.predict()

All model checkpoints, tokenizer, Trainer configuration, and evaluation pipeline
are IDENTICAL to the original. The goal is to establish, with certainty, whether
trainer.predict() returns to the Python script.

Configuration (IDENTICAL to original):
  Language Pair:       en_ti (English-Tigrinya)
  Model:               Helsinki-NLP/opus-mt-en-ti
  Tokenizer:           movoc_tok_63050_tigrinya (63051 vocab)
  Config:              configs/base.yaml + configs/en_ti.yaml
  Batch Size:          16
  Epochs:              10
  Validation Size:     1,000 examples (ultra-small, from combined val+test)
  Training Size:       1,229,400 examples
  predict_with_generate: True (critical for generation)
  generation_num_beams: 4
  generation_max_length: 128

Expected Results:
  - If both [BOUNDARY] markers print: trainer.predict() returns; issue is downstream
  - If only entry marker prints: trainer.predict() does not return; hang is internal
  - If exit marker prints but evaluation stalls: trainer.predict() returns; line 286+ hangs
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
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.data import load_split
from marianmt_comparison.tokenization import load_tokenizer
from marianmt_comparison.config import load_config
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


def load_boundary_test_set(language_pair: str, repo_root: Path, size: int = 1000):
    """
    Load small validation subset for boundary testing.

    Combines validation + test set (same as original) but takes only first `size` examples.

    Args:
        language_pair: e.g., "en_ti"
        repo_root: path to repo root
        size: number of examples (default 1000)

    Returns:
        List of `size` examples from combined validation + test set
    """
    val_examples = load_split(language_pair, "validation", repo_root)
    test_examples = load_split(language_pair, "test", repo_root)
    combined = val_examples + test_examples

    subset = combined[:size]
    print(f"Loaded boundary test set: {len(subset):,} examples (from {len(combined):,} total)")

    return subset


def train_en_ti_boundary_test(seed: int, test_size: int = 1000):
    """
    Boundary test version: IDENTICAL to original except with small validation set
    and boundary markers around trainer.predict().

    Args:
        seed: Random seed (42, 43, or 44)
        test_size: Number of validation examples for boundary test (default 1000)
    """

    language_pair = "en_ti"
    variant_name = "boundary_test"
    tokenizer_name = "movoc_tok"

    print("")
    print("╔" + "=" * 78 + "╗")
    print("║" + f" BOUNDARY TEST: trainer.predict() Return Status".center(78) + "║")
    print("║" + f" Seed: {seed} | Test Size: {test_size:,} examples".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print("")

    # Configuration
    print("📊 CONFIGURATION (IDENTICAL TO ORIGINAL)")
    print("─" * 80)
    print(f"Language pair:             {language_pair.upper()}")
    print(f"Model:                     Helsinki-NLP/opus-mt-en-ti")
    print(f"Tokenizer:                 movoc_tok_63050_tigrinya")
    print(f"Seed:                      {seed}")
    print(f"Batch size:                16")
    print(f"Epochs:                    10")
    print(f"predict_with_generate:     True")
    print(f"generation_num_beams:      4")
    print(f"generation_max_length:     128")
    print(f"Learning rate:             3.0e-5 (configured)")
    print("")
    print("BOUNDARY TEST SPECIFIC:")
    print(f"Validation size:           {test_size:,} examples (ultra-small, from val+test combined)")
    print(f"Training size:             1,229,400 examples (unchanged)")
    print(f"Expected prediction time:  ~10-30 seconds (vs 2:21 for 136,601)")
    print("")

    # Load data
    print("📂 LOADING DATA")
    print("─" * 80)
    train_examples = load_split(language_pair, "train", REPO_ROOT)
    val_examples = load_boundary_test_set(language_pair, REPO_ROOT, size=test_size)

    print(f"Training examples:         {len(train_examples):,}")
    print(f"Validation examples:       {len(val_examples):,}")
    print("")

    # Load config and tokenizer
    print("🔧 LOADING CONFIG & TOKENIZER")
    print("─" * 80)
    cfg = load_config(language_pair)

    AMSEG_ROOT = REPO_ROOT / "../amseg"
    tokenizer_path = AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_tigrinya"
    tokenizer = load_tokenizer(str(tokenizer_path))

    print(f"Config file:               configs/base.yaml + configs/en_ti.yaml")
    print(f"Tokenizer path:            {tokenizer_path}")
    print(f"Tokenizer vocab size:      {tokenizer.vocab_size:,}")
    print("")

    # Load model
    print("🤖 LOADING MODEL")
    print("─" * 80)
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-ti")
        model.resize_token_embeddings(tokenizer.vocab_size)
    except Exception as e:
        print(f"ERROR loading model: {e}")
        raise

    print(f"Model:                     Helsinki-NLP/opus-mt-en-ti")
    print(f"Model vocab (resized):     {model.config.vocab_size}")
    print(f"Device:                    {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print("")

    # Setup datasets (IDENTICAL to original)
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
    run_dir = REPO_ROOT / "experiments" / f"{language_pair}_{variant_name}" / tokenizer_name / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = run_dir / "checkpoints"

    # Training arguments (IDENTICAL to original)
    print("⚙️  SETTING UP TRAINING (CONFIG IDENTICAL TO ORIGINAL)")
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
    print(f"Batch size:                {training_args.per_device_train_batch_size}")
    print(f"Learning rate:             {training_args.learning_rate}")
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

        # ════════════════════════════════════════════════════════════════════════
        # BOUNDARY TEST: CRITICAL SECTION
        # These two markers prove whether trainer.predict() returns to Python
        # ════════════════════════════════════════════════════════════════════════

        print("📊 RUNNING BOUNDARY TEST")
        print("─" * 80)

        # BOUNDARY MARKER 1: Entry
        print("[BOUNDARY] Entering trainer.predict() at " + datetime.utcnow().isoformat() + "Z", flush=True)
        sys.stdout.flush()

        # THE CRITICAL CALL (IDENTICAL to original, line 285)
        predictions = trainer.predict(val_ds)

        # BOUNDARY MARKER 2: Exit (only prints if trainer.predict() returns)
        print("[BOUNDARY] Exiting trainer.predict() at " + datetime.utcnow().isoformat() + "Z", flush=True)
        print(f"[BOUNDARY] Returned type: {type(predictions)}", flush=True)
        if hasattr(predictions, 'predictions'):
            print(f"[BOUNDARY] predictions.predictions shape: {predictions.predictions.shape}", flush=True)
        sys.stdout.flush()

        # ════════════════════════════════════════════════════════════════════════
        # BOUNDARY TEST COMPLETE
        # If we reach here, trainer.predict() returned successfully.
        # Now continue with standard evaluation (identical to original).
        # ════════════════════════════════════════════════════════════════════════

        # Evaluate (IDENTICAL to original, lines 286-296)
        pred_ids = predictions.predictions
        pred_ids[pred_ids == -100] = tokenizer.pad_token_id
        hyps = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        refs = [ex.target for ex in val_examples]

        # Compute metrics (IDENTICAL to original, lines 292-293)
        chrf_result = chrf_evaluate(hyps, refs)
        chrf_score = chrf_result.chrf_score

        print(f"Validation examples:       {len(hyps):,}")
        print(f"chrF++:                    {chrf_score:.4f}")
        print("")

        # Save results (IDENTICAL to original, lines 300-318)
        results = {
            "language_pair": language_pair,
            "variant": variant_name,
            "tokenizer": tokenizer_name,
            "seed": seed,
            "test_size": test_size,
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

        return results

    except Exception as e:
        print("")
        print("❌ BOUNDARY TEST FAILED!")
        print("─" * 80)
        print(f"Error: {str(e)}")
        print("")

        error_results = {
            "language_pair": language_pair,
            "variant": variant_name,
            "tokenizer": tokenizer_name,
            "seed": seed,
            "test_size": test_size,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        status_file = run_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(error_results, f, indent=2)

        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Boundary test for trainer.predict() return status")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (42, 43, or 44)")
    parser.add_argument("--size", type=int, default=1000, help="Validation set size for boundary test")
    args = parser.parse_args()

    train_en_ti_boundary_test(seed=args.seed, test_size=args.size)
