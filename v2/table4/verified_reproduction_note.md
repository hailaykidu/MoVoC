# `table4_final.csv` status

`v2/table4/table4_final.csv` is the current authoritative reconstruction
because `scripts/evaluate_intrinsic.py`, run against the committed
evaluation sets and tokenizer artifacts, reproduces all 12 rows exactly. It
supersedes the earlier intrinsic result files because the evaluation set,
entropy normalization, and tokenizer coverage were corrected. However, this
reconstruction does not reproduce the numerical values reported in the
published Table 4; that discrepancy remains unresolved and is documented
separately (`intrinsic_detail.md`).

| | Earlier (`boundary_precision.csv` / `renyi_entropy.csv`) | Current (`table4_final.csv`) |
|---|---|---|
| Amharic words evaluated | 123,761 | 81,224 |
| Rényi entropy | raw nats (4.5–8.1) | normalized to [0, 1] |
| Tokenizers scored | MoVoC-Tok, BPE | MoVoC-Tok, BPE, WordPiece |
