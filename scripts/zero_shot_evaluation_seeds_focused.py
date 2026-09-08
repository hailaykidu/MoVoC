#!/usr/bin/env python3
"""
Focused Zero-Shot Evaluation: Seeds 42 & 44 for EN-Geez and EN-Tigre

This script performs zero-shot translation evaluation using:
  - PHASE 1 (EN-Tigrinya): Seeds 42 & 44 for BPE, MoVoC-Tok, WordPiece
  - PHASE 2A (EN-Amharic): Seeds 42 & 43 for BPE, MoVoC-Tok, WordPiece

Test data:
  - English-Geez: 100 parallel pairs
  - English-Tigre: 60 parallel pairs

Metrics: BLEU, chrF++, token coverage, UNK rate, fertility
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Tuple, Dict
from datetime import datetime

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

try:
    from sacrebleu.metrics import BLEU, CHRF
except ImportError:
    print("Installing sacrebleu...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "sacrebleu"], check=True)
    from sacrebleu.metrics import BLEU, CHRF

REPO_ROOT = Path(__file__).resolve().parents[1]
AMSEG_ROOT = REPO_ROOT.parent / "amseg"  # Adjacent to this repository

ZEROSHOT_DIRS = {
    "geez": REPO_ROOT / "data" / "extrinsic" / "en_gz",
    "tigre": REPO_ROOT / "data" / "extrinsic" / "en_tig",
}

class ZeroShotTranslationDataset(Dataset):
    """Dataset for zero-shot translation evaluation."""

    def __init__(self, source_lines: List[str], target_lines: List[str], tokenizer, max_length=128):
        self.source_lines = source_lines
        self.target_lines = target_lines
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.source_lines)

    def __getitem__(self, idx):
        source = self.source_lines[idx]
        target = self.target_lines[idx]

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
    """Load zero-shot evaluation set."""
    if language not in ZEROSHOT_DIRS:
        raise ValueError(f"Unknown language: {language}")

    data_dir = ZEROSHOT_DIRS[language]
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    source_file = data_dir / "source.txt"
    target_file = data_dir / "target.txt"

    if not source_file.exists() or not target_file.exists():
        raise FileNotFoundError(f"Missing source.txt or target.txt in {data_dir}")

    with open(source_file, "r", encoding="utf-8") as f:
        source_lines = [line.rstrip("\n") for line in f if line.strip()]

    with open(target_file, "r", encoding="utf-8") as f:
        target_lines = [line.rstrip("\n") for line in f if line.strip()]

    if len(source_lines) != len(target_lines):
        raise ValueError(f"Mismatch: {len(source_lines)} sources vs {len(target_lines)} targets")

    return source_lines, target_lines


def evaluate_model(
    model_path: str,
    source_lines: List[str],
    target_lines: List[str],
    batch_size: int = 8,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Dict[str, Any]:
    """
    Evaluate a single model on zero-shot translation.

    Returns metrics dict with BLEU, chrF++, token coverage, UNK rate, fertility.
    """
    print(f"  Loading model: {model_path}")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    model.to(device)
    model.eval()

    dataset = ZeroShotTranslationDataset(source_lines, target_lines, tokenizer)

    # Define custom collate function to handle variable-length sequences
    def collate_fn_pad_sequences(batch):
        """Pad sequences in batch to same length."""
        from torch.nn.utils.rnn import pad_sequence
        input_ids = pad_sequence(
            [item["input_ids"] for item in batch],
            batch_first=True,
            padding_value=tokenizer.pad_token_id or 0
        )
        attention_mask = pad_sequence(
            [item["attention_mask"] for item in batch],
            batch_first=True,
            padding_value=0
        )
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "source": [item["source"] for item in batch],
            "target": [item["target"] for item in batch],
        }

    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn_pad_sequences)

    hypotheses = []
    references = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Generating translations"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            # Generate translations
            outputs = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=128,
                num_beams=1,
                early_stopping=True,
            )

            # Decode
            batch_hyps = tokenizer.batch_decode(outputs, skip_special_tokens=True)
            hypotheses.extend(batch_hyps)
            references.extend(batch.get("target", []))

    # Compute metrics
    bleu = BLEU(effective_order=False)
    chrf = CHRF(word_order=2, lowercase=False)

    bleu_score = bleu.corpus_score(hypotheses, [references])
    chrf_score = chrf.corpus_score(hypotheses, [references])

    # Token coverage and UNK rate
    unk_token = tokenizer.unk_token or "<unk>"
    unk_count = sum(1 for hyp in hypotheses if unk_token in hyp)
    unk_rate = unk_count / len(hypotheses) if hypotheses else 0

    # Fertility (avg target/source length ratio)
    source_lengths = [len(tokenizer.encode(s, add_special_tokens=False)) for s in source_lines]
    target_lengths = [len(tokenizer.encode(h, add_special_tokens=False)) for h in hypotheses]
    fertility = sum(target_lengths) / sum(source_lengths) if source_lengths else 0

    return {
        "model_path": model_path,
        "num_examples": len(hypotheses),
        "bleu": bleu_score.score,
        "chrf": chrf_score.score,
        "unk_rate": unk_rate,
        "fertility": fertility,
        "hypotheses": hypotheses[:10],  # Sample first 10
        "references": references[:10],
    }


def main():
    parser = argparse.ArgumentParser(description="Focused zero-shot evaluation (seeds 42 & 44)")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "experiments" / "zero_shot_evaluation_seeds_focused"),
                        help="Output directory for results")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size for inference")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="Device")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define models: Phase 1 (seeds 42,44) + Phase 2 (seeds 42,43)
    models = {
        "en_ti_bpe_42": REPO_ROOT / "experiments" / "en_ti" / "bpe" / "seed_42" / "model",
        "en_ti_bpe_44": REPO_ROOT / "experiments" / "en_ti" / "bpe" / "seed_44" / "model",
        "en_ti_movoc_42": REPO_ROOT / "experiments" / "en_ti" / "movoc_tok" / "seed_42" / "model",
        "en_ti_movoc_44": REPO_ROOT / "experiments" / "en_ti" / "movoc_tok" / "seed_44" / "model",
        "en_ti_wordpiece_42": REPO_ROOT / "experiments" / "en_ti" / "wordpiece" / "seed_42" / "model",
        "en_ti_wordpiece_44": REPO_ROOT / "experiments" / "en_ti" / "wordpiece" / "seed_44" / "model",
        "en_am_bpe_42": REPO_ROOT / "experiments" / "en_am" / "bpe" / "seed_42" / "model",
        "en_am_bpe_43": REPO_ROOT / "experiments" / "en_am" / "bpe" / "seed_43" / "model",
        "en_am_movoc_42": REPO_ROOT / "experiments" / "en_am" / "movoc_tok" / "seed_42" / "model",
        "en_am_movoc_43": REPO_ROOT / "experiments" / "en_am" / "movoc_tok" / "seed_43" / "model",
        "en_am_wordpiece_42": REPO_ROOT / "experiments" / "en_am" / "wordpiece" / "seed_42" / "model",
        "en_am_wordpiece_43": REPO_ROOT / "experiments" / "en_am" / "wordpiece" / "seed_43" / "model",
    }

    # Load data
    print("Loading zero-shot test data...")
    geez_source, geez_target = load_parallel_data("geez")
    tigre_source, tigre_target = load_parallel_data("tigre")

    print(f"  Geez: {len(geez_source)} pairs")
    print(f"  Tigre: {len(tigre_source)} pairs\n")

    # Evaluate all models
    results = {}

    for language, (source, target) in [("geez", (geez_source, geez_target)), ("tigre", (tigre_source, tigre_target))]:
        print(f"\n{'='*80}")
        print(f"Evaluating on EN-{language.upper()}")
        print(f"{'='*80}\n")

        results[language] = {}

        for model_name, model_path in models.items():
            if not model_path.exists():
                print(f"⚠️  Skipping {model_name} - path not found: {model_path}")
                continue

            print(f"\nEvaluating {model_name}...")
            try:
                result = evaluate_model(str(model_path), source, target, args.batch_size, args.device)
                results[language][model_name] = result
                print(f"  ✅ BLEU: {result['bleu']:.4f} | chrF++: {result['chrf']:.4f}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results[language][model_name] = {"error": str(e)}

    # Save results
    results_file = output_dir / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Results saved to: {results_file}")
    print(f"{'='*80}\n")

    # Summary
    print("\nSUMMARY")
    print("="*80)
    for language in ["geez", "tigre"]:
        print(f"\nEN-{language.upper()}:")
        for model_name in sorted(results[language].keys()):
            result = results[language][model_name]
            if "error" in result:
                print(f"  {model_name}: ERROR - {result['error']}")
            else:
                print(f"  {model_name}: BLEU={result['bleu']:.4f} | chrF++={result['chrf']:.4f}")


if __name__ == "__main__":
    main()
