"""Paired bootstrap over held-out words, for the intrinsic metrics.

Resamples words with replacement and recomputes the corpus-level ratio on each
draw, which is the correct unit: boundary precision and MorphScore are ratios of
summed counts, not means of per-word scores. The resampled index is shared
across tokenizers, so the comparison is paired.

Reports, for MoVoC-Tok against each baseline, the observed difference, a 95%
percentile interval and a two-sided p-value.

Scores only words held out from the morpheme resource that constrained
MoVoC-Tok training, matching `evaluate_intrinsic.py --exclude-training`.

Usage:
    python scripts/bootstrap_significance.py . evaluation/results/significance_heldout.json
"""
import sys, json
from pathlib import Path
import numpy as np

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO / "scripts"))
import evaluate_intrinsic as E

N_BOOT = 10000
rng = np.random.default_rng(20251011)
tokdir = REPO / "tokenizers"
datadir = REPO / "evaluation" / "data"


def counts(tok, rows):
    m, p, gh, gt = [], [], [], []
    for word, morphs in rows:
        gold = E.boundaries(morphs)
        pred = E.boundaries(tok.segment(word))
        m.append(len(pred & gold)); p.append(len(pred))
        if pred:
            gh.append(len(gold & pred)); gt.append(len(gold))
        else:
            gh.append(0); gt.append(0)
    return (np.array(m, float), np.array(p, float),
            np.array(gh, float), np.array(gt, float))


def run(rows, movoc_dir, label, out):
    toks = {
        "BPE": E.HFTokenizer(tokdir / "bpe_32k", "BPE"),
        "WordPiece": E.HFTokenizer(tokdir / "wordpiece_32k", "WordPiece"),
        "MoVoC-Tok": E.MoVoCTokenizer(movoc_dir, "MoVoC-Tok"),
    }
    C = {k: counts(v, rows) for k, v in toks.items()}
    n = len(rows)
    idx = rng.integers(0, n, size=(N_BOOT, n))

    def boot(c):
        m, p, gh, gt = c
        M = m[idx].sum(1); P = p[idx].sum(1)
        GH = gh[idx].sum(1); GT = gt[idx].sum(1)
        return np.where(P > 0, M / np.maximum(P, 1), 0.0), np.where(GT > 0, GH / np.maximum(GT, 1), 0.0)

    B = {k: boot(c) for k, c in C.items()}
    obs = {k: (c[0].sum() / c[1].sum(), c[2].sum() / c[3].sum()) for k, c in C.items()}

    print(f"\n=== {label}  (n={n:,}) ===")
    for k in ("BPE", "WordPiece", "MoVoC-Tok"):
        print(f"  {k:11s} prec={obs[k][0]:.4f}  morph={obs[k][1]:.4f}")

    rec = {"n": n, "observed": {k: {"precision": float(v[0]), "morphscore": float(v[1])} for k, v in obs.items()}}
    for base in ("BPE", "WordPiece"):
        for i, metric in enumerate(("precision", "morphscore")):
            d = B["MoVoC-Tok"][i] - B[base][i]
            delta = obs["MoVoC-Tok"][i] - obs[base][i]
            lo, hi = np.percentile(d, [2.5, 97.5])
            p = 2 * min((d <= 0).mean(), (d >= 0).mean())
            print(f"  vs {base:9s} {metric:10s} Δ={delta:+.4f} 95%CI[{lo:+.4f},{hi:+.4f}] p={min(p,1.0):.4f} win={(d>0).mean():.3f}")
            rec.setdefault(f"vs_{base}", {})[metric] = {
                "delta": float(delta), "ci95": [float(lo), float(hi)],
                "p": float(min(p, 1.0)), "win_rate": float((d > 0).mean()),
            }
    out[label] = rec


# Every language is held out against the resource that constrained the
# tokenizer scoring it. For Tigre and Ge'ez that is the Tigrinya resource,
# since the Tigrinya MoVoC-Tok is what scores them: see
# E.SCORING_TOKENIZER_LANGUAGE.
out = {}
for lang, movoc in (("amharic", "amharic_movoc_tok_32k"),
                    ("tigrinya", "tigrinya_movoc_tok_32k"),
                    ("tigre", "tigrinya_movoc_tok_32k"),
                    ("geez", "tigrinya_movoc_tok_32k")):
    train = E.training_words(REPO, lang)
    rows = [(w, m) for w, m in E.load_testset(datadir / f"{lang}_gold.tsv")
            if w not in train]
    run(rows, tokdir / movoc, f"{lang}_heldout", out)

Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {sys.argv[2]}")
