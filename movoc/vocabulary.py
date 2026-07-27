"""
vocabulary.py -- MoVoC hybrid vocabulary construction (paper Algorithm 1).

    Require: P_am, P_ti, s (total vocabulary size),
             r (proportion of morpheme-aware tokens, 0 <= r <= 1)
    Ensure:  V_MoVoC

    Step 2: s_lang     <- s / 2
            s_BPE      <- s_lang x (1 - r)
            s_morpheme <- s_lang x r
    Step 3: V_BPE,am   <- Train_BPE(P_am, s_BPE)          [tokenizer.py]
            V_BPE,ti   <- Train_BPE(P_ti, s_BPE)
    Step 4: V_morpheme <- extract_morphemes(P, s_morpheme)
    Step 5: V_MoVoC    <- V_BPE,am u V_BPE,ti u V_morpheme,am u V_morpheme,ti

Step 4's definition, from the paper: "extract_morphemes(P, s_morpheme)
refers to a procedure that performs frequency-based morpheme extraction
from a corpus that has already been segmented using a rule-based
morphological analyzer... All resulting morphemes across the corpus are
collected, and their frequencies are computed. The morphemes are sorted by
descending frequency, and the top s_morpheme morphemes are selected."
"""

import json
from collections import Counter
from pathlib import Path

from .annotation import morphemes_of


def vocab_sizes(s: int, r: float) -> dict:
    """Algorithm 1, Step 2."""
    if not 0.0 <= r <= 1.0:
        raise ValueError(f"r must be in [0, 1], got {r}")
    s_lang = s // 2
    s_bpe = round(s_lang * (1 - r))
    # Take the remainder rather than round(s_lang * r) so the two halves sum
    # to exactly s_lang -- float r (e.g. 5/7) otherwise loses a token here.
    s_morpheme = s_lang - s_bpe
    return {"s": s, "r": r, "s_lang": s_lang, "s_bpe": s_bpe,
            "s_morpheme": s_morpheme}


def extract_morphemes(path: Path, k: int) -> tuple:
    """Algorithm 1, Step 4: frequency-rank morphemes, take the top k."""
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)

    counts = Counter()
    for entry in entries:
        counts.update(morphemes_of(entry))

    top = [m for m, _ in counts.most_common(k)]
    return top, len(counts), len(entries)


def bpe_vocabulary(tokenizer_json: Path) -> list:
    """The BPE half of one language's vocabulary, in token-id order."""
    with open(tokenizer_json, encoding="utf-8") as f:
        vocab = json.load(f)["model"]["vocab"]
    return sorted(vocab, key=vocab.get)


def merge(groups: list) -> list:
    """Algorithm 1, Step 5: union, preserving each group's own rank order."""
    merged, seen = [], set()
    for group in groups:
        for tok in group:
            if tok not in seen:
                seen.add(tok)
                merged.append(tok)
    return merged


def export(vocabulary: list, path: Path) -> None:
    """Algorithm 1, Step 7: write V_MoVoC."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(vocabulary) + "\n")
