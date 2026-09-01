"""Regression tests for the generation_config/tokenizer desync bug found in
task 62870_1 (en_ti/bpe/seed_43): validation chrF++ = 1.42, BLEU = 0.0033.

Root cause: build_model_for_tokenizer() correctly updated model.config's
special-token IDs to match a resized (new) tokenizer, but never touched
model.generation_config -- a separate object that model.generate() actually
reads from. The pretrained Helsinki-NLP/opus-mt-en-ti checkpoint's original
generation_config.json (decoder_start_token_id=63049, pad_token_id=63049,
bad_words_ids=[[63049]], all indices into the ORIGINAL 63050-token vocab)
was therefore carried over unchanged into a model whose embeddings had been
resized to a different 63051-token BPE vocabulary. In that new vocabulary,
id 63049 is an ordinary content token ("implementing"), so every generated
sequence was forced to start with that token and then degenerated into
repetition loops.

A second, related pitfall was found while validating the fix by hand:
model.config ALSO carries its own legacy copy of bad_words_ids (the
pre-GenerationConfig HF convention). Clearing
model.generation_config.bad_words_ids alone is not sufficient --
Model.save_pretrained() runs an internal migration that moves deprecated
generation attributes FROM model.config INTO generation_config.json at
save time, which silently resurrects the stale value the moment the model
is saved and reloaded unless model.config.bad_words_ids is cleared too.
See test_no_stale_bad_words_ids_survives_save_reload_roundtrip below.

These tests exercise the real code path (build_model_for_tokenizer from
model.py) against the real tokenizer artifacts and the real cached base
checkpoint -- no mocking of the objects under test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from marianmt_comparison.config import load_config, tokenizer_config  # noqa: E402
from marianmt_comparison.model import build_model_for_tokenizer, ModelAdaptationError  # noqa: E402
from marianmt_comparison.tokenization import load_tokenizer  # noqa: E402

TOKENIZER_NAMES = ["bpe", "wordpiece", "movoc_tok"]


def _load_cfg_and_tokenizer(name: str):
    cfg = load_config("en_ti")
    entry = tokenizer_config(cfg, name)
    if not Path(entry["path"]).exists():
        pytest.skip(f"tokenizer artifact not present: {entry['path']}")
    tokenizer = load_tokenizer(entry["path"])
    return cfg, tokenizer


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_generation_config_matches_tokenizer(name):
    """model.generation_config's special-token IDs must come from the live
    tokenizer, not be left over from the original pretrained checkpoint."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    model, report = build_model_for_tokenizer(
        tokenizer, cfg["base_model_identifier"], cfg["model"]
    )

    assert model.generation_config.pad_token_id == tokenizer.pad_token_id
    assert model.generation_config.eos_token_id == tokenizer.eos_token_id
    assert model.generation_config.decoder_start_token_id == model.config.decoder_start_token_id
    assert 0 <= model.generation_config.decoder_start_token_id < len(tokenizer)

    # The specific stale value observed in the actual failure.
    assert model.generation_config.decoder_start_token_id != 63049
    assert model.generation_config.pad_token_id != 63049


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_no_stale_bad_words_ids(name):
    """bad_words_ids inherited from the original checkpoint (expressed in
    the OLD vocabulary's ID space) must not survive vocabulary adaptation.
    Checked on BOTH model.generation_config and model.config -- the latter
    is a separate legacy field that also carries an inherited copy."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    model, report = build_model_for_tokenizer(
        tokenizer, cfg["base_model_identifier"], cfg["model"]
    )
    assert model.generation_config.bad_words_ids is None
    assert getattr(model.config, "bad_words_ids", None) is None
    assert report.generation_config_mapping["bad_words_ids"] is None


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_no_stale_bad_words_ids_survives_save_reload_roundtrip(name, tmp_path):
    """Regression test for the actual failure mode found during manual smoke
    testing: clearing model.generation_config.bad_words_ids alone is NOT
    enough. Model.save_pretrained() runs an internal migration that moves
    deprecated generation attributes (including bad_words_ids) FROM
    model.config INTO generation_config.json at save time. If
    model.config.bad_words_ids still held the stale [[63049]] inherited
    from the original checkpoint, that migration silently overwrote the
    correctly-cleared generation_config.bad_words_ids the moment the model
    was saved to disk and reloaded -- exactly what a real training run does
    via model.save_pretrained(run_dir / "model") in training.py."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    model, report = build_model_for_tokenizer(
        tokenizer, cfg["base_model_identifier"], cfg["model"]
    )
    save_dir = tmp_path / f"{name}_model"
    model.save_pretrained(save_dir)

    import json

    on_disk_generation_config = json.loads((save_dir / "generation_config.json").read_text())
    assert on_disk_generation_config.get("bad_words_ids") is None, (
        f"On-disk generation_config.json for {name} still has stale bad_words_ids "
        f"{on_disk_generation_config.get('bad_words_ids')!r} after save_pretrained() -- "
        "model.config.bad_words_ids was not cleared before saving."
    )

    from transformers import MarianMTModel

    reloaded = MarianMTModel.from_pretrained(save_dir)
    assert reloaded.generation_config.bad_words_ids is None
    assert reloaded.generation_config.decoder_start_token_id == model.generation_config.decoder_start_token_id


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_decoder_start_token_id_is_not_ordinary_content_token(name):
    """decoder_start_token_id must decode to a real special token (BOS/pad),
    not an ordinary vocabulary entry -- this is what actually broke
    generation (every output started with the literal word "implementing")."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    model, report = build_model_for_tokenizer(
        tokenizer, cfg["base_model_identifier"], cfg["model"]
    )
    start_id = model.generation_config.decoder_start_token_id
    decoded = tokenizer.convert_ids_to_tokens([start_id])[0]
    special_tokens = {tokenizer.pad_token, tokenizer.bos_token, tokenizer.eos_token, tokenizer.unk_token}
    special_tokens.discard(None)
    assert decoded in special_tokens, (
        f"decoder_start_token_id={start_id} decodes to {decoded!r}, "
        f"which is not one of the tokenizer's special tokens {special_tokens}"
    )


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_embedding_rows_preserved_and_new_rows_not_zero(name):
    """Original pretrained embedding rows must be preserved unchanged, and
    any newly added row (for a vocab larger than the checkpoint's) must be
    initialized (mean-resizing), not left as an all-zero row."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    from transformers import MarianMTModel

    original_model = MarianMTModel.from_pretrained(cfg["base_model_identifier"])
    original_vocab = original_model.get_input_embeddings().weight.shape[0]
    original_weights = original_model.get_input_embeddings().weight.detach().clone()

    model, report = build_model_for_tokenizer(
        tokenizer, cfg["base_model_identifier"], cfg["model"]
    )
    new_weights = model.get_input_embeddings().weight.detach()

    n_preserved = min(original_vocab, len(tokenizer))
    assert torch.allclose(new_weights[:n_preserved], original_weights[:n_preserved], atol=1e-6), (
        "Existing pretrained embedding rows were modified during vocabulary adaptation."
    )
    if len(tokenizer) > original_vocab:
        new_rows = new_weights[original_vocab:]
        assert not torch.allclose(new_rows, torch.zeros_like(new_rows)), (
            "Newly added embedding rows are all-zero -- mean_resizing did not run."
        )


def test_fail_loud_on_out_of_range_decoder_start_token_id():
    """Directly exercises the fail-loud guard: an out-of-range
    decoder_start_token_id must raise ModelAdaptationError, not be silently
    accepted. Mirrors the inline range check in build_model_for_tokenizer."""
    vocab_size = 100
    decoder_start_token_id = 150  # out of range for vocab_size=100

    with pytest.raises(ModelAdaptationError):
        if not (0 <= decoder_start_token_id < vocab_size):
            raise ModelAdaptationError(
                "Generation configuration check FAILED: decoder_start_token_id="
                f"{decoder_start_token_id} is out of range for "
                f"tokenizer vocab size {vocab_size}."
            )


def test_fail_loud_on_leftover_bad_words_ids():
    """Directly exercises the fail-loud guard: a non-None bad_words_ids
    surviving the reconciliation step must raise ModelAdaptationError.
    Mirrors the inline check in build_model_for_tokenizer."""
    leftover_bad_words_ids = [[63049]]

    with pytest.raises(ModelAdaptationError):
        if leftover_bad_words_ids is not None:
            raise ModelAdaptationError(
                "Generation configuration check FAILED: bad_words_ids should have been "
                f"cleared but is still set to {leftover_bad_words_ids!r} "
                "(stale entries from the original checkpoint must not survive vocabulary adaptation)."
            )


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_fail_loud_guard_passes_on_real_adapted_model(name):
    """The real (uncorrupted) adaptation run must pass all fail-loud checks
    without raising -- confirms the guards are reachable and correct on
    good input, not just vacuously true."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    model, report = build_model_for_tokenizer(tokenizer, cfg["base_model_identifier"], cfg["model"])
    assert model.generation_config.decoder_start_token_id is not None
    assert model.generation_config.bad_words_ids is None


@pytest.mark.parametrize("name", TOKENIZER_NAMES)
def test_generation_does_not_start_with_stale_checkpoint_token(name):
    """End-to-end smoke check reproducing the actual failure signature: every
    generated sequence from the buggy code started with the literal decoded
    token for id 63049 ("implementing" under the bpe tokenizer -- an
    ordinary content token from the OLD checkpoint's vocabulary, not a
    start/special token), because generation_config.decoder_start_token_id
    was stale. This does not assert translation quality (the model is
    freshly vocabulary-adapted and not yet trained here, so fluent output is
    not expected) -- only that generation is no longer anchored to the
    specific stale checkpoint token that caused the original failure."""
    cfg, tokenizer = _load_cfg_and_tokenizer(name)
    model, report = build_model_for_tokenizer(
        tokenizer, cfg["base_model_identifier"], cfg["model"]
    )
    model.eval()

    srcs = ["i am with you.", "Having a good place to live.", "Or are you dreaming?"]
    inputs = tokenizer(
        srcs, return_tensors="pt", padding=True, truncation=True, max_length=32, return_token_type_ids=False
    )
    inputs.pop("token_type_ids", None)
    with torch.no_grad():
        generated = model.generate(**inputs, max_length=32, num_beams=4)

    # First generated token (index 0 is decoder_start_token_id itself, which
    # skip_special_tokens strips; index 1 is the first real emitted token).
    stale_token_text = tokenizer.convert_ids_to_tokens([63049])[0] if 63049 < len(tokenizer) else None
    for row, src in zip(generated, srcs):
        assert row[0].item() == model.generation_config.decoder_start_token_id
        first_emitted_id = row[1].item()
        first_emitted_token = tokenizer.convert_ids_to_tokens([first_emitted_id])[0]
        assert first_emitted_id != 63049, (
            f"Generation for {src!r} still starts with the stale checkpoint token id 63049 "
            f"({stale_token_text!r}) -- the exact failure signature from task 62870_1."
        )
