"""
train_bpe.py

Trains a plain byte-level-free BPE tokenizer for one language, using the
`tokenizers` library (not SentencePiece Unigram -- the MoVoC paper's
Algorithm 1 specifically calls for BPE: "we train BPE small with a
vocabulary size of s(1-r)").

Reuses the already-cleaned per-language corpora from the GeezTokenizer
project rather than re-collecting/re-cleaning text.

USAGE
    python train_bpe.py --language amharic --vocab-size 16000 \
        --corpus ../../../../../GeezTokenizer/02_cleaning/corpus_clean/amharic.txt \
        --out ../vocab/amharic_bpe.txt
"""

import argparse
from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import BpeTrainer


def train_bpe(corpus_path: str, vocab_size: int, max_lines: int | None = None) -> Tokenizer:
    tokenizer = Tokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = Whitespace()
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=["<unk>"],
        show_progress=True,
    )

    if max_lines is None:
        tokenizer.train([corpus_path], trainer)
    else:
        # tokenizers' train_from_iterator lets us cap how much of a huge
        # corpus (e.g. Amharic's 12.19M lines / 3.85GB) we actually read,
        # rather than silently training on a truncated file copy.
        def line_iterator():
            with open(corpus_path, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    yield line
        tokenizer.train_from_iterator(line_iterator(), trainer)

    return tokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--vocab-size", type=int, required=True)
    parser.add_argument(
        "--max-lines", type=int, default=None,
        help="cap corpus lines read (e.g. Amharic's corpus is 12.19M lines; "
             "capping keeps BPE training fast without needing the full corpus)",
    )
    parser.add_argument("--out", required=True, help="output vocab txt path (one token per line)")
    args = parser.parse_args()

    print(f"--- training BPE for {args.language}, vocab_size={args.vocab_size} ---")
    tokenizer = train_bpe(args.corpus, args.vocab_size, args.max_lines)
    vocab = tokenizer.get_vocab()
    tokens_by_id = sorted(vocab.items(), key=lambda kv: kv[1])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for token, _id in tokens_by_id:
            f.write(token + "\n")

    print(f"  wrote {len(tokens_by_id)} BPE tokens to {out_path}")


if __name__ == "__main__":
    main()
