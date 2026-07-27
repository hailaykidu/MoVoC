"""
io.py -- reading and writing the repository's configs and vocabularies.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "configs"
VOCABULARY = ROOT / "data/vocabulary"
MODELS = ROOT / "models"
RESULTS = ROOT / "evaluation/results"


def read_config(name: str) -> dict:
    with open(CONFIGS / name, encoding="utf-8") as f:
        return json.load(f)


def write_config(name: str, config: dict) -> None:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    with open(CONFIGS / name, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def read_vocabulary(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
