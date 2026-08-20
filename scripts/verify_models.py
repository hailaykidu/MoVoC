#!/usr/bin/env python3
"""Verify, for all 6 (tokenizer x language_pair) combinations, that the
embedding/vocabulary adaptation logic in
marianmt_comparison.model.build_model_for_tokenizer succeeds -- in
dry-run/check mode, before any training happens.

Also performs the live HuggingFace Hub lookup (RESOLVED DECISION #4) for
each language pair's base_model_identifier and records found / not_found /
fallback_used.

Hard-fails (nonzero exit) if any of the 6 combinations fails adaptation.
Requires network access for the Hub lookup and enough disk/RAM to
instantiate (or download) small MarianMT models; does not require a GPU.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import load_config, manifests_dir  # noqa: E402
from marianmt_comparison.model import (  # noqa: E402
    ModelAdaptationError,
    build_from_scratch_config,
    build_model_for_tokenizer,
    resolve_base_model,
)
from marianmt_comparison.tokenization import load_tokenizer  # noqa: E402


def check_combination(language_pair: str, tokenizer_name: str, cfg: dict) -> dict:
    tok_entry = cfg["tokenizers"][tokenizer_name]
    tokenizer = load_tokenizer(tok_entry["path"])

    resolution = resolve_base_model(cfg["base_model_identifier"])
    print(f"  model resolution: {resolution.status} -- {resolution.message}")

    if resolution.status == "found":
        base = cfg["base_model_identifier"]
    else:
        pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
        base = build_from_scratch_config(len(tokenizer), cfg["model"], pad_token_id=pad_id)

    try:
        model, report = build_model_for_tokenizer(tokenizer, base, cfg["model"])
        status = "PASS"
        error = None
    except ModelAdaptationError as exc:
        status = "FAIL"
        error = str(exc)
        report = None

    result = {
        "language_pair": language_pair,
        "tokenizer": tokenizer_name,
        "model_resolution": resolution.to_dict(),
        "status": status,
        "error": error,
        "embedding_adaptation_report": report.to_dict() if report else None,
    }
    return result


def main() -> int:
    results = []
    had_failure = False

    for language_pair in ("en_ti", "en_am"):
        cfg = load_config(language_pair)
        for tokenizer_name in ("bpe", "wordpiece", "movoc_tok"):
            print(f"\n=== Checking {language_pair} / {tokenizer_name} ===")
            try:
                result = check_combination(language_pair, tokenizer_name, cfg)
            except Exception as exc:  # noqa: BLE001
                print(f"  FAIL (unexpected exception): {exc!r}")
                had_failure = True
                results.append(
                    {
                        "language_pair": language_pair,
                        "tokenizer": tokenizer_name,
                        "status": "FAIL",
                        "error": repr(exc),
                    }
                )
                continue

            results.append(result)
            if result["status"] != "PASS":
                had_failure = True
                print(f"  FAIL: {result['error']}")
            else:
                r = result["embedding_adaptation_report"]
                print(
                    f"  PASS: vocab={r['tokenizer_vocab_size']} "
                    f"base_vocab={r['base_model_original_vocab_size']} "
                    f"resize={r['resize_performed']} tie={r['tie_word_embeddings']}"
                )

    out_path = manifests_dir() / "model_verification_report.json"
    out_path.write_text(json.dumps({"combinations": results}, indent=2), encoding="utf-8")
    print(f"\nWrote report: {out_path}")

    if had_failure:
        print(f"\n{sum(1 for r in results if r['status'] != 'PASS')} combination(s) FAILED.", file=sys.stderr)
        return 1
    print("\nAll 6 (tokenizer x language_pair) embedding adaptation checks PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
