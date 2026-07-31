"""
score_multiseed.py -- Table 3 of the reconstructed evaluation.

Decodes every completed checkpoint from the multi-seed campaign, scores BLEU
and chrF++ with one metric implementation, and reports mean +/- standard
deviation over the seeds that actually finished.

This is a reconstructed evaluation following the MoVoC evaluation protocol.
It is NOT a reproduction of the paper's Table 3: the original scoring
pipeline is unavailable and the scale of the published BLEU column is
unresolved, so these values are not comparable to it.

Validation rules, applied before anything is reported:
  * a checkpoint counts as complete only if its trainer_state.json records
    global_step == max_steps and should_training_stop is true;
  * every generation id must be in range for the checkpoint's vocabulary,
    otherwise decoding is skipped and the run excluded;
  * a cell is reported only if at least two seeds survived, since a single
    run cannot carry a standard deviation.

Excluded runs are listed explicitly in the output rather than dropped
silently.

Usage
    python scripts/score_multiseed.py                 # score everything ready
    python scripts/score_multiseed.py --dry-run       # report readiness only
"""

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EXP = ROOT / "experiments" / "multiseed"
SEEDS = (42, 43, 44)
TOKENIZERS = ("bpe", "wordpiece", "movoc_tok")
TRAINED = ("amharic", "tigrinya")

# Supervised direction per trained language, plus the zero-shot languages
# every checkpoint is additionally evaluated on.
DIRECTION = {"amharic": "en-am", "tigrinya": "en-ti",
             "tigre": "en-tig", "geez": "en-gez"}
EVAL_SETS = {
    "amharic": ("data/evaluation/amharic/test.en", "data/evaluation/amharic/test.am"),
    "tigrinya": ("data/evaluation/tigrinya/test.en", "data/evaluation/tigrinya/test.ti"),
    "tigre": ("data/evaluation/tigre/test.en", "data/evaluation/tigre/test.tig"),
    "geez": ("data/evaluation/geez/test.en", "data/evaluation/geez/test.gez"),
}
ZERO_SHOT = ("tigre", "geez")
DECODING = {"num_beams": 1, "max_length": 128, "batch_size": 8}


def checkpoint_complete(ckpt: Path):
    """(ok, detail). A run is complete only if the Trainer says it finished."""
    if not ckpt.exists():
        return False, "no checkpoint directory"
    states = sorted(ckpt.glob("checkpoint-*/trainer_state.json"))
    state = ckpt / "trainer_state.json"
    path = state if state.exists() else (states[-1] if states else None)
    if path is None:
        return False, "no trainer_state.json"
    s = json.loads(path.read_text())
    step, mx = s.get("global_step"), s.get("max_steps")
    stop = (s.get("stateful_callbacks", {}).get("TrainerControl", {})
             .get("args", {}).get("should_training_stop"))
    if step != mx or not stop:
        return False, f"incomplete: step {step}/{mx}, stop={stop}"
    if not (ckpt / "model.safetensors").exists():
        return False, "no model.safetensors"
    return True, f"complete at step {step}"


def generation_ids_valid(ckpt: Path):
    """Catch the defect that invalidated the 2026-07-28 run before decoding."""
    cfg = json.loads((ckpt / "config.json").read_text())
    vocab = cfg.get("vocab_size")
    gen_path = ckpt / "generation_config.json"
    gen = json.loads(gen_path.read_text()) if gen_path.exists() else {}
    bad = []
    for field in ("pad_token_id", "eos_token_id", "decoder_start_token_id",
                  "forced_eos_token_id", "bos_token_id"):
        v = gen.get(field, cfg.get(field))
        if v is not None and not (0 <= v < vocab):
            bad.append(f"{field}={v}")
    # bad_words_ids is deliberately not checked. translate() calls
    # align_special_tokens(), which sets it to None before a single token is
    # generated, so a stale inherited value never reaches generate(). Several
    # checkpoints serialized the base model's [[63049]]; against a 32k
    # vocabulary that id is out of range, but it is a dead field in the saved
    # config rather than a decoding fault. Rejecting on it excluded runs whose
    # weights are sound -- and could not catch the inverse case anyway, where
    # the same id is in range for a 144k vocabulary and would silently
    # suppress an unrelated token. Clearing it at load time handles both.
    return (not bad), bad


