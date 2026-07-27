"""
hornmorph.py -- interface to HornMorpho.

HornMorpho (Gasser, https://github.com/hltdi/HornMorpho) supplies the
initial morphological analysis for Amharic and Tigrinya. Its raw output is
not used directly: every analysis is manually post-edited before it reaches
vocabulary construction, and the post-edited results are what
data/annotations/{amharic,tigrinya}/postedited_morphemes.json contain.

Ge'ez and Tigre are annotated manually end to end; HornMorpho offers no
usable coverage for either and is not invoked for them.

This module only reads what a HornMorpho run produced. It implements no
morphological rules of its own.
"""

from pathlib import Path

NO_SEGMENTATION = "NO_SEGMENTATION"


def read_analysis(path: Path) -> list:
    """Read a HornMorpho run recorded as `word<TAB>analysis` per line.

    Returns (word, analysis) pairs. `analysis` is NO_SEGMENTATION where the
    analyzer returned nothing, an error string where the call failed, and
    otherwise the analyzer's output for that word.
    """
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0].strip():
                continue
            word = parts[0].strip()
            analysis = parts[1].strip() if len(parts) > 1 else ""
            out.append((word, analysis))
    return out


def segmented_only(pairs: list) -> list:
    """Keep pairs where the analyzer actually returned a segmentation."""
    return [(w, a) for w, a in pairs
            if a and a != NO_SEGMENTATION and not a.startswith("ERROR") and a != w]


def input_words(pairs: list) -> list:
    """The words submitted for analysis, regardless of the outcome."""
    return [w for w, _ in pairs]
