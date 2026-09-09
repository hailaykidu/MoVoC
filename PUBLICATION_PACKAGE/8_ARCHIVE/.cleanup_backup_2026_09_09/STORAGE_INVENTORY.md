# 📦 STORAGE INVENTORY & GIT LFS RECOMMENDATIONS

**Date:** 2026-09-08  
**Repository Size:** 54 GB  
**Status:** ⚠️ **Too large for standard GitHub** — Git LFS or external hosting recommended

---

## Total Repository Size Breakdown

| Directory | Size | Files | Recommendation |
|-----------|------|-------|-----------------|
| **experiments/** | 44 GB | ~500+ | ⚠️ Use Git LFS |
| **data/** | 2.2 GB | ~1000+ | ⚠️ Use Git LFS |
| **slurm/logs/** | ~500 MB | ~100 | ❌ Delete (rebuild from scripts) |
| **Tokenizers/** | 8.5 MB | ~20 | ✅ Include with repo |
| **Code/Docs/Configs** | ~50 MB | ~300 | ✅ Include with repo |
| **Total** | **54 GB** | **~2000** | **Requires LFS** |

---

## Large Files Requiring Git LFS (Files > 100 MB)

### Model Checkpoints in `experiments_organized/`
```
./experiments_organized/phase1_tigrinya_movoc_tok_seed42/models/model.safetensors     ~750 MB
./experiments_organized/phase1_tigrinya_movoc_tok_seed42/checkpoints/*/model.safetensors  ~750 MB (×5+)
./experiments_organized/phase1_tigrinya_bpe_seed44/models/model.safetensors           ~750 MB
... (similar for all other seed/tokenizer combinations)
```

### Training Checkpoints
```
./experiments_organized/*/checkpoints/checkpoint-*/optimizer.pt  ~200 MB each (×10+)
./experiments_organized/*/checkpoints/checkpoint-*/scheduler.pt  ~50 MB each
```

### SLURM Log Files (Informational Only - Can Delete)
```
./slurm/logs/train_en_am_correct_tok_69393.err               ~120 MB (old log file)
./slurm/logs/train_en_am_correct_tok_69352.err               ~120 MB (old log file)
./slurm/logs/train_en_am_correct_tok_69317.err               ~120 MB (old log file)
... (6 more old log files, ~720 MB total)
```

---

## Three Options for GitHub Publication

### OPTION A: Git LFS + GitHub ✅ RECOMMENDED FOR REPRODUCIBILITY

**Pros:**
- Full repository reproducibility
- Models available directly from GitHub
- Users can clone full dataset
- Works with HuggingFace Hub for model hosting

**Cons:**
- Requires Git LFS setup (free tier: 1 GB bandwidth/month)
- Initial push takes longer
- LFS pointer files add complexity

**Setup:**
```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison

# Install Git LFS
git lfs install

# Track large files
git lfs track "experiments/**/*.safetensors"
git lfs track "experiments/**/*.bin"
git lfs track "experiments/**/*.pt"
git lfs track "data/**/*.tar.gz"
git lfs track "Tokenizers/**/*.json"

# Add .gitattributes
git add .gitattributes

# Commit and push
git add -A
git commit -m "Add Git LFS configuration for large model files"
git push -u origin main
```

**GitHub Cost:** Free tier (1 GB bandwidth) or Pro ($5/month for 100 GB)

---

### OPTION B: HuggingFace Hub (Recommended for Models) ⭐ BEST FOR MODELS

**Pros:**
- Free unlimited hosting for public models
- Built-in versioning and easy access
- Models can be loaded directly: `AutoModel.from_pretrained(...)`
- Excellent for research reproducibility
- Community contribution model

**Cons:**
- Requires separate repository per language pair / tokenizer
- Data must be uploaded separately
- Initial setup takes time

**Setup:**
```bash
# Create HuggingFace org or use personal account
# https://huggingface.co/new-model

# For each model checkpoint:
python -c "
from huggingface_hub import ModelCard, ModelCardData, model_info
model = 'marianmt-tokenizer-comparison-en-am-movoc-tok-seed42'
repo_id = f'your-org/{model}'
# Upload model
"
```

**Recommendation:** Use HuggingFace for all 28+ trained models, include data in GitHub with LFS.

---

### OPTION C: Zenodo Archive (Best for Permanent Data) 📊

**Pros:**
- Permanent DOI for citation
- Long-term preservation guarantee
- Large file support (up to 50 GB per upload)
- Free for non-commercial research

**Cons:**
- Not convenient for iterative development
- Limited to versioning through new uploads

**Setup:**
```bash
# Create Zenodo account
# https://zenodo.org

# Prepare archive
tar -czf marianmt-tokenizer-comparison-v1.tar.gz \
  experiments/ data/ Tokenizers/ scripts/ src/

# Upload via web interface or API
# Get permanent DOI

