#!/usr/bin/env python3
"""Evaluate a trained run's saved model on a given split (validation or
test). Test-split evaluation should only be invoked for the tokenizer
selected by scripts/select_best_tokenizer.py (spec section 8) -- this
script itself does not enforce that policy (it is a generic evaluator);
the policy is enforced by which commands slurm/pipeline.sbatch actually
issues (see docs/experimental_protocol.md).

Usage:
    python3 scripts/evaluate.py --language_pair en_ti --tokenizer bpe --seed 42 --split validation
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from transformers import MarianMTModel  # noqa: E402

from marianmt_comparison.config import VALID_SEEDS, VALID_TOKENIZERS, run_experiment_dir  # noqa: E402
from marianmt_comparison.config import load_config  # noqa: E402
from marianmt_comparison.data import load_split  # noqa: E402
from marianmt_comparison.evaluation import evaluate as chrf_evaluate  # noqa: E402
from marianmt_comparison.reproducibility import utc_timestamp  # noqa: E402
from marianmt_comparison.tokenization import load_tokenizer  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--language_pair", required=True, choices=["en_ti", "en_am"])
    p.add_argument("--tokenizer", required=True, choices=list(VALID_TOKENIZERS))
    p.add_argument("--seed", required=True, type=int, choices=list(VALID_SEEDS))
    p.add_argument("--split", required=True, choices=["validation", "test"])
    p.add_argument("--max_examples", type=int, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config(args.language_pair)
    run_dir = run_experiment_dir(args.language_pair, args.tokenizer, args.seed)
    model_dir = run_dir / "model"
    tok_dir = run_dir / "tokenizer_used"

    if not model_dir.exists():
        print(f"No trained model found at {model_dir}. Run scripts/train.py first.", file=sys.stderr)
        return 1

    if args.split == "test":
        print(
            "NOTE: evaluating on the TEST split. Per the selection procedure "
            "(spec section 8), this should only be done for the tokenizer that "
            "was already selected via mean validation chrF++. This script does "
            "not itself enforce that -- the caller is responsible."
        )

    tokenizer = load_tokenizer(tok_dir if tok_dir.exists() else cfg["tokenizers"][args.tokenizer]["path"])
    model = MarianMTModel.from_pretrained(model_dir)
    model.eval()

    examples = load_split(args.language_pair, args.split, REPO_ROOT, max_examples=args.max_examples)
    print(f"Evaluating on {len(examples)} {args.split} examples.")

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    hyps = []
    batch_size = cfg["batch_size"]
    for i in range(0, len(examples), batch_size):
        batch = examples[i : i + batch_size]
        inputs = tokenizer(
            [ex.source for ex in batch],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=cfg["max_source_length"],
        ).to(device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_length=cfg["generation_max_length"],
                num_beams=cfg["generation_num_beams"],
            )
        hyps.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))

    refs = [ex.target for ex in examples]
    result = chrf_evaluate(hyps, refs)

    out = {
        "language_pair": args.language_pair,
        "tokenizer": args.tokenizer,
        "seed": args.seed,
        "split": args.split,
        **result.to_dict(),
        "timestamp": utc_timestamp(),
    }
    out_path = run_dir / f"{args.split}_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"chrF++ = {result.chrf_score:.4f}, BLEU = {result.bleu_score:.4f}")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
