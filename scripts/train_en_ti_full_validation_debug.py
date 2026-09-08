#!/usr/bin/env python3
"""
EN-Tigrinya MoVoC-Tok Training with Full Validation Set - DEBUG VERSION

This is an instrumented version of train_en_ti_full_validation.py
with detailed logging to identify where execution stalls after trainer.predict().

Added logging:
- GPU memory before/after trainer.predict()
- Timestamps for trainer.predict() entry/exit
- Timestamps for each post-prediction operation
- GPU synchronization diagnostics
"""

import argparse
import json
import sys
import os
import time
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


def load_full_validation_set(language_pair: str, repo_root: Path):
    """
    Load combined validation + test set for expanded validation.

    EN-TI variant uses validation (68,300) + test (68,301) = 136,601 examples
    for direct comparison with reduced validation (68,300 examples only).
    """
    val_examples = load_split(language_pair, "validation", repo_root)
    test_examples = load_split(language_pair, "test", repo_root)

    combined = val_examples + test_examples
    print(f"Loaded validation set: {len(val_examples):,} + test set: {len(test_examples):,} = {len(combined):,} total")

    return combined


def print_gpu_info(label: str):
    """Print GPU memory and device info with timestamp."""
    timestamp = time.time()
    try:
        alloc_gb = torch.cuda.memory_allocated() / 1e9
        reserved_gb = torch.cuda.memory_reserved() / 1e9
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[DEBUG] {timestamp:.2f} | {label}")
        print(f"[DEBUG] {timestamp:.2f} |   Device: {device}")
        print(f"[DEBUG] {timestamp:.2f} |   GPU Memory Allocated: {alloc_gb:.2f} GB")
        print(f"[DEBUG] {timestamp:.2f} |   GPU Memory Reserved: {reserved_gb:.2f} GB")
    except Exception as e:
        print(f"[DEBUG] GPU info error: {e}")
    sys.stdout.flush()


