# V2 Reconstruction Scripts

This directory contains scripts used in the second reconstruction (v2) of the MoVoC paper results.

## Contents

### Table 2 Reproduction
- `table2_reproduction/score_official_first.py` — Official MoVoC data first, AMSEG fallback
- `table2_reproduction/score_union_tir_tig.py` — Union analysis for Tigrinya & Tigre

### Table 4 Reproduction  
- `table4_reproduction/eval_table4_official.py` — Official methodology with corrections
- `table4_reproduction/precision_linguistic.py` — Linguistic sensitivity analysis (5 variants)

### MT Experiments
- `mt_experiments/train_mt_gez.py` — English → Classical Ge'ez fine-tuning

## Usage

```bash
# Table 2 reproduction
cd table2_reproduction
python score_official_first.py
python score_union_tir_tig.py

# Table 4 reproduction
cd table4_reproduction
python eval_table4_official.py
python precision_linguistic.py

# Ge'ez MT experiment (from amseg/mt_finetune)
python train_mt_gez.py --output_dir ./mt_output_gez
```

## Paper Tables Generated

- Table 2: MorphScore (boundary precision)
- Table 4: Boundary precision and Rényi entropy (normalized)
- Sensitivity analysis: 5 linguistic variants

See parent directory README for full context.
