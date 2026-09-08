# DATA_MANIFEST.md

**Purpose:** Inventory of training, validation, test, and extrinsic evaluation datasets

**Publication Strategy:** Data stored locally (Git LFS) or excluded from GitHub; manifests provide metadata for retrieval

---

## Dataset Summary

| Dataset | Purpose | File | Size | License | Status |
|---------|---------|------|------|---------|--------|
| EN→Amharic Training | Phase 1/2 training | data/train/en_am/corpus.txt | ~2.1 GB | See LICENSE | ✅ Complete |
| EN→Amharic Validation | Phase 1/2 validation | data/train/en_am/validation.txt | ~65 MB | See LICENSE | ✅ Complete |
| EN→Tigrinya Training | Phase 1/2 training | data/train/en_ti/corpus.txt | ~1.8 GB | See LICENSE | ✅ Complete |
| EN→Tigrinya Validation | Phase 1/2 validation | data/train/en_ti/validation.txt | ~52 MB | See LICENSE | ✅ Complete |
| EN→Amharic Test | Extrinsic evaluation | data/extrinsic/en_am/test.txt | ~8 MB | See LICENSE | ✅ Complete |
| EN→Tigrinya Test | Extrinsic evaluation | data/extrinsic/en_ti/test.txt | ~7 MB | See LICENSE | ✅ Complete |
| EN→Geez Zero-Shot | Zero-shot evaluation | data/extrinsic/en_gz/source.txt + target.txt | ~50 KB | See LICENSE | ✅ Complete |
| EN→Tigre Zero-Shot | Zero-shot evaluation | data/extrinsic/en_tig/source.txt + target.txt | ~20 KB | See LICENSE | ✅ Complete |

**Total Size:** ~3.9 GB (estimated)

---

## 1. Training Corpora

### EN→Amharic Training Set

**Directory:** `data/train/en_am/`

| File | Format | Lines | Size | Description |
|------|--------|-------|------|-------------|
| corpus.txt | Parallel pairs (one per line, tab-separated) | 6,759,000 | ~2.1 GB | Full training corpus for baseline + Phase 2 |
| validation.txt | Parallel pairs (one per line, tab-separated) | 752,900 | ~65 MB | Full validation set for Phase 2 evaluation |

**Composition:** 
- Source: English sentences (one per line)
- Target: Amharic translations (one per line)
- Encoding: UTF-8
- Separator: Tab character

**Usage:**
```bash
# Training
head -752900 corpus.txt > train.txt
tail -n +752901 corpus.txt > remaining.txt

# Validation
cat validation.txt > val.txt
```

**License:** [To be specified in LICENSE file]

**Checksum:** [SHA256 to be computed]

---

### EN→Tigrinya Training Set

**Directory:** `data/train/en_ti/`

| File | Format | Lines | Size | Description |
|------|--------|-------|------|-------------|
| corpus.txt | Parallel pairs (one per line, tab-separated) | 5,482,000 | ~1.8 GB | Full training corpus for baseline + Phase 2 |
| validation.txt | Parallel pairs (one per line, tab-separated) | 136,601 | ~52 MB | Full validation set (doubled for Phase 2 evaluation) |

**Composition:** 
- Source: English sentences (one per line)
- Target: Tigrinya translations (one per line)
- Encoding: UTF-8
- Separator: Tab character

**Usage:**
- Same pattern as EN→Amharic
- Note: Validation set is larger (~136,601 vs ~68,300 in Phase 1) due to expanded validation protocol

**License:** [To be specified in LICENSE file]

**Checksum:** [SHA256 to be computed]

---

## 2. Test Sets (Extrinsic Evaluation)

### EN→Amharic Test Set

**Directory:** `data/extrinsic/en_am/`

| File | Format | Lines | Size | Purpose |
|------|--------|-------|------|---------|
| source.txt | One English sentence per line | 1,000 | ~8 MB | Source sentences for final evaluation |
| target.txt | One Amharic translation per line | 1,000 | ~15 MB | Reference translations for scoring |

**Metrics Computed:**
- BLEU: SacreBLEU corpus-level score
- ChrF++: Character-level F-score (character n-grams)
- Both at: `results/table3_final.csv`

**License:** [To be specified in LICENSE file]

**Checksum:** [SHA256 to be computed]

---

