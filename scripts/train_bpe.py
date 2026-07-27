"""
train_bpe.py -- Algorithm 1, Steps 2 and 3.

Step 2: Define vocabulary sizes
    s_lang      = s / 2
    s_BPE       = s_lang * (1 - r)
    s_morpheme  = s_lang * r

Step 3: Train BPE models
    V_BPE,am <- Train_BPE(P_am, s_BPE)
    V_BPE,ti <- Train_BPE(P_ti, s_BPE)

Corpora are the Amharic and Tigrinya sides of the NLLB parallel data
(Costa-Jussa et al., 2022). Step 4 (morpheme extraction) and Step 5 (merge)
are handled separately; this script only produces the BPE half.
"""

import argparse
import json
from pathlib import Path

from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders, normalizers

SPECIAL_TOKENS = ["<unk>", "<s>", "</s>", "<pad>", "<mask>"]


def vocab_sizes(s: int, r: float) -> dict:
    """Algorithm 1, Step 2."""
    if not 0.0 <= r <= 1.0:
        raise ValueError(f"r must be in [0, 1], got {r}")
    s_lang = s // 2
    s_bpe = round(s_lang * (1 - r))
    # Take the remainder rather than round(s_lang * r) so the two halves sum
    # to exactly s_lang -- float r (e.g. 5/7) otherwise loses a token here.
    s_morpheme = s_lang - s_bpe
    return {"s": s, "r": r, "s_lang": s_lang, "s_bpe": s_bpe, "s_morpheme": s_morpheme}


def corpus_lines(path: Path, max_lines: int | None):
    """Stream a corpus so a 1.6 GB file never lands in memory at once."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            line = line.strip()
            if line:
                yield line


def train_bpe(corpus: Path, vocab_size: int, out_dir: Path, lang: str,
              max_lines: int | None = None) -> Tokenizer:
    """Algorithm 1, Step 3: Train_BPE(P, s_BPE) for one language."""
    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    # NFC matches the corpus cleaning used elsewhere in this project; Ge'ez
    # script has composed forms that must normalize consistently.
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)
    tokenizer.decoder = decoders.ByteLevel()

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=SPECIAL_TOKENS,
        show_progress=True,
    )

    tokenizer.train_from_iterator(corpus_lines(corpus, max_lines), trainer=trainer)

    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(out_dir / f"bpe_{lang}.json"))

    vocab = tokenizer.get_vocab()
    vocab_txt = out_dir / f"vocab_bpe_{lang}.txt"
    with open(vocab_txt, "w", encoding="utf-8") as f:
        for tok, _ in sorted(vocab.items(), key=lambda kv: kv[1]):
            f.write(tok + "\n")

    print(f"[{lang}] trained: {len(vocab)} tokens -> {out_dir / f'bpe_{lang}.json'}")
    return tokenizer


def main():
    p = argparse.ArgumentParser(description="Algorithm 1 Steps 2-3: BPE training")
    p.add_argument("--amharic-corpus", type=Path, required=True)
    p.add_argument("--tigrinya-corpus", type=Path, required=True)
    p.add_argument("-s", "--vocab-size", type=int, default=152_000,
                   help="total vocabulary size s (default: paper's 152k)")
    p.add_argument("-r", "--morpheme-ratio", type=float, default=0.71,
                   help="proportion of morpheme-aware tokens r (default: 0.71)")
    p.add_argument("--max-lines", type=int, default=None,
                   help="cap lines read per corpus (default: full corpus)")
    p.add_argument("-o", "--out-dir", type=Path,
                   default=Path(__file__).resolve().parent.parent / "vocab")
    args = p.parse_args()

    sizes = vocab_sizes(args.vocab_size, args.morpheme_ratio)
    print("Algorithm 1, Step 2 -- vocabulary sizes")
    for k, v in sizes.items():
        print(f"  {k:12} = {v}")
    print()

    print("Algorithm 1, Step 3 -- training BPE models")
    train_bpe(args.amharic_corpus, sizes["s_bpe"], args.out_dir, "amharic", args.max_lines)
    train_bpe(args.tigrinya_corpus, sizes["s_bpe"], args.out_dir, "tigrinya", args.max_lines)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    meta = dict(sizes)
    meta["amharic_corpus"] = str(args.amharic_corpus)
    meta["tigrinya_corpus"] = str(args.tigrinya_corpus)
    meta["max_lines"] = args.max_lines
    with open(args.out_dir / "bpe_config.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"\nStep 3 complete. s_morpheme = {sizes['s_morpheme']} per language "
          f"remains for Step 4 (morpheme extraction), then Step 5 (merge).")


if __name__ == "__main__":
    main()
