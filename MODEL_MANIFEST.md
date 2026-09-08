# MODEL_MANIFEST.md

**Purpose:** Inventory of trained MarianMT tokenizer comparison models

**Publication Strategy:** Models stored externally (Git LFS or cloud); pointers and manifests in GitHub

---

## Phase 1: Baseline Experiments (24 Models)

### EN→Amharic BPE (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_am/bpe/seed_42/model/model.safetensors | 232 MB | ✅ Complete | Baseline BPE EN→AM |
| 43 | experiments/en_am/bpe/seed_43/model/model.safetensors | 232 MB | ✅ Complete | Baseline BPE EN→AM |
| 44 | experiments/en_am/bpe/seed_44/model/model.safetensors | 232 MB | ✅ Complete | Baseline BPE EN→AM |

### EN→Amharic WordPiece (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_am/wordpiece/seed_42/model/model.safetensors | 232 MB | ✅ Complete | Baseline WordPiece EN→AM |
| 43 | experiments/en_am/wordpiece/seed_43/model/model.safetensors | 232 MB | ✅ Complete | Baseline WordPiece EN→AM |
| 44 | experiments/en_am/wordpiece/seed_44/model/model.safetensors | 232 MB | ✅ Complete | Baseline WordPiece EN→AM |

### EN→Amharic MoVoC-Tok (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_am/movoc_tok/seed_42/model/model.safetensors | 292 MB | ✅ Complete | Baseline MoVoC-Tok EN→AM |
| 43 | experiments/en_am/movoc_tok/seed_43/model/model.safetensors | 292 MB | ✅ Complete | Baseline MoVoC-Tok EN→AM |
| 44 | experiments/en_am/movoc_tok/seed_44/model/model.safetensors | 292 MB | ✅ Complete | Baseline MoVoC-Tok EN→AM |

### EN→Tigrinya BPE (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_ti/bpe/seed_42/model/model.safetensors | 230 MB | ✅ Complete | Baseline BPE EN→TI |
| 43 | experiments/en_ti/bpe/seed_43/model/model.safetensors | 230 MB | ✅ Complete | Baseline BPE EN→TI |
| 44 | experiments/en_ti/bpe/seed_44/model/model.safetensors | 230 MB | ✅ Complete | Baseline BPE EN→TI |

### EN→Tigrinya WordPiece (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_ti/wordpiece/seed_42/model/model.safetensors | 232 MB | ✅ Complete | Baseline WordPiece EN→TI |
| 43 | experiments/en_ti/wordpiece/seed_43/model/model.safetensors | 232 MB | ✅ Complete | Baseline WordPiece EN→TI |
| 44 | experiments/en_ti/wordpiece/seed_44/model/model.safetensors | 232 MB | ✅ Complete | Baseline WordPiece EN→TI |

### EN→Tigrinya MoVoC-Tok (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_ti/movoc_tok/seed_42/model/model.safetensors | 290 MB | ✅ Complete | Baseline MoVoC-Tok EN→TI |
| 43 | experiments/en_ti/movoc_tok/seed_43/model/model.safetensors | 290 MB | ✅ Complete | Baseline MoVoC-Tok EN→TI |
| 44 | experiments/en_ti/movoc_tok/seed_44/model/model.safetensors | 290 MB | ✅ Complete | Baseline MoVoC-Tok EN→TI |

---

## Phase 2: Full Validation (6 Models)

### EN→Amharic Full Validation MoVoC-Tok (3 seeds)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_am_full_validation_correct_tok/movoc_tok/seed_42/model/model.safetensors | 290 MB | ✅ Complete | Full validation EN→AM MoVoC-Tok |
| 43 | experiments/en_am_full_validation_correct_tok/movoc_tok/seed_43/model/model.safetensors | 290 MB | ✅ Complete | Full validation EN→AM MoVoC-Tok |
| 44 | experiments/en_am_full_validation_correct_tok/movoc_tok/seed_44/model/model.safetensors | 290 MB | ✅ Complete | Full validation EN→AM MoVoC-Tok |

### EN→Tigrinya Full Validation MoVoC-Tok (2 seeds, 1 pending)
| Seed | File | Size | Status | Purpose |
|---|---|---|---|---|
| 42 | experiments/en_ti_full_validation/movoc_tok/seed_42/model/model.safetensors | 290 MB | ✅ Complete | Full validation EN→TI MoVoC-Tok |
| 43 | experiments/en_ti_full_validation/movoc_tok/seed_43/model/model.safetensors | 290 MB | ✅ Complete | Full validation EN→TI MoVoC-Tok |

---

## Optimizer & Scheduler States

**Total:** 144 .pt files (~15 GB)  
**Status:** ✅ Present in repository  
**Purpose:** Training resumption, not required for inference  
**Recommendation:** Store with models for reproducibility OR exclude from GitHub

---

## Training Configuration

Each model directory contains:
- `model.safetensors` — Trained model weights
- `config.json` — Model configuration
- `tokenizer.json` — Tokenizer (reference)
- `metadata.json` — Training metadata
- `status.json` — Experiment status
- `checkpoints/` — Intermediate checkpoints

---

## Publication Options

### Option A: GitHub + Git LFS
- All 30 models in GitHub via Git LFS
- Storage: ~6.5 GB (safetensors only)
- Access: Clone full repo, pull LFS files
- Pros: Complete reproducibility
- Cons: Requires LFS quota, large storage

### Option B: GitHub + External Storage
- GitHub: Manifests + code only
- External: HuggingFace Hub (30 model repos, FREE)
- Access: Download models individually
- Pros: Lightweight GitHub, fast model access
- Cons: Split storage, requires configuration

### Option C: GitHub + Zenodo Archive
- GitHub: Manifests + code only
- External: Zenodo complete snapshot (1 record with DOI)
- Access: Download complete archive
- Pros: Permanent DOI, archival
- Cons: Full download required

---

## Checksums (SHA256)

To be computed during final publication:

```
experiments/en_am/bpe/seed_42/model/model.safetensors: [SHA256]
experiments/en_am/bpe/seed_43/model/model.safetensors: [SHA256]
[... 27 more entries ...]
```

---

## Recommended: Option B (GitHub + HuggingFace Hub)

- ✅ Lightweight GitHub repository (~400 MB code + manifests)
- ✅ 30 free model repositories on HuggingFace
- ✅ Clear separation: code on GitHub, models on HF
- ✅ Easy per-model download
- ✅ Complete reproducibility

