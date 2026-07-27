"""
translate_eval.py -- extrinsic evaluation (paper Sec 5.1).

Translation quality is assessed with **BLEU** and **chrF++**, which measure
n-gram and character-level overlap. Both come from sacrebleu; chrF++ is CHRF
with word_order=2.

COMET is deliberately not used. It depends on pretrained models and reference
corpora that exist only for high-resource languages -- for Tigrinya, Tigre and
Ge'ez no reliable COMET-compatible models exist, which makes its use
inappropriate or misleading.

The fine-tuned MarianMT model translates between English and the two
low-resource Ge'ez-script languages it was trained on, Amharic and Tigrinya.
**Tigre was not included during training** and appears here only, to measure
the model's zero-shot translation capability.
"""

import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Test data (paper Sec 5.1). Each language pair is capped at 100 sentence
# pairs to keep the evaluation balanced; where OPUS coverage is short, the
# remainder is human-validated.
TEST_SETS = {
    "amharic": {"pairs": 100, "opus": 100, "human_validated": 0,
                "note": "100 of 213 available from OPUS"},
    "tigrinya": {"pairs": 100, "opus": 74, "human_validated": 26},
    "tigre": {"pairs": 100, "opus": 45, "human_validated": 55},
    # Ge'ez has no parallel data, so it is evaluated intrinsically only.
    "geez": {"pairs": 100, "opus": 0, "human_validated": 100,
             "note": "newly created and validated; intrinsic evaluation only"},
}

# Ge'ez is excluded from extrinsic evaluation: no parallel data exists.
EXTRINSIC_LANGUAGES = ("amharic", "tigrinya", "tigre")

# Directions the model is trained on (paper Sec 5.1).
TRAINED_DIRECTIONS = ("en-am", "am-en", "en-ti", "ti-en")

# Held out of training entirely; evaluated zero-shot.
ZERO_SHOT_DIRECTIONS = ("en-tig", "tig-en")


def score(hypotheses: list, references: list) -> dict:
    """BLEU and chrF++ for one direction."""
    from sacrebleu.metrics import BLEU, CHRF

    if len(hypotheses) != len(references):
        raise ValueError(f"{len(hypotheses)} hypotheses vs "
                         f"{len(references)} references")
    bleu = BLEU().corpus_score(hypotheses, [references])
    # chrF++ is chrF with word n-grams included (word_order=2).
    chrfpp = CHRF(word_order=2).corpus_score(hypotheses, [references])
    return {"bleu": round(bleu.score, 2),
            "chrf++": round(chrfpp.score, 2),
            "n": len(hypotheses)}


def translate(model_dir: Path, sentences: list, batch_size: int = 8,
              max_length: int = 128) -> list:
    """Decode with a fine-tuned MarianMT checkpoint.

    Batch size and maximum sequence length follow the training configuration
    reported in Sec 4.3.
    """
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(model_dir))
    model.eval()

    out = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        enc = tokenizer(batch, return_tensors="pt", padding=True,
                        truncation=True, max_length=max_length)
        gen = model.generate(**enc, max_length=max_length)
        out.extend(tokenizer.batch_decode(gen, skip_special_tokens=True))
    return out


def read_lines(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f]


def main():
    p = argparse.ArgumentParser(
        description="Extrinsic evaluation: BLEU and chrF++ (paper Sec 5.1)")
    p.add_argument("--model", type=Path, required=True,
                   help="fine-tuned MarianMT checkpoint")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--direction", required=True,
                   help="e.g. en-am, ti-en, en-tig (zero-shot)")
    p.add_argument("-o", "--out", type=Path,
                   default=Path("evaluation/results/extrinsic_eval.json"))
    args = p.parse_args()

    src = read_lines(args.source)
    ref = read_lines(args.reference)
    hyp = translate(args.model, src)

    result = score(hyp, ref)
    result["direction"] = args.direction
    result["zero_shot"] = args.direction in ZERO_SHOT_DIRECTIONS
    result["model"] = str(args.model)

    existing = {}
    if args.out.exists():
        with open(args.out, encoding="utf-8") as f:
            existing = json.load(f)
    existing.setdefault("results", {})[args.direction] = result

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    tag = " (zero-shot)" if result["zero_shot"] else ""
    print(f"{args.direction}{tag}: BLEU {result['bleu']}  "
          f"chrF++ {result['chrf++']}  n={result['n']}")


if __name__ == "__main__":
    main()
