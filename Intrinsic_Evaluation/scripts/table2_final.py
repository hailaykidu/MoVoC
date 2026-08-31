#!/usr/bin/env python3
"""Table 2 (FINAL): MoVoC-Tok MorphScore per language.

See ../reports/table2_final.md for the methodology writeup and results.

FORMULA: recall-direction (matched gold boundaries / total gold
boundaries), macro-averaged (mean of each word's own ratio), gold words
filtered by EXACT concatenation (prefix+root+suffix == surface word),
single-token words (tokenizer emits the word as one whole-vocabulary-
entry piece, i.e. zero gold-recoverable boundaries to miss) scored 1.0,
exact boundary-offset matching (no tolerance window). Model: each
language's own 32k MoVoC-Tok where one exists (amh, tir); Tigrinya's 32k
model reused cross-lingually for tig/gez, since no dedicated model
exists for either.

This script recomputes every number from scratch and reports the exact
word-count provenance at each filtering stage, so the final "n words
contributing to MorphScore" figure is independently verifiable
end-to-end.

Usage:
    python3 scripts/table2_final.py
"""
from __future__ import annotations

import json
from pathlib import Path

from transformers import AutoTokenizer, PreTrainedTokenizerBase

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"

WORD_START_MARKER = "▁"
WORDPIECE_CONTINUATION = "##"

LANG_NAMES = {"amh": "Amharic", "tir": "Tigrinya", "gez": "Ge'ez", "tig": "Tigre"}

MODEL_32K = {
    "amh": ("/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_amharic", "in_domain"),
    "tir": ("/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_tigrinya", "in_domain"),
    "tig": ("/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_tigrinya", "cross_lingual"),
    "gez": ("/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_32k_tigrinya", "cross_lingual"),
}


def load_consolidated(language: str) -> list[dict]:
    return json.loads((PROJECT_ROOT / f"{language}_annotated_clean.json").read_text(encoding="utf-8"))


def exact_filter(records: list[dict]) -> list[tuple[str, list[str]]]:
    """Keep only records where prefix+root+suffix concatenates EXACTLY to
    the surface word. Returns (word, morpheme_pieces) pairs."""
    out = []
    for r in records:
        morphemes = [r[f] for f in ("prefix", "root", "suffix") if r.get(f)]
        if not morphemes:
            continue
        if "".join(morphemes) == r["word"]:
            out.append((r["word"], morphemes))
    return out


def gold_boundaries_from_pieces(pieces: list[str]) -> set[int]:
    boundaries = set()
    offset = 0
    for p in pieces[:-1]:
        offset += len(p)
        boundaries.add(offset)
    return boundaries


def predicted_boundaries(tokenizer: PreTrainedTokenizerBase, word: str) -> tuple[bool, set[int]]:
    ids = tokenizer.encode(word, add_special_tokens=False)
    pieces = tokenizer.convert_ids_to_tokens(ids)
    cleaned = []
    for p in pieces:
        if p.startswith(WORD_START_MARKER):
            p = p[len(WORD_START_MARKER):]
        elif p.startswith(WORDPIECE_CONTINUATION):
            p = p[len(WORDPIECE_CONTINUATION):]
        cleaned.append(p)
    if "".join(cleaned) != word:
        return False, set()
    boundaries = set()
    offset = 0
    for p in cleaned[:-1]:
        offset += len(p)
        boundaries.add(offset)
    return True, boundaries


def evaluate(language: str) -> dict:
    consolidated_records = load_consolidated(language)
    n_consolidated = len(consolidated_records)

    exact_items = exact_filter(consolidated_records)
    n_exact_filtered = len(exact_items)
    n_dropped_no_exact_match = n_consolidated - n_exact_filtered

    tok_path, mode = MODEL_32K[language]
    tokenizer = AutoTokenizer.from_pretrained(tok_path)

    n_excluded_tokenizer_mismatch = 0
    per_word_scores: list[float] = []
    n_unsegmented_gold = 0  # zero gold boundaries -> scored 1.0, per spec
    n_segmented_gold = 0    # >=1 gold boundary -> boundary-matched score

    for word, pieces in exact_items:
        g_bounds = gold_boundaries_from_pieces(pieces)
        ok, p_bounds = predicted_boundaries(tokenizer, word)
        if not ok:
            n_excluded_tokenizer_mismatch += 1
            continue
        matches = len(g_bounds & p_bounds)
        if g_bounds:
            score = matches / len(g_bounds)
            n_segmented_gold += 1
        else:
            score = 1.0
            n_unsegmented_gold += 1
        per_word_scores.append(score)

    n_final_scored = len(per_word_scores)
    assert n_final_scored == n_unsegmented_gold + n_segmented_gold
    morphscore = sum(per_word_scores) / n_final_scored if n_final_scored else float("nan")

    return {
        "language": LANG_NAMES[language],
        "iso": language,
        "tokenizer_path": tok_path,
        "vocab_size": len(tokenizer),
        "mode": mode,
        "n_words_consolidated": n_consolidated,
        "n_words_dropped_not_exact_concat": n_dropped_no_exact_match,
        "n_words_exact_filtered": n_exact_filtered,
        "n_words_excluded_tokenizer_reconstruction_mismatch": n_excluded_tokenizer_mismatch,
        "n_words_unsegmented_gold_scored_1": n_unsegmented_gold,
        "n_words_segmented_gold_boundary_matched": n_segmented_gold,
        "n_words_contributing_to_morphscore": n_final_scored,
        "morphscore": round(morphscore, 4),
    }


def main() -> int:
    RESULTS_DIR.mkdir(exist_ok=True)

    results = {}
    print("=== Table 2 (final): word-count provenance + MorphScore ===\n")
    for language in ("amh", "tir", "gez", "tig"):
        r = evaluate(language)
        results[language] = r
        print(f"--- {r['language']} ({r['iso']}) ---")
        print(f"  consolidated gold words:                  {r['n_words_consolidated']}")
        print(f"  dropped (no exact prefix+root+suffix concat): {r['n_words_dropped_not_exact_concat']}")
        print(f"  exact-filtered gold words:                {r['n_words_exact_filtered']}")
        print(f"  excluded (tokenizer reconstruction mismatch): {r['n_words_excluded_tokenizer_reconstruction_mismatch']}")
        print(f"    of which unsegmented (0 gold boundaries, scored 1.0): {r['n_words_unsegmented_gold_scored_1']}")
        print(f"    of which segmented (>=1 gold boundary, boundary-matched): {r['n_words_segmented_gold_boundary_matched']}")
        print(f"  >>> words contributing to MorphScore (segmented + unsegmented): {r['n_words_contributing_to_morphscore']}")
        print(f"  MorphScore = {r['morphscore']}")
        print()

    out_json = RESULTS_DIR / "table2_final_results.json"
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # NOTE: this script deliberately does NOT (re)write reports/table2_final.md.
    # That file is hand-maintained (methodology writeup and results) and
    # must not be silently overwritten by a script re-run. Cross-check its
    # numbers against this JSON after any change to the evaluation logic
    # above.
    print(f"Written: {out_json}")
    print(f"NOTE: reports/table2_final.md is hand-maintained and was NOT regenerated. "
          f"Verify its numbers still match {out_json.name} after any logic change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
