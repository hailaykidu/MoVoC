"""
utils.py -- surface alignment of annotated morphemes.

The intrinsic metrics compare character offsets, so a gold entry is only
scorable when its morphemes map onto spans of the surface form. Literal
concatenation fails for most Ge'ez-script words: the script is a syllabary,
so a root-final consonant and a suffix-initial vowel fuse into a single
fidel (ጥበብ + አኛ surfaces as ጥበበኛ, with ብ and አ merging into በ, which keeps
the root's consonant and takes the suffix's vowel).

align_morphemes decomposes Ethiopic characters into (consonant, vowel) and
matches morphemes against the surface form allowing that fusion.
"""

from pathlib import Path

from .annotation import clean, load

ETH_START, ETH_END = 0x1200, 0x1357


def _syllable(ch: str):
    """(consonant, vowel-order) for an Ethiopic fidel, else (None, None).

    The Ge'ez script is a syllabary: each character encodes a consonant
    plus a vowel, laid out in blocks of eight vowel orders per consonant.
    """
    o = ord(ch)
    if ETH_START <= o <= ETH_END:
        return (o - ETH_START) // 8, (o - ETH_START) % 8
    return None, None


def align_morphemes(word: str, parts: list) -> list:
    """Match `parts` against `word`, tolerating fidel fusion at boundaries.

    Ge'ez-script morphemes rarely concatenate literally. Where a root ends
    in a consonant and the following suffix begins with a vowel character,
    the two merge into a single fidel that keeps the root's consonant and
    takes the suffix's vowel -- ጥበብ + አኛ surfaces as ጥበበኛ, with ብ and አ
    fusing into በ. Returns the surface span lengths for each part, or []
    if the parts cannot be aligned at all.
    """
    spans, pos = [], 0
    for i, part in enumerate(parts):
        if not part:
            spans.append(0)
            continue
        if word.startswith(part, pos):
            spans.append(len(part))
            pos += len(part)
            continue
        # Try fusion: all but the final character match literally, and the
        # final character shares its consonant with the surface character.
        head = part[:-1]
        if head and word.startswith(head, pos):
            j = pos + len(head)
            if j < len(word):
                c_part, _ = _syllable(part[-1])
                c_word, _ = _syllable(word[j])
                if c_part is not None and c_part == c_word:
                    spans.append(len(head) + 1)
                    pos = j + 1
                    continue
        # A suffix whose leading vowel was absorbed by the previous fidel.
        if i > 0 and len(part) > 1 and word.startswith(part[1:], pos):
            spans.append(len(part) - 1)
            pos += len(part) - 1
            continue
        return []
    return spans if pos == len(word) else []


def gold_triples(path: Path) -> list:
    """(word, (prefix, root, suffix)) for every usable gold entry.

    Entries are rewritten to the surface spans the metrics can compare:
    boundary offsets are character positions in `word`, so each morpheme is
    replaced by the substring it actually occupies after fusion.
    """
    out = []
    for e in load(path):
        word = clean(e.get("word") or e.get("Word"))
        pre = clean(e.get("prefix") or e.get("Prefix"))
        root = clean(e.get("root") or e.get("Root"))
        suf = clean(e.get("suffix") or e.get("Suffix"))
        if not word or not root:
            continue
        if pre + root + suf == word:
            out.append((word, (pre, root, suf)))
            continue
        spans = align_morphemes(word, [pre, root, suf])
        if not spans:
            continue
        a, b = spans[0], spans[0] + spans[1]
        out.append((word, (word[:a], word[a:b], word[b:])))
    return out


