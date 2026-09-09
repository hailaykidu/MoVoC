# ⚡ QUICK PUSH GUIDE — 5-Minute Overview

**Target:** https://github.com/hailaykidu/MoVoC/tree/main/v2/table3_extrinsic_mt

---

## 🚀 THE ESSENTIALS

### Command Sequence (Copy-Paste Ready)

```bash
# 1. Navigate to your MoVoC repository
cd ~/MoVoC
git checkout main
git pull origin main

# 2. Create v2 directory and copy files
mkdir -p v2/table3_extrinsic_mt
cd v2/table3_extrinsic_mt

# 3. Copy marianmt-tokenizer-comparison (entire directory)
cp -r /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/* .

# 4. Initialize Git LFS
git init
git lfs install

# 5. Create .gitattributes (copy exact content below)
cat > .gitattributes << 'GITATTRS'
# Model checkpoint files
experiments/**/*.safetensors filter=lfs diff=lfs merge=lfs -text
experiments/**/*.bin filter=lfs diff=lfs merge=lfs -text
experiments/**/*.pt filter=lfs diff=lfs merge=lfs -text

# Tokenizer files
Tokenizers/**/*.json filter=lfs diff=lfs merge=lfs -text
Tokenizers/**/*.txt filter=lfs diff=lfs merge=lfs -text

# Training/test data
data/train/**/*.tar.gz filter=lfs diff=lfs merge=lfs -text
data/train/**/*.pkl filter=lfs diff=lfs merge=lfs -text
data/test/**/*.tar.gz filter=lfs diff=lfs merge=lfs -text
data/test/**/*.pkl filter=lfs diff=lfs merge=lfs -text

# Result files
results/**/*.json filter=lfs diff=lfs merge=lfs -text
results/**/*.pkl filter=lfs diff=lfs merge=lfs -text

# SLURM logs
slurm/logs/**/*.out filter=lfs diff=lfs merge=lfs -text
slurm/logs/**/*.err filter=lfs diff=lfs merge=lfs -text
GITATTRS

# 6. Configure Git LFS tracking
git lfs track "experiments/**/*.safetensors"
git lfs track "experiments/**/*.bin"
git lfs track "experiments/**/*.pt"
git lfs track "Tokenizers/**/*.json"
git lfs track "Tokenizers/**/*.txt"
git lfs track "data/**/*.tar.gz"
git lfs track "data/**/*.pkl"
git lfs track "results/**/*.json"
git lfs track "results/**/*.pkl"
git lfs track "slurm/logs/**/*.out"
git lfs track "slurm/logs/**/*.err"

# 7. Stage all files
git add .

# 8. Commit with message
git commit -m "MarianMT Tokenizer Comparison: Independent Full-Scale Experiments

## Summary

Independent full-scale training and evaluation of three tokenization strategies
(BPE, WordPiece, MoVoC-Tok) for English-to-Amharic and English-to-Tigrinya
machine translation using the MarianMT framework.

## Results Summary

EN→Amharic: MoVoC-Tok achieves 0.899 ± 0.003 BLEU (14.65 ± 0.25 ChrF++)
EN→Tigrinya: BPE achieves 0.809 ± 0.247 BLEU (8.49 ± 0.40 ChrF++)

See REPRODUCIBILITY_AUDIT.md and FINAL_PUBLICATION_DECISION.md for details.

Signed-off-by: Claude Haiku 4.5 <noreply@anthropic.com>"

# 9. Set branch and push
git branch -M main
git remote add origin https://github.com/hailaykidu/MoVoC.git
git push -u origin main

# ✅ DONE! Wait 1-4 hours for push to complete
```

---

## ⏱️ TIMELINE

| Step | Action | Time |
|---|---|---|
| 1-4 | Setup | 5 min |
| 5-6 | Git LFS config | 2 min |
| 7-8 | Stage & commit | 10 min |
| 9 | Push to GitHub | **1-4 hours** |
| **TOTAL** | | **1-4 hours** |

---

## ✅ PRE-PUSH CHECKLIST

- [ ] GitHub account configured
- [ ] Write access to hailaykidu/MoVoC
- [ ] Git LFS installed (`git lfs --version`)
- [ ] ~52 GB available bandwidth
- [ ] On `main` branch
- [ ] Latest MoVoC pulled

---

## 📊 WHAT YOU'RE PUSHING

| Component | Size | Files |
|---|---|---|
| **Code** | ~100 MB | 20+ |
| **Data** | ~300 MB | 40+ |
| **Models (LFS)** | ~43 GB | 23 |
| **Tokenizers (LFS)** | ~150 MB | 7 |
| **Docs & Results** | ~50 MB | ~200 |
| **TOTAL** | ~52 GB | ~500+ |

---

## 🔍 AFTER PUSH: VERIFY SUCCESS

```bash
# 1. Check GitHub web interface
https://github.com/hailaykidu/MoVoC/tree/main/v2/table3_extrinsic_mt

# 2. Look for "Large Files Detected" badge
# 3. Verify ~500 files visible
# 4. Check README.md displays

# 5. Clone and verify (optional)
cd /tmp
git clone https://github.com/hailaykidu/MoVoC.git
cd MoVoC/v2/table3_extrinsic_mt
git lfs ls-files | wc -l
# Expected: 50+ files

du -sh .
# Expected: ~400 MB (LFS pointers)
```

---

## 🆘 QUICK TROUBLESHOOTING

### Push hangs/times out
```bash
GIT_HTTP_CONNECT_TIMEOUT=60 GIT_HTTP_TIMEOUT=300 git push -u origin main
```

### Permission denied
```bash
git remote set-url origin https://github.com/hailaykidu/MoVoC.git
git config credential.helper store
git push -u origin main
```

### LFS not tracking files
```bash
git lfs install
git lfs track "experiments/**/*.safetensors"
git add .gitattributes
git commit --amend --no-edit
git push -u origin main --force-with-lease
```

---

## 📝 OPTIONAL: CREATE GITHUB RELEASE

After successful push:

```
Go to: https://github.com/hailaykidu/MoVoC/releases/new

Tag: v2-table3-extrinsic-mt
Title: MarianMT Tokenizer Comparison: Table 3 Results

Description: Copy from GITHUB_PUSH_INSTRUCTIONS.md Section 7b
```

---

## 🎉 YOU'RE DONE WHEN

✅ `git push` completes without errors  
✅ GitHub shows ~500 files in v2/table3_extrinsic_mt  
✅ Git LFS badge visible  
✅ README.md displays correctly  
✅ Clone test succeeds  

---

**Time to publish:** 1-4 hours total (mostly waiting for push)  
**Status:** ✅ Ready to go

