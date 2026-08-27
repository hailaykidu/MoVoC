"""Intrinsic tokenizer evaluation: boundary precision, MorphScore, Rényi entropy.

Scores BPE, WordPiece and MoVoC-Tok on gold morpheme test sets, comparing the
character offsets where each tokenizer splits a word against the offsets the
gold annotation implies.

Metrics
-------
**Morpheme boundary precision** -- of all internal boundaries a tokenizer
produces, the fraction that coincide with a gold morpheme boundary. Word start
and end are not boundaries. Counted over all evaluated words.

**MorphScore** (Arnett & Bergen, 2025) -- recall of gold morpheme boundaries
among the words the tokenizer actually segmented. Words left unsegmented are
excluded entirely rather than scored as zero, and extra boundaries are not
penalised, which is what makes the measure recall-oriented.

The denominator is the count of *gold* boundaries, not predicted ones. Dividing
by predicted boundaries instead would make MorphScore algebraically identical
to boundary precision, since unsegmented words contribute nothing to either
sum -- the two metrics would then always agree, which is not the intent.

**Rényi entropy** at α=2 over the token distribution the tokenizer produces on
the evaluation corpus: ``H = 1/(1-α) · log(Σ p_i^α)``.

Every tokenizer is scored on an identical word list, verified before scoring.
No tokenizer is retrained; trained artifacts are loaded as they are.

This is the script that produced the Table 2 (MorphScore) and Table 4
(boundary precision, Rényi entropy) authoritative results in v2/table2/ and
v2/table4/. It was migrated into this repository from a separate project
(amseg) where those tables were originally generated. Running it end to end
from a fresh clone of this repository now works out of the box:

- gold morpheme test sets at ``evaluation/data/{amharic,tigrinya,tigre,geez}_gold.tsv``
  (tab-separated word / morpheme-boundary format; see load_testset() below) --
  these are not the same files as data/annotations/*/*.json in this
  repository, which use a different schema for a different purpose
  (vocabulary construction, not this evaluation)
- trained tokenizer artifacts at ``tokenizers/{bpe_32k,wordpiece_32k,
  amharic_movoc_tok_32k,tigrinya_movoc_tok_32k}/`` (HuggingFace-format for
  BPE/WordPiece, MoVoCTokBPE-format for MoVoC-Tok). bpe_32k and wordpiece_32k
  are trained on a combined corpus shared across languages, not per-language
  text -- this is the exact configuration behind the published Table 2/4
  numbers; it is not the same as the per-language amharic_bpe_32k /
  tigrinya_bpe_32k artifacts that also exist in this project's history.

Re-running ``python scripts/evaluate_intrinsic.py --datadir evaluation/data
--outdir /tmp/out --tokenizers tokenizers`` from this repository reproduces
v2/table2 and v2/table4 exactly (verified byte-for-byte against
amseg/evaluation/results/intrinsic_tokenizer_table.md at migration time).

Usage:
    python scripts/evaluate_intrinsic.py --outdir evaluation/results
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

WORD_START = "▁"
CONTINUING = "##"


class MissingArtifact(SystemExit):
    """Raised, loudly, when a required file is absent."""


def require(path: Path, what: str) -> Path:
    if not path.exists():
        raise MissingArtifact(
            f"MISSING REQUIRED ARTIFACT: {what}\n  expected at: {path}\n"
            "  Evaluation stopped. No substitute dataset was used."
        )
    return path


# --- tokenizer adapters -------------------------------------------------
# Each exposes segment(word) -> list[str] of surface pieces, so boundary
# extraction is identical across tokenizers.


class HFTokenizer:
    """BPE / WordPiece trained with huggingface/tokenizers."""

    def __init__(self, path: Path, name: str) -> None:
        from tokenizers import Tokenizer

        require(path / "tokenizer.json", f"{name} tokenizer")
        self.tok = Tokenizer.from_file(str(path / "tokenizer.json"))
        self.path = path
        self.name = name
        self.vocab_size = self.tok.get_vocab_size()

    def segment(self, word: str) -> list[str]:
        pieces = self.tok.encode(word).tokens
        # Strip the marker characters so pieces are surface substrings.
        out = []
        for piece in pieces:
            text = piece
            if text.startswith(WORD_START):
                text = text[len(WORD_START):]
            if text.startswith(CONTINUING):
                text = text[len(CONTINUING):]
            if text:
                out.append(text)
        return out


class MoVoCTokenizer:
    """Morpheme-aware constrained BPE, loaded from its learned merges.

    Evaluated without boundary constraints supplied at encoding time: the gold
    boundaries are what is being measured, so feeding them to the tokenizer
    would make the metric circular.
    """

    def __init__(self, path: Path, name: str) -> None:
        from verify_movoc_tok import MoVoCTokBPE

        require(path / "tokenizer.model", f"{name} tokenizer")
        self.tok = MoVoCTokBPE(path)
        self.path = path
        self.name = name
        self.vocab_size = len(self.tok.vocab)

    def segment(self, word: str) -> list[str]:
        pieces = self.tok.encode_word(word)
        out = []
        for piece in pieces:
            text = piece[len(WORD_START):] if piece.startswith(WORD_START) else piece
            if text:
                out.append(text)
        return out


# --- boundary arithmetic ------------------------------------------------


def boundaries(pieces: list[str]) -> set[int]:
    """Internal character offsets where a segmentation splits.

    Word start (0) and end are excluded by construction: only the cumulative
    offsets between consecutive pieces are recorded.
    """
    offsets: set[int] = set()
    cursor = 0
    for piece in pieces[:-1]:
        cursor += len(piece)
        offsets.add(cursor)
    return offsets


def normalized_renyi_entropy(counts: Counter, alpha: float = 2.0) -> float:
    """Rényi entropy divided by log(support), giving a value in [0, 1].

    Table 4 of the paper reports Rényi entropy on this normalized scale
    (0.39-0.49 at alpha=2), not in raw nats: log(support) is the entropy of a
    uniform distribution over the tokens actually used, so the ratio measures
    how far the tokenizer is from spreading its mass evenly. Lower means mass
    concentrated on fewer, more consistent subwords.
    """
    support = len(counts)
    if support <= 1:
        return 0.0
    return renyi_entropy(counts, alpha) / math.log(support)


def renyi_entropy(counts: Counter, alpha: float = 2.0) -> float:
    """Rényi entropy of a token distribution, in nats."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    if alpha == 1.0:
        return -sum(
            (c / total) * math.log(c / total) for c in counts.values() if c
        )
    power_sum = sum((c / total) ** alpha for c in counts.values())
    if power_sum <= 0:
        return 0.0
    return (1.0 / (1.0 - alpha)) * math.log(power_sum)