def translate(ckpt: Path, sentences: list) -> list:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch

    from evaluation.finetune_marianmt import align_special_tokens

    tok = AutoTokenizer.from_pretrained(str(ckpt))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(ckpt))

    # The saved checkpoints carry a generation_config inherited from the base
    # model: forced_eos_token_id=0 while the tokenizer's eos is 2, and
    # bad_words_ids=[[63049]], an id far outside a 32,000-token vocabulary.
    # Decoding without re-aligning reproduces the 2026-07-28 incident exactly
    # -- generate() raises on the resized arms, and any arm that survives
    # decodes from the wrong start id with an arbitrary token suppressed.
    # Re-aligning here makes scoring independent of what training happened to
    # persist.
    align_special_tokens(model, tok)

    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()

    out = []
    for i in range(0, len(sentences), DECODING["batch_size"]):
        batch = sentences[i:i + DECODING["batch_size"]]
        enc = tok(batch, return_tensors="pt", padding=True, truncation=True,
                  max_length=DECODING["max_length"])
        enc = {k: v for k, v in enc.items()
               if k in ("input_ids", "attention_mask")}
        if torch.cuda.is_available():
            enc = {k: v.cuda() for k, v in enc.items()}
        with torch.no_grad():
            gen = model.generate(**enc, max_length=DECODING["max_length"],
                                 num_beams=DECODING["num_beams"])
        out.extend(tok.batch_decode(gen, skip_special_tokens=True))
    return out


