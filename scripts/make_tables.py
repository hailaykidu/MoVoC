"""
make_tables.py -- regenerate the result tables from repository outputs.

Reads whatever evaluation/results/ contains and renders it as Markdown.
Nothing is hardcoded: every figure comes from a file produced by
evaluate.py or translate_eval.py in this repository. If a run has not been
performed, its row is absent rather than filled in.

  Table 4 (intrinsic)  Morpheme Boundary Precision and Renyi entropy
  Table 3 (extrinsic)  BLEU and chrF++ per tokenization strategy
"""

import argparse
import json
from pathlib import Path

ARM_LABELS = {
    "movoc_tok": "MoVoC-Tok",
    "movoc_vocab": "MoVoC vocabulary",
    "bpe": "BPE",
    "wordpiece": "WordPiece",
    "sp_shared": "SentencePiece (shared)",
}

LANG_LABELS = {"amharic": "Amharic", "tigrinya": "Tigrinya",
               "tigre": "Tigre", "geez": "Ge'ez"}


def intrinsic_table(path: Path) -> str:
    if not path.exists():
        return "_No intrinsic results yet — run `evaluate.py`._\n"
    data = json.load(open(path, encoding="utf-8"))
    alpha = data.get("alpha", 2.0)

    out = [f"### Intrinsic evaluation (alpha = {alpha})", "",
           "| Language | Tokenization | Boundary Precision ↑ | MorphScore ↑ | "
           "Rényi entropy ↓ | Gold words |",
           "|---|---|---|---|---|---|"]
    for row in data.get("results", []):
        lang = LANG_LABELS.get(row["language"], row["language"])
        if "error" in row:
            out.append(f"| {lang} | — | _{row['error']}_ | | | |")
            continue
        for arm in ARM_LABELS:
            if arm not in row:
                continue
            a = row[arm]
            out.append(f"| {lang} | {ARM_LABELS[arm]} | "
                       f"{a['boundary_precision']} | {a['morphscore']} | "
                       f"{a['renyi_entropy']} | {row['gold_words']} |")
    out.append("")
    out.append("Boundary Precision is computed over multi-morphemic gold "
               "words; see `movoc/metrics.py`.")
    return "\n".join(out) + "\n"


def is_multiseed(data: dict) -> bool:
    """Aggregate multi-seed schema, as written by scripts/score_multiseed.py.

    That file reports mean +/- std over seeds under "cells" rather than a
    single figure per direction under "results", so it cannot be rendered by
    the per-arm path below.
    """
    return "cells" in data and "results" not in data


def multiseed_table(data: dict, source: Path) -> str:
    """Render the aggregate multi-seed schema: one row per reported cell.

    Cells the scorer declined to report (fewer than two seeds, so no standard
    deviation) are listed after the table rather than dropped silently.
    """
    out = [f"#### Multi-seed aggregate — `{source.name}`", "",
           f"Seeds {', '.join(str(s) for s in data.get('seeds_requested', []))}; "
           f"{data.get('usable_runs', '?')} usable runs.", ""]

    note = data.get("not_a_reproduction")
    if note:
        out += [f"_{note}_", ""]

    out += ["| Trained on | Eval language | Tokenization | Type | "
            "BLEU ↑ (mean ± std) | chrF++ ↑ (mean ± std) | Seeds |",
            "|---|---|---|---|---|---|---|"]

    def order(cell):
        return (cell.get("trained_on", ""),
                list(LANG_LABELS).index(cell["eval_language"])
                if cell["eval_language"] in LANG_LABELS else 99,
                cell.get("tokenizer", ""))

    skipped = []
    for c in sorted(data.get("cells", []), key=order):
        if not c.get("reported"):
            skipped.append(c)
            continue
        trained = LANG_LABELS.get(c.get("trained_on"), c.get("trained_on"))
        lang = LANG_LABELS.get(c["eval_language"], c["eval_language"])
        arm = ARM_LABELS.get(c["tokenizer"], c["tokenizer"])
        kind = "supervised" if c["eval_language"] == c.get("trained_on") \
            else "zero-shot"
        out.append(
            f"| {trained} | {lang} | {arm} | {kind} | "
            f"{c['BLEU_mean']:.4f} ± {c['BLEU_std']:.4f} | "
            f"{c['chrF++_mean']:.4f} ± {c['chrF++_std']:.4f} | "
            f"{c.get('n_seeds', '')} |")

    for c in skipped:
        arm = ARM_LABELS.get(c["tokenizer"], c["tokenizer"])
        lang = LANG_LABELS.get(c["eval_language"], c["eval_language"])
        out += ["", f"_Not reported — {lang} / {arm}: "
                    f"{c.get('reason', 'unreported')}._"]

    for e in data.get("excluded_runs", []):
        out += ["", f"_Excluded — {e.get('language')}/{e.get('tokenizer')}/"
                    f"seed{e.get('seed')}: {e.get('reason')}._"]

    return "\n".join(out) + "\n"


def extrinsic_table(results_dir: Path, multiseed: Path = None) -> str:
    files = sorted(results_dir.glob("table3_*.json"))
    if multiseed and multiseed.exists():
        files.append(multiseed)
    if not files:
        return ("_No translation results yet — run "
                "`scripts/run_table3.sh`._\n")

    out = ["### Extrinsic evaluation (machine translation)", ""]
    rows, extra = [], []
    for f in files:
        data = json.load(open(f, encoding="utf-8"))
        # The aggregate multi-seed file carries mean/std per cell and has no
        # per-direction "results" block; it gets its own renderer below.
        if is_multiseed(data):
            extra.append(multiseed_table(data, f))
            continue
        parts = f.stem.split("_")          # table3_<lang>_<strategy>
        lang = LANG_LABELS.get(parts[1], parts[1])
        arm = ARM_LABELS.get("_".join(parts[2:]), "_".join(parts[2:]))
        for direction, r in data.get("results", {}).items():
            tag = " (zero-shot)" if r.get("zero_shot") else ""
            rows.append(f"| {lang} | {arm} | {direction}{tag} | "
                        f"{r['bleu']} | {r['chrf++']} | {r['n']} |")

    if rows:
        out += ["| Language | Tokenization | Direction | BLEU ↑ | chrF++ ↑ | n |",
                "|---|---|---|---|---|---|"] + rows
    elif not extra:
        return ("_No translation results yet — run "
                "`scripts/run_table3.sh`._\n")

    for block in extra:
        out += ["", block]
    return "\n".join(out) + "\n"


def main():
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Regenerate result tables")
    p.add_argument("--results-dir", type=Path,
                   default=here / "evaluation/results")
    p.add_argument("-o", "--out", type=Path,
                   default=here / "evaluation/results/RESULTS.md")
    p.add_argument("--multiseed", type=Path,
                   default=here / "experiments/multiseed/results"
                                  "/table3_multiseed.json",
                   help="aggregate multi-seed results, if present")
    args = p.parse_args()

    body = "\n".join([
        "# Results",
        "",
        "Generated by `scripts/make_tables.py` from the contents of",
        "`evaluation/results/`. Every figure below was produced by this",
        "repository; nothing is copied from the paper.",
        "",
        intrinsic_table(args.results_dir / "intrinsic_eval.json"),
        "",
        extrinsic_table(args.results_dir, args.multiseed),
    ])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body, encoding="utf-8")
    print(body)
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
