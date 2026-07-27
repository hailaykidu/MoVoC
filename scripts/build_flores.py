"""
build_flores.py -- extract the FLORES-200 dev/devtest sets (paper Sec 5.1).

Amharic and Tigrinya are directly supported by FLORES-200 (Goyal et al.,
2022), so its development and test sets are used for automatic evaluation.
This pulls `amh_Ethi` and `tir_Ethi` alongside `eng_Latn` from FLORES+, the
openly maintained continuation of the benchmark, and writes plain aligned
text.

Sentences are paired by their FLORES sentence `id`, not by line order, so
the alignment is guaranteed rather than assumed.
"""

import argparse
import json
from pathlib import Path

LANGUAGES = {"amharic": "amh_Ethi", "tigrinya": "tir_Ethi"}
ENGLISH = "eng_Latn"
SPLITS = ("dev", "devtest")
DATASET = "openlanguagedata/flores_plus"


def read_split(root: Path, split: str, code: str) -> dict:
    path = root / split / f"{code}.jsonl"
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r["text"].strip()
                for r in (json.loads(l) for l in f)}


def main():
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Extract FLORES-200 dev/devtest")
    p.add_argument("--flores-dir", type=Path, default=None,
                   help="local FLORES+ checkout; downloaded if omitted")
    p.add_argument("-o", "--out-dir", type=Path,
                   default=here / "data/evaluation")
    args = p.parse_args()

    root = args.flores_dir
    if root is None:
        from huggingface_hub import snapshot_download
        root = Path(snapshot_download(
            DATASET, repo_type="dataset",
            allow_patterns=["*amh_Ethi*", "*tir_Ethi*", "*eng_Latn*"]))
        print(f"FLORES+ -> {root}")

    for split in SPLITS:
        eng = read_split(root, split, ENGLISH)
        for lang, code in LANGUAGES.items():
            tgt = read_split(root, split, code)
            ids = sorted(set(eng) & set(tgt))
            out = args.out_dir / lang
            out.mkdir(parents=True, exist_ok=True)
            ext = "am" if lang == "amharic" else "ti"
            with open(out / f"flores_{split}.en", "w", encoding="utf-8") as f:
                f.write("\n".join(eng[i] for i in ids) + "\n")
            with open(out / f"flores_{split}.{ext}", "w", encoding="utf-8") as f:
                f.write("\n".join(tgt[i] for i in ids) + "\n")
            print(f"  {split:8} {lang:9} {len(ids)} aligned sentences")


if __name__ == "__main__":
    main()
