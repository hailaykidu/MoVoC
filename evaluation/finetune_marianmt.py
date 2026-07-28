"""
finetune_marianmt.py -- extrinsic evaluation: MarianMT fine-tuning.

Paper Sec 4.3. MarianMT (Junczys-Dowmunt et al., 2018) is fine-tuned on the
English-Amharic and English-Tigrinya parallel corpora released by Meta AI as
part of NLLB (Costa-Jussa et al., 2022), using the MoVoC vocabulary, and
compared against the BPE and WordPiece baselines.

Reported training configuration, kept in TRAINING_CONFIG below:

    3 epochs, batch size 8, max sequence length 128 tokens
    learning rate 1.44e-07, decayed throughout training
    transformers 4.51.3
    1 GPU, 6 CPU cores, 32 GB RAM, 24 h max runtime (Slurm)
    Conda-managed environment

This module builds the training arguments and dataset exactly as described.
Running it requires a GPU and the NLLB corpora; see scripts/submit_job.sh
for the Slurm wrapper.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TRAINING_CONFIG = {
    "model": "MarianMT",
    "num_train_epochs": 3,
    "per_device_train_batch_size": 8,
    "max_seq_length": 128,
    "learning_rate": 1.44e-07,
    "lr_scheduler_type": "linear",
    "transformers_version": "4.51.3",
    "fp16": False,
}

# Paper Sec 4.3 architecture. Every field here was verified against the
# reported run's config.json (checkpoint-524316) and matches exactly.
MODEL_CONFIG = {
    "encoder_layers": 6,
    "decoder_layers": 6,
    "encoder_attention_heads": 8,
    "decoder_attention_heads": 8,
    "d_model": 512,
    "encoder_ffn_dim": 2048,
    "decoder_ffn_dim": 2048,
    "activation_function": "swish",
    "share_encoder_decoder_embeddings": True,
    "static_position_embeddings": True,
    "vocab_size": 63050,
}

# Trained on English-Amharic and English-Tigrinya. Tigre is held out of
# training entirely and appears only at evaluation, to measure zero-shot
# transfer between Ge'ez-script languages.
TRAINING_PAIRS = ("en-am", "en-ti")
ZERO_SHOT_PAIRS = ("en-tig",)

# Evaluation data (paper Sec 5.1). Development and test sets are external,
# not carved out of the training corpus:
#
#   Amharic, Tigrinya -- directly supported by FLORES-200 (Goyal et al.,
#     2022); its dev and devtest sets are used for automatic evaluation.
#   Ge'ez, Tigre -- absent from FLORES-200 and from the NLLB fine-tuning
#     data, so evaluation falls back to OPUS.
#
# Final evaluation for all languages uses 100 OPUS sentence pairs
# (Tiedemann, 2012); see TEST_SETS below.
EVAL_BENCHMARK = {
    "amharic": "flores200",
    "tigrinya": "flores200",
    "tigre": "opus",
    "geez": "opus",
}

SEED = 42


def build_model_config(**overrides):
    """A MarianConfig matching the paper's reported architecture."""
    from transformers import MarianConfig

    cfg = dict(MODEL_CONFIG)
    cfg.update(overrides)
    return MarianConfig(**cfg)

SLURM_RESOURCES = {
    "gpus": 1,
    "cpus": 6,
    "mem_gb": 32,
    "max_runtime_hours": 24,
}


def build_training_arguments(output_dir: Path, **overrides):
    """Seq2SeqTrainingArguments matching the paper's reported configuration.

    Identical for every tokenizer strategy: same optimizer, learning-rate
    schedule, batch size, and epoch count.
    """
    from transformers import Seq2SeqTrainingArguments

    cfg = dict(TRAINING_CONFIG)
    cfg.update(overrides)
    return Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=cfg["num_train_epochs"],
        per_device_train_batch_size=cfg["per_device_train_batch_size"],
        learning_rate=cfg["learning_rate"],
        lr_scheduler_type=cfg["lr_scheduler_type"],
        fp16=cfg["fp16"],
        seed=SEED,
        data_seed=SEED,
        logging_steps=100,
        save_strategy="epoch",
        report_to=[],
    )


# Pretrained MarianMT checkpoint. The paper fine-tunes MarianMT rather than
# training it from scratch, and the reported learning rate (1.44e-07) is a
# fine-tuning rate: from a random initialisation it cannot converge in three
# epochs. The released checkpoint carries a 63,050-token Marian vocabulary
# and source.spm/target.spm. Every field of its config -- vocab_size 63,050,
# d_model 512, 6+6 layers, 8 heads, FFN 2048, Swish, static positional
# encodings, decoder_start_token_id 63049 -- matches
# Helsinki-NLP/opus-mt-en-ti exactly, which identifies it as the base.
BASE_MODEL = "Helsinki-NLP/opus-mt-en-ti"

