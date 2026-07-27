"""
tokenize.py -- segment text with a trained MoVoC-Tok tokenizer.

Applies the constrained merge table learned in Algorithm 1, Step 6.
"""

import argparse
import sys
from pathlib import Path

from movoc import io, tokenizer


def main():
    p = argparse.ArgumentParser(description="Tokenize with MoVoC-Tok")
    p.add_argument("language", choices=("amharic", "tigrinya"))
    p.add_argument("text", nargs="*", help="text to tokenize; omit to read stdin")
    p.add_argument("--merges", type=Path, default=None)
    args = p.parse_args()

    path = args.merges or io.MODELS / f"movoc_tok_merges_{args.language}.txt"
    if not path.exists():
        sys.exit(f"no merge table at {path}; run train.py first")
    ranks = tokenizer.load_merges(path)

    lines = [" ".join(args.text)] if args.text else (l.rstrip("\n") for l in sys.stdin)
    for line in lines:
        if not line.strip():
            continue
        out = []
        for word in line.split():
            out.extend(tokenizer.encode(word, ranks))
        print(" ".join(out))


if __name__ == "__main__":
    main()
