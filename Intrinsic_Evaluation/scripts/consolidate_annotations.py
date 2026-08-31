#!/usr/bin/env python3
"""Consolidate morpheme-annotated resources for Amharic, Tigrinya, Tigre,
and Ge'ez into one clean per-language dataset.

INDEPENDENT of the MoVoC repository and of any existing evaluation
pipeline in amseg/ (e.g. amseg/scripts/build_gold_testsets.py,
amseg/evaluation/data/*_gold.tsv) -- this script reads only the raw,
per-annotator source JSON files (copied read-only into ../raw_sources/)
and re-implements its own merge/clean/normalize logic from scratch. It
does not import, call, or depend on any amseg code.

Per-language source composition (see project root for full source
inventory; this reflects what actually exists on disk, not an assumed
uniform "gold + HornMorpho-postedited" structure for every language):

  Amharic (amh):   postedited_morphemes.json + user_provided_segmented.tsv
                    (word<TAB>segmented-morphemes, "-" or "_" separated,
                    same source kind: HornMorpho + human post-editing),
                    merged and deduplicated by word. No separate
                    gold-standard file exists for Amharic.
  Tigrinya (tir):  gold_morphemes.json (held-out gold, 206 records) +
                    postedited_morphemes.json (7,531 records), merged.
  Tigre (tig):     manual_morphemes.json only.
                    No HornMorpho-postedited layer exists for Tigre --
                    this is direct manual annotation.
  Ge'ez (gez):     manual_morphemes.json + user_provided_segmented.tsv
                    (word<TAB>dash-segmented-morphemes format, same source
                    kind: manual annotation), merged and deduplicated by
                    word. No HornMorpho-postedited layer exists for Ge'ez.

Each source uses a different field schema and a different placeholder
convention for "no morpheme present" (null / "-" / "–" (en dash) / "--").
This script normalizes all of them to one schema:

    {"word": str, "prefix": str|None, "root": str, "suffix": str|None,
     "infix": str|None, "clitic": str|None, "source_file": str}

A record is dropped if:
  - "word" is missing/empty, or
  - "root" is missing/empty after placeholder normalization (a record
    with no identifiable root carries no usable morphological signal).

Within a language, duplicate words (same surface form) are deduplicated
keeping the FIRST occurrence in source-list order (gold before
postedited, where both exist) -- deterministic, not random.

Output: one file per language, both as JSON (full records) and TSV
(word<TAB>prefix+root+suffix, matching the amseg gold.tsv convention for
readability, but independently generated) at
../amh_annotated_clean.json / .tsv (and tir/tig/gez equivalents),
plus a provenance.json documenting exactly which source contributed
each retained word.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # .../Intrinsic_Evaluation/
RAW_SOURCES = PROJECT_ROOT / "raw_sources"

# Placeholder tokens meaning "this morpheme slot is empty", observed across
# the four source files' differing conventions.
EMPTY_PLACEHOLDERS = {None, "", "-", "--", "–", "—"}  # "", -, --, en dash, em dash

# Dash-family characters used by Tigrinya and Tigre's source annotations as
# an ATTACHMENT-SIDE MARKER, not literal content: prefixes are written with
# a trailing dash ("ኣይ-"), suffixes with a leading dash ("-ኣዊ") -- e.g.
# raw_sources/tigrinya/gold_morphemes.json's "ኣይናቱን" record has
# prefix="ኣይ-", root="ናቱ", suffix="-ን", and prefix+root+suffix must equal
# "ኣይናቱን" (i.e. the dashes must be stripped, not concatenated as
# characters). Amharic's source does not use this convention at all (its
# non-empty fields are plain morpheme strings with no dash marker).
DASH_CHARS = "-–—"


def _clean_field(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    if value in EMPTY_PLACEHOLDERS or value == "":
        return None
    # Strip a single leading and/or trailing attachment-marker dash from
    # otherwise-real content (see DASH_CHARS comment). A field consisting
    # of dash characters only was already caught by EMPTY_PLACEHOLDERS
    # above, so what remains here always has real content on at least one
    # side of the strip.
    value = value.strip(DASH_CHARS)
    if value == "":
        return None
    return value


def _normalize_record(raw: dict, source_file: str) -> dict | None:
    """Normalize one raw record (any of the four JSON source schemas, or a
    TSV "segments" record from load_source) to the common schema. Returns
    None if the record must be dropped."""
    word = raw.get("word", raw.get("Word"))
    word = _clean_field(word)
    if word is None:
        return None

    if "segments" in raw:
        # Flat dash-segmented TSV format: no prefix/root/suffix distinction
        # is encoded, so the first segment is treated as root and any
        # remaining segments are concatenated (order-preserved) into
        # suffix, which is the closest honest mapping onto the common
        # schema without inventing a prefix/root split the source doesn't
        # provide.
        segments = raw["segments"]
        if not segments:
            return None
        root = segments[0]
        suffix = "+".join(segments[1:]) if len(segments) > 1 else None
        return {
            "word": word,
            "prefix": None,
            "root": root,
            "suffix": suffix,
            "infix": None,
            "clitic": None,
            "source_file": source_file,
        }

    root = raw.get("root", raw.get("Root"))
    root = _clean_field(root)
    if root is None:
        return None

    prefix = _clean_field(raw.get("prefix", raw.get("Prefix")))
    suffix = _clean_field(raw.get("suffix", raw.get("Suffix")))
    infix = _clean_field(raw.get("infix", raw.get("Infix")))
    clitic = _clean_field(raw.get("clitic", raw.get("Clitic")))

    return {
        "word": word,
        "prefix": prefix,
        "root": root,
        "suffix": suffix,
        "infix": infix,
        "clitic": clitic,
        "source_file": source_file,
    }


def load_source(path: Path) -> list[dict]:
    """Load a source file, dispatching on extension. JSON sources use the
    four languages' native {word/Word, prefix/Prefix, root/Root, ...}
    schema (handled by _normalize_record). TSV sources use a simpler
    word<TAB>segmented-morphemes format, segment-separated by "-" or "_"
    (both appear, including mixed within the same file for the Amharic
    user-provided source, e.g. "ከየቤቱና\tከ_እየ_ቤት_ኡ_እና" and "በዓል\tበዓል-") --
    converted here into the same raw-record shape {"word":..., "segments":
    [...]} so _normalize_record can treat it uniformly (first segment ->
    root, remaining non-empty segments concatenated into suffix, since
    this flat format does not distinguish prefix/root/suffix/infix/clitic
    the way the JSON sources do)."""
    if path.suffix == ".tsv":
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            word, morph_str = parts[0].strip(), parts[1].strip()
            # Normalize both separators to one before splitting.
            segments = [s for s in morph_str.replace("_", "-").split("-") if s.strip()]
            records.append({"word": word, "segments": segments})
        return records
    return json.loads(path.read_text(encoding="utf-8"))


def consolidate_language(
    language: str, sources: list[tuple[Path, str]]
) -> tuple[list[dict], dict]:
    """sources: list of (path, source_kind_label), in priority order
    (earlier sources win on duplicate words)."""
    seen_words: set[str] = set()
    consolidated: list[dict] = []
    stats = {
        "language": language,
        "sources": [],
        "total_records_read": 0,
        "dropped_missing_word": 0,
        "dropped_missing_root": 0,
        "dropped_duplicate_word": 0,
        "retained": 0,
    }

    for path, source_kind in sources:
        raw_records = load_source(path)
        n_read = len(raw_records)
        n_contributed = 0
        n_dropped_word = 0
        n_dropped_root = 0
        n_dropped_dup = 0

        for raw in raw_records:
            word_field = raw.get("word", raw.get("Word"))
            if _clean_field(word_field) is None:
                n_dropped_word += 1
                continue

            normalized = _normalize_record(raw, path.name)
            if normalized is None:
                n_dropped_root += 1
                continue

            if normalized["word"] in seen_words:
                n_dropped_dup += 1
                continue

            seen_words.add(normalized["word"])
            normalized["source_kind"] = source_kind
            consolidated.append(normalized)
            n_contributed += 1

        stats["sources"].append(
            {
                "path": str(path),
                "source_kind": source_kind,
                "records_read": n_read,
                "words_contributed": n_contributed,
                "dropped_missing_word": n_dropped_word,
                "dropped_missing_root": n_dropped_root,
                "dropped_duplicate_word": n_dropped_dup,
            }
        )
        stats["total_records_read"] += n_read
        stats["dropped_missing_word"] += n_dropped_word
        stats["dropped_missing_root"] += n_dropped_root
        stats["dropped_duplicate_word"] += n_dropped_dup

    stats["retained"] = len(consolidated)
    return consolidated, stats


LANGUAGE_SOURCES: dict[str, list[tuple[str, str]]] = {
    "amh": [
        ("amharic/postedited_morphemes.json", "HornMorpho initial analysis with human post-editing"),
        ("amharic/user_provided_segmented.tsv", "HornMorpho initial analysis with human post-editing"),
    ],
    "tir": [
        ("tigrinya/gold_morphemes.json", "gold, held out from training/vocab construction"),
        ("tigrinya/postedited_morphemes.json", "HornMorpho initial analysis with human post-editing"),
    ],
    "tig": [
        ("tigre/manual_morphemes.json", "manual annotation (no HornMorpho post-editing layer exists for Tigre)"),
    ],
    "gez": [
        ("geez/manual_morphemes.json", "manual annotation (no HornMorpho post-editing layer exists for Ge'ez)"),
        ("geez/user_provided_segmented.tsv", "manual annotation (no HornMorpho post-editing layer exists for Ge'ez)"),
    ],
}


def write_outputs(language: str, records: list[dict], stats: dict) -> None:
    json_path = PROJECT_ROOT / f"{language}_annotated_clean.json"
    tsv_path = PROJECT_ROOT / f"{language}_annotated_clean.tsv"
    prov_path = PROJECT_ROOT / f"{language}_provenance.json"

    json_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with open(tsv_path, "w", encoding="utf-8") as fh:
        for r in records:
            morphemes = "+".join(
                m for m in (r["prefix"], r["root"], r["suffix"]) if m is not None
            )
            fh.write(f"{r['word']}\t{morphemes}\n")

    prov_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[{language}] retained {stats['retained']} words "
          f"(from {stats['total_records_read']} raw records across {len(stats['sources'])} source(s))")
    print(f"  -> {json_path.name}, {tsv_path.name}, {prov_path.name}")


def main() -> int:
    print("=== Consolidating morpheme annotations (independent pipeline) ===\n")
    for language, source_specs in LANGUAGE_SOURCES.items():
        sources = [(RAW_SOURCES / rel_path, kind) for rel_path, kind in source_specs]
        for path, _ in sources:
            if not path.exists():
                raise FileNotFoundError(f"Missing source for {language}: {path}")
        records, stats = consolidate_language(language, sources)
        write_outputs(language, records, stats)
        print()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
