# Intrinsic tokenizer evaluation

## In-language MoVoC-Tok evaluation

MoVoC-Tok was trained on these languages' own morpheme resources.

| Language | Tokenizer | Boundary Precision | MorphScore | Rényi α=2 |
|----------|-----------|-------------------|------------|-----------|
| Amharic | BPE | 0.3170 | 0.4105 | 6.2487 |
| Amharic | WordPiece | 0.3005 | 0.3842 | 5.9949 |
| Amharic | MoVoC-Tok | 0.3208 | 0.4139 | 6.0589 |
| Tigrinya | BPE | 0.3142 | 0.4200 | 6.3747 |
| Tigrinya | WordPiece | 0.3167 | 0.4186 | 5.6979 |
| Tigrinya | MoVoC-Tok | 0.3242 | 0.4366 | 6.2727 |

## Cross-lingual MoVoC-Tok evaluation

Tigre and Ge'ez were excluded from MoVoC-Tok training because no
independent training morpheme resources were available. Their manual
annotations were reserved exclusively for intrinsic evaluation.
MoVoC-Tok results for these languages (marked `*`) are a cross-lingual
generalization measurement and do not represent language-specific
training.

| Language | Tokenizer | Boundary Precision | MorphScore | Rényi α=2 |
|----------|-----------|-------------------|------------|-----------|
| Tigre | BPE | 0.5380 | 0.5004 | 5.4060 |
| Tigre | WordPiece | 0.5123 | 0.4778 | 5.0260 |
| Tigre | MoVoC-Tok* | 0.5629 | 0.5278 | 5.3192 |
| Geez | BPE | 0.4326 | 0.6667 | 3.8639 |
| Geez | WordPiece | 0.4201 | 0.6392 | 3.9152 |
| Geez | MoVoC-Tok* | 0.4301 | 0.6561 | 3.9735 |