def load_testset(path: Path) -> list[tuple[str, list[str]]]:
    rows: list[tuple[str, list[str]]] = []
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        if "\t" not in line:
            raise MissingArtifact(
                f"INVALID EVALUATION DATA: {path}:{lineno} has no tab separator"
            )
        word, morphs = line.split("\t", 1)
        parts = [p for p in morphs.split("+") if p]
        if len(parts) < 2:
            raise MissingArtifact(
                f"INVALID EVALUATION DATA: {path}:{lineno} states no boundary"
            )
        rows.append((word, parts))
    if not rows:
        raise MissingArtifact(f"EMPTY EVALUATION DATA: {path}")
    return rows


def evaluate(tokenizer, rows: list[tuple[str, list[str]]]) -> dict:
    matched = predicted = 0
    # MorphScore accumulators: gold boundaries recovered, over gold boundaries
    # present, counted only on words the tokenizer segmented.
    morph_gold = morph_hit = 0
    unsegmented = 0
    token_counts: Counter = Counter()

    for word, morphemes in rows:
        gold = boundaries(morphemes)
        pieces = tokenizer.segment(word)
        token_counts.update(pieces)
        pred = boundaries(pieces)

        predicted += len(pred)
        matched += len(pred & gold)

        if not pred:
            # No internal boundary: excluded from MorphScore per the paper,
            # rather than scored as zero.
            unsegmented += 1
            continue
        morph_gold += len(gold)
        morph_hit += len(gold & pred)

    return {
        "num_words": len(rows),
        "boundary_precision": round(matched / predicted, 6) if predicted else 0.0,
        "predicted_boundaries": predicted,
        "matched_boundaries": matched,
        "morphscore": round(morph_hit / morph_gold, 6) if morph_gold else 0.0,
        "morphscore_gold_boundaries_evaluated": morph_gold,
        "morphscore_gold_boundaries_recovered": morph_hit,
        "excluded_unsegmented_words": unsegmented,
        "boundary_precision_pct": round(
            100 * matched / predicted, 2
        ) if predicted else 0.0,
        "renyi_alpha_2": round(renyi_entropy(token_counts, 2.0), 6),
        "renyi_alpha_2_normalized": round(
            normalized_renyi_entropy(token_counts, 2.0), 4
        ),
        "unique_tokens": len(token_counts),
        "total_tokens": sum(token_counts.values()),
        "tokenizer_path": str(tokenizer.path.resolve()),
        "vocab_size": tokenizer.vocab_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datadir", type=Path, default=Path("evaluation/data"))
    parser.add_argument("--outdir", type=Path, default=Path("evaluation/results"))
    parser.add_argument("--tokenizers", type=Path, default=Path("tokenizers"))
    args = parser.parse_args()

    require(args.datadir / "manifest.json", "evaluation data manifest")
    manifest = json.loads((args.datadir / "manifest.json").read_text(encoding="utf-8"))

    # Which MoVoC-Tok model is applied to each language, and whether that
    # constitutes in-language or cross-lingual evaluation.
    #
    # Tigre and Ge'ez were excluded from MoVoC-Tok training because no
    # independent training morpheme resources were available -- their manual
    # annotations are reserved exclusively for intrinsic evaluation. They are
    # therefore scored with the Tigrinya model, which makes their MoVoC-Tok
    # numbers a cross-lingual generalization result, not language-specific
    # training. Tigrinya is the nearest trained relative: Tigre and Tigrinya
    # are both Ethio-Semitic and Ge'ez is their shared ancestor.
    movoc_models = {
        "amharic": (args.tokenizers / "amharic_movoc_tok_32k", "in-language"),
        "tigrinya": (args.tokenizers / "tigrinya_movoc_tok_32k", "in-language"),
        "tigre": (args.tokenizers / "tigrinya_movoc_tok_32k", "cross-lingual"),
        "geez": (args.tokenizers / "tigrinya_movoc_tok_32k", "cross-lingual"),
    }

    results: dict[str, dict] = {}
    reproducibility: dict[str, object] = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "random_seed": None,
        "seed_note": (
            "Not applicable: every tokenizer is deterministic and evaluation "
            "performs no sampling."
        ),
        "languages": {},
    }

    for language in ("amharic", "tigrinya", "tigre", "geez"):
        testset = args.datadir / f"{language}_gold.tsv"
        if not testset.exists():
            raise MissingArtifact(
                f"MISSING REQUIRED ARTIFACT: gold test set for {language}\n"
                f"  expected at: {testset}"
            )
        rows = load_testset(testset)
        words = [w for w, _ in rows]

        tokenizers_to_run: list = [
            HFTokenizer(args.tokenizers / "bpe_32k", "BPE"),
            HFTokenizer(args.tokenizers / "wordpiece_32k", "WordPiece"),
        ]
        movoc_path, movoc_mode = movoc_models[language]
        tokenizers_to_run.append(MoVoCTokenizer(movoc_path, "MoVoC-Tok"))

        results[language] = {}
        for tokenizer in tokenizers_to_run:
            scored = evaluate(tokenizer, rows)
            # Validation: identical word list for every tokenizer.
            assert scored["num_words"] == len(words), "word list mismatch"
            if tokenizer.name == "MoVoC-Tok":
                scored["evaluation_mode"] = movoc_mode
                scored["trained_on_this_language"] = movoc_mode == "in-language"
            results[language][tokenizer.name] = scored

        reproducibility["languages"][language] = {
            "test_set": str(testset.resolve()),
            "num_words": len(rows),
            "unique_words": len(set(words)),
            "excluded_placeholder_only": manifest[language][
                "excluded_placeholder_only"
            ],
            "excluded_single_morpheme": manifest[language][
                "excluded_single_morpheme"
            ],
            "excluded_unaligned_to_surface": manifest[language][
                "excluded_unaligned_to_surface"
            ],
            "tokenizers_evaluated": [t.name for t in tokenizers_to_run],
            "movoc_tok_model": str(movoc_path.resolve()),
            "movoc_tok_evaluation_mode": movoc_mode,
            "sources": manifest[language]["sources"],
        }
        print(
            f"{language}: {len(rows):,} words, "
            f"{len([t for t in tokenizers_to_run])} tokenizers"
        )

    args.outdir.mkdir(parents=True, exist_ok=True)
    payload = {"results": results, "reproducibility": reproducibility}
    (args.outdir / "intrinsic_tokenizer_evaluation.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    def rows_for(languages: list[str]) -> list[str]:
        out = []
        for language in languages:
            for name, scores in results[language].items():
                mode = scores.get("evaluation_mode", "")
                label = f"{name}*" if mode == "cross-lingual" else name
                out.append(
                    f"| {language.capitalize()} | {label} | "
                    f"{scores['boundary_precision']:.4f} | "
                    f"{scores['morphscore']:.4f} | "
                    f"{scores['renyi_alpha_2']:.4f} |"
                )
        return out

    header = [
        "| Language | Tokenizer | Boundary Precision | MorphScore | Rényi α=2 |",
        "|----------|-----------|-------------------|------------|-----------|",
    ]

    lines = [
        "# Intrinsic tokenizer evaluation",
        "",
        "## In-language MoVoC-Tok evaluation",
        "",
        "MoVoC-Tok was trained on these languages' own morpheme resources.",
        "",
        *header,
        *rows_for(["amharic", "tigrinya"]),
        "",
        "## Cross-lingual MoVoC-Tok evaluation",
        "",
        "Tigre and Ge'ez were excluded from MoVoC-Tok training because no",
        "independent training morpheme resources were available. Their manual",
        "annotations were reserved exclusively for intrinsic evaluation.",
        "MoVoC-Tok results for these languages (marked `*`) are a cross-lingual",
        "generalization measurement and do not represent language-specific",
        "training.",
        "",
        *header,
        *rows_for(["tigre", "geez"]),
        "",
    ]
    (args.outdir / "intrinsic_tokenizer_table.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(f"\nwrote {args.outdir}/intrinsic_tokenizer_evaluation.json")
    print(f"wrote {args.outdir}/intrinsic_tokenizer_table.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
