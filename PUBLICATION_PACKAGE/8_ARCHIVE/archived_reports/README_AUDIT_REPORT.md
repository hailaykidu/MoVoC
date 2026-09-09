# README Audit Report & Consolidation Plan
## Repository Documentation Streamlining for Paper Submission

**Status:** Dry-run complete - awaiting approval before execution  
**Date:** Current  
**Action Required:** Review and approve before deletion

---

## 📋 AUDIT FINDINGS

### README Files Identified (12 total)

| File | Lines | Type | Status | Recommendation |
|------|-------|------|--------|---|
| `./README.md` | 101 | **Root** | ✅ Current | **CONSOLIDATE INTO MASTER** |
| `./PUBLICATION_PACKAGE/README.md` | 436 | Package-level | ⚠️ Detailed | **MERGE CRITICAL INFO** |
| `./PUBLICATION_PACKAGE/5_RESULTS/README.md` | 263 | Results-level | ⚠️ Specialized | **KEEP** (shortened) |
| `./PUBLICATION_PACKAGE/7_DOCUMENTATION/README.md` | 101 | Symbolic link | ⏮️ Duplicate | **DELETE** |
| `./PUBLICATION_PACKAGE/8_ARCHIVE/ARCHIVE_README.md` | N/A | Archive | 📦 Archive | **DELETE** (archived) |
| `./data/README.md` | 17 | Data guide | ✅ Brief | **KEEP** (minimal) |
| `./data/extrinsic/en_am/README.md` | 22 | Data description | ✅ Brief | **KEEP** (minimal) |
| `./data/extrinsic/en_ti/README.md` | 30 | Data description | ✅ Brief | **KEEP** (minimal) |
| `./data/extrinsic/en_tig/README.md` | 44 | Data description | ✅ Brief | **KEEP** (minimal) |
| `./data/extrinsic/en_gz/README.md` | 36 | Data description | ✅ Brief | **KEEP** (minimal) |
| `./Tokenizers/bpe/README.md` | 24 | Pointer doc | 📍 Reference | **KEEP** (pointer) |
| `./Tokenizers/wordpiece/README.md` | 19 | Pointer doc | 📍 Reference | **KEEP** (pointer) |
| `./Tokenizers/movoc_tok/README.md` | 85 | Pointer doc | 📍 Reference | **KEEP** (pointer) |

---

## 🎯 CONSOLIDATION STRATEGY

### **MASTER README.md Structure** (Proposed)

The root `README.md` will be restructured into a comprehensive, publication-ready document with sections:

1. **Title & Overview** (2-3 sentences)
2. **⚠️ Important Disclaimer** (link to REPOSITORY_CONTEXT.md)
3. **🎯 Key Findings** (Table with main results)
4. **📋 Quick Start** (Setup & reproduction commands)
5. **📁 Repository Structure** (Directory tree with brief descriptions)
6. **🔬 Experimental Design** (Overview of methodology)
7. **📊 Results** (Link to PUBLICATION_PACKAGE/5_RESULTS/)
8. **🚀 Running Experiments** (Commands for SLURM, GPU training)
9. **📚 Documentation** (Links to key files)
10. **📝 Citation** (Proper citation format)
11. **✅ Status & Validation** (Publication readiness)

---

## 📊 CONTENT EXTRACTION PLAN

### From `./PUBLICATION_PACKAGE/README.md` → Root README
✓ Important disclaimer about extrinsic vs. intrinsic evaluation  
✓ 16 complete models summary  
✓ Directory structure (condensed)  
✓ Quick summary of what's reproducible  
✓ Key file locations  

### From `./PUBLICATION_PACKAGE/5_RESULTS/README.md` → Keep as-is
✓ Highly specialized - focuses on TABLE 3 results interpretation  
✓ Points users to specific result files  
✓ Contains results-specific commands  
✓ Shorter version link from root README  

### From `./data/README.md` → Integrate into root
✓ Data overview (merged into Repository Structure section)  
✓ Keep minimal data/README.md as quick reference  

### From `./data/extrinsic/*/README.md` → Keep minimal versions
✓ Each describes ONE test set (4-5 sentences)  
✓ Quick reference for evaluators  
✓ No overlap with root README  

### From `./Tokenizers/*/README.md` → Keep as pointers
✓ Each explains tokenizer is external reference  
✓ Minimal (19-85 lines)  
✓ Serves educational purpose  

---

## ✅ FILES TO DELETE

### Files Flagged for Deletion (3 total)

