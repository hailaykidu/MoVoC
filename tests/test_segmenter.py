"""
Real pytest tests for movoc.segmenter.MorphemeSegmenter and movoc.metrics.

Previously this file (despite its name) was not a test at all: no
assertions, a standalone script with two hardcoded Amharic-only
prefix/suffix lists that didn't even read the project's own
rules/*.json, writing output to a hardcoded /home/teklehaymanot/... path
that doesn't exist on this machine. Replaced with real, running
assertions against the actual segmenter/metrics modules.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from movoc.segmenter import MorphemeSegmenter, Segmentation, SUPPORTED_LANGUAGES
from movoc.metrics import boundaries_from_triple, boundary_precision, morphscore, renyi_entropy
from collections import Counter


@pytest.mark.parametrize("language", sorted(SUPPORTED_LANGUAGES))
def test_segmenter_loads_for_every_supported_language(language):
    segmenter = MorphemeSegmenter(language)
    assert segmenter.prefixes
    assert segmenter.suffixes
    assert segmenter.source in ("documented", "bootstrapped_from_related_language")


def test_unsupported_language_raises():
    with pytest.raises(ValueError):
        MorphemeSegmenter("klingon")


def test_amharic_negation_circumfix():
    # The paper's own worked example: "they didn't break" -> al-...-mm negation.
    segmenter = MorphemeSegmenter("amharic")
    seg = segmenter.segment_word("አልሰበሩም")
    assert seg.prefix == "አል"
    assert seg.suffix == "ም"
    assert seg.root  # non-empty stem remains


def test_tigrinya_negation_circumfix():
    # The paper's own worked example: "do not do it" -> ay-...-n negation.
    segmenter = MorphemeSegmenter("tigrinya")
    seg = segmenter.segment_word("ኣይትከውንን")
    assert seg.prefix == "ኣይ"
    assert seg.suffix == "ን"


def test_segment_word_never_strips_the_whole_word():
    # A prefix/suffix match must leave a non-empty root.
    segmenter = MorphemeSegmenter("amharic")
    seg = segmenter.segment_word("ት")  # a single-character word, itself a listed prefix
    assert seg.root  # something must remain; can't fully consume the word


def test_segment_sentence_returns_one_segmentation_per_word():
    segmenter = MorphemeSegmenter("tigrinya")
    result = segmenter.segment_sentence("ኣይትከውንን ገዛና")
    assert len(result) == 2
    assert all(isinstance(s, Segmentation) for s in result)


def test_bootstrapped_languages_are_labeled_honestly():
    for lang in ("tigre", "geez"):
        segmenter = MorphemeSegmenter(lang)
        assert segmenter.source == "bootstrapped_from_related_language"


# --- metrics ---

def test_boundaries_from_triple_basic():
    # "un" + "do" + "able" -> cuts after char 2 and char 4.
    assert boundaries_from_triple("un", "do", "able") == {2, 4}


def test_boundaries_from_triple_no_prefix_or_suffix():
    assert boundaries_from_triple("", "word", "") == set()


def test_boundary_precision_perfect_match():
    predicted = [("un", "do", "able")]
    gold = [("un", "do", "able")]
    assert boundary_precision(predicted, gold) == 1.0


def test_boundary_precision_partial_match():
    # predicted has 2 boundaries (after "un" and after "undo"), gold only agrees on 1.
    predicted = [("un", "do", "able")]
    gold = [("", "undo", "able")]
    # predicted boundaries: {2, 4}; gold boundaries: {4}; 1 of 2 predicted is correct.
    assert boundary_precision(predicted, gold) == pytest.approx(0.5)


def test_boundary_precision_empty_input_is_zero_not_error():
    assert boundary_precision([], []) == 0.0


def test_morphscore_excludes_unsegmented_predictions():
    # predicted has zero boundaries (whole word, unsegmented) -> excluded entirely,
    # not counted as a miss.
    predicted = [("", "undoable", "")]
    gold = [("un", "do", "able")]
    assert morphscore(predicted, gold) == 0.0  # no included words -> 0.0, not an error


def test_morphscore_recall_oriented_ignores_false_positives():
    # predicted over-segments (extra boundary not in gold) but still gets full
    # recall credit for every gold boundary it does hit.
    predicted = [("un", "do", "able")]  # boundaries {2, 4}
    gold = [("", "undo", "able")]  # boundaries {4}
    assert morphscore(predicted, gold) == 1.0  # the one gold boundary (4) was hit


def test_renyi_entropy_uniform_distribution_is_higher_than_skewed():
    uniform = Counter({"a": 10, "b": 10, "c": 10, "d": 10})
    skewed = Counter({"a": 37, "b": 1, "c": 1, "d": 1})
    assert renyi_entropy(uniform) > renyi_entropy(skewed)


def test_renyi_entropy_empty_counter_is_zero():
    assert renyi_entropy(Counter()) == 0.0
