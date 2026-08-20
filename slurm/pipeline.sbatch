#!/usr/bin/env bash
#SBATCH --job-name=mtcmp-pipeline
#SBATCH --partition=ampere
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=slurm/logs/pipeline_%j.out
#SBATCH --error=slurm/logs/pipeline_%j.err
# --account=<YOUR_ACCOUNT>   # <-- set this if your site requires an explicit account; `sacctmgr show associations user=$USER` lists yours.
#
# Top-level orchestrator (spec sections 10-13, 18). `sbatch slurm/pipeline.sbatch`
# is intended to be the only manual command needed to run this comparison --
# subject to the two-stage behavior below, which is a DELIBERATE,
# explicitly-requested exception to full one-shot automation:
#
#   PIPELINE_STAGE=verify_and_smoke   (default; this is what a first,
#       un-parameterized `sbatch slurm/pipeline.sbatch` runs)
#       -> environment sanity, tokenizer verification, OPUS data
#          preparation + verification, model/embedding-adaptation
#          verification, ONE smoke test (en_ti, bpe, seed 42, small
#          subset). Then STOPS. Writes results/pipeline_status.json and
#          prints the exact follow-up command for the full sweep.
#          Does NOT submit the 18 training jobs.
#
#   PIPELINE_STAGE=full
#       -> (assumes verify_and_smoke already passed) submits the 18-way
#          training array, the 18-way validation-evaluation array
#          (afterok the training array), and the aggregation/report job
#          (afterok the evaluation array), via slurm/run_all_experiments.sbatch.
#
# Usage:
#   sbatch slurm/pipeline.sbatch                       # stage 1 only
#   PIPELINE_STAGE=full sbatch slurm/pipeline.sbatch    # stage 2 (deliberate, separate step)
set -euo pipefail

# NOTE: sbatch copies the script to a spool dir (e.g. /var/lib/slurm/slurmd/jobNNN/)
# before executing it, so BASH_SOURCE[0] does NOT point at this file's real
# location under sbatch -- it points at the spool copy, owned by root, which
# breaks any REPO_ROOT derived from dirname(BASH_SOURCE). Use SLURM_SUBMIT_DIR
# (the directory `sbatch` was invoked from -- i.e. the repo root, since the
# usage contract is `cd marianmt-tokenizer-comparison && sbatch slurm/pipeline.sbatch`)
# instead, with a BASH_SOURCE-based fallback only for direct
# `bash slurm/pipeline.sbatch` invocation (no sbatch).
if [ -n "${SLURM_SUBMIT_DIR:-}" ] && [ -f "${SLURM_SUBMIT_DIR}/pyproject.toml" ]; then
    REPO_ROOT="${SLURM_SUBMIT_DIR}"
else
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
cd "${REPO_ROOT}"
mkdir -p slurm/logs results

PIPELINE_STAGE="${PIPELINE_STAGE:-verify_and_smoke}"

# shellcheck disable=SC1091
source "${REPO_ROOT}/slurm/env_setup.sh"

write_status () {
    python3 - "$1" "$2" "$3" <<'PYEOF'
import json, sys
from pathlib import Path
stage, status, message = sys.argv[1:4]
path = Path("results/pipeline_status.json")
path.parent.mkdir(parents=True, exist_ok=True)
existing = {}
if path.exists():
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        existing = {}
existing[stage] = {"status": status, "message": message}
path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
PYEOF
}

echo "=== marianmt-tokenizer-comparison pipeline: PIPELINE_STAGE=${PIPELINE_STAGE} ==="

if [ "${PIPELINE_STAGE}" = "full" ]; then
    if [ ! -f results/pipeline_status.json ] || ! python3 -c "
