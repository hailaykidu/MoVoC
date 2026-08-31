"""Deterministic seeding and provenance metadata helpers shared by every
script that trains, evaluates, or otherwise produces recorded results.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import os
import random
from pathlib import Path
from typing import Any

import numpy as np


def set_all_seeds(seed: int) -> None:
    """Seed python, numpy, and torch (CPU + all CUDA devices) identically.

    Does not set torch.use_deterministic_algorithms(True) globally because
    some MarianMT/attention kernels do not have deterministic
    implementations on all hardware; full run-to-run bit-identical
    determinism is not claimed. What IS guaranteed: identical data
    ordering, identical initialization seed, identical dropout mask seed
    stream. This is standard practice for this kind of comparison and is
    recorded as such in the metadata (see build_run_metadata).
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def utc_timestamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def build_run_metadata(
    *,
    language_pair: str,
    tokenizer_name: str,
    seed: int,
    model_identifier: str,
    model_revision: str,
    tokenizer_identifier: str,
    tokenizer_revision: str,
    tokenizer_vocab_size: int,
    dataset_identifier: str,
    dataset_manifest_path: str,
    learning_rate: float,
    batch_size: int,
    epochs: int,
    max_source_length: int,
    max_target_length: int,
    optimizer: str,
    scheduler: str,
    sacrebleu_version: str,
    chrf_signature: str,
    git_commit: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the exact metadata fields required by the experimental
    protocol (spec section 14). Every run writes this dict to
    metadata.json in its experiment directory.
    """
    meta = {
        "language_pair": language_pair,
        "tokenizer": tokenizer_name,
        "seed": seed,
        "model_identifier": model_identifier,
        "model_revision": model_revision,
        "tokenizer_identifier": tokenizer_identifier,
        "tokenizer_revision": tokenizer_revision,
        "tokenizer_vocab_size": tokenizer_vocab_size,
        "dataset_identifier": dataset_identifier,
        "dataset_manifest": dataset_manifest_path,
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "epochs": epochs,
        "max_source_length": max_source_length,
        "max_target_length": max_target_length,
        "optimizer": optimizer,
        "scheduler": scheduler,
        "sacrebleu_version": sacrebleu_version,
        "chrf_signature": chrf_signature,
        "git_commit": git_commit,
        "timestamp": utc_timestamp(),
    }
    if extra:
        meta["extra"] = extra
    return meta
