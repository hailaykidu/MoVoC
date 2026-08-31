# Table 4: Morpheme Boundary Precision and Rényi Entropy (α = 2)

32k-vocabulary BPE vs MoVoC-Tok (constrained-BPE), across four
Ethio-Semitic languages.

| Language | Tokenization | Precision ↑ | Rényi Entropy ↓ |
|-----------|-------------|------------:|----------------:|
| Amharic | MoVoC-Tok | 32.1 | 0.6379 |
| Amharic | BPE | 31.7 | 0.6698 |
| Tigrinya | MoVoC-Tok | 24.1 | 0.7897 |
| Tigrinya | BPE | 24.4 | 0.8024 |
| Tigre | MoVoC-Tok | 56.3 | 0.7766 |
| Tigre | BPE | 53.8 | 0.7882 |
| Ge'ez | MoVoC-Tok | 36.9 | 0.8255 |
| Ge'ez | BPE | 38.3 | 0.7991 |

Source: `results/table4_32k_results.json`.

## Tokenizer checkpoint

MoVoC-Tok rows use the constrained-BPE checkpoint (Section 3.3 method):
`amseg/tokenizers/hf/movoc_tok_32k_{amharic,tigrinya}`, verified
HuggingFace exports of the native `{amharic,tigrinya}_movoc_tok_32k`
checkpoints.

## Cross-lingual handling

Amharic and Tigrinya are in-language evaluations: each uses its own
dedicated MoVoC-Tok checkpoint.

Tigre and Ge'ez are cross-lingual intrinsic evaluations: their own gold
morpheme evaluation data is scored using the Tigrinya MoVoC-Tok
tokenizer as the cross-lingual substitute, since no dedicated MoVoC-Tok
model was ever trained for either language.

## Methodology

- **Boundary Precision**: for every boundary a tokenizer's segmentation
  produces, match = 1 if it coincides exactly with a gold morpheme
  boundary, else 0. Precision = matched predicted boundaries / total
  predicted boundaries, micro-averaged, reported as a percentage.
- **Rényi entropy (α = 2)**, normalized: `H₂ = (1/(1-α))·log(Σpᵢ²)` in
  nats over the tokenizer's empirical token-frequency distribution on
  the evaluation word list, divided by `log(support)` (support = number
  of unique tokens used), landing in [0, 1].
- Gold boundaries come from the surface-projected morpheme sets
  (`{lang}_boundary_projected.tsv`).
- Words the tokenizer emits with zero predicted boundaries are excluded
  from Boundary Precision.

Reproduce with:

```bash
cd /homes/neumann/teklehaymanot/marianmt-tokenizer-comparison/Intrinsic_Evaluation
python3 scripts/table4_final.py
```
