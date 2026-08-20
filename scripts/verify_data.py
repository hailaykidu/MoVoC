#!/usr/bin/env python3
"""Verify processed data splits exist, are non-empty, parallel-aligned, and
match the checksums recorded in data/manifests/{language_pair}.json.

Must be run after scripts/prepare_opus_data.py and before any training.
Exits non-zero on any mismatch.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.reproducibility import sha256_file  # noqa: E402


def verify_language_pair(language_pair: str) -> list[str]:
    problems = []
    manifest_path = REPO_ROOT / "data" / "manifests" / f"{language_pair}.json"
    if not manifest_path.exists():
        return [f"Missing manifest: {manifest_path}. Run scripts/prepare_opus_data.py first."]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = REPO_ROOT / "data" / "processed" / language_pair

    for split_name in ("train", "validation", "test"):
        split_dir = base / split_name
        src_path, tgt_path = split_dir / "src.txt", split_dir / "tgt.txt"
        if not src_path.exists() or not tgt_path.exists():
            problems.append(f"{language_pair}/{split_name}: missing src.txt/tgt.txt in {split_dir}")
            continue

        src_lines = src_path.read_text(encoding="utf-8").splitlines()
        tgt_lines = tgt_path.read_text(encoding="utf-8").splitlines()
        if len(src_lines) != len(tgt_lines):
            problems.append(
                f"{language_pair}/{split_name}: line count mismatch src={len(src_lines)} tgt={len(tgt_lines)}"
            )
        if len(src_lines) == 0:
            problems.append(f"{language_pair}/{split_name}: empty split")

        expected_size = manifest.get("split_sizes", {}).get(split_name)
        if expected_size is not None and expected_size != len(src_lines):
            problems.append(
                f"{language_pair}/{split_name}: size {len(src_lines)} != manifest split_sizes {expected_size}"
            )

        expected_checksums = manifest.get("checksums_sha256", {}).get(split_name, {})
        if expected_checksums:
            actual_src_sha = sha256_file(src_path)
            actual_tgt_sha = sha256_file(tgt_path)
            if actual_src_sha != expected_checksums.get("src_sha256"):
                problems.append(
                    f"{language_pair}/{split_name}: src.txt SHA256 mismatch "
                    f"(manifest={expected_checksums.get('src_sha256')} actual={actual_src_sha})"
                )
            if actual_tgt_sha != expected_checksums.get("tgt_sha256"):
                problems.append(
                    f"{language_pair}/{split_name}: tgt.txt SHA256 mismatch "
                    f"(manifest={expected_checksums.get('tgt_sha256')} actual={actual_tgt_sha})"
                )

    # Test set isolation: sanity-check it doesn't share exact lines with train.
    train_src = (base / "train" / "src.txt")
    test_src = (base / "test" / "src.txt")
    if train_src.exists() and test_src.exists():
        train_set = set(train_src.read_text(encoding="utf-8").splitlines())
        test_set = set(test_src.read_text(encoding="utf-8").splitlines())
        overlap = train_set & test_set
        if overlap:
            problems.append(
                f"{language_pair}: {len(overlap)} exact-duplicate source lines found in both train and test splits."
            )

    return problems


def main() -> int:
    all_problems = []
    for language_pair in ("en_ti", "en_am"):
        print(f"=== Verifying data for {language_pair} ===")
        problems = verify_language_pair(language_pair)
        if problems:
            for p in problems:
                print(f"  FAIL: {p}")
            all_problems.extend(problems)
        else:
            print("  OK")

    if all_problems:
        print(f"\n{len(all_problems)} data verification problem(s) found.", file=sys.stderr)
        return 1
    print("\nAll data verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
