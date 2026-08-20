#!/usr/bin/env python3
"""Verify all tokenizer artifacts (read-only) for both language pairs and
write a machine-readable manifest to data/manifests/tokenizer_manifest.json.

Run locally (no GPU/network/data required):
    python3 scripts/verify_tokenizers.py

Exits non-zero if any tokenizer fails a required integrity check. The
cross-lingual-reuse case (en_am/movoc_tok) is explicitly NOT a failure --
it prints a loud warning with measured fertility/UNK rate instead.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import load_config, manifests_dir  # noqa: E402
from marianmt_comparison.tokenization import (  # noqa: E402
    TokenizerVerificationError,
    verify_tokenizer,
)


def main() -> int:
    all_reports = []
    had_failure = False

    for language_pair in ("en_ti", "en_am"):
        print(f"\n=== Verifying tokenizers for {language_pair} ===")
        cfg = load_config(language_pair)
        for tok_name, entry in cfg["tokenizers"].items():
            print(f"\n--- {language_pair} / {tok_name} ---")
            print(f"path: {entry['path']}")
            try:
                report = verify_tokenizer(
                    name=tok_name,
                    language_pair=language_pair,
                    path=entry["path"],
                    declared_vocab_size=entry["vocab_size"],
                    cross_lingual_reuse=entry.get("cross_lingual_reuse", False),
                    warning=entry.get("warning"),
                )
            except TokenizerVerificationError as exc:
                print(f"FAILED: {exc}")
                had_failure = True
                continue

            d = report.to_dict()
            all_reports.append(d)
            print(f"tokenizer_class: {d['tokenizer_class']}")
            print(f"len(tokenizer): {d['vocab_size_len']}  |  declared: {d['declared_vocab_size']}")
            print(f"special_token_ids: {d['special_token_ids']}")
            for label, info in d["sample_tokenizations"].items():
                print(
                    f"  [{label}] tokens={info['num_tokens']} "
                    f"fertility={info['fertility']} unk_rate={info['unk_rate']} "
                    f"preview={info['tokens_preview'][:8]}"
                )
            if d["cross_lingual_reuse"]:
                print(f"  *** CROSS-LINGUAL REUSE WARNING: {d['warning']}")
                print(
                    f"  *** Amharic fertility={d['amharic_fertility']} "
                    f"UNK rate={d['amharic_unk_rate']} (accepted tradeoff, not a failure)"
                )
            print("PASSED" if d["passed"] else "FAILED")

        # Reference tokenizer (marian_original) -- informational only.
        ref = cfg.get("reference_tokenizer")
        if ref:
            print(f"\n--- {language_pair} / reference (marian_original) ---")
            try:
                report = verify_tokenizer(
                    name="marian_original",
                    language_pair=language_pair,
                    path=ref["path"],
                    declared_vocab_size=ref["vocab_size"],
                )
                d = report.to_dict()
                all_reports.append(d)
                print(f"tokenizer_class: {d['tokenizer_class']}, len={d['vocab_size_len']}")
                print("PASSED")
            except TokenizerVerificationError as exc:
                print(f"FAILED (reference tokenizer, non-blocking for experimental conditions): {exc}")

    out_path = manifests_dir() / "tokenizer_manifest.json"
    out_path.write_text(json.dumps({"tokenizers": all_reports}, indent=2), encoding="utf-8")
    print(f"\nWrote manifest: {out_path}")

    if had_failure:
        print("\nOne or more REQUIRED tokenizer verifications FAILED. See above.", file=sys.stderr)
        return 1
    print("\nAll required tokenizer verifications PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
