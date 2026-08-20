"""Read-only loading and verification of the pre-trained tokenizer
artifacts. Never trains, resizes, truncates, merges, or otherwise mutates a
tokenizer. All functions here either load-and-inspect or raise.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer, PreTrainedTokenizerBase

# Sample sentences used for live tokenization checks in the manifest.
# Deliberately short, script-diverse, and includes English + Ge'ez-script
# Tigrinya/Amharic so fertility/UNK behavior is directly observable.
SAMPLE_ENGLISH = "The quick brown fox jumps over the lazy dog near the river."
SAMPLE_TIGRINYA = "ሰላም ንኹልኹም! ኣብዚ ሃገር ብዙሕ ህዝቢ ኣሎ።"
SAMPLE_AMHARIC = "ሰላም ለሁሉም! በዚህ ሀገር ብዙ ሰዎች አሉ።"


class TokenizerVerificationError(RuntimeError):
    """Raised when a tokenizer artifact fails a required integrity check.
    This must stop the pipeline -- never caught-and-ignored by callers that
    need a verified tokenizer."""


@dataclass
class TokenizerReport:
    name: str
    language_pair: str
    path: str
    tokenizer_class: str
    vocab_size_len: int  # len(tokenizer)
    vocab_size_get_vocab: int  # len(tokenizer.get_vocab())
    declared_vocab_size: int
    special_tokens: dict[str, Any]
    special_token_ids: dict[str, int | None]
    cross_lingual_reuse: bool = False
    warning: str | None = None
    sample_tokenizations: dict[str, dict[str, Any]] = field(default_factory=dict)
    amharic_fertility: float | None = None
    amharic_unk_rate: float | None = None
    passed: bool = True
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "language_pair": self.language_pair,
            "path": self.path,
            "tokenizer_class": self.tokenizer_class,
            "vocab_size_len": self.vocab_size_len,
            "vocab_size_get_vocab": self.vocab_size_get_vocab,
            "declared_vocab_size": self.declared_vocab_size,
            "special_tokens": self.special_tokens,
            "special_token_ids": self.special_token_ids,
            "cross_lingual_reuse": self.cross_lingual_reuse,
            "warning": self.warning,
            "sample_tokenizations": self.sample_tokenizations,
            "amharic_fertility": self.amharic_fertility,
            "amharic_unk_rate": self.amharic_unk_rate,
            "passed": self.passed,
            "issues": self.issues,
        }


def load_tokenizer(path: str | Path) -> PreTrainedTokenizerBase:
    """Load a tokenizer strictly read-only from an absolute local path.
    Never downloads, never trains. Raises TokenizerVerificationError with a
    clear message if the path is missing or the artifact cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise TokenizerVerificationError(f"Tokenizer path does not exist: {path}")
    try:
        tok = AutoTokenizer.from_pretrained(str(path))
    except Exception as exc:  # noqa: BLE001 - re-raise with context
        raise TokenizerVerificationError(
            f"Failed to load tokenizer from {path}: {exc!r}"
        ) from exc
    return tok


def _fertility_and_unk(tok: PreTrainedTokenizerBase, text: str) -> tuple[float, float]:
    """fertility = tokens / whitespace-words; unk_rate = fraction of tokens
    that are the unk token."""
    words = text.split()
    ids = tok.encode(text, add_special_tokens=False)
    n_tokens = max(len(ids), 1)
    unk_id = tok.unk_token_id
    n_unk = sum(1 for i in ids if unk_id is not None and i == unk_id)
    fertility = n_tokens / max(len(words), 1)
    unk_rate = n_unk / n_tokens
    return fertility, unk_rate


