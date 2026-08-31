#!/usr/bin/env python3
"""Project citation-form gold morphemes onto their surface word, producing
a filtered, boundary-aligned evaluation subset per language.

INDEPENDENT of the MoVoC repository and of amseg's own
scripts/build_gold_testsets.py: this is a from-scratch reimplementation of
the same general technique (longest-contiguous-match projection via
difflib.SequenceMatcher, since Ethiopic gold annotations are stored in
citation/lemma form and do not usually concatenate to the surface word
directly -- e.g. "sselam" + "-awi" fuses to "sselamawi" through vowel
fusion, not plain string concatenation). It reads ONLY this project's own
already-consolidated files (../amh_annotated_clean.json etc., produced by
consolidate_annotations.py) -- it does not read, import, or call anything
under amseg/scripts/ or amseg/evaluation/.

WHY THIS EXISTS, separate from morphscore_eval.py's gold_boundaries():
that function requires EXACT concatenation (prefix+root+suffix == word)
and excludes everything else, which is the strict, conservative choice
but discards most citation-form Ethiopic gold data. This script instead
locates each morpheme within the remaining suffix of the word (exact
prefix match first, then longest shared contiguous block), producing many
more usable, boundary-aligned words -- at the cost of the alignment being
approximate rather than guaranteed-exact for morphemes that do not appear
as a literal substring. Both are legitimate, differently-conservative
choices; this script's output is a SEPARATE, clearly-labeled evaluation
set, not a replacement for morphscore_eval.py's stricter one.

Exclusion rules (all counted and reported, nothing silently dropped):
  - placeholder-only records (no morphemes stated at all)
  - single-morpheme records (no internal boundary exists to project)
  - records whose morphemes cannot be located in the surface word in
    left-to-right, non-overlapping order (excluded rather than guessed)
  - duplicate words within a language (first-seen kept)

Output: one TSV per language at
../amh_boundary_projected.tsv (and tir/tig/gez equivalents), plus
../{lang}_boundary_projection_stats.json documenting exclusion counts.

Usage:
    python3 scripts/project_surface_boundaries.py
"""
from __future__ import annotations

import json
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

LANGUAGES = ("amh", "tir", "tig", "gez")
FIELD_ORDER = ("prefix", "root", "infix", "suffix", "clitic")


def morphemes_of(record: dict) -> list[str]:
    """Morphemes in surface order, reading only the already-cleaned fields
    consolidate_annotations.py produced (placeholder/dash-marker stripping
    already applied there -- see that script's _clean_field)."""
    out: list[str] = []
    for field in FIELD_ORDER:
        value = record.get(field)
        if value:
            out.append(value)
    return out


def project_to_surface(word: str, morphemes: list[str]) -> list[str] | None:
    """Cut `word` at the offsets its citation-form morphemes imply, using
    exact-prefix match where possible and falling back to the longest
    shared contiguous block otherwise. Returns None (word excluded, not
    guessed) if any morpheme cannot be located in left-to-right,
    non-overlapping order, or if the resulting pieces do not rejoin to
    `word` exactly."""
    cuts: list[int] = []
    cursor = 0
    for morpheme in morphemes[:-1]:
        remainder = word[cursor:]
        if not remainder:
            return None
        if remainder.startswith(morpheme):
            cursor += len(morpheme)
        else:
            matcher = SequenceMatcher(None, remainder, morpheme, autojunk=False)
            block = matcher.find_longest_match(0, len(remainder), 0, len(morpheme))
            if block.size == 0:
                return None
            cursor += block.a + block.size
        if not (0 < cursor < len(word)):
            return None
        if cuts and cursor <= cuts[-1]:
            return None  # non-monotonic alignment
        cuts.append(cursor)

    if not cuts:
        return None
    pieces = [word[i:j] for i, j in zip([0] + cuts, cuts + [len(word)])]
    if any(not p for p in pieces) or "".join(pieces) != word:
        return None
    return pieces


def process_language(language: str) -> dict:
    in_path = PROJECT_ROOT / f"{language}_annotated_clean.json"
    records = json.loads(in_path.read_text(encoding="utf-8"))

    chosen: dict[str, tuple[list[str], str]] = {}
    excluded_placeholder = 0
    excluded_single = 0
    excluded_unaligned = 0
    duplicate = 0

    for record in records:
        word = unicodedata.normalize("NFC", str(record.get("word") or "").strip())
        if not word:
            excluded_placeholder += 1
            continue
        parts = [unicodedata.normalize("NFC", m) for m in morphemes_of(record)]
        if not parts:
            excluded_placeholder += 1
            continue
        if len(parts) < 2:
            excluded_single += 1
            continue
        surface = project_to_surface(word, parts)
        if surface is None:
            excluded_unaligned += 1
            continue
        if word in chosen:
            duplicate += 1
            continue
        chosen[word] = (surface, record.get("source_file", "unknown"))

    out_tsv = PROJECT_ROOT / f"{language}_boundary_projected.tsv"
    with open(out_tsv, "w", encoding="utf-8") as fh:
        for word, (pieces, source) in chosen.items():
            fh.write(f"{word}\t{'+'.join(pieces)}\n")

    stats = {
        "language": language,
        "records_read": len(records),
        "words_kept": len(chosen),
        "excluded_placeholder_only": excluded_placeholder,
        "excluded_single_morpheme": excluded_single,
        "excluded_unaligned_to_surface": excluded_unaligned,
        "excluded_duplicate_word": duplicate,
    }
    stats_path = PROJECT_ROOT / f"{language}_boundary_projection_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"[{language}] kept {len(chosen)} words "
        f"(placeholder={excluded_placeholder}, single_morpheme={excluded_single}, "
        f"unaligned={excluded_unaligned}, duplicate={duplicate}) "
        f"-> {out_tsv.name}"
    )
    return stats


def main() -> int:
    print("=== Projecting citation-form morphemes onto surface boundaries (independent implementation) ===\n")
    for language in LANGUAGES:
        process_language(language)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
