"""
segmenter.py

Rule-based prefix/root/suffix morphological segmenter for Ge'ez-script
languages, used uniformly across all four languages in this project
(Amharic, Tigrinya, Tigre, Ge'ez).

An earlier attempt integrated HornMorpho (github.com/hltdi/HornMorpho, a
real, actively-maintained FST-based analyzer with genuine linguistic data
for Amharic/Tigrinya/Tigre) as the paper describes for Amharic/Tigrinya.
HornMorpho's data loads correctly (real, versioned FST + lexicon files),
but its Python API returned an unanalyzed result for every test word tried
-- including the exact worked examples from HornMorpho's own README -- in
this environment, for reasons not resolved within a reasonable debugging
budget. Rather than ship a silently-broken integration, this segmenter
uses a single, transparent longest-match prefix/suffix stripper for all
four languages, driven by ../rules/{lang}_rules.json.

Each rule file's "source" field records provenance honestly:
  - "documented": Amharic and Tigrinya rules reflect commonly-documented
    affixes from reference grammars.
  - "bootstrapped_from_related_language": Tigre and Ge'ez rules are
    adapted from their closest documented relatives (see each rule file's
    source_notes), NOT expert-verified annotation. The paper itself
    required expert linguists for these two languages; this project does
    not fabricate that.

This is intentionally a much simpler segmenter than a real supervised
morphological analyzer: it strips at most one prefix and one suffix per
word (longest match), leaving the remainder as the root/stem. It will not
handle multi-affix stacking, root-and-pattern (templatic) morphology, or
irregular forms -- see README.md Limitations.
"""

import json
from pathlib import Path
from typing import NamedTuple

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"
SUPPORTED_LANGUAGES = {"amharic", "tigrinya", "tigre", "geez"}


class Segmentation(NamedTuple):
    prefix: str
    root: str
    suffix: str

    def morphemes(self):
        return [m for m in (self.prefix, self.root, self.suffix) if m]


class MorphemeSegmenter:
    """Longest-match prefix/suffix stripper, parameterized by a per-language
    rules/{lang}_rules.json file (see RULES_DIR).
    """

    def __init__(self, language: str):
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language {language!r}; expected one of {SUPPORTED_LANGUAGES}"
            )
        self.language = language
        rules_path = RULES_DIR / f"{language}_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            rules = json.load(f)
        self.source = rules["source"]
        # Longest-first so e.g. "እያለች" matches before the shorter "እ".
        self.prefixes = sorted(set(rules["prefixes"]), key=len, reverse=True)
        self.suffixes = sorted(set(rules["suffixes"]), key=len, reverse=True)

    def segment_word(self, word: str) -> Segmentation:
        remainder = word
        prefix = ""
        for p in self.prefixes:
            if remainder.startswith(p) and len(remainder) > len(p):
                prefix = p
                remainder = remainder[len(p):]
                break

        suffix = ""
        for s in self.suffixes:
            if remainder.endswith(s) and len(remainder) > len(s):
                suffix = s
                remainder = remainder[: -len(s)]
                break

        return Segmentation(prefix=prefix, root=remainder, suffix=suffix)

    def segment_sentence(self, sentence: str) -> list:
        return [self.segment_word(w) for w in sentence.strip().split()]
