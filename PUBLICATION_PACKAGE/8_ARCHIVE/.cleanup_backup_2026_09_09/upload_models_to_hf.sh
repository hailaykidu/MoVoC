#!/bin/bash

################################################################################
# Upload MarianMT Models to HuggingFace Hub
#
# Purpose: Upload all 16 trained model checkpoints to HuggingFace Hub
# Usage: ./upload_models_to_hf.sh
# Requirements: huggingface-cli installed, HF token configured
################################################################################

set -euo pipefail

cd "$(dirname "$0")"

echo "════════════════════════════════════════════════════════════════"
echo "🤗 MarianMT Model Upload to HuggingFace Hub"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ huggingface-cli not found. Install with: pip install huggingface-hub"
    exit 1
fi

# Check authentication
if ! huggingface-cli whoami &> /dev/null; then
    echo "⚠️  Not authenticated with HuggingFace"
    echo "Run: huggingface-cli login"
    echo ""
    echo "Getting token from https://huggingface.co/settings/tokens"
    exit 1
fi

USER=$(huggingface-cli whoami | head -1)
echo "✅ Authenticated as: $USER"
echo ""

# Define models to upload (local_path -> hf_repo_id)
declare -a models=(
    "experiments/en_am/bpe/seed_43:marianmt-en-am-bpe-seed43"
    "experiments/en_am/bpe/seed_44:marianmt-en-am-bpe-seed44"
    "experiments/en_am/movoc_tok/seed_42:marianmt-en-am-movoc-tok-seed42"
    "experiments/en_am/movoc_tok/seed_43:marianmt-en-am-movoc-tok-seed43"
    "experiments/en_am/wordpiece/seed_42:marianmt-en-am-wordpiece-seed42"
    "experiments/en_am/wordpiece/seed_43:marianmt-en-am-wordpiece-seed43"
    "experiments/en_am/wordpiece/seed_44:marianmt-en-am-wordpiece-seed44"
    "experiments/en_ti/bpe/seed_42:marianmt-en-ti-bpe-seed42"
    "experiments/en_ti/bpe/seed_43:marianmt-en-ti-bpe-seed43"
    "experiments/en_ti/bpe/seed_44:marianmt-en-ti-bpe-seed44"
    "experiments/en_ti/movoc_tok/seed_42:marianmt-en-ti-movoc-tok-seed42"
    "experiments/en_ti/movoc_tok/seed_43:marianmt-en-ti-movoc-tok-seed43"
    "experiments/en_ti/movoc_tok/seed_44:marianmt-en-ti-movoc-tok-seed44"
    "experiments/en_ti/wordpiece/seed_42:marianmt-en-ti-wordpiece-seed42"
    "experiments/en_ti/wordpiece/seed_43:marianmt-en-ti-wordpiece-seed43"
    "experiments/en_ti/wordpiece/seed_44:marianmt-en-ti-wordpiece-seed44"
)

echo "Models to upload: ${#models[@]}"
echo ""

# Counter
count=0
success=0
failed=0

# Upload each model
for model_pair in "${models[@]}"
do
    count=$((count + 1))
    IFS=':' read -r local_path repo_id <<< "$model_pair"

    repo_id_full="hailaykidu/$repo_id"
    model_dir="$local_path/model"

    echo "────────────────────────────────────────────────────────────────"
    echo "[$count/${#models[@]}] Uploading: $repo_id"
    echo "────────────────────────────────────────────────────────────────"

    # Check if local directory exists
    if [ ! -d "$model_dir" ]; then
        echo "❌ Directory not found: $model_dir"
        failed=$((failed + 1))
        continue
    fi

    # Check if model files exist
    if [ ! -f "$model_dir/model.safetensors" ]; then
        echo "❌ Model file not found: $model_dir/model.safetensors"
        failed=$((failed + 1))
        continue
    fi

    echo "Local path: $model_dir"
    echo "HF repo: $repo_id_full"
    echo ""

    # Upload model
    if huggingface-cli upload "$repo_id_full" \
        "$model_dir" \
        --repo-type model \
        --private; then
        echo "✅ Successfully uploaded: $repo_id_full"
        success=$((success + 1))
    else
        echo "❌ Failed to upload: $repo_id_full"
        failed=$((failed + 1))
    fi

    echo ""
done

# Summary
echo "════════════════════════════════════════════════════════════════"
echo "📊 Upload Summary"
echo "════════════════════════════════════════════════════════════════"
echo "Total models: $count"
echo "✅ Successful: $success"
echo "❌ Failed: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "🎉 All models uploaded successfully!"
    exit 0
else
    echo "⚠️  Some models failed to upload. Check logs above."
    exit 1
fi
