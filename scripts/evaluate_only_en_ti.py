#!/usr/bin/env python3
"""
Evaluation-only script for Phase 1 (EN-Tigrinya)

This script:
1. Loads TRAINED checkpoints (does NOT retrain)
2. Runs predictions on validation set
3. Computes chrF++ and BLEU metrics
4. Saves results.json

Purpose: Decouple evaluation from training to avoid losing training work
         when evaluation fails
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import torch
from transformers import AutoModelForSeq2SeqLM

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.data import load_split
from marianmt_comparison.tokenization import load_tokenizer
from marianmt_comparison.config import load_config
from marianmt_comparison.evaluation import evaluate as chrf_evaluate


def evaluate_phase1_checkpoint(seed: int) -> dict:
    """
    Evaluate a trained Phase 1 checkpoint.

    Args:
        seed: Random seed (42, 43, or 44)

    Returns:
        Results dictionary with metrics
    """

    language_pair = "en_ti"
    variant_name = "full_validation"

    print("")
    print("╔" + "=" * 80 + "╗")
    print("║" + f" PHASE 1 EVALUATION-ONLY (EN-TIGRINYA)".center(80) + "║")
    print("║" + f" Seed: {seed}".center(80) + "║")
    print("╚" + "=" * 80 + "╝")
    print("")

    # Load data
    print("📂 LOADING DATA")
    print("─" * 80)
    train_examples = load_split(language_pair, "train", REPO_ROOT)
    val_examples = load_split(language_pair, "validation", REPO_ROOT)
    test_examples = load_split(language_pair, "test", REPO_ROOT)
    val_examples = val_examples + test_examples

    print(f"Training examples:         {len(train_examples):,}")
    print(f"Validation examples:       {len(val_examples):,} (val+test combined)")
    print("")

    # Load config and tokenizer
    print("🔧 LOADING CONFIG & TOKENIZER")
    print("─" * 80)
    cfg = load_config(language_pair)

    AMSEG_ROOT = REPO_ROOT / "../amseg"
    tokenizer_path = AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_tigrinya"
    tokenizer = load_tokenizer(str(tokenizer_path))

    print(f"Tokenizer:                 movoc_tok_63050_tigrinya (63050 vocab)")
    print(f"Vocab size:                {tokenizer.vocab_size:,}")
    print("")

    # Find and load best checkpoint
    print("🤖 LOADING CHECKPOINT")
    print("─" * 80)

    checkpoint_dir = REPO_ROOT / "experiments" / f"{language_pair}_{variant_name}" / "movoc_tok" / f"seed_{seed}" / "checkpoints"

    if not checkpoint_dir.exists():
        print(f"❌ ERROR: Checkpoint directory not found: {checkpoint_dir}")
        return {"status": "FAILED", "error": f"Checkpoint directory not found"}

    # Find best checkpoint (usually the last one saved)
    checkpoints = sorted(checkpoint_dir.glob("checkpoint-*"), key=lambda x: int(x.name.split("-")[1]))
    if not checkpoints:
        print(f"❌ ERROR: No checkpoints found in {checkpoint_dir}")
        return {"status": "FAILED", "error": "No checkpoints found"}

    best_checkpoint = checkpoints[-1]  # Use latest checkpoint
    print(f"Checkpoint dir:            {checkpoint_dir}")
    print(f"Using checkpoint:          {best_checkpoint.name}")
    print("")

    try:
        model = AutoModelForSeq2SeqLM.from_pretrained(str(best_checkpoint))
        model.to("cuda" if torch.cuda.is_available() else "cpu")
        model.eval()

        print(f"Model loaded:              Helsinki-NLP/opus-mt-en-ti (finetuned)")
        print(f"Device:                    {'cuda' if torch.cuda.is_available() else 'cpu'}")
        print("")
    except Exception as e:
        print(f"❌ ERROR loading checkpoint: {e}")
        return {"status": "FAILED", "error": str(e)}

    # Evaluate
    print("📊 RUNNING EVALUATION")
    print("─" * 80)

    try:
        # Generate predictions
        sources = [ex.source for ex in val_examples]
        refs = [ex.target for ex in val_examples]

        print(f"Generating predictions for {len(sources):,} examples...")

        # Batch prediction
        batch_size = 16
        hyps = []

        with torch.no_grad():
            for i in range(0, len(sources), batch_size):
                batch_sources = sources[i:i+batch_size]

                inputs = tokenizer(
                    batch_sources,
                    max_length=128,
                    truncation=True,
                    padding=True,
                    return_tensors="pt"
                ).to(model.device)

                outputs = model.generate(
                    **inputs,
                    max_length=128,
                    num_beams=4,
                    length_penalty=2.0
                )

                batch_hyps = tokenizer.batch_decode(outputs, skip_special_tokens=True)
                hyps.extend(batch_hyps)

                if (i // batch_size + 1) % 10 == 0:
                    print(f"  └─ {min(i+batch_size, len(sources)):,} / {len(sources):,} done")

        print(f"✅ Predictions generated: {len(hyps):,}")
        print("")

        # Compute metrics
        print("📈 COMPUTING METRICS")
        print("─" * 80)

        chrf_result = chrf_evaluate(hyps, refs)
        chrf_score = chrf_result.chrf_score
        bleu_score = chrf_result.bleu_score

        print(f"Validation examples:       {len(hyps):,}")
        print(f"chrF++:                    {chrf_score:.4f}")
        print(f"BLEU:                      {bleu_score:.4f}")
        print("")

        # Save results
        print("💾 SAVING RESULTS")
        print("─" * 80)

        run_dir = REPO_ROOT / "experiments" / f"{language_pair}_{variant_name}" / "movoc_tok" / f"seed_{seed}"
        run_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "language_pair": language_pair,
            "variant": variant_name,
            "tokenizer": "movoc_tok_63050_tigrinya",
            "seed": seed,
            "checkpoint": best_checkpoint.name,
            "status": "COMPLETED",
            "chrfpp": float(chrf_score),
            "bleu": float(bleu_score),
            "validation_examples": len(val_examples),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        results_file = run_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Results saved to: {results_file}")
        print("")

        return results

    except Exception as e:
        print("")
        print("❌ EVALUATION FAILED!")
        print("─" * 80)
        print(f"Error: {str(e)}")
        print("")

        import traceback
        traceback.print_exc()

        return {
            "language_pair": language_pair,
            "variant": variant_name,
            "seed": seed,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate Phase 1 (EN-Tigrinya) trained checkpoints"
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
        results = evaluate_phase1_checkpoint(seed=args.seed)

        if results.get("status") == "COMPLETED":
            print("╔" + "=" * 80 + "╗")
            print("║" + " EVALUATION COMPLETE".center(80) + "║")
            print("╚" + "=" * 80 + "╝")
            print("")
            print(f"✅ Seed {args.seed} evaluation complete")
            print(f"   chrF++: {results['chrfpp']:.4f}")
            print(f"   BLEU:   {results['bleu']:.4f}")
            print("")
            return 0
        else:
            print("╔" + "=" * 80 + "╗")
            print("║" + " EVALUATION FAILED".center(80) + "║")
            print("╚" + "=" * 80 + "╝")
            print("")
            return 1

    except Exception as e:
        print("")
        print("╔" + "=" * 80 + "╗")
        print("║" + " EVALUATION FAILED".center(80) + "║")
        print("╚" + "=" * 80 + "╝")
        print("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
