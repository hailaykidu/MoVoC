"""Config loading: merges configs/base.yaml with a per-language-pair
override file (configs/en_ti.yaml or configs/en_am.yaml).

No hidden defaults live outside these YAML files -- if you need to change a
hyperparameter, edit the YAML, not the code, so every run's provenance is
fully captured by simply hashing/copying the YAML files (which training.py
also does per-run).
"""
from __future__ import annotations

import copy
import subprocess
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs"

VALID_LANGUAGE_PAIRS = ("en_ti", "en_am")
VALID_TOKENIZERS = ("bpe", "wordpiece", "movoc_tok")
VALID_SEEDS = (42, 43, 44)


class ConfigError(RuntimeError):
    """Raised when configuration is missing, malformed, or internally
    inconsistent in a way that must stop the pipeline rather than be
    silently patched around."""


def _deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"Config file did not parse to a mapping: {path}")
    return data


def load_config(language_pair: str) -> dict:
    """Load and merge base.yaml + {language_pair}.yaml.

    Returns a plain dict. Callers needing dotted access can wrap it, but a
    dict keeps the on-disk provenance 1:1 with what gets hashed/copied into
    each run's metadata.
    """
    if language_pair not in VALID_LANGUAGE_PAIRS:
        raise ConfigError(
            f"Unknown language_pair '{language_pair}'. Expected one of {VALID_LANGUAGE_PAIRS}."
        )
    base = load_yaml(CONFIGS_DIR / "base.yaml")
    override = load_yaml(CONFIGS_DIR / f"{language_pair}.yaml")
    merged = _deep_merge(base, override)

    if merged.get("language_pair") != language_pair:
        raise ConfigError(
            f"configs/{language_pair}.yaml declares language_pair="
            f"{merged.get('language_pair')!r}, expected {language_pair!r}."
        )
    for tok in VALID_TOKENIZERS:
        if tok not in merged.get("tokenizers", {}):
            raise ConfigError(f"configs/{language_pair}.yaml missing tokenizers.{tok}")
    return merged


def tokenizer_config(cfg: dict, tokenizer_name: str) -> dict:
    if tokenizer_name not in VALID_TOKENIZERS:
        raise ConfigError(
            f"Unknown tokenizer '{tokenizer_name}'. Expected one of {VALID_TOKENIZERS}."
        )
    entry = cfg["tokenizers"][tokenizer_name]
    path = Path(entry["path"])
    if not path.exists():
        raise ConfigError(
            f"Tokenizer path for '{tokenizer_name}' does not exist: {path}. "
            "Tokenizers are read-only external artifacts and must already exist "
            "on disk -- this repository never creates or trains them."
        )
    return entry


def git_commit(short: bool = True) -> str:
    """Best-effort current commit hash of *this* repo (not amseg)."""
    try:
        args = ["git", "rev-parse", "--short", "HEAD"] if short else ["git", "rev-parse", "HEAD"]
        out = subprocess.run(
            args, cwd=REPO_ROOT, capture_output=True, text=True, timeout=10, check=True
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def run_experiment_dir(language_pair: str, tokenizer_name: str, seed: int) -> Path:
    if seed not in VALID_SEEDS:
        raise ConfigError(f"Unknown seed {seed}. Expected one of {VALID_SEEDS}.")
    d = REPO_ROOT / "experiments" / language_pair / tokenizer_name / f"seed_{seed}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def results_dir(language_pair: str) -> Path:
    d = REPO_ROOT / "results" / language_pair
    d.mkdir(parents=True, exist_ok=True)
    return d


def data_dir(language_pair: str, split: str | None = None) -> Path:
    d = REPO_ROOT / "data" / "finetuning" / language_pair
    if split is not None:
        d = d / split
    return d


def manifests_dir() -> Path:
    d = REPO_ROOT / "data" / "manifests"
    d.mkdir(parents=True, exist_ok=True)
    return d
