"""
train.py -- MoVoC vocabulary construction and tokenizer training.

Runs the paper's Algorithm 1 end to end:

    Step 2  vocabulary sizes           movoc.vocabulary.vocab_sizes
    Step 3  Train_BPE per language     movoc.tokenizer.train_bpe
    Step 4  extract_morphemes          movoc.vocabulary.extract_morphemes
    Step 5  merge into V_MoVoC         movoc.vocabulary.merge
    Step 6  Train_MoVoC_Model          movoc.tokenizer.learn_merges
    Step 7  return V_MoVoC

Morphemes come from the post-edited HornMorpho annotations (Amharic,
Tigrinya) and the manual annotations (Ge'ez, Tigre); see movoc/annotation.py.
"""

import argparse
from pathlib import Path

from movoc import annotation, io, tokenizer, vocabulary

LANGS = ("amharic", "tigrinya")


def main():
    p = argparse.ArgumentParser(description="MoVoC Algorithm 1")
    p.add_argument("--amharic-corpus", type=Path, required=True)
    p.add_argument("--tigrinya-corpus", type=Path, required=True)
    p.add_argument("-s", "--vocab-size", type=int, default=224_000,
                   help="total vocabulary size s (paper Table 5: 224,000)")
    p.add_argument("-r", "--morpheme-ratio", type=float, default=5 / 7,
                   help="proportion of morpheme-aware tokens r")
    p.add_argument("--max-lines", type=int, default=None,
                   help="cap lines read per corpus; omit for the full corpus")
    p.add_argument("--merge-lines", type=int, default=None,
                   help="lines used for Step 6 merge learning")
    p.add_argument("--skip-step6", action="store_true",
                   help="stop after Step 5")
    p.add_argument("--skip-bpe", action="store_true",
                   help="reuse the BPE tokenizers already in data/vocabulary/ "
                        "instead of retraining them in Step 3")
    args = p.parse_args()

    corpora = {"amharic": args.amharic_corpus, "tigrinya": args.tigrinya_corpus}

    sizes = vocabulary.vocab_sizes(args.vocab_size, args.morpheme_ratio)
    print("Step 2 -- vocabulary sizes")
    for k, v in sizes.items():
        print(f"  {k:12} = {v}")

    print("\nStep 3 -- Train_BPE(P, s_BPE)")
    for lang in LANGS:
        existing = io.VOCABULARY / f"bpe_{lang}.json"
        if args.skip_bpe and existing.exists():
            print(f"  [{lang}] reusing {existing}")
            continue
        tokenizer.train_bpe(corpora[lang], sizes["s_bpe"],
                            io.VOCABULARY, lang, args.max_lines)

    print(f"\nStep 4 -- extract_morphemes(P, s_morpheme={sizes['s_morpheme']})")
    v_morph = {}
    for lang in LANGS:
        src = annotation.VOCAB_SOURCES[lang]
        top, available, n = vocabulary.extract_morphemes(src, sizes["s_morpheme"])
        v_morph[lang] = top
        note = "" if available >= sizes["s_morpheme"] else \
               "  (all available morphemes selected)"
        print(f"  {lang:9} {n:7} entries -> {available:6} distinct "
              f"-> selected {len(top):6}{note}")

    print("\nStep 5 -- merge all vocabularies")
    v_bpe = {lang: vocabulary.bpe_vocabulary(io.VOCABULARY / f"bpe_{lang}.json")
             for lang in LANGS}
    for lang in LANGS:
        print(f"  V_BPE,{lang[:2]}      = {len(v_bpe[lang]):6}")
    for lang in LANGS:
        print(f"  V_morpheme,{lang[:2]} = {len(v_morph[lang]):6}")

    groups = [v_bpe["amharic"], v_bpe["tigrinya"],
              v_morph["amharic"], v_morph["tigrinya"]]
    merged = vocabulary.merge(groups)
    total = sum(len(g) for g in groups)
    print(f"\n  sum of parts   = {total}")
    print(f"  V_MoVoC        = {len(merged)}  "
          f"({total - len(merged)} overlapping tokens collapsed)")

    out = io.VOCABULARY / "vocab_movoc.txt"
    vocabulary.export(merged, out)

    config = dict(sizes)
    config.update({
        "amharic_corpus": str(args.amharic_corpus),
        "tigrinya_corpus": str(args.tigrinya_corpus),
        "max_lines": args.max_lines,
        **{f"v_bpe_{l}": len(v_bpe[l]) for l in LANGS},
        **{f"v_morpheme_{l}": len(v_morph[l]) for l in LANGS},
        "v_movoc": len(merged),
    })
    io.write_config("movoc_config.json", config)

    if args.skip_step6:
        print(f"\nStep 7 -- returned V_MoVoC: {out}")
        return

    print("\nStep 6 -- Train_MoVoC_Model(V_MoVoC): constrained merges")
    for lang in LANGS:
        cons = tokenizer.load_constraints([annotation.VOCAB_SOURCES[lang]])
        print(f"  [{lang}] morpheme-boundary constraints: {len(cons)} words")
        wf = tokenizer.word_frequencies(corpora[lang], args.merge_lines)
        merges = tokenizer.learn_merges(wf, cons, sizes["s_bpe"])
        path = io.MODELS / f"movoc_tok_merges_{lang}.txt"
        tokenizer.save_merges(merges, path)
        print(f"  [{lang}] learned {len(merges)} constrained merges -> {path}")

    print(f"\nStep 7 -- returned V_MoVoC: {out}")


if __name__ == "__main__":
    main()
