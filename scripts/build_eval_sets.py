"""
build_eval_sets.py -- assemble the OPUS test sets (paper Sec 5.1).

Test data is 100 sentence pairs per target language, drawn from the OPUS
parallel corpus (Tiedemann, 2012) via its Tatoeba corpus:

    Amharic   100 of 213 available from OPUS
    Tigrinya   74 from OPUS + 26 human-validated
    Tigre      45 from OPUS + 55 human-validated

Pairs where either side is empty are dropped -- an empty reference makes
BLEU undefined and inflates chrF -- so the usable OPUS counts come out
slightly below the raw line counts. The shortfall against 100 is reported
per language; filling it requires the human-validated pairs, which are not
part of this repository.

Ge'ez is not built: it has no parallel data and is evaluated intrinsically.
"""

import argparse
import json
from pathlib import Path

# language -> (english side, target side, target file extension)
SOURCES = {
    "amharic": ("Tatoeba.am-en.en", "Tatoeba.am-en.am", "am"),
    "tigrinya": ("Tatoeba.en-ti.en", "Tatoeba.en-ti.ti", "ti"),
    "tigre": ("Tatoeba.en-tig.en", "Tatoeba.en-tig.tig", "tig"),
}

TARGET_PAIRS = 100


def read_pairs(src: Path, tgt: Path):
    s = [l.rstrip("\n") for l in open(src, encoding="utf-8")]
    t = [l.rstrip("\n") for l in open(tgt, encoding="utf-8")]
    if len(s) != len(t):
        raise SystemExit(f"{src.name}/{tgt.name} misaligned: {len(s)} vs {len(t)}")
    return [(a.strip(), b.strip()) for a, b in zip(s, t)
            if a.strip() and b.strip()]


def main():
    p = argparse.ArgumentParser(description="Build OPUS test sets")
    p.add_argument("--opus-dir", type=Path, required=True,
                   help="directory holding the Tatoeba.* files")
    p.add_argument("-o", "--out-dir", type=Path,
                   default=Path(__file__).resolve().parent.parent
                   / "data/evaluation")
    args = p.parse_args()

    manifest = {}
    for lang, (src_name, tgt_name, ext) in SOURCES.items():
        src, tgt = args.opus_dir / src_name, args.opus_dir / tgt_name
        if not src.exists() or not tgt.exists():
            print(f"  {lang:9} skipped -- {src_name} not found")
            continue

        raw = len(open(src, encoding="utf-8").readlines())
        pairs = read_pairs(src, tgt)[:TARGET_PAIRS]

        out = args.out_dir / lang
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "test.en", "w", encoding="utf-8") as f:
            f.write("\n".join(a for a, _ in pairs) + "\n")
        with open(out / f"test.{ext}", "w", encoding="utf-8") as f:
            f.write("\n".join(b for _, b in pairs) + "\n")

        shortfall = TARGET_PAIRS - len(pairs)
        manifest[lang] = {
            "source": "OPUS / Tatoeba (Tiedemann, 2012)",
            "raw_lines": raw,
            "usable_opus_pairs": len(pairs),
            "target_pairs": TARGET_PAIRS,
            "human_validated_needed": shortfall,
        }
        note = "complete" if not shortfall else \
               f"needs {shortfall} human-validated pairs"
        print(f"  {lang:9} {raw:3} raw -> {len(pairs):3} usable  ({note})")

    manifest["geez"] = {
        "source": "none -- no parallel data",
        "note": "evaluated intrinsically only (paper Sec 5.1)",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with open(args.out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nmanifest -> {args.out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