# Sec 4.3 and Table 5 differ on vocabulary size, and Sec 4.3 is authoritative
# for the MT experiments. The released checkpoint uses Marian's own 63,050
# vocabulary, which keeps the pretrained embedding and output layers intact --
# consistent with the low initial training loss it reports. Substituting a
# 32,000-token vocabulary (Table 5's s_BPE) forces those matrices to be
# resized and reinitialised, which changes the optimization problem and the
# training dynamics entirely. Table 5 describes the intended tokenizer
# configuration rather than the released run.
#
# So `marian` is the default: it reproduces Sec 4.3. The three MoVoC
# strategies remain available for the tokenizer comparison, with the caveat
# above.
TOKENIZER_STRATEGIES = ("marian", "movoc_tok", "bpe", "wordpiece")
PRETRAINED_VOCAB_STRATEGY = "marian"


def load_tokenizer(strategy: str, language: str):
    """The one experimental variable: which tokenizer the model uses.

    All three strategies are wrapped as a PreTrainedTokenizerFast over the
    same vocabulary size, so the model architecture is unchanged between
    arms and only the segmentation differs.
    """
    from transformers import PreTrainedTokenizerFast
    from tokenizers import Tokenizer as HFTokenizer

    from movoc import io

    if strategy not in TOKENIZER_STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; "
                         f"expected one of {TOKENIZER_STRATEGIES}")

    if strategy == PRETRAINED_VOCAB_STRATEGY:
        # Sec 4.3: Marian's own 63,050-token vocabulary, left untouched so
        # the pretrained embedding and output layers are preserved.
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(BASE_MODEL)

    if strategy == "movoc_tok":
        # MoVoC-Tok: the constrained merge table from Algorithm 1, Step 6,
        # over the hybrid vocabulary V_MoVoC.
        path = io.MODELS / f"movoc_tok_{language}.json"
        if not path.exists():
            raise SystemExit(
                f"no MoVoC-Tok tokenizer at {path}; run train.py first")
        tok = HFTokenizer.from_file(str(path))
    else:
        path = io.VOCABULARY / f"{strategy}_{language}.json"
        if not path.exists():
            raise SystemExit(f"no {strategy} tokenizer at {path}")
        tok = HFTokenizer.from_file(str(path))

    return PreTrainedTokenizerFast(
        tokenizer_object=tok,
        unk_token="<unk>", bos_token="<s>", eos_token="</s>",
        pad_token="<pad>", mask_token="<mask>",
    )


def align_special_tokens(model, tokenizer):
    """Point every special-token id at the *new* vocabulary after resizing.

    Swapping the tokenizer changes what every id means. `resize_token
    _embeddings` grows or shrinks the embedding matrix but does not touch
    `config` or `generation_config`, so any id inherited from the base
    checkpoint still refers to the base vocabulary and is now either wrong
    or out of range.

    Missing one of these does not fail loudly at training time. It surfaces
    much later, at generation, and the failure mode differs per field:

      pad / eos / decoder_start   wrong id -> decoding starts from or stops
                                  on the wrong token; training "succeeds"
                                  and the model produces garbage.

      bad_words_ids               inherited [[63049]] is the *base* model's
                                  pad id. Against a 32k BPE vocabulary that
                                  id does not exist and generate() raises
                                  "The model vocabulary size is 32000, but
                                  the following tokens were being biased:
                                  [63049]". Against the 143,963-token MoVoC
                                  vocabulary it exists but denotes an
                                  unrelated token, which is then silently
                                  suppressed for the whole run.

      forced_eos_token_id         inherited 0 while the new tokenizer's eos
                                  is 2 -> the model is forced to emit the
                                  wrong token at max_length.

    An earlier evaluation run was invalidated by exactly this: the BPE and
    WordPiece arms crashed, and MoVoC-Tok scored ~0.01 BLEU while decoding
    from the wrong start id with an arbitrary token suppressed. Those
    numbers measured the misconfiguration, not the tokenizers.

    Everything vocabulary-dependent is therefore reset here in one place,
    and ids that have no equivalent under the new vocabulary are cleared
    rather than left pointing at a stale value.
    """
    pad, eos = tokenizer.pad_token_id, tokenizer.eos_token_id

    for cfg in (model.config, model.generation_config):
        cfg.pad_token_id = pad
        cfg.eos_token_id = eos
        # Marian starts decoding from pad, not bos.
        cfg.decoder_start_token_id = pad
        cfg.forced_eos_token_id = eos
        # Carries base-vocabulary ids with no meaning under the new one.
        cfg.bad_words_ids = None

    vocab_size = model.get_input_embeddings().weight.shape[0]
    model.config.vocab_size = vocab_size

    # Cheap assertion, but it is the one that would have caught the run
    # described above before 40 GPU-hours were spent on it.
    for name, value in (("pad_token_id", pad), ("eos_token_id", eos),
                        ("decoder_start_token_id", pad),
                        ("forced_eos_token_id", eos)):
        if value is None or not (0 <= value < vocab_size):
            raise ValueError(
                f"{name}={value} is not a valid id for a {vocab_size}-token "
                f"vocabulary. The tokenizer and model are out of sync; "
                f"fine-tuning would produce a checkpoint that cannot "
                f"generate.")

    print(f"  special tokens: pad={pad} eos={eos} "
          f"decoder_start={pad} vocab={vocab_size} bad_words=cleared")


