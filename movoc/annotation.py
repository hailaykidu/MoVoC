"""
annotation.py -- loading and validating morpheme annotations.

The paper distinguishes three kinds of annotation, and this module keeps
them distinct:

  * HornMorpho-generated analyses  -- the initial automatic pass for
    Amharic and Tigrinya.
  * Human post-edited annotations  -- those analyses after manual
    correction; this is what feeds vocabulary construction.
  * Gold-standard manual annotation -- Tigrinya's held-out evaluation set,
    and the fully manual Ge'ez and Tigre sets.

No morphological analysis happens here. This module only reads what the
annotation workflow produced.
"""

import json
from pathlib import Path

# Placeholders used across the annotation files to mean "no morpheme here".
EMPTY = {"", "-", "–", "—", "_", "None", "null"}

# Field names differ between the Amharic file (capitalized, five-way) and the
# hand-annotated sets (lowercase, three- or four-way).
FIELDS = ("Prefix", "Root", "Suffix", "Infix", "Clitic",
          "prefix", "root", "suffix", "infix", "clitic")

# Surface order, used when a segmentation must be reconstructed.
FIELDS_ORDERED = [
    ("Prefix", "Root", "Infix", "Suffix", "Clitic"),
    ("prefix", "root", "infix", "suffix", "clitic"),
]

DATA = Path(__file__).resolve().parent.parent / "data/annotations"

# Which file backs each language's vocabulary contribution, per the paper:
# post-edited HornMorpho output for Amharic and Tigrinya, manual annotation
# for Ge'ez and Tigre.
VOCAB_SOURCES = {
    "amharic": DATA / "amharic/postedited_morphemes.json",
    "tigrinya": DATA / "tigrinya/postedited_morphemes.json",
    "geez": DATA / "geez/manual_morphemes.json",
    "tigre": DATA / "tigre/manual_morphemes.json",
}

# Held-out gold standard, used only for evaluation.
GOLD_SOURCES = {
    "tigrinya": DATA / "tigrinya/gold_morphemes.json",
    "geez": DATA / "geez/manual_morphemes.json",
    "tigre": DATA / "tigre/manual_morphemes.json",
    "amharic": DATA / "amharic/postedited_morphemes.json",
}


def clean(val) -> str:
    """Normalize one annotation field to a bare morpheme, or ''."""
    if val is None:
        return ""
    v = str(val).strip().strip("-").strip("–").strip()
    return "" if v in EMPTY else v


def load(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def morphemes_of(entry: dict) -> list:
    """Every non-placeholder morpheme in one annotation record."""
    out = []
    for key in FIELDS:
        if key not in entry:
            continue
        val = entry[key]
        if val is None:
            continue
        # Strip whitespace on both sides of the affix hyphens too: some gold
        # entries carry a trailing space (e.g. "ዘይ ") that would otherwise
        # make the morpheme a distinct, unmatchable token.
        val = str(val).strip().strip("-").strip("–").strip()
        if val and val not in EMPTY:
            out.append(val)
    return out


def segmentation_of(entry: dict) -> tuple:
    """(word, [morpheme, ...]) in surface order, or (word, []) if unusable."""
    word = clean(entry.get("word") or entry.get("Word"))
    if not word:
        return "", []
    for scheme in FIELDS_ORDERED:
        if any(k in entry for k in scheme):
            parts = [clean(entry.get(k)) for k in scheme]
            return word, [p for p in parts if p]
    return word, []


def triple_of(entry: dict) -> tuple:
    """(word, prefix, root, suffix) as annotated, without alignment."""
    return (clean(entry.get("word") or entry.get("Word")),
            clean(entry.get("prefix") or entry.get("Prefix")),
            clean(entry.get("root") or entry.get("Root")),
            clean(entry.get("suffix") or entry.get("Suffix")))


def validate(path: Path) -> dict:
    """Summarize one annotation file: entries, distinct morphemes, schema."""
    entries = load(path)
    distinct = set()
    for e in entries:
        distinct.update(morphemes_of(e))
    keys = sorted({k for e in entries for k in e})
    return {"path": str(path), "entries": len(entries),
            "distinct_morphemes": len(distinct), "fields": keys}
