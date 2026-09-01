"""Two-stage model-selection procedure (spec section 8):

  1. Train all 9 (3 tokenizers x 3 seeds) for a language pair.
  2. Evaluate all 9 on the validation set.
  3. Compute mean+std validation chrF++ per tokenizer across seeds.
  4. Select the tokenizer with the highest MEAN validation chrF++
     (never a single best seed).
  5. Only then evaluate the selected tokenizer on the held-out test set.

This module is pure aggregation logic over already-computed per-run results;
it never re-runs training or evaluation itself.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any


@dataclass
class SeedResult:
    tokenizer: str
    seed: int
    validation_chrfpp: float
    test_chrfpp: float | None = None


@dataclass
class TokenizerSummary:
    tokenizer: str
    seed_count: int
    validation_chrfpp_mean: float
    validation_chrfpp_std: float
    test_chrfpp_mean: float | None
    test_chrfpp_std: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tokenizer": self.tokenizer,
            "seed_count": self.seed_count,
            "validation_chrfpp_mean": self.validation_chrfpp_mean,
            "validation_chrfpp_std": self.validation_chrfpp_std,
            "test_chrfpp_mean": self.test_chrfpp_mean,
            "test_chrfpp_std": self.test_chrfpp_std,
        }


def summarize_by_tokenizer(results: list[SeedResult]) -> list[TokenizerSummary]:
    by_tok: dict[str, list[SeedResult]] = {}
    for r in results:
        by_tok.setdefault(r.tokenizer, []).append(r)

    summaries = []
    for tok, rs in by_tok.items():
        val_scores = [r.validation_chrfpp for r in rs]
        test_scores = [r.test_chrfpp for r in rs if r.test_chrfpp is not None]
        summaries.append(
            TokenizerSummary(
                tokenizer=tok,
                seed_count=len(rs),
                validation_chrfpp_mean=round(statistics.mean(val_scores), 4),
                validation_chrfpp_std=round(statistics.pstdev(val_scores), 4) if len(val_scores) > 1 else 0.0,
                test_chrfpp_mean=round(statistics.mean(test_scores), 4) if test_scores else None,
                test_chrfpp_std=(
                    round(statistics.pstdev(test_scores), 4) if len(test_scores) > 1 else (0.0 if test_scores else None)
                ),
            )
        )
    return summaries


def select_best_tokenizer(summaries: list[TokenizerSummary]) -> TokenizerSummary:
    """Selects strictly by highest mean validation chrF++. Never touches
    test scores for the selection decision itself."""
    if not summaries:
        raise ValueError("No tokenizer summaries to select from.")
    return max(summaries, key=lambda s: s.validation_chrfpp_mean)
