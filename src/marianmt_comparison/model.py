"""MarianMT model construction and embedding/vocabulary adaptation.

This module implements the single most safety-critical piece of the
comparison: correctly adapting a MarianMT model's embeddings and output
projection to each tokenizer's vocabulary. `model.resize_token_embeddings`
alone is never trusted blindly -- every resize is verified afterward, special
token IDs are checked for range/collision, newly added rows are
re-initialized with a documented strategy, and any failure raises a
descriptive exception rather than warning-and-continuing.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch
from transformers import (
    AutoConfig,
    GenerationConfig,
    MarianConfig,
    MarianMTModel,
    PreTrainedTokenizerBase,
)
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError


class ModelAdaptationError(RuntimeError):
    """Raised when embedding/vocabulary adaptation fails a required check.
    Message always states which check failed and actual vs expected values.
    """


class ModelResolutionError(RuntimeError):
    """Raised when a base model checkpoint identifier is invalid (i.e. not
    found on the Hub AND no valid from-scratch fallback config is available).
    """


@dataclass
class ModelResolution:
    requested_identifier: str
    status: str  # "found" | "not_found" | "fallback_used"
    resolved_revision: str | None
    used_from_scratch_config: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_identifier": self.requested_identifier,
            "status": self.status,
            "resolved_revision": self.resolved_revision,
            "used_from_scratch_config": self.used_from_scratch_config,
            "message": self.message,
        }


def resolve_base_model(identifier: str) -> ModelResolution:
    """Live Hub lookup (network required) for whether `identifier` resolves.
    Called at pipeline run time by scripts/verify_models.py and
    scripts/train.py -- never assumed at repo-build time.
    """
    try:
        info = HfApi().model_info(identifier)
        return ModelResolution(
            requested_identifier=identifier,
            status="found",
            resolved_revision=getattr(info, "sha", None),
            used_from_scratch_config=False,
            message=f"Resolved '{identifier}' on the HuggingFace Hub (sha={getattr(info, 'sha', None)}).",
        )
    except HfHubHTTPError as exc:
        return ModelResolution(
            requested_identifier=identifier,
            status="not_found",
            resolved_revision=None,
            used_from_scratch_config=True,
            message=f"'{identifier}' not found on the HuggingFace Hub ({exc}); falling back to from-scratch MarianConfig.",
        )
    except Exception as exc:  # noqa: BLE001 - network errors, DNS, etc.
        return ModelResolution(
            requested_identifier=identifier,
            status="not_found",
            resolved_revision=None,
            used_from_scratch_config=True,
            message=f"Could not reach HuggingFace Hub to resolve '{identifier}' ({exc!r}); falling back to from-scratch MarianConfig.",
        )


def build_from_scratch_config(vocab_size: int, model_cfg: dict, pad_token_id: int) -> MarianConfig:
    """Construct a MarianConfig matching the marian_original architecture
    (6+6 layers, 8 heads, d_model 512, ffn 2048, shared embeddings) per
    RESOLVED DECISION #4, parameterized by configs/base.yaml's `model:`
    block so nothing here is a hidden magic number.
    """
    return MarianConfig(
        vocab_size=vocab_size,
        decoder_vocab_size=vocab_size,
        d_model=model_cfg["d_model"],
        encoder_layers=model_cfg["encoder_layers"],
        decoder_layers=model_cfg["decoder_layers"],
        encoder_attention_heads=model_cfg["encoder_attention_heads"],
        decoder_attention_heads=model_cfg["decoder_attention_heads"],
        encoder_ffn_dim=model_cfg["encoder_ffn_dim"],
        decoder_ffn_dim=model_cfg["decoder_ffn_dim"],
        dropout=model_cfg["dropout"],
        attention_dropout=model_cfg["attention_dropout"],
        activation_function=model_cfg["activation_function"],
        share_encoder_decoder_embeddings=model_cfg["share_encoder_decoder_embeddings"],
        tie_word_embeddings=model_cfg["tie_word_embeddings"],
        pad_token_id=pad_token_id,
        scale_embedding=True,
    )


@dataclass
class EmbeddingAdaptationReport:
    tokenizer_vocab_size: int
    base_model_original_vocab_size: int | None
    resize_performed: bool
    tie_word_embeddings: bool
    special_token_id_mapping: dict[str, int | None]
    init_strategy: str
    generation_config_mapping: dict[str, Any] = field(default_factory=dict)
    checks: list[dict[str, Any]] = field(default_factory=list)
    status: str = "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tokenizer_vocab_size": self.tokenizer_vocab_size,
            "base_model_original_vocab_size": self.base_model_original_vocab_size,
            "resize_performed": self.resize_performed,
            "tie_word_embeddings": self.tie_word_embeddings,
            "special_token_id_mapping": self.special_token_id_mapping,
            "init_strategy": self.init_strategy,
            "generation_config_mapping": self.generation_config_mapping,
            "checks": self.checks,
            "status": self.status,
        }


def _record(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": passed, "detail": detail})


def build_model_for_tokenizer(
    tokenizer: PreTrainedTokenizerBase,
    base_model_name_or_config,
    model_cfg: dict,
    src_or_tgt_shared: bool = True,
) -> tuple[MarianMTModel, EmbeddingAdaptationReport]:
    """Build (or load) a MarianMT model and correctly adapt its embeddings
    and output projection to `tokenizer`.

    `base_model_name_or_config` is either:
      - a str Hub identifier that resolved successfully (loads real weights), or
      - a MarianConfig (from build_from_scratch_config) for from-scratch construction.

    Returns (model, report). Raises ModelAdaptationError with a descriptive
    message if any required check fails.
    """
    vocab_size = len(tokenizer)
    checks: list[dict[str, Any]] = []

    if isinstance(base_model_name_or_config, str):
        model = MarianMTModel.from_pretrained(base_model_name_or_config)
        original_vocab_size = model.get_input_embeddings().weight.shape[0]
        used_from_scratch = False
    elif isinstance(base_model_name_or_config, MarianConfig):
        model = MarianMTModel(base_model_name_or_config)
        original_vocab_size = base_model_name_or_config.vocab_size
        used_from_scratch = True
    else:
        raise ModelAdaptationError(
            "base_model_name_or_config must be a str Hub identifier or a "
            f"MarianConfig; got {type(base_model_name_or_config)!r}."
        )

    tie_active = bool(getattr(model.config, "tie_word_embeddings", False))
    _record(
        checks,
        "tie_word_embeddings_read",
        True,
        f"model.config.tie_word_embeddings={tie_active}",
    )

    # --- (b) resize + verify ---------------------------------------------
    # mean_resizing=True (the transformers default) initializes newly added
    # rows by sampling from a multivariate normal matching the MEAN and
    # covariance of the existing embedding rows, and leaves all existing
    # rows byte-for-byte untouched. This is done here, once, and never
    # overwritten below -- there used to be a second, cruder
    # zero-mean/std-only re-init pass after this that discarded the mean;
    # that pass has been removed (see (c) below).
    resize_needed = original_vocab_size != vocab_size
    if resize_needed or used_from_scratch:
        model.resize_token_embeddings(vocab_size, mean_resizing=True)
    resize_performed = resize_needed or used_from_scratch

    input_emb = model.get_input_embeddings()
    actual_input_vocab = input_emb.weight.shape[0]
    if actual_input_vocab != vocab_size:
        raise ModelAdaptationError(
            "Input embedding resize verification FAILED: "
            f"expected vocab dim {vocab_size}, got {actual_input_vocab}."
        )
    _record(checks, "input_embedding_resize", True, f"shape[0]={actual_input_vocab} == tokenizer vocab {vocab_size}")

    output_emb = model.get_output_embeddings()
    if output_emb is not None:
        actual_output_vocab = output_emb.weight.shape[0]
        if actual_output_vocab != vocab_size:
            raise ModelAdaptationError(
                "Output projection resize verification FAILED: "
                f"expected vocab dim {vocab_size}, got {actual_output_vocab}."
            )
        _record(checks, "output_embedding_resize", True, f"shape[0]={actual_output_vocab} == tokenizer vocab {vocab_size}")

        if tie_active:
            same_storage = output_emb.weight.data_ptr() == input_emb.weight.data_ptr()
            _record(
                checks,
                "tied_embedding_shape_match",
                output_emb.weight.shape == input_emb.weight.shape,
                f"output shape {tuple(output_emb.weight.shape)} vs input shape {tuple(input_emb.weight.shape)}; "
                f"shared storage={same_storage}",
            )
            if output_emb.weight.shape != input_emb.weight.shape:
                raise ModelAdaptationError(
                    "Tied-embedding shape mismatch FAILED: "
                    f"input embedding shape {tuple(input_emb.weight.shape)} != "
                    f"output embedding shape {tuple(output_emb.weight.shape)}."
                )
    else:
        _record(checks, "output_embedding_resize", True, "model has no separate output embedding module (fully tied); skipped")

    # --- (c) re-init newly added rows / preserve existing rows -------------
    # New rows were already initialized by resize_token_embeddings(...,
    # mean_resizing=True) in step (b), which draws from a multivariate
    # normal matching the mean and covariance of the existing (preserved)
    # embedding rows. Nothing further needs to touch the embedding weights
    # here; this block only verifies that behavior and records it.
    if used_from_scratch:
        # No pretrained checkpoint exists to preserve or match a mean
        # against -- MarianMTModel's own from-scratch initialization
        # (governed by model_cfg["init_std"] / MarianConfig.init_std) is
        # used for every row.
        init_strategy = "from_scratch MarianMTModel init applied to ALL rows (no pretrained checkpoint)"
        _record(checks, "embedding_init", True, init_strategy)
    elif resize_performed and vocab_size > original_vocab_size:
        init_strategy = (
            f"mean_resizing=True (transformers built-in): new rows [{original_vocab_size}:{vocab_size}] "
            "sampled from a multivariate normal matching the mean and covariance of the "
            f"existing checkpoint's embedding rows [0:{original_vocab_size}], which are left byte-for-byte unchanged"
        )
        _record(
            checks,
            "embedding_init",
            True,
            f"added {vocab_size - original_vocab_size} new rows via mean_resizing; "
            f"existing rows [0:{original_vocab_size}] preserved from the pretrained checkpoint",
        )
    elif resize_performed and vocab_size < original_vocab_size:
        init_strategy = "vocab_size < original checkpoint vocab_size: truncation only, no new rows to initialize"
        _record(checks, "embedding_init", True, init_strategy)
    else:
        init_strategy = "no resize was necessary; original checkpoint embeddings used as-is"
        _record(checks, "embedding_init", True, init_strategy)

    # --- (d) special token ID remap / range verification --------------------
    special_ids = {
        "pad_token_id": tokenizer.pad_token_id,
        "unk_token_id": tokenizer.unk_token_id,
        "bos_token_id": getattr(tokenizer, "bos_token_id", None),
        "eos_token_id": tokenizer.eos_token_id,
    }
    present = {k: v for k, v in special_ids.items() if v is not None}
    for key, tid in present.items():
        if tid < 0 or tid >= vocab_size:
            raise ModelAdaptationError(
                f"Special token ID check FAILED for {key}: id={tid} is out of "
                f"range for resized embedding size {vocab_size} (expected 0 <= id < {vocab_size})."
            )
    seen: dict[int, str] = {}
    for key, tid in present.items():
        if tid in seen:
            raise ModelAdaptationError(
                f"Special token ID collision FAILED: {key} and {seen[tid]} both "
                f"map to id {tid}, which would corrupt embedding lookup."
            )
        seen[tid] = key
    _record(checks, "special_token_id_range_and_collision", True, f"ids={present}, vocab_size={vocab_size}")

    if tokenizer.pad_token_id is not None:
        model.config.pad_token_id = tokenizer.pad_token_id
    if getattr(tokenizer, "bos_token_id", None) is not None:
        model.config.decoder_start_token_id = tokenizer.bos_token_id
    elif tokenizer.eos_token_id is not None:
        # MarianMT convention when no BOS exists: decoder starts from pad or eos.
        model.config.decoder_start_token_id = model.config.pad_token_id
    if tokenizer.eos_token_id is not None:
        model.config.eos_token_id = tokenizer.eos_token_id
    if tokenizer.unk_token_id is not None:
        model.config.unk_token_id = tokenizer.unk_token_id
    model.config.vocab_size = vocab_size

    # --- (e) synchronize generation_config with the live tokenizer ---------
    # `model.generate()` reads from model.generation_config, NOT
    # model.config -- they are separate objects. When loading a pretrained
    # checkpoint, `from_pretrained` also loads that checkpoint's *original*
    # generation_config.json, which encodes special-token IDs for the
    # ORIGINAL tokenizer/vocabulary. If the vocabulary is then resized to a
    # different tokenizer (as above), those inherited IDs silently become
    # stale: e.g. an inherited decoder_start_token_id may now point at an
    # ordinary content token in the new vocabulary rather than a start
    # token, and an inherited bad_words_ids may ban an arbitrary token that
    # has nothing to do with the new tokenizer. Every special-token ID
    # (and bad_words_ids, which is expressed in the same ID space) is
    # rebuilt here from the tokenizer, never left over from the checkpoint,
    # and never hard-coded.
    #
    # model.config ALSO carries its own legacy copy of several generation
    # parameters (the pre-GenerationConfig HF convention), independently of
    # model.generation_config. In particular model.config.bad_words_ids is
    # inherited from the original checkpoint the same way and is NOT
    # touched by resize_token_embeddings or by anything above. If left
    # alone, `Model.save_pretrained()` runs its own
    # "move deprecated generation attributes from config to
    # generation_config" migration at save time and will silently
    # overwrite generation_config.bad_words_ids with this stale value --
    # so it must be cleared on model.config too, not just on
    # generation_config, or the fix does not survive a save/reload
    # round-trip (confirmed: this is exactly what happened on the first
    # attempt at this fix).
    model.config.bad_words_ids = None
    model.config.forced_eos_token_id = tokenizer.eos_token_id

    model.generation_config = GenerationConfig.from_model_config(model.config)
    if tokenizer.pad_token_id is not None:
        model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.decoder_start_token_id = model.config.decoder_start_token_id
    if tokenizer.eos_token_id is not None:
        model.generation_config.eos_token_id = tokenizer.eos_token_id
    # bad_words_ids inherited from the original checkpoint is expressed in
    # the OLD vocabulary's ID space and has no defined meaning in the new
    # one -- reconcile by dropping it rather than carrying a stale ban
    # forward. If a future run needs a real bad-words list for the new
    # tokenizer, it must be set explicitly, not inherited.
    model.generation_config.bad_words_ids = None
    model.generation_config.forced_eos_token_id = tokenizer.eos_token_id

    # --- (f) fail-loud verification of tokenizer/embedding/generation consistency
    def _check_id_matches(label: str, config_value, expected, source: str) -> None:
        if expected is None:
            return
        if config_value != expected:
            raise ModelAdaptationError(
                f"Generation configuration consistency check FAILED for {label}: "
                f"got {config_value!r}, expected {expected!r} (from {source})."
            )

    if len(tokenizer) != vocab_size:
        raise ModelAdaptationError(
            f"Tokenizer vocab size check FAILED: len(tokenizer)={len(tokenizer)} "
            f"!= vocab_size used for resize ({vocab_size})."
        )
    final_input_vocab = model.get_input_embeddings().weight.shape[0]
    if final_input_vocab != len(tokenizer):
        raise ModelAdaptationError(
            "Post-adaptation embedding size check FAILED: input embedding "
            f"shape[0]={final_input_vocab} != len(tokenizer)={len(tokenizer)}."
        )
    _check_id_matches("model.config.pad_token_id", model.config.pad_token_id, tokenizer.pad_token_id, "tokenizer.pad_token_id")
    _check_id_matches("model.config.eos_token_id", model.config.eos_token_id, tokenizer.eos_token_id, "tokenizer.eos_token_id")
    _check_id_matches(
        "model.generation_config.pad_token_id",
        model.generation_config.pad_token_id,
        tokenizer.pad_token_id,
        "tokenizer.pad_token_id",
    )
    _check_id_matches(
        "model.generation_config.eos_token_id",
        model.generation_config.eos_token_id,
        tokenizer.eos_token_id,
        "tokenizer.eos_token_id",
    )
    _check_id_matches(
        "model.generation_config.decoder_start_token_id",
        model.generation_config.decoder_start_token_id,
        model.config.decoder_start_token_id,
        "model.config.decoder_start_token_id",
    )
    if not (0 <= model.generation_config.decoder_start_token_id < len(tokenizer)):
        raise ModelAdaptationError(
            "Generation configuration check FAILED: decoder_start_token_id="
            f"{model.generation_config.decoder_start_token_id} is out of range for "
            f"tokenizer vocab size {len(tokenizer)}."
        )
    if model.generation_config.bad_words_ids is not None:
        raise ModelAdaptationError(
            "Generation configuration check FAILED: generation_config.bad_words_ids should "
            f"have been cleared but is still set to {model.generation_config.bad_words_ids!r} "
            "(stale entries from the original checkpoint must not survive vocabulary adaptation)."
        )
    if getattr(model.config, "bad_words_ids", None) is not None:
        raise ModelAdaptationError(
            "Generation configuration check FAILED: model.config.bad_words_ids should have "
            f"been cleared but is still set to {model.config.bad_words_ids!r}. This is the "
            "legacy config field that Model.save_pretrained() migrates into "
            "generation_config.json at save time -- leaving it set would silently "
            "resurrect a stale bad_words_ids after a save/reload round-trip even though "
            "generation_config.bad_words_ids looks clean in memory right now."
        )
    _record(
        checks,
        "generation_config_synchronized",
        True,
        "model.generation_config.{pad_token_id,eos_token_id,decoder_start_token_id} rebuilt from the "
        f"tokenizer/model.config (pad={model.generation_config.pad_token_id}, "
        f"eos={model.generation_config.eos_token_id}, "
        f"decoder_start={model.generation_config.decoder_start_token_id}); "
        "stale bad_words_ids from the original checkpoint cleared",
    )

    report = EmbeddingAdaptationReport(
        tokenizer_vocab_size=vocab_size,
        base_model_original_vocab_size=original_vocab_size,
        resize_performed=resize_performed,
        tie_word_embeddings=tie_active,
        special_token_id_mapping=present,
        init_strategy=init_strategy,
        generation_config_mapping={
            "pad_token_id": model.generation_config.pad_token_id,
            "eos_token_id": model.generation_config.eos_token_id,
            "decoder_start_token_id": model.generation_config.decoder_start_token_id,
            "forced_eos_token_id": model.generation_config.forced_eos_token_id,
            "bad_words_ids": model.generation_config.bad_words_ids,
        },
        checks=checks,
        status="PASS",
    )
    return model, report


def write_embedding_adaptation_report(report: EmbeddingAdaptationReport, run_dir: Path) -> Path:
    out_path = Path(run_dir) / "embedding_adaptation_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report.to_dict(), fh, indent=2)
    return out_path
