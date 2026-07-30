"""
build_extended_arms.py -- Ge'ez and Tigre tokenizer arms for the EXTENDED
intrinsic verification (Tables 2 and 4).

Builds, per language, using the paper's Algorithm 1 steps:
  Step 3  BPE at s_bpe = 32,000              -> data/vocabulary/bpe_<lang>.json
  Step 6  constrained merges (MoVoC-Tok)     -> models/movoc_tok_merges_<lang>.txt

Corpora (supplied by the user; NOT part of the MoVoC repository):
  Ge'ez  data/scripts/Geez from Kibra negest 19.txt   (running text)
  Tigre  data/tigre-words-only.txt                    (one word per line)

Morpheme-boundary constraints for Step 6 come from the existing manual
annotations (data/annotations/{geez,tigre}/manual_morphemes.json). Neither
new corpus carries morpheme segmentations, so no annotation is invented:
the corpora supply *text* for learning merges, the annotations supply
*boundaries* for constraining them.

Writes nothing for Amharic or Tigrinya -- those artifacts are untouched.
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from movoc import annotation, io, tokenizer

S_BPE = 32_000                      # paper's vocabulary setting
EXTENDED = ROOT / "data/raw/extended"
LANGS = ("geez", "tigre")
WORDS = {"geez": EXTENDED / "geez_words.txt",
         "tigre": EXTENDED / "tigre_words.txt"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vocab-size", type=int, default=S_BPE)
    args = p.parse_args()

    report = {"generated": datetime.now(timezone.utc).isoformat(),
              "vocab_size_requested": args.vocab_size,
              "note": ("Extended intrinsic verification arms. Corpora are "
                       "user-supplied and not part of the MoVoC repository."),
              "languages": {}}

    for lang in LANGS:
        wl = WORDS[lang]
        if not wl.exists():
            raise SystemExit(f"missing word list {wl}; run the extraction step")
        words = [w for w in wl.read_text(encoding="utf-8").splitlines() if w]
        print(f"\n=== {lang}: {len(words)} tokens, {len(set(words))} unique")

        # --- Step 3: BPE baseline at the paper's 32k setting ---
        bpe_path = io.VOCABULARY / f"bpe_{lang}.json"
        tok = tokenizer.train_bpe(wl, args.vocab_size, io.VOCABULARY, lang)
        achieved = tok.get_vocab_size()
        print(f"  BPE requested {args.vocab_size} -> achieved {achieved}")

        # --- Step 6: constrained merges over the same corpus ---
        cons = tokenizer.load_constraints([annotation.VOCAB_SOURCES[lang]])
        wf = Counter(words)
        # A deduplicated word list (Tigre) gives every type frequency 1, so
        # the default min_freq=2 would discard the entire corpus and learn
        # zero merges. Word lists therefore need min_freq=1; running text
        # (Ge'ez) keeps the default so genuine hapaxes stay filtered.
        is_type_list = max(wf.values()) == 1
        min_freq = 1 if is_type_list else 2
        print(f"  corpus form: {'type list' if is_type_list else 'running text'}"
              f" -> min_freq={min_freq}")
        merges = tokenizer.learn_merges(wf, cons, args.vocab_size,
                                        min_freq=min_freq)
        mpath = io.MODELS / f"movoc_tok_merges_{lang}.txt"
        io.MODELS.mkdir(parents=True, exist_ok=True)
        tokenizer.save_merges(merges, mpath)
        print(f"  constraints from {len(cons)} annotated words")
        print(f"  MoVoC-Tok merges learned: {len(merges)} -> {mpath.name}")

        report["languages"][lang] = {
            "corpus_word_list": str(wl.relative_to(ROOT)),
            "tokens": len(words),
            "unique_words": len(set(words)),
            "bpe_artifact": str(bpe_path.relative_to(ROOT)),
            "bpe_vocab_requested": args.vocab_size,
            "bpe_vocab_achieved": achieved,
            "movoc_tok_artifact": str(mpath.relative_to(ROOT)),
            "movoc_tok_merges": len(merges),
            "corpus_form": "type list" if is_type_list else "running text",
            "min_freq": min_freq,
            "constraint_source": str(
                annotation.VOCAB_SOURCES[lang].relative_to(ROOT)),
            "constraint_words": len(cons),
        }

    out = ROOT / "evaluation/results/extended_arms_build.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