# Add DOI to README and CITATION.md
```

---

## Recommended Hybrid Strategy

**Best Practice for Publication:**

1. **GitHub (Public, Code)** — Use Git LFS
   - Scripts, configs, documentation
   - Large files: use LFS pointers
   - Size: ~2-5 GB with LFS pointers (~50 MB actual)

2. **HuggingFace Hub (Public, Models)** — Free hosting
   - Upload each trained model checkpoint
   - Users can load: `AutoModel.from_pretrained("your-org/model-name")`
   - No GitHub LFS fees

3. **Zenodo Archive (Permanent, Complete Dataset)** — One-time upload
   - Complete tarball with all experiments
   - Permanent DOI for citation
   - For reproducibility verification

**Publication Flow:**
```
GitHub (code) → HuggingFace (models) ← README links
    ↓
Zenodo (full archive with DOI)
    ↓
    ↓
CITATION.md includes both GitHub link + Zenodo DOI
```

---

## Immediate Action Items

### 1. Clean Up Logs (Remove 720 MB of Old SLURM Logs)

Old SLURM log files can be deleted — they're not needed for reproducibility:

```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison

# Find old training logs
ls -lh slurm/logs/train_en_am_correct_tok_*.err

# Delete them
rm slurm/logs/train_en_am_correct_tok_69393.err
rm slurm/logs/train_en_am_correct_tok_69352.err
rm slurm/logs/train_en_am_correct_tok_69317.err
rm slurm/logs/train_en_am_correct_tok_69106.err
rm slurm/logs/train_en_am_correct_tok_69105.err
rm slurm/logs/train_en_am_correct_tok_69102.err
# (Total: 720 MB freed)

git add -A  # Stage the removal
```

### 2. Set Up Git LFS Configuration

```bash
git lfs install

# Create .gitattributes
cat > .gitattributes << 'ATTRS'
# Model files
experiments/**/*.safetensors filter=lfs diff=lfs merge=lfs -text
experiments/**/*.bin filter=lfs diff=lfs merge=lfs -text
experiments/**/*.pt filter=lfs diff=lfs merge=lfs -text

# Tokenizer files
Tokenizers/**/*.json filter=lfs diff=lfs merge=lfs -text

# Data archives (if compressed)
data/**/*.tar.gz filter=lfs diff=lfs merge=lfs -text

# Large text logs
slurm/logs/*.out filter=lfs diff=lfs merge=lfs -text
slurm/logs/*.err filter=lfs diff=lfs merge=lfs -text
ATTRS

git add .gitattributes
git commit -m "Add Git LFS configuration for large files"
```

### 3. GitHub Repository Setup

```bash
# Create repository on GitHub
# https://github.com/new
# Name: marianmt-tokenizer-comparison
# Description: Independent full-scale MarianMT tokenizer experiments

# Add remote
git remote add origin https://github.com/YOUR-USERNAME/marianmt-tokenizer-comparison.git

# First push (with LFS)
git branch -M main
git push -u origin main
```

---

## File Statistics for GitHub LFS

### What Gets Tracked by LFS (Large Files)

```
experiments/
  ├── en_am/
  │   ├── bpe/seed_42/pytorch_model.bin           ~750 MB ← LFS
  │   ├── bpe/seed_43/pytorch_model.bin           ~750 MB ← LFS
  │   ├── ... (3 seeds × 3 tokenizers = 9 files)  ~6.75 GB ← LFS
  │
  └── en_ti/
      ├── bpe/seed_42/pytorch_model.bin           ~750 MB ← LFS
      └── ... (3 seeds × 3 tokenizers = 9 files)  ~6.75 GB ← LFS

Total Models (24 Phase 1 + Phase 2):   ~40+ GB (all LFS)
```

### What Does NOT Need LFS (Small Files)

```
src/                    ~2 MB  (Python source)
scripts/                ~5 MB  (Training/eval scripts)
data/manifests/         ~1 MB  (Metadata)
docs/                   ~2 MB  (Documentation)
configs/                ~100 KB (YAML configs)
Tokenizers/configs/     ~5 MB  (Tokenizer JSON configs)

Total (no LFS):         ~15 MB
```

---

## GitHub LFS Cost Estimate

| Scenario | Storage | Bandwidth | Cost |
|----------|---------|-----------|------|
| Single model download | 750 MB | 750 MB | Free (< 1 GB/month) |
| 10 users download full repo | 40 GB | 40 GB | $20/month (LFS Pro) |
| Recommended: Use HuggingFace for models | 0 GB Git LFS | 0 GB | Free |

**Bottom Line:** Use HuggingFace for model distribution, GitHub+LFS for code.

---

## RECOMMENDATION SUMMARY

✅ **Use Option B/Hybrid Strategy:**
1. Push code + data to GitHub with Git LFS (~5 GB)
2. Upload models to HuggingFace Hub (free)
3. Archive complete dataset to Zenodo (one-time DOI)
4. Update README with links to all three

**Benefits:**
- Full reproducibility
- Permanent archival (Zenodo DOI)
- Free model hosting (HuggingFace)
- Minimal GitHub costs (just code + data with LFS)
- Easy for users: code from GitHub, models from HuggingFace

---

**Ready for publication:** ✅ After cleanup of old log files (720 MB)