def verify_tokenizer(
    name: str,
    language_pair: str,
    path: str | Path,
    declared_vocab_size: int,
    cross_lingual_reuse: bool = False,
    warning: str | None = None,
) -> TokenizerReport:
    """Load a tokenizer and run the required integrity checks (spec
    section 2): type, vocab size, special tokens + IDs, config, sample
    tokenization on English/Tigrinya/Amharic. Does NOT raise on the
    cross-lingual-reuse warning case -- that is expected and must not block
    the pipeline. Raises TokenizerVerificationError only on genuine
    integrity failures (unreadable artifact, vocab size mismatch beyond
    tolerance, special-token IDs colliding/out of range).
    """
    tok = load_tokenizer(path)
    issues: list[str] = []

    vocab_size_len = len(tok)
    vocab_size_get_vocab = len(tok.get_vocab())

    # HF tokenizers commonly report len(tok) == declared vocab size exactly,
    # but some SentencePiece-based exports can differ by the count of added
    # special tokens. Allow a small, explicitly-tolerated delta and record
    # any mismatch as an issue rather than silently ignoring it.
    if abs(vocab_size_len - declared_vocab_size) > 8:
        issues.append(
            f"len(tokenizer)={vocab_size_len} differs from declared_vocab_size="
            f"{declared_vocab_size} by more than tolerance (8)."
        )

    special_tokens = {
        "pad_token": tok.pad_token,
        "unk_token": tok.unk_token,
        "bos_token": getattr(tok, "bos_token", None),
        "eos_token": tok.eos_token,
    }
    special_token_ids = {
        "pad_token_id": tok.pad_token_id,
        "unk_token_id": tok.unk_token_id,
        "bos_token_id": getattr(tok, "bos_token_id", None),
        "eos_token_id": tok.eos_token_id,
    }

    # Special token IDs must be within [0, vocab_size) and must not silently
    # collide with each other (collision between e.g. pad and unk would be
    # a real integrity bug, not a normal design choice).
    present_ids = {k: v for k, v in special_token_ids.items() if v is not None}
    for key, tid in present_ids.items():
        if tid < 0 or tid >= vocab_size_len:
            issues.append(
                f"{key}={tid} is out of range for vocab size {vocab_size_len}."
            )
    seen: dict[int, str] = {}
    for key, tid in present_ids.items():
        if tid in seen:
            issues.append(
                f"Special token ID collision: {key} and {seen[tid]} both map to id {tid}."
            )
        else:
            seen[tid] = key

    sample_tokenizations: dict[str, dict[str, Any]] = {}
    for label, text in (
        ("english", SAMPLE_ENGLISH),
        ("tigrinya", SAMPLE_TIGRINYA),
        ("amharic", SAMPLE_AMHARIC),
    ):
        ids = tok.encode(text, add_special_tokens=False)
        tokens = tok.convert_ids_to_tokens(ids)
        fertility, unk_rate = _fertility_and_unk(tok, text)
        sample_tokenizations[label] = {
            "text": text,
            "num_tokens": len(ids),
            "num_whitespace_words": len(text.split()),
            "fertility": round(fertility, 4),
            "unk_rate": round(unk_rate, 4),
            "tokens_preview": tokens[:24],
        }

    amharic_fertility = sample_tokenizations["amharic"]["fertility"]
    amharic_unk_rate = sample_tokenizations["amharic"]["unk_rate"]

    if cross_lingual_reuse:
        print(
            f"[verify_tokenizers] WARNING ({name}/{language_pair}): {warning} "
            f"Amharic sample fertility={amharic_fertility:.4f} tokens/word, "
            f"UNK rate={amharic_unk_rate:.4f}. This is an accepted, documented "
            "tradeoff and does NOT fail verification."
        )

    passed = len(issues) == 0
    if not passed:
        raise TokenizerVerificationError(
            f"Tokenizer '{name}' ({language_pair}) failed verification: {'; '.join(issues)}"
        )

    return TokenizerReport(
        name=name,
        language_pair=language_pair,
        path=str(path),
        tokenizer_class=type(tok).__name__,
        vocab_size_len=vocab_size_len,
        vocab_size_get_vocab=vocab_size_get_vocab,
        declared_vocab_size=declared_vocab_size,
        special_tokens=special_tokens,
        special_token_ids=special_token_ids,
        cross_lingual_reuse=cross_lingual_reuse,
        warning=warning,
        sample_tokenizations=sample_tokenizations,
        amharic_fertility=amharic_fertility,
        amharic_unk_rate=amharic_unk_rate,
        passed=passed,
        issues=issues,
    )
