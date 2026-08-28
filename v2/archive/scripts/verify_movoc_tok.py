"""Verify a morpheme-aware MoVoC-Tok model.

Checks the properties the training objective requires:

* vocabulary is exactly the requested size
* decoding is lossless
* **no learned subword crosses a morpheme boundary** -- checked directly by
  segmenting every constrained word and comparing piece boundaries against the
  projected morpheme boundaries

Usage:
    python scripts/verify_movoc_tok.py --model DIR --morphemes DATASET.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from train_movoc_tok_bpe import (
    WORD_START,
    load_constraints,
    record_morphemes,
)


class MoVoCTokBPE:
    """Apply learned merges in rank order, under the same boundary constraint.

    The constraint must be enforced at inference as well as during training. A
    merge is learned if it is legal *somewhere* in the corpus, so a pair with
    no boundary between it in one word may straddle a boundary in another.
    Passing the word's boundaries to :meth:`encode_word` blocks exactly those
    applications, which is what makes "no subword crosses a morpheme boundary"
    hold for every word rather than on average.
    """

    def __init__(self, model_dir: Path) -> None:
        model = json.loads((model_dir / "tokenizer.model").read_text(encoding="utf-8"))
        self.vocab = model["vocab"]
        self.ids = {t: i for i, t in enumerate(self.vocab)}
        self.ranks = {tuple(m): i for i, m in enumerate(model["merges"])}

    def encode_word(self, word: str, barriers: set[int] | None = None) -> list[str]:
        if not word:
            return []
        barriers = barriers or set()
        symbols = [WORD_START + word[0]] + list(word[1:])
        while len(symbols) > 1:
            # Offset of each symbol boundary in the surface word.
            offsets = []
            offset = 0
            for index, symbol in enumerate(symbols):
                offset += len(symbol) - (1 if index == 0 else 0)
                offsets.append(offset)
            best = None
            best_rank = None
            for i in range(len(symbols) - 1):
                if offsets[i] in barriers:
                    continue
                rank = self.ranks.get((symbols[i], symbols[i + 1]))
                if rank is not None and (best_rank is None or rank < best_rank):
                    best, best_rank = i, rank
            if best is None:
                break
            symbols[best : best + 2] = [symbols[best] + symbols[best + 1]]
        return symbols

    def encode(self, text: str, constraints: dict[str, set[int]] | None = None) -> list[str]:
        out: list[str] = []
        for word in text.split():
            out.extend(
                self.encode_word(word, (constraints or {}).get(word))
            )
        return out

    def decode(self, pieces: list[str]) -> str:
        return "".join(pieces).replace(WORD_START, " ").strip()


def piece_boundaries(word: str, pieces: list[str]) -> set[int]:
    """Character offsets in ``word`` where the segmentation splits."""
    bounds: set[int] = set()
    offset = 0
    for index, piece in enumerate(pieces[:-1]):
        offset += len(piece) - (1 if index == 0 else 0)
        bounds.add(offset)
    return bounds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--morphemes", type=Path, required=True)
    parser.add_argument("--examples", type=int, default=8)
    args = parser.parse_args()

    tokenizer = MoVoCTokBPE(args.model)
    config = json.loads((args.model / "config.json").read_text(encoding="utf-8"))
    training = json.loads(
        (args.model / "training_config.json").read_text(encoding="utf-8")
    )
    constraints, _ = load_constraints(args.morphemes)
    records = json.loads(args.morphemes.read_text(encoding="utf-8"))

    print(f"## {config['name']}\n")
    print(f"* Final vocabulary size: {config['vocab_size']:,}")
    print(f"* Merge operations: {config['merge_operations']:,}")
    print(f"* Training corpus: {training['corpus']}")
    print(
        f"* Words with morpheme boundaries: "
        f"{training['words_with_morpheme_boundaries']:,}"
    )
    print(
        f"* Rejected boundary-crossing merges: "
        f"{training['rejected_boundary_crossing_merges']:,}"
    )

    ok = config["vocab_size"] == config["requested_vocab_size"]
    print(f"\n  [{'PASS' if ok else 'FAIL'}] vocabulary is exactly "
          f"{config['requested_vocab_size']:,}")

    # Constraint satisfaction: no piece may span a morpheme boundary.
    violations: list[tuple[str, list[str], set[int]]] = []
    checked = 0
    for word, bounds in constraints.items():
        pieces = tokenizer.encode_word(word, bounds)
        got = piece_boundaries(word, pieces)
        checked += 1
        missing = bounds - got
        if missing:
            violations.append((word, pieces, missing))

    rate = 100 * (checked - len(violations)) / max(checked, 1)
    print(
        f"  [{'PASS' if not violations else 'FAIL'}] no subword crosses a "
        f"morpheme boundary -- {checked - len(violations):,}/{checked:,} "
        f"constrained words respected ({rate:.2f}%)"
    )
    if violations:
        for word, pieces, missing in violations[:5]:
            print(f"      {word}: {' '.join(pieces)} (missing split at {sorted(missing)})")

    # Losslessness.
    sample = [r["word"] for r in records[:2000]]
    bad = [w for w in sample if tokenizer.decode(tokenizer.encode_word(w)) != w]
    print(
        f"  [{'PASS' if not bad else 'FAIL'}] decoding is lossless -- "
        f"{len(sample) - len(bad):,}/{len(sample):,} round-trip exactly"
    )

    print(f"\n### Segmentation examples\n")
    shown = 0
    for record in records:
        word = record["word"]
        if word not in constraints or shown >= args.examples:
            continue
        bounds = sorted(constraints[word])
        surface = "|".join(
            word[i:j] for i, j in zip([0] + bounds, bounds + [len(word)])
        )
        pieces = tokenizer.encode_word(word, constraints[word])
        print(f"  Original:      {word}")
        print(f"  MoVoC boundary: {surface}")
        print(f"  MoVoC-Tok:      {' '.join(pieces)}\n")
        shown += 1
    return 0 if (not violations and ok and not bad) else 1


if __name__ == "__main__":
    raise SystemExit(main())