**1. `./PUBLICATION_PACKAGE/7_DOCUMENTATION/README.md` (101 lines)**
- **Reason:** Exact duplicate of root README.md (symbolic link)
- **Content:** Redundant - same title, same disclaimers
- **Impact:** Removing link does not affect functionality
- **Action:** DELETE symbolic link

**2. `./PUBLICATION_PACKAGE/8_ARCHIVE/ARCHIVE_README.md`**
- **Reason:** Archive documentation for deprecated/incomplete runs
- **Content:** Historical notes on failed Job 69317_44 (now complete)
- **Impact:** Outdated - seed 44 is now complete
- **Action:** DELETE (archive material)

**3. `./.cleanup_backup_2026_09_09/README_INDEPENDENT.md` & `.RECONSTRUCTION_V2_README.md`**
- **Reason:** Backup files from cleanup operation
- **Content:** Redundant versions
- **Impact:** Temporary backup files
- **Action:** DELETE (already in cleanup backup)

---

## 🔒 FILES TO RETAIN

### Data Description READMEs (Keep minimal versions)

**`./data/README.md`** (17 lines) ✅ KEEP
- Brief overview of data structure
- Links to subdirectories
- Currently minimal - OK to keep

**`./data/extrinsic/en_am/README.md`** (22 lines) ✅ KEEP
- Describes 100 EN→Amharic test sentence pairs
- Quick reference for evaluators
- No bloat

**`./data/extrinsic/en_ti/README.md`** (30 lines) ✅ KEEP
- Describes 102 EN→Tigrinya test pairs
- Notes on data expansion (31 new pairs added)
- Useful for reproducibility

**`./data/extrinsic/en_tig/README.md`** (44 lines) ✅ KEEP
- Describes 103 EN→Tigre zero-shot test pairs
- Notes on expansion (60 new pairs)
- Quick reference

**`./data/extrinsic/en_gz/README.md`** (36 lines) ✅ KEEP
- Describes 100 EN→Ge'ez zero-shot test pairs
- Zero-shot transfer evaluation notes
- Minimal documentation

### Tokenizer Reference READMEs (Keep as pointers)

**`./Tokenizers/bpe/README.md`** (24 lines) ✅ KEEP
- Explains BPE is external reference (not stored)
- Points to HuggingFace repository
- Educational value

**`./Tokenizers/wordpiece/README.md`** (19 lines) ✅ KEEP
- Explains WordPiece is external reference
- Pointer to BERT tokenizer documentation
- Educational value

**`./Tokenizers/movoc_tok/README.md`** (85 lines) ✅ KEEP
- Detailed explanation of MoVoC-Tok morpheme-aware approach
- Technical documentation of tokenizer design
- Research reference

### Results Documentation (Keep specialized)

**`./PUBLICATION_PACKAGE/5_RESULTS/README.md`** (263 lines) ✅ KEEP
- Specialized guide to TABLE 3 results interpretation
- Links to specific result files and analysis
- Contains results-specific evaluation notes
- NOT redundant with root README
- Justification: Readers needing detailed result interpretation should have this

**`./PUBLICATION_PACKAGE/README.md`** (436 lines) ⚠️ CONSOLIDATE
- **Action:** Extract key sections into root README
- **Keep:** As secondary reference with condensed version
- **Detail:** Most content can be summarized in root README

---

## 📐 PROPOSED ROOT README.md (Outline)

```markdown
# MarianMT Tokenizer Comparison: EN-Amharic & EN-Tigrinya Translation
## Independent Full-Scale Extrinsic Evaluation for Low-Resource African Languages

### ⚠️ Important Disclaimer
[Link to REPOSITORY_CONTEXT.md - 3 sentences]

### 🎯 Key Findings
[Results table - 6 rows]

### 📋 Quick Start
```bash
pip install -r requirements.txt
cd PUBLICATION_PACKAGE
bash ../scripts/evaluate_models.sh
```

### 📁 Repository Structure
[Consolidated directory tree - 50 lines max]

### 🔬 Experimental Design
- **Phases:** Phase 1, Phase 2, Phase 3 overview
- **Models:** 36 total experiments (35/36 complete, 97%)
- **Languages:** EN→Amharic, EN→Tigrinya (+ zero-shot EN→Ge'ez, EN→Tigre)
- **Tokenizers:** BPE, WordPiece, MoVoC-Tok

### 🚀 Running Experiments
```bash
# SLURM job submission
sbatch slurm/train_one.sbatch