def read_lines(p: Path) -> list:
    return [l.rstrip("\n") for l in open(p, encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report checkpoint readiness without decoding")
    ap.add_argument("-o", "--out", type=Path,
                    default=EXP / "results" / "table3_multiseed.json")
    args = ap.parse_args()

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()

    # ---- inventory: which of the 18 runs are usable ----
    runs, excluded = [], []
    for seed in SEEDS:
        for lang in TRAINED:
            for tok in TOKENIZERS:
                ckpt = EXP / "checkpoints" / f"{lang}_{tok}_seed{seed}"
                ok, detail = checkpoint_complete(ckpt)
                if not ok:
                    excluded.append({"checkpoint": str(ckpt.relative_to(ROOT)),
                                     "seed": seed, "language": lang,
                                     "tokenizer": tok, "reason": detail})
                    continue
                ids_ok, bad = generation_ids_valid(ckpt)
                if not ids_ok:
                    excluded.append({"checkpoint": str(ckpt.relative_to(ROOT)),
                                     "seed": seed, "language": lang,
                                     "tokenizer": tok,
                                     "reason": f"invalid generation ids: {bad}"})
                    continue
                runs.append({"seed": seed, "language": lang,
                             "tokenizer": tok, "checkpoint": ckpt})

    print(f"usable runs: {len(runs)}/18")
    for e in excluded:
        print(f"  EXCLUDED {e['language']}/{e['tokenizer']}/seed{e['seed']}: "
              f"{e['reason']}")

    if args.dry_run:
        print("\ndry run: nothing decoded")
        return
    if not runs:
        print("\nNo usable checkpoint. Table 3 cannot be produced yet; "
              "run scripts/submit_multiseed.sh and wait for jobs to finish.")
        return

    from sacrebleu.metrics import BLEU, CHRF
    bleu, chrf = BLEU(), CHRF(word_order=2)

    # ---- decode + score every (run, evaluation language) ----
    per_run = []
    for r in runs:
        targets = [r["language"]] + list(ZERO_SHOT)
        for eval_lang in targets:
            src_rel, ref_rel = EVAL_SETS[eval_lang]
            src, ref = read_lines(ROOT / src_rel), read_lines(ROOT / ref_rel)
            hyps = translate(r["checkpoint"], src)

            pred = (EXP / "predictions" /
                    f"{r['language']}_{r['tokenizer']}_seed{r['seed']}"
                    f"_{DIRECTION[eval_lang]}.txt")
            pred.parent.mkdir(parents=True, exist_ok=True)
            pred.write_text("\n".join(hyps), encoding="utf-8")

            b = bleu.corpus_score(hyps, [ref])
            c = chrf.corpus_score(hyps, [ref])
            per_run.append({
                "eval_language": eval_lang,
                "direction": DIRECTION[eval_lang],
                "tokenizer": r["tokenizer"],
                "trained_on": r["language"],
                "seed": r["seed"],
                "evaluation_type": ("supervised" if eval_lang == r["language"]
                                    else "zero_shot"),
                "BLEU": round(b.score, 4),
                "chrF++": round(c.score, 4),
                "n": len(hyps),
                "checkpoint": str(r["checkpoint"].relative_to(ROOT)),
                "predictions": str(pred.relative_to(ROOT)),
                "bleu_signature": str(bleu.get_signature()),
                "chrf_signature": str(chrf.get_signature()),
            })
            print(f"  {DIRECTION[eval_lang]} {r['tokenizer']:10} "
                  f"seed{r['seed']} trained_on={r['language']:9} "
                  f"BLEU {b.score:.4f} chrF++ {c.score:.4f} n={len(hyps)}")

    # ---- aggregate: mean +/- std over seeds ----
    agg = {}
    for row in per_run:
        key = (row["eval_language"], row["tokenizer"], row["trained_on"])
        agg.setdefault(key, []).append(row)

    cells = []
    for (eval_lang, tok, trained), rows in sorted(agg.items()):
        bl = [r["BLEU"] for r in rows]
        cf = [r["chrF++"] for r in rows]
        if len(rows) < 2:
            cells.append({"eval_language": eval_lang, "tokenizer": tok,
                          "trained_on": trained, "n_seeds": len(rows),
                          "reported": False,
                          "reason": "fewer than 2 seeds; no std possible",
                          "seeds": [r["seed"] for r in rows]})
            continue
        cells.append({
            "eval_language": eval_lang, "tokenizer": tok,
            "trained_on": trained, "n_seeds": len(rows), "reported": True,
            "seeds": [r["seed"] for r in rows],
            "BLEU_mean": round(statistics.mean(bl), 4),
            "BLEU_std": round(statistics.stdev(bl), 4),
            "chrF++_mean": round(statistics.mean(cf), 4),
            "chrF++_std": round(statistics.stdev(cf), 4),
            "per_seed": {r["seed"]: {"BLEU": r["BLEU"], "chrF++": r["chrF++"],
                                     "checkpoint": r["checkpoint"],
                                     "predictions": r["predictions"]}
                         for r in rows},
        })

    report = {
        "title": ("Reconstructed evaluation following the MoVoC evaluation "
                  "protocol -- Table 3 layout"),
        "not_a_reproduction": (
            "Not a reproduction of the published Table 3. The original "
            "scoring pipeline is unavailable and the scale of the published "
            "BLEU column is unresolved, so these values are not comparable "
            "to it."),
        "generated": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "seeds_requested": list(SEEDS),
        "decoding": DECODING,
        "metrics": {"library": "sacrebleu",
                    "bleu_signature": str(bleu.get_signature()),
                    "chrf_signature": str(chrf.get_signature()),
                    "scale": "0-100 for both"},
        "usable_runs": len(runs),
        "excluded_runs": excluded,
        "per_run": per_run,
        "cells": cells,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")

    # ---- print the paper-layout table ----
    for eval_lang in ("amharic", "tigrinya", "tigre", "geez"):
        rel = [c for c in cells
               if c["eval_language"] == eval_lang and c.get("reported")]
        if not rel:
            continue
        label = {"amharic": "Amharic", "tigrinya": "Tigrinya",
                 "tigre": "Tigre", "geez": "Ge'ez"}[eval_lang]
        zs = " (zero-shot)" if eval_lang in ZERO_SHOT else ""
        print(f"\n## English -> {label}{zs}\n")
        print("| Strategy | BLEU ↑ | chrF++ ↑ |")
        print("|---|---|---|")
        best_b = max(c["BLEU_mean"] for c in rel)
        best_c = max(c["chrF++_mean"] for c in rel)
        for c in sorted(rel, key=lambda x: TOKENIZERS.index(x["tokenizer"])):
            name = {"bpe": "BPE", "wordpiece": "WordPiece",
                    "movoc_tok": "MoVoC-Tok"}[c["tokenizer"]]
            b = f"{c['BLEU_mean']:.4f} ± {c['BLEU_std']:.4f}"
            f = f"{c['chrF++_mean']:.4f} ± {c['chrF++_std']:.4f}"
            if c["BLEU_mean"] == best_b:
                b = f"**{b}**"
            if c["chrF++_mean"] == best_c:
                f = f"**{f}**"
            print(f"| {name} | {b} | {f} |")

    print(f"\nwrote {args.out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
