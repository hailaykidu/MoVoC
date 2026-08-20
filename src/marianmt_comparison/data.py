"""Shared data helpers: reading processed parallel splits, and the
deterministic split logic used once by scripts/prepare_opus_data.py so the
exact same train/validation/test partition is reused by every tokenizer.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class ParallelExample:
    source: str
    target: str


def read_parallel(src_path: Path, tgt_path: Path) -> list[ParallelExample]:
    with open(src_path, "r", encoding="utf-8") as fs, open(tgt_path, "r", encoding="utf-8") as ft:
        src_lines = [l.rstrip("\n") for l in fs]
        tgt_lines = [l.rstrip("\n") for l in ft]
    if len(src_lines) != len(tgt_lines):
        raise ValueError(
            f"Parallel file line-count mismatch: {src_path} has {len(src_lines)} lines, "
            f"{tgt_path} has {len(tgt_lines)} lines."
        )
    return [ParallelExample(s, t) for s, t in zip(src_lines, tgt_lines)]


def filter_examples(
    examples: list[ParallelExample],
    max_whitespace_tokens: int,
    min_line_length_chars: int,
    drop_empty_lines: bool,
) -> list[ParallelExample]:
    out = []
    for ex in examples:
        s, t = ex.source.strip(), ex.target.strip()
        if drop_empty_lines and (not s or not t):
            continue
        if len(s) < min_line_length_chars or len(t) < min_line_length_chars:
            continue
        if len(s.split()) > max_whitespace_tokens or len(t.split()) > max_whitespace_tokens:
            continue
        out.append(ParallelExample(s, t))
    return out


def deduplicate_examples(examples: list[ParallelExample]) -> tuple[list[ParallelExample], int]:
    """Drop examples whose source sentence has already been seen.

    OPUS NLLB (a web-mined corpus) contains a non-trivial fraction of exact
    duplicate source lines (~2-6% observed here) -- if left in, a random
    train/validation/test split will place the same source sentence in both
    train and test, contaminating held-out evaluation. Deduplicating on the
    source side alone (not just the (source, target) pair) is deliberate:
    even a source sentence paired with a *different* target elsewhere in the
    corpus still leaks n-gram/surface information into scoring if it also
    appears in train. First occurrence (in the given, not-yet-shuffled input
    order) is kept, so this is deterministic and independent of the split
    seed. Returns (deduplicated_examples, number_dropped).
    """
    seen: set[str] = set()
    out: list[ParallelExample] = []
    for ex in examples:
        if ex.source in seen:
            continue
        seen.add(ex.source)
        out.append(ex)
    return out, len(examples) - len(out)


def deterministic_split(
    examples: list[ParallelExample],
    split_seed: int,
    train_fraction: float,
    validation_fraction: float,
    test_fraction: float,
) -> dict[str, list[ParallelExample]]:
    total = train_fraction + validation_fraction + test_fraction
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Split fractions must sum to 1.0, got {total}")

    indices = list(range(len(examples)))
    rng = random.Random(split_seed)
    rng.shuffle(indices)

    n = len(indices)
    n_train = int(n * train_fraction)
    n_val = int(n * validation_fraction)
    train_idx = indices[:n_train]
    val_idx = indices[n_train : n_train + n_val]
    test_idx = indices[n_train + n_val :]

    return {
        "train": [examples[i] for i in train_idx],
        "validation": [examples[i] for i in val_idx],
        "test": [examples[i] for i in test_idx],
    }


def write_split(examples: list[ParallelExample], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    src_path = out_dir / "src.txt"
    tgt_path = out_dir / "tgt.txt"
    with open(src_path, "w", encoding="utf-8") as fs, open(tgt_path, "w", encoding="utf-8") as ft:
        for ex in examples:
            fs.write(ex.source + "\n")
            ft.write(ex.target + "\n")
    return src_path, tgt_path


def load_split(language_pair: str, split: str, repo_root: Path, max_examples: int | None = None) -> list[ParallelExample]:
    d = repo_root / "data" / "processed" / language_pair / split
    src_path, tgt_path = d / "src.txt", d / "tgt.txt"
    if not src_path.exists() or not tgt_path.exists():
        raise FileNotFoundError(
            f"Processed split not found for {language_pair}/{split}: expected {src_path} and {tgt_path}. "
            "Run scripts/prepare_opus_data.py first."
        )
    examples = read_parallel(src_path, tgt_path)
    if max_examples is not None:
        examples = examples[:max_examples]
    return examples