### EN→Tigrinya Test Set

**Directory:** `data/extrinsic/en_ti/`

| File | Format | Lines | Size | Purpose |
|------|--------|-------|------|---------|
| source.txt | One English sentence per line | 1,000 | ~7 MB | Source sentences for final evaluation |
| target.txt | One Tigrinya translation per line | 1,000 | ~14 MB | Reference translations for scoring |

**Metrics Computed:**
- BLEU: SacreBLEU corpus-level score
- ChrF++: Character-level F-score
- Both at: `results/table3_final.csv`

**License:** [To be specified in LICENSE file]

**Checksum:** [SHA256 to be computed]

---

## 3. Zero-Shot Evaluation Sets

### EN→Geez Zero-Shot Evaluation

**Directory:** `data/extrinsic/en_gz/`

| File | Format | Pairs | Size | Purpose |
|------|--------|-------|------|---------|
| source.txt | One English sentence per line | 100 | ~20 KB | Zero-shot source (language never trained) |
| target.txt | One Ge'ez translation per line | 100 | ~25 KB | Reference for scoring generalization |
| README.md | Metadata | - | ~2 KB | Dataset description |

**Evaluation Protocol:**
- Models trained on EN→Amharic / EN→Tigrinya used to translate EN→Ge'ez (unseen language)
- Measures transfer to related Ethiopic language
- BLEU and ChrF++ computed

**Results Location:** `results/ZERO_SHOT_SUPPLEMENTARY.md`

**License:** [To be specified in LICENSE file]

**Checksum:** [SHA256 to be computed]

---

### EN→Tigre Zero-Shot Evaluation

**Directory:** `data/extrinsic/en_tig/`

| File | Format | Pairs | Size | Purpose |
|------|--------|-------|------|---------|
| source.txt | One English sentence per line | 43 | ~8 KB | Zero-shot source (language never trained) |
| target.txt | One Tigre translation per line | 43 | ~10 KB | Reference for scoring generalization |
| README.md | Metadata | - | ~2 KB | Dataset description |

**Evaluation Protocol:**
- Models trained on EN→Tigrinya used to translate EN→Tigre (different Ethiopic language)
- Measures transfer to closely-related but distinct language
- BLEU and ChrF++ computed

**Results Location:** `results/ZERO_SHOT_SUPPLEMENTARY.md`

**License:** [To be specified in LICENSE file]

**Checksum:** [SHA256 to be computed]

---

## 4. Data Processing & Reproducibility

### Data Pipeline

```
Raw data files (data/train/{en_am,en_ti}/)
         ↓
   Load & validation (scripts/verify_data.py)
         ↓
   Tokenize (BPE/WordPiece/MoVoC-Tok)
         ↓
   Train MarianMT models
         ↓
   Evaluate on test sets (data/extrinsic/)
         ↓
   Report metrics (results/table3_final.csv)
```

### Reproducibility

**To verify data integrity:**
```bash
# Check training set size
wc -l data/train/en_am/corpus.txt  # Expected: 6,759,000
wc -l data/train/en_ti/corpus.txt  # Expected: 5,482,000

# Check validation set size
wc -l data/train/en_am/validation.txt  # Expected: 752,900
wc -l data/train/en_ti/validation.txt  # Expected: 136,601

# Check test set size
wc -l data/extrinsic/en_am/source.txt  # Expected: 1,000
wc -l data/extrinsic/en_ti/target.txt  # Expected: 1,000

# Compute SHA256 checksums
sha256sum data/train/en_am/corpus.txt
sha256sum data/train/en_ti/corpus.txt
```

**Data access from scripts:**
```python
# Standard data access pattern (used by all training/eval scripts)
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TRAIN_DATA = DATA_DIR / "train" / language_pair
EXTRINSIC_DATA = DATA_DIR / "extrinsic" / language_pair

# Load training corpus
with open(TRAIN_DATA / "corpus.txt", encoding="utf-8") as f:
    pairs = [line.strip().split("\t") for line in f]
```

---

## 5. Storage & Publication Options

### Option A: Include All Data in GitHub (Not Recommended)

- Size: ~3.9 GB
- Pros: Complete reproducibility from single clone
- Cons: Large repository, slow clone, long push time
- Status: ✅ Currently in experiments/ directory

### Option B: GitHub + Git LFS for Data

