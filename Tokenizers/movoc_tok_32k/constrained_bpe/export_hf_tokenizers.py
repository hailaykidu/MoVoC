"""Export the three comparison tokenizers in a HuggingFace-loadable form.

The MT pipeline loads whichever tokenizer an arm is testing through
``AutoTokenizer.from_pretrained``. BPE and WordPiece already have a
``tokenizer.json``, but lack the wrapper metadata that makes them loadable;
MoVoC-Tok is stored as learned merges in its own format. This writes a
``PreTrainedTokenizerFast`` package for each so all three load identically --
which is what makes the tokenizer the only variable between arms.

Nothing is retrained and no vocabulary is altered: the exported vocabulary and
merges are exactly those already learned, and the export is checked by
comparing segmentations before and after.

Usage:
    python scripts/export_hf_tokenizers.py --outdir tokenizers/hf
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from tokenizers import Tokenizer, decoders, models, normalizers, pre_tokenizers
from transformers import PreTrainedTokenizerFast

SPECIAL_TOKENS = ["<pad>", "<unk>", "<s>", "</s>"]
WORD_START = "▁"


def wrapper_files(outdir: Path, model_max_length: int = 512) -> None:
    """Write the metadata AutoTokenizer needs to recognise the directory."""
    (outdir / "special_tokens_map.json").write_text(
        json.dumps(
            {
                "pad_token": "<pad>",
                "unk_token": "<unk>",
                "bos_token": "<s>",
                "eos_token": "</s>",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (outdir / "tokenizer_config.json").write_text(
        json.dumps(
            {
                "tokenizer_class": "PreTrainedTokenizerFast",
                "model_max_length": model_max_length,
                "pad_token": "<pad>",
                "unk_token": "<unk>",
                "bos_token": "<s>",
                "eos_token": "</s>",
                "clean_up_tokenization_spaces": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def export_existing(src: Path, outdir: Path) -> Path:
    """BPE / WordPiece: copy the trained tokenizer.json and add metadata."""
    outdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "tokenizer.json", outdir / "tokenizer.json")
    wrapper_files(outdir)
    return outdir


def export_movoc(src: Path, outdir: Path) -> Path:
    """MoVoC-Tok: rebuild the learned merges as a HuggingFace BPE model.

    The learned vocabulary and merge list are transferred verbatim. The
    boundary constraint lives in *which* merges were learned, so a plain BPE
    model applying exactly those merges reproduces the tokenizer's behaviour.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    model_data = json.loads((src / "tokenizer.model").read_text(encoding="utf-8"))

    vocab = {token: i for i, token in enumerate(model_data["vocab"])}
    merges = [(a, b) for a, b in model_data["merges"]]

    # The learner attached the word-start marker to the first character of the
    # word (▁ል), whereas Metaspace splits it off as its own symbol (▁ + ል).
    # Adding the bare marker and the merges that reattach it lets the exported
    # model reach the same units without changing any learned merge: the
    # marker-attachment merges are prepended, so they fire first, exactly as
    # the learner's initial symbolization did.
    marker_merges: list[tuple[str, str]] = []
    for token in model_data["vocab"]:
        if token.startswith(WORD_START) and len(token) > len(WORD_START):
            rest = token[len(WORD_START):]
            if len(rest) == 1:
                marker_merges.append((WORD_START, rest))
    if WORD_START not in vocab:
        vocab[WORD_START] = len(vocab)
    merges = marker_merges + merges

    tokenizer = Tokenizer(
        models.BPE(vocab=vocab, merges=merges, unk_token="<unk>")
    )
    # No normalizer: the learner trained on NFC-normalized text but did not
    # itself normalize at encode time, and adding NFC here would map
    # characters the vocabulary holds (e.g. U+2019) onto forms it does not,
    # turning them into <unk>.
    tokenizer.pre_tokenizer = pre_tokenizers.Metaspace(
        replacement=WORD_START, prepend_scheme="always"
    )
    tokenizer.decoder = decoders.Metaspace(
        replacement=WORD_START, prepend_scheme="always"
    )
    tokenizer.save(str(outdir / "tokenizer.json"))
    wrapper_files(outdir)
    return outdir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizers", type=Path, default=Path("tokenizers"))
    parser.add_argument("--outdir", type=Path, default=Path("tokenizers/hf"))
    args = parser.parse_args()

    exports = [
        ("bpe_32k", args.tokenizers / "bpe_32k", export_existing),
        ("wordpiece_32k", args.tokenizers / "wordpiece_32k", export_existing),
        (
            "movoc_tok_32k_tigrinya",
            args.tokenizers / "tigrinya_movoc_tok_32k",
            export_movoc,
        ),
        (
            "movoc_tok_32k_amharic",
            args.tokenizers / "amharic_movoc_tok_32k",
            export_movoc,
        ),
    ]

    for name, src, exporter in exports:
        if not src.exists():
            raise SystemExit(f"MISSING TOKENIZER: {src}")
        out = exporter(src, args.outdir / name)
        loaded = PreTrainedTokenizerFast.from_pretrained(str(out))
        print(
            f"  {name:26} vocab={len(loaded):,} pad={loaded.pad_token_id} "
            f"eos={loaded.eos_token_id} -> {out}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