def load_eval_set(source: Path, reference: Path):
    """Read an external evaluation set (FLORES-200 or OPUS).

    Evaluation data never comes from the training corpus: Amharic and
    Tigrinya are scored on FLORES-200 dev/devtest, and the final evaluation
    for every language uses 100 OPUS sentence pairs.
    """
    src = [l.rstrip("\n") for l in open(source, encoding="utf-8")]
    ref = [l.rstrip("\n") for l in open(reference, encoding="utf-8")]
    if len(src) != len(ref):
        raise SystemExit(f"eval set mismatch: {len(src)} vs {len(ref)}")
    return src, ref


def main():
    p = argparse.ArgumentParser(
        description="Fine-tune MarianMT under one tokenizer strategy (Table 3)")
    p.add_argument("--strategy", required=True, choices=TOKENIZER_STRATEGIES,
                   help="the only experimental variable")
    p.add_argument("--language", required=True, choices=("amharic", "tigrinya"),
                   help="which language's tokenizer to use")
    p.add_argument("--source", type=Path, required=True, help="English side")
    p.add_argument("--target", type=Path, required=True, help="am/ti side")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--valid-source", type=Path, default=None,
                   help="FLORES-200 dev source (Amharic/Tigrinya)")
    p.add_argument("--valid-reference", type=Path, default=None,
                   help="FLORES-200 dev reference")
    p.add_argument("--base-model", default=BASE_MODEL,
                   help="pretrained MarianMT checkpoint to fine-tune")
    p.add_argument("--max-samples", type=int, default=None)
    args = p.parse_args()

    from datasets import Dataset
    from transformers import (AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq,
                              MarianMTModel, Seq2SeqTrainer)

    src = [l.rstrip("\n") for l in open(args.source, encoding="utf-8")]
    tgt = [l.rstrip("\n") for l in open(args.target, encoding="utf-8")]
    if len(src) != len(tgt):
        raise SystemExit(f"corpora differ in length: {len(src)} vs {len(tgt)}")
    if args.max_samples:
        src, tgt = src[:args.max_samples], tgt[:args.max_samples]

    # --- the only variable ---
    tokenizer = load_tokenizer(args.strategy, args.language)

    # --- everything below is identical across strategies ---
    # Fine-tune the pretrained MarianMT model (Sec 4.3). The embedding matrix
    # is resized to the tokenizer's vocabulary -- that resizing is the whole
    # point of the comparison, since the tokenizer is the variable under test.
    model = MarianMTModel.from_pretrained(args.base_model)
    if args.strategy != PRETRAINED_VOCAB_STRATEGY:
        # Only the MoVoC strategies need resizing; see the note on
        # TOKENIZER_STRATEGIES for what that costs.
        model.resize_token_embeddings(len(tokenizer))
    align_special_tokens(model, tokenizer)

    max_len = TRAINING_CONFIG["max_seq_length"]

    def encode(batch):
        return tokenizer(batch["src"], text_target=batch["tgt"],
                         max_length=max_len, truncation=True)

    # The whole parallel corpus is training data; evaluation sets are
    # external (FLORES-200 dev/devtest, OPUS), never carved out of it.
    train_ds = Dataset.from_dict({"src": src, "tgt": tgt}).map(
        encode, batched=True, remove_columns=["src", "tgt"])

    eval_ds = None
    if args.valid_source and args.valid_reference:
        v_src, v_ref = load_eval_set(args.valid_source, args.valid_reference)
        eval_ds = Dataset.from_dict({"src": v_src, "tgt": v_ref}).map(
            encode, batched=True, remove_columns=["src", "tgt"])

    print(f"strategy={args.strategy} language={args.language} "
          f"vocab={len(tokenizer)}")
    print(f"  train      {len(train_ds)}")
    print(f"  validation {len(eval_ds) if eval_ds is not None else 0} "
          f"({EVAL_BENCHMARK.get(args.language, 'external')})")

    trainer = Seq2SeqTrainer(
        model=model,
        args=build_training_arguments(args.output_dir),
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )
    result = trainer.train()
    trainer.save_model()
    tokenizer.save_pretrained(str(args.output_dir))

    print(result)


if __name__ == "__main__":
    main()
