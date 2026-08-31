"""Construct the MoVoC hybrid vocabulary (Algorithm 1, paper Sec. 3.2).

Implements the published algorithm step by step, with no additional selection
rules:

    slang      = s / N            (N = number of languages)
    sBPE       = slang * (1 - r)
    smorpheme  = slang * r

    for each language:
        V_BPE[lang]      = first sBPE entries of the trained BPE vocabulary
        V_morpheme[lang] = top smorpheme morphemes by descending frequency
    V_MoVoC = union of all V_BPE[lang] and V_morpheme[lang]

BPE vocabularies are read from the already-trained SentencePiece models in
their native order; nothing is retrained and no token order is changed.
Morphemes come from the HornMorpho segmentation datasets, counted over unique
morpheme types rather than occurrences.

Where a language has fewer distinct morphemes than ``smorpheme``, every
available morpheme is taken -- selecting the top-k of a set smaller than k is
the whole set. This is recorded in the statistics as ``budget_unfilled`` so
the shortfall is visible rather than silent.

Usage:
    python scripts/build_movoc_vocab.py --outdir movoc
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import sentencepiece as spm

#: Placeholder used by the segmentation datasets for an absent category.
PLACEHOLDER = "–"
MORPHEME_FIELDS = ("prefix", "root", "suffix", "infix", "clitic")

#: Published MoVoC parameters (configs/movoc_config.json of the MoVoC paper
#: repository): s = 224,000 over two languages with r = 5/7, giving
#: slang = 112,000, sBPE = 32,000 and smorpheme = 80,000.
DEFAULT_TOTAL_VOCAB = 224_000
DEFAULT_R = 0.7142857142857143

LANGUAGES = ("Amharic", "Tigrinya")

#: Official MoVoC annotation datasets released with the paper. Used only to
#: supplement the morpheme vocabulary when HornMorpho alone cannot fill
#: ``s_morpheme``.
ANNOTATION_ROOT = (
    "/homes/neumann/teklehaymanot/TigrinyaTokenizer/MPETokenization/Paralleldata"
    "/MoVoC-official/data/annotations"
)


def allocate(s: int, r: float, n_languages: int) -> dict[str, int]:
    """Step 2 -- vocabulary size allocation, exactly as published."""
    slang = s / n_languages
    return {
        "s": s,
        "r": r,
        "n_languages": n_languages,
        "s_lang": int(slang),
        "s_bpe": int(slang * (1 - r)),
        "s_morpheme": int(slang * r),
    }


def load_bpe_vocab(model_dir: Path, limit: int) -> list[str]:
    """Step 3 -- first ``limit`` entries of a trained BPE vocabulary.

    Order is the SentencePiece model's own piece order, preserved as-is.
    """
    processor = spm.SentencePieceProcessor(
        model_file=str(model_dir / "tokenizer.model")
    )
    pieces = [processor.id_to_piece(i) for i in range(processor.get_piece_size())]
    return pieces[:limit]


def count_morphemes(dataset: Path) -> Counter:
    """Frequency of each distinct morpheme in a segmentation dataset."""
    records = json.loads(dataset.read_text(encoding="utf-8"))
    counts: Counter = Counter()
    for record in records:
        for field in MORPHEME_FIELDS:
            value = record.get(field, PLACEHOLDER)
            if value and value != PLACEHOLDER:
                counts.update(
                    part for part in value.split("-") if part and part != PLACEHOLDER
                )
    return counts


def count_annotation_morphemes(path: Path) -> Counter:
    """Frequency of each morpheme in an official MoVoC annotation file.

    The released annotation files use two different shapes: the Amharic set
    capitalizes its keys and marks absence with ``null``; the Tigrinya set uses
    lowercase keys, marks absence with ``-``, and writes affixes with a leading
    hyphen (``-ት``) as segmentation notation. Both are normalized here, and the
    notation hyphen is stripped so the stored morpheme is the morpheme itself.
    """
    records = json.loads(path.read_text(encoding="utf-8"))
    counts: Counter = Counter()
    for record in records:
        for key, value in record.items():
            if key.lower() in ("no", "word"):
                continue
            if not value or not isinstance(value, str):
                continue
            for part in value.split("-"):
                part = part.strip()
                if part and part != PLACEHOLDER:
                    counts[part] += 1
    return counts


def select_morphemes(counts: Counter, limit: int) -> list[tuple[str, int]]:
    """Step 4 -- unique morphemes, ranked by descending frequency, top ``limit``.

    Ties are broken by the morpheme string so the selection is deterministic.
    """
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path("movoc"))
    parser.add_argument("--total-vocab-size", type=int, default=DEFAULT_TOTAL_VOCAB)
    parser.add_argument("--r", type=float, default=DEFAULT_R)
    parser.add_argument(
        "--amharic-bpe", type=Path, default=Path("tokenizers/amharic_bpe_32k")
    )
    parser.add_argument(
        "--tigrinya-bpe", type=Path, default=Path("tokenizers/tigrinya_bpe_32k")
    )
    parser.add_argument(
        "--amharic-morphemes",
        type=Path,
        default=Path("data/segmented/amharic_morpheme_segmented.json"),
    )
    parser.add_argument(
        "--tigrinya-morphemes",
        type=Path,
        default=Path("data/segmented/tigrinya_morpheme_segmented.json"),
    )
    parser.add_argument(
        "--amharic-annotations",
        type=Path,
        default=Path(ANNOTATION_ROOT) / "amharic" / "postedited_morphemes.json",
        help="official MoVoC Amharic annotations, used only if HornMorpho "
        "morphemes cannot fill s_morpheme",
    )
    parser.add_argument(
        "--tigrinya-annotations",
        type=Path,
        # The Tigrinya gold set is deliberately NOT used: the paper holds it
        # out of vocabulary construction for evaluation.
        default=Path(ANNOTATION_ROOT) / "tigrinya" / "postedited_morphemes.json",
        help="official MoVoC Tigrinya annotations (post-edited set only)",
    )
    args = parser.parse_args()

    sizes = allocate(args.total_vocab_size, args.r, len(LANGUAGES))
    print(
        f"Step 2 -- s={sizes['s']:,} r={sizes['r']:.10f} N={sizes['n_languages']}\n"
        f"  s_lang={sizes['s_lang']:,}  s_BPE={sizes['s_bpe']:,}  "
        f"s_morpheme={sizes['s_morpheme']:,}"
    )

    bpe_dirs = {"Amharic": args.amharic_bpe, "Tigrinya": args.tigrinya_bpe}
    morph_files = {
        "Amharic": args.amharic_morphemes,
        "Tigrinya": args.tigrinya_morphemes,
    }

    bpe_vocabs: dict[str, list[str]] = {}
    morph_vocabs: dict[str, list[tuple[str, int]]] = {}
    morph_totals: dict[str, int] = {}

    for language in LANGUAGES:
        bpe_vocabs[language] = load_bpe_vocab(bpe_dirs[language], sizes["s_bpe"])
        print(f"Step 3 -- {language} BPE: {len(bpe_vocabs[language]):,} entries")

    annotation_files = {
        "Amharic": args.amharic_annotations,
        "Tigrinya": args.tigrinya_annotations,
    }
    provenance: dict[str, dict[str, list[str]]] = {}
    supplement_report: dict[str, dict[str, int]] = {}

    for language in LANGUAGES:
        counts = count_morphemes(morph_files[language])
        hornmorpho_types = set(counts)
        morph_totals[language] = len(counts)
        origins = {token: ["HornMorpho"] for token in counts}

        added = 0
        overlap = 0
        annotation_available = 0
        path = annotation_files[language]

        # Supplement only when HornMorpho alone cannot fill the budget.
        if len(counts) < sizes["s_morpheme"] and path and path.exists():
            annotated = count_annotation_morphemes(path)
            annotation_available = len(annotated)
            for token, frequency in annotated.items():
                if token in hornmorpho_types:
                    # Present in both: frequencies combine, provenance records
                    # both sources.
                    counts[token] += frequency
                    origins[token] = ["HornMorpho", "MoVoC_annotation"]
                    overlap += 1
                else:
                    counts[token] = frequency
                    origins[token] = ["MoVoC_annotation"]
                    added += 1

        provenance[language] = origins
        morph_vocabs[language] = select_morphemes(counts, sizes["s_morpheme"])
        supplement_report[language] = {
            "hornmorpho_morphemes": len(hornmorpho_types),
            "annotation_morphemes_available": annotation_available,
            "annotation_morphemes_added": added,
            "duplicates_removed_between_sources": overlap,
            "combined_unique_morphemes": len(counts),
            "selected_for_v_morpheme": len(morph_vocabs[language]),
            "s_morpheme": sizes["s_morpheme"],
            "annotation_file": str(path.resolve()) if path and path.exists() else None,
        }
        print(
            f"Step 4 -- {language} morphemes: {len(hornmorpho_types):,} HornMorpho "
            f"+ {added:,} annotation ({overlap:,} shared) = {len(counts):,} unique; "
            f"{len(morph_vocabs[language]):,} selected (budget {sizes['s_morpheme']:,})"
        )

    # Step 5 -- union, preserving uniqueness. Insertion order is BPE first then
    # morphemes, per language, so the result is deterministic. A token already
    # present is not added again; the first source to contribute it wins, and
    # every collision is counted.
    entries: list[dict[str, object]] = []
    seen: dict[str, dict[str, object]] = {}
    duplicates: list[dict[str, str]] = []

    for language in LANGUAGES:
        for token in bpe_vocabs[language]:
            if token in seen:
                duplicates.append(
                    {
                        "token": token,
                        "kept_from": f"{seen[token]['language']}/{seen[token]['type']}",
                        "duplicate_from": f"{language}/BPE",
                    }
                )
                continue
            entry = {
                "token": token,
                "type": "BPE",
                "language": language,
                "source": "SentencePiece",
            }
            seen[token] = entry
            entries.append(entry)

    for language in LANGUAGES:
        for token, frequency in morph_vocabs[language]:
            if token in seen:
                duplicates.append(
                    {
                        "token": token,
                        "kept_from": f"{seen[token]['language']}/{seen[token]['type']}",
                        "duplicate_from": f"{language}/morpheme",
                    }
                )
                continue
            origin = provenance[language].get(token, ["HornMorpho"])
            entry = {
                "token": token,
                "type": "morpheme",
                "language": language,
                "frequency": frequency,
                "source": origin[0] if len(origin) == 1 else origin,
            }
            seen[token] = entry
            entries.append(entry)

    total_contributed = sum(len(v) for v in bpe_vocabs.values()) + sum(
        len(v) for v in morph_vocabs.values()
    )

    # Step 6 -- save.
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "movoc_vocab.txt").write_text(
        "\n".join(e["token"] for e in entries) + "\n", encoding="utf-8"
    )
    (args.outdir / "movoc_vocab.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    stats = {
        "algorithm": "MoVoC Algorithm 1 (paper Sec. 3.2)",
        "parameters": sizes,
        "total_vocabulary_size": len(entries),
        "final_vocabulary_size": len(entries),
        "amharic_bpe_tokens": len(bpe_vocabs["Amharic"]),
        "tigrinya_bpe_tokens": len(bpe_vocabs["Tigrinya"]),
        "amharic_morphemes": len(morph_vocabs["Amharic"]),
        "tigrinya_morphemes": len(morph_vocabs["Tigrinya"]),
        "total_bpe_tokens_in_vocab": sum(1 for e in entries if e["type"] == "BPE"),
        "total_morphemes_in_vocab": sum(
            1 for e in entries if e["type"] == "morpheme"
        ),
        "tokens_contributed_before_dedup": total_contributed,
        "duplicate_tokens_removed": len(duplicates),
        "morphemes_available": morph_totals,
        "morpheme_sources": supplement_report,
        "budget_unfilled": {
            language: sizes["s_morpheme"] - len(morph_vocabs[language])
            for language in LANGUAGES
        },
        "inputs": {
            "amharic_bpe": str(bpe_dirs["Amharic"].resolve()),
            "tigrinya_bpe": str(bpe_dirs["Tigrinya"].resolve()),
            "amharic_morphemes": str(morph_files["Amharic"].resolve()),
            "tigrinya_morphemes": str(morph_files["Tigrinya"].resolve()),
        },
        "duplicate_examples": duplicates[:20],
    }
    (args.outdir / "movoc_statistics.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"\nStep 5 -- union: {total_contributed:,} contributed, "
        f"{len(duplicates):,} duplicates removed, {len(entries):,} final"
    )
    print(f"Step 6 -- wrote {args.outdir}/movoc_vocab.txt")
    print(f"          wrote {args.outdir}/movoc_vocab.json")
    print(f"          wrote {args.outdir}/movoc_statistics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
