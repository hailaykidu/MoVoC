"""Train MoVoC-Tok: a morpheme-aware tokenizer over the MoVoC vocabulary.

Selects a 32,000-token working vocabulary from the constructed candidate
vocabulary V_MoVoC and builds a longest-match segmenter over it.

Selection policy (morpheme-priority, frequency-ranked):

1. Special tokens (``<pad> <unk> <s> </s>``) are kept first and always.
2. Morphemes are taken next, ranked by descending frequency. Morphemes are
   what distinguishes MoVoC-Tok from plain BPE, so they have priority.
3. Remaining slots are filled with BPE pieces in their native model order.

V_MoVoC is read but never modified: this step selects a subset and records
which entries were selected. No BPE model is retrained and no new subword
units are derived -- every token in the result already exists in V_MoVoC.

Segmentation is greedy longest-match over the selected vocabulary, applied
left to right within each whitespace token, with the SentencePiece word-start
marker (U+2581) prepended so BPE pieces match as the BPE model would produce
them. Characters no vocabulary entry covers fall back to ``<unk>``.

Usage:
    python scripts/train_movoc_tok.py --vocab movoc/movoc_vocab.json \\
        --outdir tokenizers/movoc_tok_32k --vocab-size 32000
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

#: SentencePiece word-boundary marker.
WORD_START = "▁"

SPECIAL_TOKENS = ["<pad>", "<unk>", "<s>", "</s>"]


def load_candidates(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_vocabulary(
    candidates: list[dict], vocab_size: int, bpe_floor: int
) -> tuple[list[dict], dict[str, int]]:
    """Select ``vocab_size`` entries, morphemes first by frequency.

    ``bpe_floor`` reserves slots for BPE pieces before morphemes are taken.
    This reservation is required for the tokenizer to function at all: MoVoC
    morphemes are stored without the SentencePiece word-start marker (▁),
    while every word begins with one, so a vocabulary of morphemes alone can
    never match a word-initial unit and would segment all input to <unk>.
    The reserved BPE pieces supply word-start and character coverage; morphemes
    still take priority for every remaining slot.

    Returns the selected entries in final id order and a breakdown of what was
    taken from where.
    """
    specials = [e for e in candidates if e["token"] in SPECIAL_TOKENS]
    morphemes = [e for e in candidates if e["type"] == "morpheme"]
    bpe = [
        e
        for e in candidates
        if e["type"] == "BPE" and e["token"] not in SPECIAL_TOKENS
    ]

    # Morphemes by descending frequency, ties broken on the token so the
    # selection is deterministic.
    morphemes.sort(key=lambda e: (-e.get("frequency", 0), e["token"]))

    selected: list[dict] = []
    seen: set[str] = set()

    for entry in specials:
        if entry["token"] not in seen:
            seen.add(entry["token"])
            selected.append(entry)

    n_specials = len(selected)

    # Guarantee character coverage before anything else. Without every single
    # character in the vocabulary, a longest-match segmenter emits <unk> for
    # any position no multi-character unit covers, which loses input outright.
    # These come from V_MoVoC itself -- no new units are invented.
    n_chars = 0
    for entry in candidates:
        if len(entry["token"]) == 1 and entry["token"] not in seen:
            seen.add(entry["token"])
            selected.append(entry)
            n_chars += 1

    # Reserve the BPE floor next, in native model order. SentencePiece emits
    # its most frequent pieces first, so the reserved head is the highest-value
    # coverage the BPE model has.
    reserved: list[dict] = []
    for entry in bpe:
        if len(reserved) >= bpe_floor:
            break
        if entry["token"] not in seen:
            seen.add(entry["token"])
            reserved.append(entry)

    morpheme_budget = vocab_size - n_specials - n_chars - len(reserved)
    taken_morphemes: list[dict] = []
    for entry in morphemes:
        if len(taken_morphemes) >= morpheme_budget:
            break
        if entry["token"] not in seen:
            seen.add(entry["token"])
            taken_morphemes.append(entry)

    selected.extend(taken_morphemes)
    selected.extend(reserved)

    # Any slots left (morphemes exhausted) go to further BPE pieces.
    for entry in bpe:
        if len(selected) >= vocab_size:
            break
        if entry["token"] not in seen:
            seen.add(entry["token"])
            selected.append(entry)

    n_morphemes = len(taken_morphemes)
    n_bpe = len(selected) - n_specials - n_chars - n_morphemes

    return selected, {
        "special_tokens": n_specials,
        "characters": n_chars,
        "morphemes": n_morphemes,
        "bpe": n_bpe,
        "total": len(selected),
    }


class MoVoCTok:
    """Greedy longest-match segmenter over a fixed vocabulary."""

    def __init__(self, tokens: list[str]) -> None:
        self.vocab = {token: i for i, token in enumerate(tokens)}
        self.ids = tokens
        self.max_len = max((len(t) for t in tokens), default=1)
        self.unk = self.vocab.get("<unk>", 1)

    def _segment_word(self, word: str) -> list[str]:
        pieces: list[str] = []
        i = 0
        n = len(word)
        while i < n:
            # Longest match first: the longest vocabulary entry starting here.
            upper = min(n, i + self.max_len)
            for j in range(upper, i, -1):
                candidate = word[i:j]
                if candidate in self.vocab:
                    pieces.append(candidate)
                    i = j
                    break
            else:
                # No entry covers this character.
                pieces.append("<unk>")
                i += 1
        return pieces

    def encode(self, text: str) -> list[str]:
        out: list[str] = []
        for word in text.split():
            out.extend(self._segment_word(WORD_START + word))
        return out

    def encode_ids(self, text: str) -> list[int]:
        return [self.vocab.get(p, self.unk) for p in self.encode(text)]

    def decode(self, pieces: list[str]) -> str:
        return "".join(pieces).replace(WORD_START, " ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vocab", type=Path, default=Path("movoc/movoc_vocab.json"))
    parser.add_argument(
        "--outdir", type=Path, default=Path("tokenizers/movoc_tok_32k")
    )
    parser.add_argument("--vocab-size", type=int, default=32_000)
    parser.add_argument(
        "--bpe-floor",
        type=int,
        default=16_000,
        help="BPE pieces reserved before morphemes are taken; required for "
        "word-start and character coverage (see select_vocabulary)",
    )
    args = parser.parse_args()

    started = time.time()
    candidates = load_candidates(args.vocab)
    source_md5 = hashlib.md5(args.vocab.read_bytes()).hexdigest()
    print(f"V_MoVoC candidates: {len(candidates):,} (md5 {source_md5})")

    selected, breakdown = select_vocabulary(
        candidates, args.vocab_size, args.bpe_floor
    )
    print(
        f"selected {breakdown['total']:,}: {breakdown['special_tokens']} special, "
        f"{breakdown['characters']:,} character, {breakdown['morphemes']:,} morphemes, "
        f"{breakdown['bpe']:,} BPE"
    )

    args.outdir.mkdir(parents=True, exist_ok=True)

    tokens = [e["token"] for e in selected]
    (args.outdir / "vocab.txt").write_text(
        "\n".join(tokens) + "\n", encoding="utf-8"
    )
    (args.outdir / "vocab.json").write_text(
        json.dumps(
            [{**entry, "id": i} for i, entry in enumerate(selected)],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    by_language: dict[str, int] = {}
    for entry in selected:
        key = f"{entry['language']}/{entry['type']}"
        by_language[key] = by_language.get(key, 0) + 1

    config = {
        "name": "MoVoC-Tok",
        "vocab_size": len(selected),
        "requested_vocab_size": args.vocab_size,
        "segmentation": "greedy longest-match",
        "word_start_marker": WORD_START,
        "special_tokens": {t: i for i, t in enumerate(SPECIAL_TOKENS)},
        "selection_policy": (
            "special tokens; all single-character units from V_MoVoC for "
            "guaranteed character coverage; a reserved floor of BPE pieces in "
            "native model order for word-start coverage; then morphemes by "
            "descending frequency; then further BPE pieces if slots remain"
        ),
        "bpe_floor": args.bpe_floor,
        "composition": breakdown,
        "composition_by_language": by_language,
        "source_vocabulary": str(args.vocab.resolve()),
        "source_vocabulary_size": len(candidates),
        "source_vocabulary_md5": source_md5,
        "source_vocabulary_modified": False,
        "bpe_retrained": False,
        "build_seconds": round(time.time() - started, 2),
    }
    (args.outdir / "config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"wrote {args.outdir}/vocab.txt")
    print(f"wrote {args.outdir}/vocab.json")
    print(f"wrote {args.outdir}/config.json")

    tokenizer = MoVoCTok(tokens)
    print("\nexample segmentations:")
    for text in ["ልጆቹን ከቤቱ ወሰደ።", "ቤታችን ትልቅ ነው።", "ንዝተተኮሱ ሚሳይላትን", "መጻእና"]:
        print(f"  {text}\n    -> {' '.join(tokenizer.encode(text))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
