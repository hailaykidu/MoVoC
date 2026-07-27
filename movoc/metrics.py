"""
metrics.py

Intrinsic evaluation metrics from the MoVoC paper (arXiv:2509.08812),
Section 6:

- **Morpheme Boundary Precision** (Nouri and Yangarber, 2016): "all
  predicted boundaries (across all words) are compared to gold-standard
  boundaries." Aggregate precision: of every boundary position the
  segmenter predicts across the whole test set, what fraction are real
  gold morpheme boundaries.

- **MorphScore** (Arnett and Bergen, 2025): "assigning 1 if a token
  boundary aligns with the gold morpheme boundary, and 0 otherwise.
  Unsegmented words... are excluded. [...] a recall-oriented metric that
  does not penalize false positives." Aggregate recall: of every gold
  boundary across the test set (for words the segmenter didn't leave as
  a single whole-word token), what fraction did the segmenter also mark.

Both operate on a word's (prefix, root, suffix) triple by converting it to
a set of character-offset cut positions, so the same representation used
by movoc.segmenter.Segmentation works directly as either "predicted" or
"gold" input.
"""

import math
from collections import Counter


def boundaries_from_triple(prefix: str, root: str, suffix: str) -> set:
    """Character-offset positions (from the start of prefix+root+suffix)
    where a morpheme cut occurs. E.g. ("un", "do", "able") -> {2, 4}.
    """
    boundaries = set()
    pos = 0
    parts = [p for p in (prefix, root, suffix) if p]
    for part in parts[:-1]:
        pos += len(part)
        boundaries.add(pos)
    return boundaries


def boundary_precision(predicted: list, gold: list) -> float:
    """predicted, gold: parallel lists of (prefix, root, suffix) triples,
    one per word in the test set. Returns the aggregate precision of
    predicted boundaries against gold boundaries across the whole set.
    """
    total_predicted = 0
    total_correct = 0
    for pred_triple, gold_triple in zip(predicted, gold):
        pred_b = boundaries_from_triple(*pred_triple)
        gold_b = boundaries_from_triple(*gold_triple)
        total_predicted += len(pred_b)
        total_correct += len(pred_b & gold_b)
    if total_predicted == 0:
        return 0.0
    return total_correct / total_predicted


def morphscore(predicted: list, gold: list) -> float:
    """predicted, gold: parallel lists of (prefix, root, suffix) triples.
    Words where the predicted triple has zero boundaries (i.e. the
    segmenter treated the whole word as a single unsegmented token) are
    excluded entirely, per the paper's definition. Returns the aggregate
    recall of gold boundaries among the remaining words.
    """
    total_gold = 0
    total_hit = 0
    for pred_triple, gold_triple in zip(predicted, gold):
        pred_b = boundaries_from_triple(*pred_triple)
        if not pred_b:
            continue  # unsegmented word: excluded, not scored as 0
        gold_b = boundaries_from_triple(*gold_triple)
        total_gold += len(gold_b)
        total_hit += len(gold_b & pred_b)
    if total_gold == 0:
        return 0.0
    return total_hit / total_gold


def renyi_entropy(token_frequencies: Counter, alpha: float = 2.0) -> float:
    """Renyi entropy (order alpha) over a token frequency distribution --
    the paper's third intrinsic metric (Table 4), used as a secondary,
    optional signal here. Lower values indicate a sharper, more
    consistent segmentation distribution.
    """
    total = sum(token_frequencies.values())
    if total == 0:
        return 0.0
    probs = [count / total for count in token_frequencies.values()]
    if abs(alpha - 1.0) < 1e-9:
        return -sum(p * math.log(p) for p in probs if p > 0)
    sum_p_alpha = sum(p ** alpha for p in probs)
    if sum_p_alpha <= 0:
        return 0.0
    return (1.0 / (1.0 - alpha)) * math.log(sum_p_alpha)
