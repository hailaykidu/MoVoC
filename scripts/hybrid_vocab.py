"""
hybrid_vocab.py

Full MoVoC Algorithm 1 orchestration (paper's pseudocode, generalized from
2 languages to all 4 we actually have corpora for -- the paper itself only
built vocab for Amharic/Tigrinya since "we did not get data for BPE
training" for Tigre/Ge'ez; this project has real cleaned corpora for all
four from the GeezTokenizer project, so we extend the same algorithm to
all of them):

    slang = s / N                  (N = number of languages)
    sBPE = slang * (1 - r)
    smorpheme = slang * r
    for each language:
        V_BPE[lang]       = Train_BPE(corpus[lang], sBPE)
        V_morpheme[lang]  = extract_morphemes(corpus[lang], smorpheme)
    V_MoVoC = union of all V_BPE[lang] and V_morpheme[lang]

`r` (morpheme-token proportion) is a hyperparameter the paper doesn't give
an exact value for in the text available to us -- default 0.3 here,
clearly labeled as our own choice, not lifted from the paper.

USAGE
    python hybrid_vocab.py --total-vocab-size 32000 --r 0.3 \
        --max-lines-per-language 500000
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from create_vocab import extract_morphemes
from train_bpe import train_bpe

GEEZTOKENIZER_CORPUS_DIR = (
    Path(__file__).resolve().parents[5] / "GeezTokenizer" / "02_cleaning" / "corpus_clean"
)
LANGUAGES = ["amharic", "tigrinya", "tigre", "geez"]


def build_hybrid_vocab(total_vocab_size: int, r: float, max_lines_per_language: int | None, outdir: Path):
    n_languages = len(LANGUAGES)
    slang = total_vocab_size // n_languages
    s_bpe = int(slang * (1 - r))
    s_morpheme = int(slang * r)
    print(f"slang={slang}, sBPE={s_bpe}, smorpheme={s_morpheme} (r={r}, N={n_languages})")

    report = {"total_vocab_size": total_vocab_size, "r": r, "slang": slang,
              "sBPE": s_bpe, "smorpheme": s_morpheme, "languages": {}}
    full_vocab = set()

    for lang in LANGUAGES:
        corpus_path = GEEZTOKENIZER_CORPUS_DIR / f"{lang}.txt"
        print(f"\n=== {lang} ({corpus_path}) ===")

        print(f"  training BPE (target size {s_bpe})...")
        bpe_tokenizer = train_bpe(str(corpus_path), s_bpe, max_lines_per_language)
        bpe_vocab = set(bpe_tokenizer.get_vocab().keys())
        print(f"  BPE vocab actually produced: {len(bpe_vocab)} tokens")

        print(f"  extracting top-{s_morpheme} morphemes...")
        morphemes = extract_morphemes(str(corpus_path), lang, s_morpheme, max_lines_per_language)
        print(f"  morphemes actually produced: {len(morphemes)}")

        lang_vocab = bpe_vocab | set(morphemes)
        full_vocab |= lang_vocab

        out_path = outdir / f"{lang}_hybrid.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for tok in sorted(lang_vocab):
                f.write(tok + "\n")

        report["languages"][lang] = {
            "bpe_tokens": len(bpe_vocab),
            "morpheme_tokens": len(morphemes),
            "hybrid_vocab_size": len(lang_vocab),
            "hybrid_vocab_path": str(out_path),
        }
        print(f"  wrote {len(lang_vocab)} hybrid tokens to {out_path}")

    report["total_vmovoc_size"] = len(full_vocab)
    return report, full_vocab


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-vocab-size", type=int, default=32000)
    parser.add_argument("--r", type=float, default=0.3, help="morpheme-token proportion (our choice, not from paper)")
    parser.add_argument("--max-lines-per-language", type=int, default=500_000)
    parser.add_argument("--outdir", default="../vocab")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    report, full_vocab = build_hybrid_vocab(
        args.total_vocab_size, args.r, args.max_lines_per_language, outdir
    )

    import json
    with open(outdir / "hybrid_vocab_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n=== VMoVoC total (union across all languages): {report['total_vmovoc_size']} ===")
    print(f"Report written to {outdir / 'hybrid_vocab_report.json'}")


if __name__ == "__main__":
    main()
