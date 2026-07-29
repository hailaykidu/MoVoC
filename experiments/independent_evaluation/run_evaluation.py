"""
run_evaluation.py -- independent reproducibility evaluation of the MoVoC
tokenizer comparison.

THIS IS NOT A REPRODUCTION OF THE PUBLISHED TABLE 3. The scoring pipeline
behind the paper's figures was not recovered, and the scale of its BLEU
column is unresolved, so nothing produced here can be compared against it.
What this measures is the *relative* ordering of BPE, WordPiece and
MoVoC-Tok under identical conditions, with the tokenizer as the only
variable.

Reads configs/independent_evaluation.yaml. Writes predictions, per-run
results and a combined tokenizer_comparison.json under
experiments/independent_evaluation/.

Stages:
  --verify    pre-flight checks only; loads every tokenizer, resizes the
              backbone against each, asserts the generation config is
              valid, and scores a tiny sample end to end. No training.
  --score     decode + score existing checkpoints.
  (default)   verify, then score whatever checkpoints exist.

Training itself is submitted separately (scripts/submit_marianmt.sh); this
script never launches a multi-hour job implicitly.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "experiments" / "independent_evaluation"


def load_config():
    import yaml
    with open(ROOT / "configs" / "independent_evaluation.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_tokenizer(cfg, tokenizer_name, language):
    """Load one tokenizer arm exactly as training will."""
    from tokenizers import Tokenizer as HFTokenizer
    from transformers import PreTrainedTokenizerFast

    path = ROOT / cfg["tokenizers"][tokenizer_name][language]
    if not path.exists():
        raise FileNotFoundError(
            f"{tokenizer_name}/{language} tokenizer not found at {path}. "
            f"MoVoC-Tok tables are produced by train.py; BPE and WordPiece "
            f"ship in data/vocabulary/.")
    return PreTrainedTokenizerFast(
        tokenizer_object=HFTokenizer.from_file(str(path)),
        unk_token="<unk>", bos_token="<s>", eos_token="</s>",
        pad_token="<pad>", mask_token="<mask>")


def verify(cfg):
    """Pre-flight. Every check here is cheap; each one has already caught a
    real defect that would otherwise have surfaced hours into a run."""
    import torch
    from transformers import MarianMTModel
    from evaluation.finetune_marianmt import align_special_tokens
    from sacrebleu.metrics import BLEU, CHRF

    print("=== pre-flight verification ===\n")
    ok = True

    # 1) every tokenizer loads and encodes
    print("[1] tokenizer vocabularies")
    tokenizers = {}
    for name in cfg["tokenizers"]:
        for lang in ("amharic", "tigrinya"):
            try:
                tok = load_tokenizer(cfg, name, lang)
                tokenizers[(name, lang)] = tok
                enc = tok("ሰላም ዓለም")["input_ids"]
                assert enc, "empty encoding"
                print(f"    OK  {name:10} {lang:9} vocab={len(tok):>7} "
                      f"pad={tok.pad_token_id} eos={tok.eos_token_id}")
            except Exception as exc:
                ok = False
                print(f"    FAIL {name:10} {lang:9} {exc}")

    # 2) resize + special-token alignment, per arm
    print("\n[2] special-token alignment after resizing")
    base = cfg["model"]["base_checkpoint"]
    for (name, lang), tok in tokenizers.items():
        try:
            model = MarianMTModel.from_pretrained(base)
            model.resize_token_embeddings(len(tok))
            align_special_tokens(model, tok)
            print(f"    OK  {name:10} {lang:9}")
            del model
        except Exception as exc:
            ok = False
            print(f"    FAIL {name:10} {lang:9} {exc}")

    # 3) generation config holds no out-of-range ids
    print("\n[3] generation config validity")
    for (name, lang), tok in tokenizers.items():
        model = MarianMTModel.from_pretrained(base)
        model.resize_token_embeddings(len(tok))
        align_special_tokens(model, tok)
        gc, vocab = model.generation_config, len(tok)
        bad = []
        for field in ("pad_token_id", "eos_token_id", "decoder_start_token_id",
                      "forced_eos_token_id", "bos_token_id"):
            v = getattr(gc, field, None)
            if v is not None and not (0 <= v < vocab):
                bad.append(f"{field}={v}")
        for group in (gc.bad_words_ids or []):
            bad += [f"bad_words_ids={i}" for i in group if i >= vocab]
        if bad:
            ok = False
            print(f"    FAIL {name:10} {lang:9} out of range: {bad}")
        else:
            print(f"    OK  {name:10} {lang:9} all ids < {vocab}")
        del model

    # 4) scoring runs end to end on a tiny sample
    print("\n[4] metrics on a sample")
    hyps = ["ሰላም ዓለም", "እንዴት ነህ"]
    refs = ["ሰላም ዓለም", "እንዴት ናችሁ"]
    bleu, chrf = BLEU(), CHRF(word_order=2)
    b, c = bleu.corpus_score(hyps, [refs]), chrf.corpus_score(hyps, [refs])
    print(f"    BLEU   {b.score:.4f}  {bleu.get_signature()}")
    print(f"    chrF++ {c.score:.4f}  {chrf.get_signature()}")
    for got, want in ((str(bleu.get_signature()), cfg["metrics"]["bleu"]["signature"]),
                      (str(chrf.get_signature()), cfg["metrics"]["chrf_plus_plus"]["signature"])):
        if got != want:
            ok = False
            print(f"    FAIL signature drift:\n      config {want}\n      actual {got}")

    # 5) evaluation sets present and aligned
    print("\n[5] evaluation sets")
    for lang, spec in cfg["datasets"]["evaluation"].items():
        if not isinstance(spec, dict) or "src" not in spec:
            continue
        src, ref = ROOT / spec["src"], ROOT / spec["ref"]
        if not (src.exists() and ref.exists()):
            ok = False
            print(f"    FAIL {lang}: missing {src if not src.exists() else ref}")
            continue
        n_s = sum(1 for _ in open(src, encoding="utf-8"))
        n_r = sum(1 for _ in open(ref, encoding="utf-8"))
        status = "OK " if n_s == n_r == spec["pairs"] else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"    {status} {lang:9} src={n_s} ref={n_r} expected={spec['pairs']}")

    print("\n=== verification", "PASSED" if ok else "FAILED", "===")
    return ok


def translate(model_dir, sentences, cfg):
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch

    d = cfg["decoding"]
    tok = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(model_dir))
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()

    out = []
    for i in range(0, len(sentences), d["batch_size"]):
        batch = sentences[i:i + d["batch_size"]]
        enc = tok(batch, return_tensors="pt", padding=True,
                  truncation=True, max_length=d["max_length"])
        enc = {k: v for k, v in enc.items()
               if k in ("input_ids", "attention_mask")}
        if torch.cuda.is_available():
            enc = {k: v.cuda() for k, v in enc.items()}
        with torch.no_grad():
            gen = model.generate(**enc, max_length=d["max_length"],
                                 num_beams=d["num_beams"])
        out.extend(tok.batch_decode(gen, skip_special_tokens=True))
    return out


def score(cfg, checkpoints_only=True):
    """Decode and score every checkpoint that exists; write the comparison."""
    from sacrebleu.metrics import BLEU, CHRF

    bleu, chrf = BLEU(), CHRF(word_order=2)
    rows = []

    targets = [(r["language"], r["direction"], r["tokenizer"]) for r in cfg["runs"]]
    zs = cfg["zero_shot"]

    for language, direction, tokenizer in targets:
        ckpt = OUT / "checkpoints" / f"{language}_{tokenizer}"
        if not ckpt.exists():
            print(f"  skip {language}/{tokenizer}: no checkpoint at {ckpt}")
            continue

        for eval_lang, eval_dir in ((language, direction),
                                    (zs["language"], zs["direction"])):
            spec = cfg["datasets"]["evaluation"][eval_lang]
            src = [l.rstrip("\n") for l in open(ROOT / spec["src"], encoding="utf-8")]
            ref = [l.rstrip("\n") for l in open(ROOT / spec["ref"], encoding="utf-8")]

            hyps = translate(ckpt, src, cfg)

            pred_path = (OUT / "predictions" /
                         f"{language}_{tokenizer}_{eval_dir}.txt")
            pred_path.write_text("\n".join(hyps), encoding="utf-8")

            b = bleu.corpus_score(hyps, [ref])
            c = chrf.corpus_score(hyps, [ref])
            row = {
                "language": eval_lang,
                "tokenizer": tokenizer,
                "direction": eval_dir,
                "zero_shot": eval_dir == zs["direction"],
                "BLEU": round(b.score, 4),
                "chrF++": round(c.score, 4),
                "sacreBLEU_signature": str(bleu.get_signature()),
                "chrF++_signature": str(chrf.get_signature()),
                "seed": cfg["training"]["seed"],
                "checkpoint": str(ckpt.relative_to(ROOT)),
                "n": len(hyps),
                "predictions": str(pred_path.relative_to(ROOT)),
            }
            rows.append(row)
            tag = " (zero-shot)" if row["zero_shot"] else ""
            print(f"  {eval_dir} {tokenizer:10}{tag}: "
                  f"BLEU {row['BLEU']}  chrF++ {row['chrF++']}  n={row['n']}")

    report = {
        "experiment": cfg["experiment"]["title"],
        "not_a_reproduction_of": cfg["experiment"]["not_a_reproduction_of"],
        "note": ("New measurements under this repository's protocol. Not "
                 "comparable to the published Table 3: its scoring pipeline "
                 "was not recovered and its BLEU scale is unresolved."),
        "generated": datetime.now(timezone.utc).isoformat(),
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                 capture_output=True, text=True).stdout.strip(),
        "config": "configs/independent_evaluation.yaml",
        "environment": cfg["environment"],
        "results": rows,
    }
    out_path = OUT / "results" / "tokenizer_comparison.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nwrote {out_path.relative_to(ROOT)} ({len(rows)} rows)")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--verify", action="store_true",
                   help="pre-flight checks only; no decoding, no training")
    p.add_argument("--score", action="store_true",
                   help="decode and score existing checkpoints")
    args = p.parse_args()

    cfg = load_config()
    for d in ("configs", "checkpoints", "predictions", "results", "logs"):
        (OUT / d).mkdir(parents=True, exist_ok=True)

    if args.verify or not args.score:
        if not verify(cfg):
            raise SystemExit("pre-flight verification failed; not proceeding")
    if args.score:
        score(cfg)


if __name__ == "__main__":
    main()
