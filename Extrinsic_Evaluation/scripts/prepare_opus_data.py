#!/usr/bin/env python3
"""Download OPUS NLLB parallel data for en_ti and en_am, apply shared
preprocessing filters, and write one deterministic train/validation/test
split per language pair to data/processed/{en_ti,en_am}/.

Uses only `requests` + `zipfile` (opustools is NOT installed on this host
and must not be a hard dependency). Verifies both URLs resolve (HTTP 200,
HEAD request) before downloading either.

Tokenization never happens here -- this script produces plain-text parallel
files shared identically across all three tokenizer conditions.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import load_config, manifests_dir  # noqa: E402
from marianmt_comparison.data import (  # noqa: E402
    deduplicate_examples,
    deterministic_split,
    filter_examples,
    read_parallel,
    write_split,
)
from marianmt_comparison.reproducibility import sha256_file, utc_timestamp  # noqa: E402

RAW_DIR = REPO_ROOT / "data" / "raw"


def check_url(url: str) -> None:
    resp = requests.head(url, timeout=30, allow_redirects=True)
    if resp.status_code != 200:
        raise RuntimeError(
            f"OPUS URL did not resolve with HTTP 200 (got {resp.status_code}): {url}. "
            "Adjust the corpus name in configs/{language_pair}.yaml if this corpus was renamed/removed."
        )
    print(f"  OK  {url}  ({resp.headers.get('content-length', '?')} bytes)")


def download_and_extract(url: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} ...")
    resp = requests.get(url, timeout=600)
    resp.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    zf.extractall(dest_dir)
    print(f"  extracted to {dest_dir}: {zf.namelist()}")
    return dest_dir


def find_moses_files(extract_dir: Path, source_suffix: str, target_suffix: str) -> tuple[Path, Path]:
    src_candidates = list(extract_dir.rglob(f"*.{source_suffix}"))
    tgt_candidates = list(extract_dir.rglob(f"*.{target_suffix}"))
    if not src_candidates or not tgt_candidates:
        raise RuntimeError(
            f"Could not find moses-format files with suffixes .{source_suffix}/.{target_suffix} "
            f"under {extract_dir}. Found: {list(extract_dir.rglob('*'))}"
        )
    return src_candidates[0], tgt_candidates[0]


def prepare_language_pair(language_pair: str, base_cfg: dict) -> dict:
    cfg = load_config(language_pair)
    opus_cfg = cfg["opus"]
    url = opus_cfg["url"]

    print(f"\n=== Checking OPUS URL for {language_pair} ===")
    check_url(url)

    raw_dir = RAW_DIR / f"opus_{language_pair}"
    extract_dir = download_and_extract(url, raw_dir)

    src_file, tgt_file = find_moses_files(
        extract_dir, opus_cfg["moses_source_suffix"], opus_cfg["moses_target_suffix"]
    )
    print(f"source file: {src_file}")
    print(f"target file: {tgt_file}")

    examples = read_parallel(src_file, tgt_file)
    print(f"raw parallel examples: {len(examples)}")

    filtered = filter_examples(
        examples,
        max_whitespace_tokens=cfg["max_whitespace_tokens"],
        min_line_length_chars=cfg["min_line_length_chars"],
        drop_empty_lines=cfg["drop_empty_lines"],
    )
    print(f"after filtering: {len(filtered)} (dropped {len(examples) - len(filtered)})")

    deduped, n_duplicates_dropped = deduplicate_examples(filtered)
    print(
        f"after source-side deduplication: {len(deduped)} "
        f"(dropped {n_duplicates_dropped} examples with a source sentence seen earlier in the corpus -- "
        "OPUS NLLB is web-mined and contains exact-duplicate source lines; leaving them in would let the "
        "same sentence land in both train and test)"
    )

    splits = deterministic_split(
        deduped,
        split_seed=cfg["data_split_seed"],
        train_fraction=cfg["train_fraction"],
        validation_fraction=cfg["validation_fraction"],
        test_fraction=cfg["test_fraction"],
    )

    checksums = {}
    split_sizes = {}
    out_base = REPO_ROOT / "data" / "processed" / language_pair
    for split_name, split_examples in splits.items():
        out_dir = out_base / split_name
        src_path, tgt_path = write_split(split_examples, out_dir)
        checksums[split_name] = {
            "src_sha256": sha256_file(src_path),
            "tgt_sha256": sha256_file(tgt_path),
        }
        split_sizes[split_name] = len(split_examples)
        print(f"  wrote {split_name}: {len(split_examples)} examples -> {out_dir}")

    manifest = {
        "language_pair": language_pair,
        "corpus_name": opus_cfg["corpus"],
        "source_url": url,
        "retrieval_date": utc_timestamp(),
        "raw_example_count": len(examples),
        "filtered_example_count": len(filtered),
        "deduplicated_example_count": len(deduped),
        "duplicate_source_examples_dropped": n_duplicates_dropped,
        "split_sizes": split_sizes,
        "preprocessing_steps": [
            "whitespace strip of each line",
            f"drop_empty_lines={cfg['drop_empty_lines']}",
            f"min_line_length_chars={cfg['min_line_length_chars']}",
            f"max_whitespace_tokens={cfg['max_whitespace_tokens']} (drop lines with more whitespace-split tokens than this, either side)",
            "source-side exact-duplicate removal (first occurrence kept; prevents the same source "
            "sentence appearing in both train and test after splitting -- OPUS NLLB is web-mined and "
            "contains a non-trivial fraction of duplicate lines)",
        ],
        "split_procedure": {
            "method": "deterministic shuffle + contiguous partition",
            "data_split_seed": cfg["data_split_seed"],
            "train_fraction": cfg["train_fraction"],
            "validation_fraction": cfg["validation_fraction"],
            "test_fraction": cfg["test_fraction"],
            "note": "This seed is independent of the 3 training seeds (42,43,44) and is fixed once for all tokenizer conditions.",
        },
        "checksums_sha256": checksums,
    }

    manifest_path = manifests_dir() / f"{language_pair}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest: {manifest_path}")
    return manifest


def main() -> int:
    from marianmt_comparison.config import load_yaml, CONFIGS_DIR

    base_cfg = load_yaml(CONFIGS_DIR / "base.yaml")
    for language_pair in ("en_ti", "en_am"):
        prepare_language_pair(language_pair, base_cfg)
    print("\nOPUS data preparation complete for en_ti and en_am.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