def train_en_ti_full_validation(
    seed: int,
    tokenizer_name: str = "movoc_tok"
) -> dict[str, Any]:
    """
    Train MoVoC-Tok on EN-TI with expanded validation set.

    Args:
        seed: Random seed (42, 43, or 44)
        tokenizer_name: Tokenizer to use (default: movoc_tok)

    Returns:
        Results dictionary with metrics
    """

    language_pair = "en_ti"
    variant_name = "full_validation"

    print("")
    print("╔" + "=" * 78 + "╗")
    print("║" + f" EN-Tigrinya MoVoC-Tok Training (Full Validation Set) - DEBUG".center(78) + "║")
    print("║" + f" Seed: {seed}".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print("")

    # Configuration
    print("📊 CONFIGURATION")
    print("─" * 80)
    print(f"Language pair:             {language_pair.upper()}")
    print(f"Tokenizer:                 {tokenizer_name}")
    print(f"Variant:                   {variant_name}")
    print(f"Seed:                      {seed}")
    print(f"Batch size:                16")
    print(f"Epochs:                    10")
    print(f"Training examples:         1,229,400")
    print(f"Validation examples:       136,601 (val+test combined)")
    print(f"Validation steps/epoch:    {136601 // 16:,} (136,601 ÷ 16)")
    print(f"Training steps/epoch:      {1229400 // 16:,} (1,229,400 ÷ 16)")
    print("")
    print("Comparison to Previous:")
    print(f"  Old validation size:     68,300 examples → chrF++ 7.60")
    print(f"  New validation size:     136,601 examples (2× larger)")
    print("")

    # Load data
    print("📂 LOADING DATA")
    print("─" * 80)
    train_examples = load_split(language_pair, "train", REPO_ROOT)
    val_examples = load_full_validation_set(language_pair, REPO_ROOT)

    print(f"Training examples:         {len(train_examples):,}")
    print(f"Validation examples:       {len(val_examples):,}")
    print("")

    # Load config and tokenizer
    print("🔧 LOADING CONFIG & TOKENIZER")
    print("─" * 80)
    cfg = load_config(language_pair)

    # Use 63050 constrained BPE for Tigrinya (Algorithm 3.3, morpheme-aware)
    AMSEG_ROOT = REPO_ROOT / "../amseg"
    tokenizer_path = AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_tigrinya"
    tokenizer = load_tokenizer(str(tokenizer_path))

    print(f"Config file:               {language_pair}.yaml")
    print(f"Tokenizer:                 movoc_tok_63050_tigrinya (63050 vocab, constrained BPE + padding)")
    print(f"Vocab size:                {tokenizer.vocab_size:,}")
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
    run_dir = REPO_ROOT / "experiments" / f"{language_pair}_{variant_name}" / tokenizer_name / f"seed_{seed}"
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

        # ════════════════════════════════════════════════════════════════════════════
        # EVALUATION WITH DEBUGGING
        # ════════════════════════════════════════════════════════════════════════════
        print("📊 RUNNING FINAL EVALUATION")
        print("─" * 80)

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 1: PRE-PREDICT STATE
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_pre = time.time()
        print(f"[DEBUG] {timestamp_pre:.2f} | Pre-prediction state:")
        print_gpu_info("Pre-predict GPU info")

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 2: ENTERING trainer.predict()
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_enter = time.time()
        print(f"[DEBUG] {timestamp_enter:.2f} | >>> Entering trainer.predict(val_ds)")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # THE CRITICAL CALL: trainer.predict()
        # ───────────────────────────────────────────────────────────────────────────
        predictions = trainer.predict(val_ds)

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 3: EXITING trainer.predict()
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_exit = time.time()
        elapsed = timestamp_exit - timestamp_enter
        print(f"[DEBUG] {timestamp_exit:.2f} | <<< Exiting trainer.predict() after {elapsed:.2f}s")
        print(f"[DEBUG] {timestamp_exit:.2f} | Predictions type: {type(predictions)}")
        print(f"[DEBUG] {timestamp_exit:.2f} | Predictions keys: {predictions.__dict__.keys() if hasattr(predictions, '__dict__') else 'N/A'}")
        print_gpu_info("Post-predict GPU info")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 4: ACCESSING predictions.predictions
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_attr = time.time()
        print(f"[DEBUG] {timestamp_attr:.2f} | >>> Accessing predictions.predictions")
        sys.stdout.flush()

        pred_ids = predictions.predictions

        timestamp_attr_done = time.time()
        print(f"[DEBUG] {timestamp_attr_done:.2f} | <<< Got pred_ids")
        print(f"[DEBUG] {timestamp_attr_done:.2f} | pred_ids shape: {pred_ids.shape}")
        print(f"[DEBUG] {timestamp_attr_done:.2f} | pred_ids dtype: {pred_ids.dtype}")
        print(f"[DEBUG] {timestamp_attr_done:.2f} | pred_ids device: {pred_ids.device if hasattr(pred_ids, 'device') else 'N/A'}")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 5: MASKING OPERATION
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_mask_start = time.time()
        print(f"[DEBUG] {timestamp_mask_start:.2f} | >>> Starting masking operation")
        sys.stdout.flush()

        pred_ids[pred_ids == -100] = tokenizer.pad_token_id

        timestamp_mask_done = time.time()
        print(f"[DEBUG] {timestamp_mask_done:.2f} | <<< Masking completed in {timestamp_mask_done - timestamp_mask_start:.2f}s")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 6: TOKENIZER BATCH DECODE
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_decode_start = time.time()
        print(f"[DEBUG] {timestamp_decode_start:.2f} | >>> Starting tokenizer.batch_decode()")
        sys.stdout.flush()

        hyps = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)

        timestamp_decode_done = time.time()
        print(f"[DEBUG] {timestamp_decode_done:.2f} | <<< Batch decode completed in {timestamp_decode_done - timestamp_decode_start:.2f}s")
        print(f"[DEBUG] {timestamp_decode_done:.2f} | Decoded {len(hyps)} hypotheses")
        print(f"[DEBUG] {timestamp_decode_done:.2f} | First 3 samples:")
        for i, h in enumerate(hyps[:3]):
            print(f"[DEBUG]   [{i}]: {h[:100]}...")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 7: REFERENCE LIST CREATION
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_refs_start = time.time()
        print(f"[DEBUG] {timestamp_refs_start:.2f} | >>> Creating reference list")
        sys.stdout.flush()

        refs = [ex.target for ex in val_examples]

        timestamp_refs_done = time.time()
        print(f"[DEBUG] {timestamp_refs_done:.2f} | <<< Reference list created in {timestamp_refs_done - timestamp_refs_start:.2f}s")
        print(f"[DEBUG] {timestamp_refs_done:.2f} | Generated {len(refs)} references")
        print(f"[DEBUG] {timestamp_refs_done:.2f} | First 3 samples:")
        for i, r in enumerate(refs[:3]):
            print(f"[DEBUG]   [{i}]: {r[:100]}...")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 8: METRIC COMPUTATION
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_metric_start = time.time()
        print(f"[DEBUG] {timestamp_metric_start:.2f} | >>> Starting chrf_evaluate()")
        sys.stdout.flush()

        chrf_result = chrf_evaluate(hyps, refs)

        timestamp_metric_done = time.time()
        print(f"[DEBUG] {timestamp_metric_done:.2f} | <<< Metric computation completed in {timestamp_metric_done - timestamp_metric_start:.2f}s")
        sys.stdout.flush()

        # ───────────────────────────────────────────────────────────────────────────
        # DEBUG 9: SCORE EXTRACTION
        # ───────────────────────────────────────────────────────────────────────────
        timestamp_score = time.time()
        print(f"[DEBUG] {timestamp_score:.2f} | >>> Extracting chrf_score")
        sys.stdout.flush()

        chrf_score = chrf_result.chrf_score

        print(f"[DEBUG] {timestamp_score:.2f} | <<< chrf_score extracted: {chrf_score}")
        sys.stdout.flush()

        # ═══════════════════════════════════════════════════════════════════════════
        # NORMAL EVALUATION CONTINUES (All prior operations succeeded)
        # ═══════════════════════════════════════════════════════════════════════════

        print(f"Validation examples:       {len(hyps):,}")
        print(f"chrF++:                    {chrf_score:.4f}")
        print("")

        # Save results
        results = {
            "language_pair": language_pair,
            "variant": variant_name,
            "tokenizer": tokenizer_name,
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
            "tokenizer": tokenizer_name,
            "seed": seed,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        status_file = run_dir / "status.json"
        with open(status_file, "w") as f:
            json.dump(error_results, f, indent=2)

        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train EN-Tigrinya MoVoC-Tok with full validation set")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--tokenizer", type=str, default="movoc_tok", help="Tokenizer name")
    args = parser.parse_args()

    train_en_ti_full_validation(seed=args.seed, tokenizer_name=args.tokenizer)
