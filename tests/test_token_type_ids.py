"""Regression test for the MarianMT smoke-test failure:

    TypeError: MarianMTModel.forward() got an unexpected keyword argument
    'token_type_ids'

All three tokenizer artifacts (bpe, wordpiece, movoc_tok) are
PreTrainedTokenizerFast instances that include `token_type_ids` in their
default output. MarianMTModel does not accept that key, so it must never
appear in the dict handed to `model(**inputs)` / `model.generate(**inputs)`.

This test exercises the actual code paths (TranslationDataset.__getitem__
from training.py, and the tokenizer call in evaluate.py) against the real
tokenizer artifacts -- it does not modify or fake the tokenizers themselves.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from transformers import AutoTokenizer

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.data import ParallelExample  # noqa: E402
from marianmt_comparison.training import TranslationDataset  # noqa: E402

TOKENIZER_PATHS = {
    "bpe": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/bpe_63051",
    "wordpiece": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/wordpiece_63051",
    "movoc_tok": "/homes/neumann/teklehaymanot/amseg/tokenizers/hf/movoc_tok_63050_tigrinya",
}


def _available_tokenizers():
    return {name: path for name, path in TOKENIZER_PATHS.items() if Path(path).exists()}


@pytest.mark.parametrize("name", list(TOKENIZER_PATHS))
def test_tokenizer_produces_token_type_ids_by_default(name):
    """Sanity check establishing the root cause: confirm this transformers
    version really does emit token_type_ids by default for each tokenizer
    type, so the test below is exercising a real hazard, not a strawman."""
    paths = _available_tokenizers()
    if name not in paths:
        pytest.skip(f"tokenizer artifact not present: {TOKENIZER_PATHS[name]}")
    tok = AutoTokenizer.from_pretrained(paths[name])
    out = tok("hello world", max_length=10, truncation=True)
    assert "token_type_ids" in out


@pytest.mark.parametrize("name", list(TOKENIZER_PATHS))
def test_translation_dataset_strips_token_type_ids(name):
    """TranslationDataset.__getitem__ (used by the Trainer -> model(**inputs)
    path) must never return token_type_ids, for any of the three tokenizer
    types."""
    paths = _available_tokenizers()
    if name not in paths:
        pytest.skip(f"tokenizer artifact not present: {TOKENIZER_PATHS[name]}")
    tok = AutoTokenizer.from_pretrained(paths[name])
    ds = TranslationDataset(
        examples=[ParallelExample(source="hello world", target="hola mundo")],
        tokenizer=tok,
        max_source_length=16,
        max_target_length=16,
    )
    model_inputs = ds[0]
    assert "token_type_ids" not in model_inputs
    assert "input_ids" in model_inputs
    assert "labels" in model_inputs


@pytest.mark.parametrize("name", list(TOKENIZER_PATHS))
def test_evaluate_tokenization_strips_token_type_ids(name):
    """Mirrors the tokenizer call + defensive pop in scripts/evaluate.py
    (the model.generate(**inputs) path)."""
    paths = _available_tokenizers()
    if name not in paths:
        pytest.skip(f"tokenizer artifact not present: {TOKENIZER_PATHS[name]}")
    tok = AutoTokenizer.from_pretrained(paths[name])

    inputs = tok(
        ["hello world", "goodbye"],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=16,
        return_token_type_ids=False,
    )
    inputs.pop("token_type_ids", None)

    assert "token_type_ids" not in inputs
    assert "input_ids" in inputs
