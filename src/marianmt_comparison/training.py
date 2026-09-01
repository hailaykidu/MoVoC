"""Training orchestration for a single (language_pair, tokenizer, seed) run.

Wraps HuggingFace's Seq2SeqTrainer. All hyperparameters come from
configs/base.yaml + configs/{language_pair}.yaml -- nothing is hardcoded
here except the well-known HF Trainer plumbing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    PreTrainedTokenizerBase,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from . import config as cfgmod
from .data import ParallelExample
from .evaluation import evaluate as chrf_evaluate
from .model import (
    ModelAdaptationError,
    build_from_scratch_config,
    build_model_for_tokenizer,
    resolve_base_model,
    write_embedding_adaptation_report,
)
from .reproducibility import build_run_metadata, set_all_seeds, utc_timestamp


class TranslationDataset(Dataset):
    def __init__(
        self,
        examples: list[ParallelExample],
        tokenizer: PreTrainedTokenizerBase,
        max_source_length: int,
        max_target_length: int,
    ):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        ex = self.examples[idx]
        model_inputs = self.tokenizer(
            ex.source,
            max_length=self.max_source_length,
            truncation=True,
            return_token_type_ids=False,
        )
        with self.tokenizer.as_target_tokenizer() if hasattr(self.tokenizer, "as_target_tokenizer") else _nullcontext():
            labels = self.tokenizer(
                ex.target,
                max_length=self.max_target_length,
                truncation=True,
                return_token_type_ids=False,
            )
        model_inputs["labels"] = labels["input_ids"]
        # MarianMTModel.forward() does not accept token_type_ids. Some
        # tokenizer backends (e.g. WordPiece/BERT-style) return it regardless
        # of return_token_type_ids on certain transformers versions, so strip
        # it defensively as well as requesting it not be produced above.
        model_inputs.pop("token_type_ids", None)
        return model_inputs


class _nullcontext:
    def __enter__(self):
        return None

    def __exit__(self, *a):
        return False


def resolve_model_and_report(
    base_model_identifier: str,
    tokenizer: PreTrainedTokenizerBase,
    model_cfg: dict,
) -> tuple[Any, dict, dict]:
    """Returns (model, model_resolution_dict, embedding_adaptation_report_dict).
    Raises ModelAdaptationError / ModelResolutionError on failure (never
    silently continues with a broken model)."""
    resolution = resolve_base_model(base_model_identifier)

    if resolution.status == "found":
        base = base_model_identifier
    else:
        pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
        base = build_from_scratch_config(len(tokenizer), model_cfg, pad_token_id=pad_id)

    model, adaptation_report = build_model_for_tokenizer(tokenizer, base, model_cfg)
    return model, resolution.to_dict(), adaptation_report.to_dict()


def run_training(
    *,
    language_pair: str,
    tokenizer_name: str,
    seed: int,
    tokenizer: PreTrainedTokenizerBase,
    tokenizer_identifier: str,
    tokenizer_vocab_size: int,
    train_examples: list[ParallelExample],
    val_examples: list[ParallelExample],
    cfg: dict,
    run_dir: Path,
    dataset_identifier: str,
    dataset_manifest_path: str,
    max_steps: int | None = None,
) -> dict[str, Any]:
    """Executes one full training run and returns a result dict with
    validation chrF++/BLEU and paths to all artifacts written. Writes
    metadata.json, embedding_adaptation_report.json, and
    validation_results.json into run_dir.
    """
    set_all_seeds(seed)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    model, model_resolution, adaptation_report = resolve_model_and_report(
        base_model_identifier=cfg["base_model_identifier"],
        tokenizer=tokenizer,
        model_cfg=cfg["model"],
    )
    write_embedding_adaptation_report_from_dict(adaptation_report, run_dir)

    train_ds = TranslationDataset(train_examples, tokenizer, cfg["max_source_length"], cfg["max_target_length"])
    val_ds = TranslationDataset(val_examples, tokenizer, cfg["max_source_length"], cfg["max_target_length"])

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

    training_args_kwargs = {
        "output_dir": str(run_dir / "checkpoints"),
        "seed": seed,
        "data_seed": seed,
        "learning_rate": cfg["learning_rate"],
        "per_device_train_batch_size": cfg["batch_size"],
        "per_device_eval_batch_size": cfg["batch_size"],
        "gradient_accumulation_steps": cfg["gradient_accumulation_steps"],
        "weight_decay": cfg["weight_decay"],
        "adam_beta1": cfg["adam_beta1"],
        "adam_beta2": cfg["adam_beta2"],
        "adam_epsilon": cfg["adam_epsilon"],
        "lr_scheduler_type": cfg["lr_scheduler"],
        "warmup_steps": cfg["warmup_steps"],
        "label_smoothing_factor": cfg["label_smoothing"],
        "predict_with_generate": True,
        "generation_max_length": cfg["generation_max_length"],
        "generation_num_beams": cfg["generation_num_beams"],
        "logging_steps": cfg["logging_steps"],
        "eval_strategy": cfg["eval_strategy"],
        "save_strategy": cfg["save_strategy"],
        "save_total_limit": cfg["save_total_limit"],
        "load_best_model_at_end": cfg["load_best_model_at_end"],
        "metric_for_best_model": cfg["metric_for_best_model"],
        "greater_is_better": cfg["greater_is_better"],
        "report_to": [],
        "disable_tqdm": True,
        "fp16": torch.cuda.is_available(),
    }
    if max_steps is not None:
        training_args_kwargs["max_steps"] = max_steps
    else:
        training_args_kwargs["num_train_epochs"] = cfg["epochs"]

    training_args = Seq2SeqTrainingArguments(**training_args_kwargs)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
        tokenizer=tokenizer,
    )

    torch.serialization.add_safe_globals(
        [np._core.multiarray._reconstruct, np.ndarray, np.dtype, type(np.dtype(np.uint32))]
    )
    # Resume from checkpoint if one exists, otherwise start fresh
    checkpoint_dir = run_dir / "checkpoints"
    resume_checkpoint = checkpoint_dir if checkpoint_dir.exists() and any(checkpoint_dir.iterdir()) else None
    train_result = trainer.train(resume_from_checkpoint=resume_checkpoint)
    finite_loss = bool(train_result.training_loss == train_result.training_loss) and (
        train_result.training_loss not in (float("inf"), float("-inf"))
    )

    predictions = trainer.predict(val_ds, max_length=cfg["generation_max_length"], num_beams=cfg["generation_num_beams"])
    pred_ids = predictions.predictions
    pred_ids[pred_ids == -100] = tokenizer.pad_token_id
    hyps = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    refs = [ex.target for ex in val_examples]

    eval_result = chrf_evaluate(hyps, refs)

    metadata = build_run_metadata(
        language_pair=language_pair,
        tokenizer_name=tokenizer_name,
        seed=seed,
        model_identifier=model_resolution["requested_identifier"],
        model_revision=model_resolution.get("resolved_revision") or "n/a (from-scratch construction)",
        tokenizer_identifier=tokenizer_identifier,
        tokenizer_revision="n/a (local artifact, no git revision)",
        tokenizer_vocab_size=tokenizer_vocab_size,
        dataset_identifier=dataset_identifier,
        dataset_manifest_path=dataset_manifest_path,
        learning_rate=cfg["learning_rate"],
        batch_size=cfg["batch_size"],
        epochs=cfg["epochs"],
        max_source_length=cfg["max_source_length"],
        max_target_length=cfg["max_target_length"],
        optimizer=cfg["optimizer"],
        scheduler=cfg["lr_scheduler"],
        sacrebleu_version=eval_result.sacrebleu_version,
        chrf_signature=eval_result.chrf_signature,
        git_commit=cfgmod.git_commit(),
        extra={
            "model_resolution": model_resolution,
            "training_loss": train_result.training_loss,
            "finite_loss": finite_loss,
        },
    )

    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    validation_results = {
        "language_pair": language_pair,
        "tokenizer": tokenizer_name,
        "seed": seed,
        "split": "validation",
        **eval_result.to_dict(),
        "timestamp": utc_timestamp(),
    }
    (run_dir / "validation_results.json").write_text(json.dumps(validation_results, indent=2), encoding="utf-8")

    model.save_pretrained(run_dir / "model")
    tokenizer.save_pretrained(run_dir / "tokenizer_used")

    return {
        "run_dir": str(run_dir),
        "metadata": metadata,
        "validation_results": validation_results,
        "finite_loss": finite_loss,
    }


def write_embedding_adaptation_report_from_dict(report_dict: dict, run_dir: Path) -> Path:
    out_path = Path(run_dir) / "embedding_adaptation_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
    return out_path
