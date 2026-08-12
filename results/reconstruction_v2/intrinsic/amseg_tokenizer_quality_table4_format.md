# Table 4 format — this rerun's measurements

Morpheme Boundary Precision and Rényi Entropy (α = 2) for 32k vocabularies.
↑ / ↓ indicates the metric should be maximized / minimized.

| Language | Tokenization | Precision ↑ | Rényi Entropy ↓ |
|----------|--------------|------------:|----------------:|
| Amharic | MoVoC-Tok | 32.1 | 0.63 |
|  | BPE | 31.7 | 0.66 |
|  | WordPiece | 30.1 | 0.63 |
| Tigrinya | MoVoC-Tok | 32.4 | 0.76 |
|  | BPE | 31.4 | 0.77 |
|  | WordPiece | 31.7 | 0.68 |
| Tigre | MoVoC-Tok* | 56.3 | 0.73 |
|  | BPE | 53.8 | 0.75 |
|  | WordPiece | 51.2 | 0.69 |
| Ge‘ez | MoVoC-Tok* | 43.0 | 0.82 |
|  | BPE | 43.3 | 0.81 |
|  | WordPiece | 42.0 | 0.82 |

`*` = cross-lingual: MoVoC-Tok was not trained on this language.

---

## Side by side with the published Table 4

Published values are cited from the paper for orientation only; they were
produced by a different run on different data and are not a target this
rerun attempts to match.

| Language | Tokenization | Precision (paper) | Precision (ours) | Rényi (paper) | Rényi (ours) |
|----------|--------------|------------------:|-----------------:|--------------:|-------------:|
| Amharic | MoVoC-Tok | 85.5 | 32.1 | 0.40 | 0.63 |
|  | BPE | 85.3 | 31.7 | 0.41 | 0.66 |
| Tigrinya | MoVoC-Tok | 88.3 | 32.4 | 0.39 | 0.76 |
|  | BPE | 83.9 | 31.4 | 0.40 | 0.77 |
| Tigre | MoVoC-Tok* | 83.9 | 56.3 | 0.44 | 0.73 |
|  | BPE | 74.6 | 53.8 | 0.49 | 0.75 |
| Ge‘ez | MoVoC-Tok* | 85.6 | 43.0 | 0.40 | 0.82 |
|  | BPE | 73.9 | 43.3 | 0.44 | 0.81 |
