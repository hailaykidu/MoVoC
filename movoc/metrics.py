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
a set of character-offset cut positions, so the same representation serves
as either "predicted" or "gold" input.
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


def boundary_precision(predicted: list, gold: list,
                       segmentable_only: bool = True) -> float:
    """predicted, gold: parallel lists of (prefix, root, suffix) triples,
    one per word in the test set. Returns the aggregate precision of
    predicted boundaries against gold boundaries across the whole set.

    `segmentable_only` restricts scoring to words the gold set marks as
    multi-morphemic. Half of the Amharic gold set (18,727 of 37,048) is
    monomorphemic -- it has no gold boundary at all -- so every cut a
    tokenizer makes there is counted as a false positive no matter how
    reasonable, which measures segmentation *rate* rather than accuracy.
    This mirrors MorphScore, which already excludes unsegmented words.
    Pass False for precision over every word.
    """
    total_predicted = 0
    total_correct = 0
    for pred_triple, gold_triple in zip(predicted, gold):
        gold_b = boundaries_from_triple(*gold_triple)
        if segmentable_only and not gold_b:
            continue
        pred_b = boundaries_from_triple(*pred_triple)
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


def normalized_renyi_entropy(token_frequencies: Counter,
                             alpha: float = 2.0) -> float:
    """Renyi entropy divided by log(support), giving a value in [0, 1].

    The paper reports Renyi entropy on this scale (Table 4: 0.39-0.49 at
    alpha = 2), where the maximum log(support) corresponds to a perfectly
    uniform distribution over the tokens used. Lower means the tokenizer
    concentrates its mass on fewer, more consistent subwords.
    """
    support = len(token_frequencies)
    if support <= 1:
        return 0.0
    return renyi_entropy(token_frequencies, alpha) / math.log(support)