- Size: ~3.9 GB via LFS
- Pros: Faster initial clone, optional full data download
- Cons: Requires LFS quota
- Configuration: Add to `.gitattributes`
  ```
  data/**/*.txt filter=lfs diff=lfs merge=lfs -text
  ```

### Option C: GitHub + External Data Repository (Recommended)

- GitHub: Manifests + scripts only (~50 MB)
- External: Zenodo/HuggingFace Datasets Hub
- Pros: Lightweight, permanent DOI, easy discovery
- Cons: Split storage, requires download step
- Setup:
  ```bash
  # Upload to Zenodo
  zenodo_upload --directory data/ --title "MarianMT Tokenizer Comparison Datasets"
  
  # Update DATA_MANIFEST.md with DOI
  DOI: https://zenodo.org/record/XXXXX
  ```

### Option D: Exclude Data from GitHub (Code Only)

- GitHub: Scripts + manifests only
- Data: Users download from original source (if public)
- Pros: Minimal repository, avoid licensing issues
- Cons: Not reproducible without data access
- Use Case: Code release only (results preserved)

---

## 6. License Considerations

All datasets contain:
- **English:** Standard licensed corpora (OPUS, CCMatrix, etc.)
- **Amharic/Tigrinya:** Original annotations or licensed collections

**Recommended License Declaration:**

```
LICENSE INFORMATION
===================

Training Data (data/train/):
  - Source: [cite original source]
  - License: [specify license, e.g., CC-BY-4.0, commercial use restrictions]
  - Attribution: [cite any required attribution]

Test Data (data/extrinsic/):
  - Source: [cite original source]
  - License: [specify license]
  - Attribution: [cite any required attribution]

Zero-Shot Data (data/extrinsic/en_gz, en_tig/):
  - Source: [cite original source]
  - License: [specify license]
  - Attribution: [cite any required attribution]
```

**Action Required:** Review LICENSE file for dataset attributions before publication.

---

## 7. Checksum Verification

To verify downloaded data integrity:

```bash
# Create checksums
find data/ -type f -name "*.txt" -exec sha256sum {} \; > data/CHECKSUMS.sha256

# Verify after download
sha256sum --check data/CHECKSUMS.sha256
```

**Checksum file:** `data/CHECKSUMS.sha256` (to be generated)

---

## 8. Data Access & Download

### From Local Repository
```bash
# Clone full repository with all data
git clone https://github.com/hailaykidu/MoVoC.git
cd MoVoC/v2/table3_extrinsic_mt

# All data in data/ directory
ls -lh data/train/
ls -lh data/extrinsic/
```

### From External Source (if published separately)
```bash
# Download from Zenodo (if Option C chosen)
wget https://zenodo.org/record/XXXXX/files/marianmt_datasets.tar.gz
tar -xzf marianmt_datasets.tar.gz

# Or from HuggingFace Datasets (if uploaded there)
from datasets import load_dataset
dataset = load_dataset("hailaykidu/marianmt-am-ti-corpora")
```

---

## 9. Summary Table

| Dataset | Size | Lines | License | Status | Path |
|---------|------|-------|---------|--------|------|
| EN→AM Training | 2.1 GB | 6.76M | [TBD] | ✅ | data/train/en_am/ |
| EN→AM Validation | 65 MB | 752K | [TBD] | ✅ | data/train/en_am/ |
| EN→TI Training | 1.8 GB | 5.48M | [TBD] | ✅ | data/train/en_ti/ |
| EN→TI Validation | 52 MB | 136K | [TBD] | ✅ | data/train/en_ti/ |
| EN→AM Test | 8 MB | 1K | [TBD] | ✅ | data/extrinsic/en_am/ |
| EN→TI Test | 7 MB | 1K | [TBD] | ✅ | data/extrinsic/en_ti/ |
| EN→GZ Zero-Shot | 50 KB | 100 | [TBD] | ✅ | data/extrinsic/en_gz/ |
| EN→TIG Zero-Shot | 20 KB | 43 | [TBD] | ✅ | data/extrinsic/en_tig/ |

**Total:** ~3.9 GB

---

**Generated:** 2026-09-08  
**Status:** Manifest complete; checksums to be computed at publication  
**Next Step:** Decide storage option (A-D above) and implement accordingly

