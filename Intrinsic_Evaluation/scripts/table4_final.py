#!/usr/bin/env python3
"""Table 4 (FINAL): Morpheme Boundary Precision and Renyi Entropy (alpha=2)
for 32k vocabularies, MoVoC-Tok vs BPE.

Evaluation data: the surface-projected morpheme boundary sets
(../{lang}_boundary_projected.tsv, produced by
project_surface_boundaries.py from ../{lang}_annotated_clean.json),
not resource-size estimates (corpus sizes, vocabulary-building
resources, NLLB/HornMT/FLORES/OPUS totals, Mermru.com counts, Tigre
corpus counts).

LANGUAGE ROLES:
  In-language (MoVoC-Tok vocabulary construction used these):
    Amharic (amh), Tigrinya (tir)
  Cross-lingual (NOT used for MoVoC-Tok vocabulary construction; each
  still evaluated on its own gold annotations, using Tigrinya's MoVoC-Tok
  model since no dedicated model exists for either):
    Ge'ez (gez), Tigre (tig)

PRECISION (per predicted boundary, exact matching, no tolerance):
  Step 1: tokenizer segmentation of the word.
  Step 2: segmentation -> character-offset boundary positions.
  Step 3: gold morpheme boundary positions from the annotated dataset.
  Step 4: for every PREDICTED boundary, match=1 if it equals a gold
          boundary exactly, else match=0.
  Step 5: Precision = matched predicted boundaries / total predicted
          boundaries (micro-averaged: summed over the whole evaluation
          set, then divided once).
  Step 6: reported as a percentage (0.855 -> 85.5).

RENYI ENTROPY (alpha=2), over the empirical token frequency distribution
induced by tokenizing the full evaluation word list:
  H_2(nats) = (1/(1-alpha)) * log( sum_i p_i^alpha ),  alpha=2
  H_2(normalized) = H_2(nats) / log(support)

where p_i is token i's empirical probability under the tokenizer's
segmentation of the evaluation corpus, and support = number of unique
tokens actually used. The normalization (dividing by log(support), the
entropy of a uniform distribution over the tokens in use) matches the
existing intrinsic evaluation framework's convention
(amseg/scripts/evaluate_intrinsic.py:normalized_renyi_entropy).

Usage:
    python3 scripts/table4_final.py
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer, PreTrainedTokenizerBase

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"

WORD_START_MARKER = "▁"
WORDPIECE_CONTINUATION = "##"

LANG_NAMES = {"amh": "Amharic", "tir": "Tigrinya", "gez": "Ge'ez", "tig": "Tigre"}

TOKENIZERS_32K = {
    "amh": {
        "bpe": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_32k",
        "movoc_tok": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_amharic",
        "mode": "in_language",
    },
    "tir": {
        "bpe": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_32k",
        "movoc_tok": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_tigrinya",
        "mode": "in_language",
    },
    "tig": {
        "bpe": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_32k",
        "movoc_tok": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_tigrinya",
        "mode": "cross_lingual",
    },
    "gez": {
        "bpe": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_32k",
        "movoc_tok": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_tigrinya",
        "mode": "cross_lingual",
    },
}


def load_gold_words(language: str) -> list[tuple[str, list[str]]]:
    """Load the surface-projected gold set ({lang}_boundary_projected.tsv).
    Returns (word, morpheme pieces) pairs, including single-morpheme
    (unsegmented) words -- exclusion of those happens in
    evaluate_tokenizer, based on the TOKENIZER's predicted boundary count,
    not the gold boundary count."""
    path = PROJECT_ROOT / f"{language}_boundary_projected.tsv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run scripts/project_surface_boundaries.py first."
        )
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        word, pieces_str = line.split("\t")
        out.append((word, pieces_str.split("+")))
    return out


def gold_boundaries_from_pieces(pieces: list[str]) -> set[int]:
    boundaries = set()
    offset = 0
    for p in pieces[:-1]:
        offset += len(p)
        boundaries.add(offset)
    return boundaries


def predicted_boundaries(tokenizer: PreTrainedTokenizerBase, word: str) -> tuple[set[int], list[str]]:
    """Strip word-start/continuation markers, drop any resulting empty
    piece, and compute boundaries from the cleaned piece list directly."""
    ids = tokenizer.encode(word, add_special_tokens=False)
    pieces = tokenizer.convert_ids_to_tokens(ids)
    cleaned = []
    for p in pieces:
        text = p
        if text.startswith(WORD_START_MARKER):
            text = text[len(WORD_START_MARKER):]
        if text.startswith(WORDPIECE_CONTINUATION):
            text = text[len(WORDPIECE_CONTINUATION):]
        if text:
            cleaned.append(text)
    boundaries = set()
    offset = 0
    for p in cleaned[:-1]:
        offset += len(p)
        boundaries.add(offset)
    return boundaries, pieces


def evaluate_tokenizer(tokenizer_path: str, gold_items: list[tuple[str, list[str]]]) -> dict[str, Any]:
    """Words with zero PREDICTED boundaries ("unsegmented") are excluded
    from Boundary Precision, not scored as either a match or a failure --
    counted separately for transparency."""
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    total_matched = 0
    total_predicted = 0
    n_words_evaluated = 0
    n_excluded_unsegmented = 0

    token_counts: Counter[str] = Counter()
    total_tokens = 0

    for word, pieces in gold_items:
        g_bounds = gold_boundaries_from_pieces(pieces)
        p_bounds, tok_pieces = predicted_boundaries(tokenizer, word)

        for tp in tok_pieces:
            token_counts[tp] += 1
            total_tokens += 1

        if not p_bounds:
            n_excluded_unsegmented += 1
            continue

        matched = len(p_bounds & g_bounds)
        total_matched += matched
        total_predicted += len(p_bounds)
        n_words_evaluated += 1

    precision = (total_matched / total_predicted) if total_predicted > 0 else float("nan")
    precision_pct = round(precision * 100, 1) if precision == precision else float("nan")

    # Renyi entropy (alpha=2), NORMALIZED by log(support): divides raw
    # Renyi entropy (in nats) by log(support) -- support = number of
    # unique tokens actually used -- so the result lands in [0, 1] rather
    # than raw bits/nats, which scale with vocabulary size.
    if total_tokens > 0 and len(token_counts) > 1:
        probs = [c / total_tokens for c in token_counts.values()]
        power_sum = sum(p * p for p in probs)  # alpha=2
        raw_renyi_nats = math.log(power_sum) / (1.0 - 2.0) if power_sum > 0 else float("nan")
        support = len(token_counts)
        renyi_entropy = raw_renyi_nats / math.log(support)
    else:
        renyi_entropy = 0.0

    return {
        "tokenizer_path": tokenizer_path,
        "vocab_size": len(tokenizer),
        "n_gold_words": len(gold_items),
        "n_words_evaluated": n_words_evaluated,
        "n_excluded_unsegmented": n_excluded_unsegmented,
        "total_predicted_boundaries": total_predicted,
        "total_matched_boundaries": total_matched,
        "precision": round(precision, 4) if precision == precision else "nan",
        "precision_pct": precision_pct,
        "renyi_entropy_alpha2": round(renyi_entropy, 4) if renyi_entropy == renyi_entropy else "nan",
        "unique_tokens_used": len(token_counts),
        "total_tokens_emitted": total_tokens,
    }


def run() -> dict[str, dict[str, dict]]:
    results: dict[str, dict[str, dict]] = {}
    for language in ("amh", "tir", "gez", "tig"):
        gold_items = load_gold_words(language)
        entry = TOKENIZERS_32K[language]
        results[language] = {"mode": entry["mode"], "n_gold_words_filtered": len(gold_items)}
        for tok_name in ("movoc_tok", "bpe"):
            r = evaluate_tokenizer(entry[tok_name], gold_items)
            results[language][tok_name] = r
            print(
                f"{LANG_NAMES[language]:10} {tok_name:10} "
                f"n_words={r['n_words_evaluated']:>7} "
                f"Precision={r['precision_pct']}  RenyiEntropy(a=2)={r['renyi_entropy_alpha2']}"
            )
    return results


def main() -> int:
    RESULTS_DIR.mkdir(exist_ok=True)

    print("=== Table 4: 32k vocabulary ===\n")
    results = run()
    out_path = RESULTS_DIR / "table4_32k_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
