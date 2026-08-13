# Reconstruction-v2 extrinsic MT evaluation (Table 3 structure)

**New measurements from the reconstructed pipeline.** These are not the
published Table 3 values and are not a reproduction of them. The published
results remain in the paper and are cited in the repository root README.

Structure follows the paper's Table 3 (tokenizer strategies × BLEU/chrF++).
Values are this reconstruction's own.

9 runs — 3 tokenizers × 3 seeds (42/43/44), one multilingual MarianMT per run,
trained on English→Amharic and English→Tigrinya only. Tigre and Ge'ez are
never trained on and appear as zero-shot evaluation.

### FLORES-200 devtest (n=1012)

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ | Valid Seeds | n | Output quality |
|---|---|---:|---:|---|---:|---|
| English → Amharic | BPE | 1.4937 ± 0.0866 | 21.5573 ± 0.2167 | 42/43/44 | 1012 | clean |
| English → Amharic | WordPiece | 0.0534 ± 0.0140 | 11.5990 ± 0.0295 | 42/43/44 | 1012 | clean |
| English → Amharic | MoVoC-Tok | 0.7907 ± 0.0363 | 18.3999 ± 0.1711 | 42/43/44 | 1012 | flagged (42/43/44) |
| English → Tigrinya | BPE | 1.2557 ± 0.2135 | 10.8757 ± 0.0708 | 42/43/44 | 1012 | clean |
| English → Tigrinya | WordPiece | 0.0439 ± 0.0037 | 6.7069 ± 0.1085 | 42/43/44 | 1012 | clean |
| English → Tigrinya | MoVoC-Tok | 0.2710 ± 0.0775 | 7.8489 ± 0.2845 | 42/43/44 | 1012 | flagged (42/43/44) |

### OPUS/Tatoeba — supervised directions

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ | Valid Seeds | n | Output quality |
|---|---|---:|---:|---|---:|---|
| English → Amharic | BPE | 0.4131 ± 0.1039 | 18.4723 ± 2.0884 | 42/43/44 | 100 | flagged (42/43/44) |
| English → Amharic | WordPiece | 0.0286 ± 0.0103 | 6.7737 ± 0.1963 | 42/43/44 | 100 | flagged (42/43/44) |
| English → Amharic | MoVoC-Tok | 0.1694 ± 0.0418 | 10.2681 ± 0.9363 | 42/43/44 | 100 | flagged (42/43/44) |
| English → Tigrinya | BPE | 0.1909 ± 0.0487 | 11.2057 ± 0.3469 | 42/43/44 | 71 | flagged (42/43/44) |
| English → Tigrinya | WordPiece | 0.0347 ± 0.0036 | 5.0109 ± 0.1487 | 42/43/44 | 71 | flagged (42/43/44) |
| English → Tigrinya | MoVoC-Tok | 0.1279 ± 0.0409 | 5.1444 ± 0.1739 | 42/43/44 | 71 | flagged (42/43/44) |

### OPUS/Tatoeba — zero-shot directions

| Direction | Tokenizer | BLEU ↑ | chrF++ ↑ | Valid Seeds | n | Output quality |
|---|---|---:|---:|---|---:|---|
| English → Tigre | BPE | 1.1460 ± 0.0535 | 10.3310 ± 0.6563 | 42/43/44 | 43 | flagged (42/43/44) |
| English → Tigre | WordPiece | 0.0912 ± 0.0220 | 5.2580 ± 0.2879 | 42/43/44 | 43 | flagged (42/43/44) |
| English → Tigre | MoVoC-Tok | 0.1677 ± 0.0632 | 5.5903 ± 0.6641 | 42/43/44 | 43 | flagged (42/43/44) |
| English → Ge'ez | BPE | 0.0195 ± 0.0059 | 5.0322 ± 0.0504 | 42/43/44 | 100 | clean |
| English → Ge'ez | WordPiece | 0.0000 ± 0.0000 | 4.2900 ± 0.0920 | 42/43/44 | 100 | clean |
| English → Ge'ez | MoVoC-Tok | 0.0150 ± 0.0012 | 4.8138 ± 0.1196 | 42/43/44 | 100 | clean |

## Aggregation

Mean and sample standard deviation (ddof=1) over the three run-level scores
per cell. sacreBLEU 2.6.0; `BLEU()` and `CHRF(word_order=2)`.

## Scientific validity

BLEU is below 2 in every cell. Final training loss is 3.00–3.59 against
~3.13 for a comparable from-scratch MarianMT trained with 5.5× more
optimizer steps. **These runs support no ranking claim about the tokenizers**
in either direction.

All 18 FLORES cells have 1012/1012 unique hypotheses, 0% empty output, no
`<unk>` collapse, and aligned hypothesis/reference counts. Cells marked
*flagged* tripped an automated repetition detector; see `PROVENANCE.md` for
which are genuine repetition and which are an artifact of Ge'ez punctuation
frequency.
