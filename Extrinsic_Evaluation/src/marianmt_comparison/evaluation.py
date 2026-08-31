"""chrF++ (primary) and BLEU (secondary) evaluation via sacrebleu, using the
exact API/signature confirmed for sacrebleu==2.6.0 on the target host.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sacrebleu
from sacrebleu.metrics import CHRF, BLEU

# Fixed per RESOLVED DECISION #7 -- do not change without a new explicit
# decision; every run records these values + the exact signature string.
CHRF_CONFIG = dict(char_order=6, word_order=2, beta=2, lowercase=False, whitespace=False)


@dataclass
class EvaluationResult:
    chrf_score: float
    chrf_signature: str
    bleu_score: float
    bleu_signature: str
    sacrebleu_version: str
    num_hypotheses: int
    num_references: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chrf_plus_plus": self.chrf_score,
            "chrf_signature": self.chrf_signature,
            "bleu": self.bleu_score,
            "bleu_signature": self.bleu_signature,
            "sacrebleu_version": self.sacrebleu_version,
            "num_hypotheses": self.num_hypotheses,
            "num_references": self.num_references,
        }


def evaluate(hypotheses: list[str], references: list[str]) -> EvaluationResult:
    """references: one reference per hypothesis (single-reference OPUS data).
    sacrebleu expects references as list-of-lists (one list per reference set).
    """
    if len(hypotheses) != len(references):
        raise ValueError(
            f"hypotheses/references length mismatch: {len(hypotheses)} vs {len(references)}"
        )
    refs = [references]

    chrf_metric = CHRF(**CHRF_CONFIG)
    chrf_result = chrf_metric.corpus_score(hypotheses, refs)
    chrf_signature = chrf_metric.get_signature().format()

    bleu_metric = BLEU()
    bleu_result = bleu_metric.corpus_score(hypotheses, refs)
    bleu_signature = bleu_metric.get_signature().format()

    return EvaluationResult(
        chrf_score=chrf_result.score,
        chrf_signature=chrf_signature,
        bleu_score=bleu_result.score,
        bleu_signature=bleu_signature,
        sacrebleu_version=sacrebleu.__version__,
        num_hypotheses=len(hypotheses),
        num_references=len(references),
    )