import json, sys
d = json.load(open('results/pipeline_status.json'))
sys.exit(0 if d.get('smoke_test', {}).get('status') == 'PASSED' else 1)
" 2>/dev/null; then
        echo "ERROR: PIPELINE_STAGE=full requested, but results/pipeline_status.json does not show a PASSED smoke_test stage."
        echo "Run 'sbatch slurm/pipeline.sbatch' (default verify_and_smoke stage) first and confirm it succeeds."
        exit 1
    fi
    echo "Verification + smoke test previously PASSED. Submitting the 18-run full sweep now."
    bash slurm/run_all_experiments.sbatch
    write_status "full_stage_submission" "SUBMITTED" "18-run training/eval/aggregate chain submitted via run_all_experiments.sbatch"
    echo "=== Full sweep submitted. Track with: squeue -u \$USER ==="
    exit 0
fi

if [ "${PIPELINE_STAGE}" != "verify_and_smoke" ]; then
    echo "ERROR: unknown PIPELINE_STAGE='${PIPELINE_STAGE}'. Expected 'verify_and_smoke' or 'full'."
    exit 1
fi

STAGE_FAILED=0

echo "--- Stage: tokenizer verification ---"
if python3 scripts/verify_tokenizers.py; then
    write_status "tokenizer_verification" "PASSED" "All required tokenizer checks passed."
else
    write_status "tokenizer_verification" "FAILED" "See slurm/logs/pipeline_${SLURM_JOB_ID:-local}.out"
    STAGE_FAILED=1
fi

if [ "${STAGE_FAILED}" -eq 0 ]; then
    echo "--- Stage: OPUS data preparation ---"
    if python3 scripts/prepare_opus_data.py; then
        write_status "data_preparation" "PASSED" "OPUS data downloaded, filtered, split, manifests written."
    else
        write_status "data_preparation" "FAILED" "See slurm/logs/pipeline_${SLURM_JOB_ID:-local}.out"
        STAGE_FAILED=1
    fi
fi

if [ "${STAGE_FAILED}" -eq 0 ]; then
    echo "--- Stage: data verification ---"
    if python3 scripts/verify_data.py; then
        write_status "data_verification" "PASSED" "Split sizes, alignment, and checksums verified."
    else
        write_status "data_verification" "FAILED" "See slurm/logs/pipeline_${SLURM_JOB_ID:-local}.out"
        STAGE_FAILED=1
    fi
fi

if [ "${STAGE_FAILED}" -eq 0 ]; then
    echo "--- Stage: model / embedding-adaptation verification (6 combinations) ---"
    if python3 scripts/verify_models.py; then
        write_status "model_verification" "PASSED" "All 6 (tokenizer x language_pair) embedding adaptation checks passed."
    else
        write_status "model_verification" "FAILED" "See slurm/logs/pipeline_${SLURM_JOB_ID:-local}.out"
        STAGE_FAILED=1
    fi
fi

if [ "${STAGE_FAILED}" -eq 0 ]; then
    echo "--- Stage: smoke test (en_ti, bpe, seed 42, small subset) ---"
    if python3 scripts/train.py --smoke_test; then
        write_status "smoke_test" "PASSED" "Smoke test completed: data loading, tokenizer/model integration, forward pass, generation, chrF++, checkpoint writing all verified."
    else
        write_status "smoke_test" "FAILED" "See slurm/logs/pipeline_${SLURM_JOB_ID:-local}.out"
        STAGE_FAILED=1
    fi
fi

echo ""
if [ "${STAGE_FAILED}" -ne 0 ]; then
    echo "=== VERIFICATION+SMOKE STAGE FAILED. Diagnostic report: results/pipeline_status.json ==="
    echo "=== Do NOT submit the 18 full training runs until this is fixed and this stage passes. ==="
    exit 1
fi

echo "=== VERIFICATION+SMOKE STAGE PASSED. ==="
echo "=== Status report written to results/pipeline_status.json ==="
echo ""
echo "Next step (deliberate, separate command -- this run did NOT launch the 18 training jobs):"
echo ""
echo "    PIPELINE_STAGE=full sbatch slurm/pipeline.sbatch"
echo ""
