"""
preprocessing.py -- corpus preparation.

The corpora used for vocabulary construction are the Amharic and Tigrinya
sides of the NLLB parallel data (Costa-Jussa et al., 2022), read as plain
text, one sentence per line. The HornMT parallel corpus (data/raw/hornmt/)
supplies the words submitted for morphological analysis.

Preparation is deliberately thin: corpora are streamed line by line so a
multi-gigabyte side is never held in memory, blank lines are dropped, and
NFC normalization is applied inside the BPE trainer (see tokenizer.py) so
Ge'ez-script composed forms normalize consistently.

No train/dev/test splitting is performed -- the paper's vocabulary
construction runs over the full corpus, and evaluation uses separate
annotated sets rather than a held-out corpus slice.
"""

import re
from pathlib import Path

# Ethiopic block: used to keep Ge'ez-script word forms and drop punctuation
# and Latin-script strays when deriving word lists from a corpus.
GEEZ_SCRIPT = re.compile(r"^[ሀ-፿]+$")


def read_lines(path: Path, max_lines: int | None = None):
    """Stream non-empty lines from a corpus file."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            line = line.strip()
            if line:
                yield line


def word_types(path: Path, max_lines: int | None = None) -> set:
    """Distinct Ge'ez-script word forms in a corpus."""
    return {w for line in read_lines(path, max_lines)
            for w in line.split() if GEEZ_SCRIPT.match(w)}
