"""
build_geez_zeroshot_split.py -- held-out English-Ge'ez evaluation split.

Creates a reproducible held-out split for an ADDITIONAL ZERO-SHOT
evaluation of English->Ge'ez.

WHAT THIS IS NOT
----------------
This is **not** a reproduction of the published Table 3 Ge'ez score. That
block cannot be reproduced from released artifacts: the paper states
(Sec. 4.2) that Ge'ez "was evaluated only intrinsically" for want of
parallel data, no held-out Ge'ez set survives, and the scoring pipeline
behind the reported figures is unavailable. See docs/REPRODUCIBILITY.md §1.

WHY A ZERO-SHOT SPLIT IS SOUND HERE
-----------------------------------
The models under evaluation are fine-tuned on English-Amharic and
English-Tigrinya NLLB data only, and their vocabularies are built from
those same two corpora. No Ge'ez text enters training or tokenizer
construction at any point, so every sentence in this corpus is unseen.
Ge'ez is therefore evaluated on the same footing as Tigre: a Ge'ez-script
language held out entirely, measuring cross-lingual transfer.

The corpus is used for EVALUATION ONLY. It must not be added to training
or tokenizer training -- doing so would destroy the zero-shot property this
split exists to measure.

CORPUS
------
Mermru English-Ge'ez parallel corpus (https://mermru.com/), 2,107
verse-aligned pairs of biblical text, distributed via the Bedru/Eng-Geez
dataset on the HuggingFace Hub.

SPLIT
-----
A fixed seed selects a held-out subset. The seed, the indices and a
checksum of the emitted files are recorded in the manifest so the split can
be regenerated and verified exactly.
"""

import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARROW = (Path.home() / ".cache/huggingface/datasets/Bedru___eng-geez"
                 / "default/0.0.0"
                 / "1a9438956b247dcb1dfae772794f7bae13c6f2e9"
                 / "eng-geez-train.arrow")

SEED = 42
HELD_OUT = 100          # matches the per-language size the paper describes


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arrow", type=Path, default=DEFAULT_ARROW,
                   help="cached Bedru/Eng-Geez arrow file")
    p.add_argument("--out-dir", type=Path,
                   default=ROOT / "data" / "evaluation" / "geez")
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--n", type=int, default=HELD_OUT)
    args = p.parse_args()

    from datasets import Dataset

    if not args.arrow.exists():
        raise SystemExit(
            f"corpus not found at {args.arrow}\n"
            f"Fetch it with:  "
            f"python -c \"from datasets import load_dataset; "
            f"load_dataset('Bedru/Eng-Geez')\"")

    ds = Dataset.from_file(str(args.arrow))
    pairs = [(r["English"].strip(), r["Geez"].strip()) for r in ds]
    # Drop empties and exact duplicates before sampling: an empty reference
    # makes BLEU undefined, and duplicates would let one sentence carry
    # more weight than another in a 100-pair set.
    seen, clean = set(), []
    for en, gez in pairs:
        if not en or not gez or (en, gez) in seen:
            continue
        seen.add((en, gez))
        clean.append((en, gez))

    if len(clean) < args.n:
        raise SystemExit(f"only {len(clean)} usable pairs; need {args.n}")

    rng = random.Random(args.seed)
    indices = sorted(rng.sample(range(len(clean)), args.n))
    held_out = [clean[i] for i in indices]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    src_path = args.out_dir / "test.en"
    ref_path = args.out_dir / "test.gez"
    src_path.write_text("\n".join(en for en, _ in held_out) + "\n",
                        encoding="utf-8")
    ref_path.write_text("\n".join(gez for _, gez in held_out) + "\n",
                        encoding="utf-8")

    manifest = {
        "purpose": ("additional zero-shot English->Ge'ez evaluation; NOT a "
                    "reproduction of the published Table 3 Ge'ez score"),
        "corpus": {
            "name": "Mermru English-Ge'ez parallel corpus",
            "origin": "https://mermru.com/",
            "distributed_via": "Bedru/Eng-Geez (HuggingFace Hub)",
            "total_pairs": len(ds),
            "usable_after_cleaning": len(clean),
            "cleaning": "dropped empty sides and exact duplicate pairs",
        },
        "split": {
            "seed": args.seed,
            "held_out_pairs": args.n,
            "selection": "random.Random(seed).sample over cleaned pairs",
            "indices": indices,
        },
        "files": {
            "source": str(src_path.relative_to(ROOT)),
            "reference": str(ref_path.relative_to(ROOT)),
            "source_sha256": sha256(src_path),
            "reference_sha256": sha256(ref_path),
        },
        "usage": {
            "evaluation_only": True,
            "excluded_from": ["MT training", "tokenizer training",
                              "vocabulary construction"],
            "rationale": ("The evaluated models train on English-Amharic and "
                          "English-Tigrinya NLLB data only, and their "
                          "vocabularies are built from those corpora, so no "
                          "Ge'ez text is seen during training."),
        },
    }
    manifest_path = args.out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2,
                                        ensure_ascii=False), encoding="utf-8")

    print(f"  corpus       {len(ds)} pairs -> {len(clean)} usable")
    print(f"  held out     {args.n} pairs (seed {args.seed})")
    print(f"  source       {src_path.relative_to(ROOT)}")
    print(f"  reference    {ref_path.relative_to(ROOT)}")
    print(f"  manifest     {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
