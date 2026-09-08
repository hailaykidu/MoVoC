#!/usr/bin/env python3
"""
Zero-Shot Evaluation for EN-Geez and EN-Tigre

This script performs zero-shot translation evaluation on models trained on:
  - EN-Amharic (MoVoC-Tok with full validation + correct tokenizer)
  - EN-Tigrinya (MoVoC-Tok with expanded validation + correct tokenizer)
  - BPE and WordPiece (best results from prior experiments)

Test data:
  - English-Geez: 100 parallel pairs  (data/extrinsic/en_gz/)
  - English-Tigre: 43 parallel pairs  (data/extrinsic/en_tig/)

Evaluates generalization to unseen languages via chrF++ and BLEU.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Tuple
from datetime import datetime

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from torch.utils.data import Dataset
from tqdm import tqdm

# For metrics
try:
    from sacrebleu.metrics import BLEU, CHRF
except ImportError:
    print("Installing sacrebleu...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "sacrebleu"], check=True)
    from sacrebleu.metrics import BLEU, CHRF

REPO_ROOT = Path(__file__).resolve().parents[1]

# Tokenizer weights are never vendored into this repo (see .gitignore); they
# are read read-only from the sibling amseg/ checkout by relative path, the
# same convention configs/*.yaml use.
AMSEG_ROOT = Path(__file__).resolve().parents[2] / "amseg"  # Adjacent repository

# Zero-shot evaluation sets live in the repo under data/extrinsic/<pair>/,
# each with source.txt + target.txt (one sentence per line) and a README.
# (en_tig and en_gz are the untrained / zero-shot directions; en_am and en_ti
# under the same directory are the trained pairs' held-out MT test sets.)
ZEROSHOT_DIRS = {
    "geez": REPO_ROOT / "data" / "extrinsic" / "en_gz",
    "tigre": REPO_ROOT / "data" / "extrinsic" / "en_tig",
}


class ZeroShotTranslationDataset(Dataset):
    """Dataset for zero-shot translation evaluation."""

    def __init__(self, source_lines: List[str], target_lines: List[str], tokenizer, max_length=128):
        """
        Initialize dataset.

        Args:
            source_lines: List of source language sentences
            target_lines: List of target language sentences (references)
            tokenizer: HuggingFace tokenizer
            max_length: Maximum sequence length
        """
        self.source_lines = source_lines
        self.target_lines = target_lines
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.source_lines)

    def __getitem__(self, idx):
        source = self.source_lines[idx]
        target = self.target_lines[idx]

        # Tokenize source
        source_tokens = self.tokenizer(
            source,
            max_length=self.max_length,
            truncation=True,
            return_tensors="pt"
        )

        return {
            "source": source,
            "target": target,
            "input_ids": source_tokens["input_ids"].squeeze(),
            "attention_mask": source_tokens["attention_mask"].squeeze(),
        }


def load_parallel_data(language: str) -> Tuple[List[str], List[str]]:
    """
    Load a zero-shot evaluation set from data/extrinsic/<pair>/.

    Args:
        language: "geez" or "tigre"

    Returns:
        Tuple of (source_lines, target_lines)
    """
    try:
        data_dir = ZEROSHOT_DIRS[language]
    except KeyError:
        raise ValueError(f"Unknown language: {language}")

    src_path, tgt_path = data_dir / "source.txt", data_dir / "target.txt"
    if not src_path.exists() or not tgt_path.exists():
        raise FileNotFoundError(
            f"Zero-shot set not found for {language}: expected {src_path} and {tgt_path}. "
            f"See {data_dir / 'README.md'}."
        )

    print(f"Loading {language.upper()} data from: {data_dir}")
    source_lines = src_path.read_text(encoding="utf-8").splitlines()
    target_lines = tgt_path.read_text(encoding="utf-8").splitlines()
    if len(source_lines) != len(target_lines):
        raise ValueError(
            f"{language}: source/target line count mismatch "
            f"({len(source_lines)} vs {len(target_lines)})"
        )

    print(f"Loaded {len(source_lines)} parallel pairs for {language.upper()}")
    return source_lines, target_lines


def translate_batch(
    model,
    tokenizer,
    source_lines: List[str],
    batch_size: int = 8,
    max_length: int = 128,
    num_beams: int = 4,
) -> List[str]:
    """
    Translate a batch of source sentences.

    Args:
        model: Seq2Seq model
        tokenizer: Tokenizer
        source_lines: Source sentences
        batch_size: Batch size for inference
        max_length: Maximum generation length
        num_beams: Number of beams for beam search

    Returns:
        List of translated sentences
    """
    translations = []
    device = next(model.parameters()).device

    for i in tqdm(range(0, len(source_lines), batch_size), desc="Translating"):
        batch_sources = source_lines[i : i + batch_size]

        # Tokenize batch
        inputs = tokenizer(
            batch_sources,
            max_length=max_length,
            truncation=True,
            return_tensors="pt",
            padding=True,
        ).to(device)

        # Generate translations
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
            )

        # Decode translations
        batch_translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translations.extend(batch_translations)

    return translations


def evaluate_zero_shot(
    model_name: str,
    model_path: str,
    tokenizer_path: str,
    language: str,
    source_lines: List[str],
    reference_lines: List[str],
) -> dict:
    """
    Evaluate zero-shot translation for a single model.

    Args:
        model_name: Name for results reporting
        model_path: Path to model weights
        tokenizer_path: Path to tokenizer
        language: Target language (geez or tigre)
        source_lines: Source sentences (English)
        reference_lines: Reference translations

    Returns:
        Dictionary with evaluation metrics
    """
    print(f"\n{'=' * 80}")
    print(f"Evaluating: {model_name} on {language.upper()}")
    print(f"{'=' * 80}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Load model and tokenizer
    print(f"Loading model from: {model_path}")
    print(f"Loading tokenizer from: {tokenizer_path}")

    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    # Translate
    print(f"Translating {len(source_lines)} sentences...")
    hypotheses = translate_batch(model, tokenizer, source_lines)

    # Evaluate metrics
    print("Computing metrics...")

    bleu = BLEU()
    chrf = CHRF()

    bleu_score = bleu.corpus_score(hypotheses, [reference_lines])
    chrf_score = chrf.corpus_score(hypotheses, [reference_lines])

    results = {
        "model": model_name,
        "language": language,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "test_set_size": len(hypotheses),
        "bleu": bleu_score.score,
        "chrf": chrf_score.score,
        "bleu_signature": str(bleu_score),
        "chrf_signature": str(chrf_score),
    }

    print(f"\nResults for {model_name} on {language.upper()}:")
    print(f"  BLEU:  {bleu_score.score:.4f}")
    print(f"  chrF:  {chrf_score.score:.4f}")
    print(f"  Signature: {bleu_score.signature}")

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Zero-shot translation evaluation for EN-Geez and EN-Tigre"
    )
    parser.add_argument(
        "--language",
        choices=["geez", "tigre", "both"],
        default="both",
        help="Language to evaluate",
    )
    parser.add_argument(
        "--models",
        choices=["movoc_only", "all", "best"],
        default="movoc_only",
        help="Which models to evaluate",
    )

    args = parser.parse_args()

    languages = ["geez", "tigre"] if args.language == "both" else [args.language]

    all_results = []

    # Define models to evaluate
    models_config = {
        "movoc_tigrinya_seed42": {
            "model_path": REPO_ROOT / "experiments/en_ti_full_validation/movoc_tok/seed_42",
            "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_tigrinya",
            "label": "MoVoC-Tok Tigrinya (Seed 42, Full Val)",
        },
        "movoc_tigrinya_seed43": {
            "model_path": REPO_ROOT / "experiments/en_ti_full_validation/movoc_tok/seed_43",
            "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_tigrinya",
            "label": "MoVoC-Tok Tigrinya (Seed 43, Full Val)",
        },
        "movoc_tigrinya_seed44": {
            "model_path": REPO_ROOT / "experiments/en_ti_full_validation/movoc_tok/seed_44",
            "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_tigrinya",
            "label": "MoVoC-Tok Tigrinya (Seed 44, Full Val)",
        },
        "movoc_amharic_seed42": {
            "model_path": REPO_ROOT / "experiments/en_am_full_validation_correct_tok/movoc_tok/seed_42",
            "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_amharic",
            "label": "MoVoC-Tok Amharic (Seed 42, Correct Tok)",
        },
        "movoc_amharic_seed43": {
            "model_path": REPO_ROOT / "experiments/en_am_full_validation_correct_tok/movoc_tok/seed_43",
            "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_amharic",
            "label": "MoVoC-Tok Amharic (Seed 43, Correct Tok)",
        },
        "movoc_amharic_seed44": {
            "model_path": REPO_ROOT / "experiments/en_am_full_validation_correct_tok/movoc_tok/seed_44",
            "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/movoc_tok_63050_amharic",
            "label": "MoVoC-Tok Amharic (Seed 44, Correct Tok)",
        },
    }

    # Add best from other tokenizers if requested
    if args.models in ["all", "best"]:
        # These would be populated from existing best results
        models_config.update({
            "bpe_best": {
                "model_path": REPO_ROOT / "experiments/en_am/bpe/seed_42",  # placeholder
                "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/bpe_63051",
                "label": "BPE (Best seed)",
            },
            "wordpiece_best": {
                "model_path": REPO_ROOT / "experiments/en_am/wordpiece/seed_42",  # placeholder
                "tokenizer_path": AMSEG_ROOT / "tokenizers/hf/wordpiece_63051",
                "label": "WordPiece (Best seed)",
            },
        })

    # Filter models based on --models argument
    if args.models == "movoc_only":
        models_to_eval = {k: v for k, v in models_config.items() if "movoc" in k}
    else:
        models_to_eval = models_config

    # Evaluate each language
    for language in languages:
        print(f"\n{'#' * 80}")
        print(f"# Evaluating {language.upper()}")
        print(f"{'#' * 80}")

        # Load data
        source_lines, reference_lines = load_parallel_data(language)

        # Evaluate each model
        for model_key, config in models_to_eval.items():
            try:
                results = evaluate_zero_shot(
                    model_name=config["label"],
                    model_path=str(config["model_path"]),
                    tokenizer_path=str(config["tokenizer_path"]),
                    language=language,
                    source_lines=source_lines,
                    reference_lines=reference_lines,
                )
                all_results.append(results)
            except Exception as e:
                print(f"ERROR evaluating {config['label']}: {e}")
                continue

    # Save results
    results_file = REPO_ROOT / "results/zero_shot_evaluation_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"Results saved to: {results_file}")
    print(f"{'=' * 80}")

    # Print summary
    print("\nSUMMARY:")
    print("-" * 80)
    for result in all_results:
        print(f"{result['model']:50} | {result['language'].upper():5} | BLEU: {result['bleu']:6.2f} | chrF: {result['chrf']:6.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