# Local training
python src/marianmt_comparison/training.py --language_pair en_am --tokenizer bpe --seed 42

# Evaluation
python scripts/evaluate_models.sh
```

### 📊 Results & Analysis
- Main results: [PUBLICATION_PACKAGE/5_RESULTS/TABLE_3_UPDATED_STATUS.md]
- Complete analysis: [PUBLICATION_PACKAGE/5_RESULTS/README.md]
- Multi-seed evaluation: [COMPLETE_MULTI_SEED_RESULTS_TABLE.md]

### 📚 Key Documentation
- [REPOSITORY_CONTEXT.md] - Full context & disclaimers
- [PUBLICATION_PACKAGE/README.md] - Publication package guide
- [docs/experiment_status.md] - Current experiment status

### ✅ Status & Validation
- Completion: 35/36 experiments (97%)
- Convergence: ✅ Validated across all models
- Publication Status: ✅ READY

### 📝 Citation
[BibTeX]
```

**Estimated lines:** 200-250 (consolidates ~600 lines from PUBLICATION_PACKAGE/README.md)

---

## 🔄 EXECUTION PHASES

### Phase 1: Create New Root README
- [ ] Extract key sections from existing READMEs
- [ ] Consolidate PUBLICATION_PACKAGE/README.md content
- [ ] Add commands for SLURM, GPU training, evaluation
- [ ] Create comprehensive but concise structure
- [ ] **Output:** New root README.md (200-250 lines)

### Phase 2: Approve & Review
- [ ] **User review** - Approve before deletion
- [ ] Adjust structure/content as needed
- [ ] Verify all links are correct
- [ ] Check commands are executable

### Phase 3: Execute Deletions
- [ ] Delete `./PUBLICATION_PACKAGE/7_DOCUMENTATION/README.md` (symlink)
- [ ] Delete `./PUBLICATION_PACKAGE/8_ARCHIVE/ARCHIVE_README.md`
- [ ] Keep all data READMEs (minimal)
- [ ] Keep all tokenizer READMEs (pointers)
- [ ] Keep PUBLICATION_PACKAGE/5_RESULTS/README.md (specialized)

### Phase 4: Verification
- [ ] All links in new README work correctly
- [ ] Subdirectory READMEs still accessible
- [ ] No documentation loss
- [ ] Repository is cleaner & more professional

---

## 📊 EXPECTED OUTCOME

### Before Consolidation
- **Total README files:** 12
- **Root-level documentation:** Scattered across directories
- **Overlapping content:** Multiple READMEs repeat same info
- **User experience:** Confusing navigation between similar READMEs

### After Consolidation
- **Total README files:** 9 (12 - 3 deleted)
- **Root-level documentation:** Comprehensive master README
- **Minimal duplication:** Each README serves specific purpose
- **User experience:** Clear single entry point, links to specialists

### Directory Structure Comparison
```
BEFORE:
├── README.md (101 lines)
├── PUBLICATION_PACKAGE/README.md (436 lines) [similar content]
├── PUBLICATION_PACKAGE/7_DOCUMENTATION/README.md (101 lines) [duplicate link]
├── PUBLICATION_PACKAGE/8_ARCHIVE/ARCHIVE_README.md [outdated]
└── ... 8 more specialized READMEs

AFTER:
├── README.md (200-250 lines) [comprehensive master]
├── PUBLICATION_PACKAGE/5_RESULTS/README.md (263 lines) [specialized]
├── data/README.md (17 lines) [minimal]
├── data/extrinsic/*/README.md (4 files, 22-44 lines each) [pointers]
└── Tokenizers/*/README.md (3 files, 19-85 lines) [pointers]
```

---

## ✅ NEXT STEPS

**AWAITING YOUR APPROVAL:**

1. **Review** the proposed master README outline above
2. **Confirm** which files should be deleted
3. **Approve** the consolidation strategy

**Then I will execute:**
1. Create new comprehensive root README.md
2. Delete flagged redundant READMEs
3. Verify all links and navigation work
4. Confirm repository is publication-ready

---

## 🎯 SUCCESS CRITERIA

✓ Root README is comprehensive (user can understand everything from it)  
✓ Each remaining README serves a unique purpose (no duplication)  
✓ Documentation is optimized for paper reviewers  
✓ All links work and navigation is clear  
✓ Repository feels professional and well-organized  

---

**Status:** 🔴 AWAITING USER APPROVAL  
**Ready for:** Phase 1 (Create Master README)

