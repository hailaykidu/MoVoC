# Dataset Inventory

Every dataset used in the paper *MoVoC: Morphology-Aware Subword Construction for
Ge'ez Script Languages* (Findings of EMNLP 2025, arXiv:2509.08812). One row per
dataset. A reviewer can locate every dataset from this table without searching
the repository.

## Fine-tuning (extrinsic MT, Table 3)

The MarianMT models scored in Table 3 are fine-tuned on the **OPUS NLLB**
parallel corpus (No Language Left Behind; Costa-Jussà et al., 2022).

This corpus is too large to commit — 16.1 M pairs (~2.6 GB) for en→am, 1.4 M
pairs (~220 MB) for en→ti, and individual files exceed GitHub's 100 MB
per-file limit. `data/finetuning/en_am/` and `data/finetuning/en_ti/` therefore
hold a **manifest** rather than the bitext; the manifest is the reproducible
substitute.

| Language pair | Corpus | Corpus files | Available pairs | Manifest | Released here? | Paper section |
|---|---|---|---:|---|---|---|
| English → Amharic (en→am) | **OPUS NLLB** (Costa-Jussà et al., 2022) | `NLLB.am-en.en` / `NLLB.am-en.am` | 16,137,053 | `data/finetuning/en_am/manifest.json` | No — 2.6 GB CC-BY-SA bitext; manifest carries SHA256 + OPUS URL | §4.3, Table 3 |
| English → Tigrinya (en→ti) | **OPUS NLLB** (Costa-Jussà et al., 2022) | `NLLB.en-ti.en` / `NLLB.en-ti.ti` | 1,398,173 | `data/finetuning/en_ti/manifest.json` | No — 220 MB CC-BY-SA bitext; manifest carries SHA256 + OPUS URL | §4.3, Table 3 |

`data/finetuning/en_am/manifest.json` and `data/finetuning/en_ti/manifest.json`
record the corpus name, exact source-file names, byte size, line count and
SHA256 of each, the OPUS download URL, and the 800k/100k/100k
train/valid/test sample sizes the V2 reconstruction used
(`v2/table3/PROVENANCE.md`, `v2/table3/table3_multiseed.json`). Corpus identity
is also in `configs/tokenizer_comparison.yaml`,
`evaluation/finetune_marianmt.py` and each
`tokenizers/*/training_config.json`. Ge'ez and Tigre are **not** in the NLLB
fine-tuning data (paper §4.1) and are evaluated zero-shot.

## Extrinsic MT test sets (Table 3)

| Dataset | Purpose | Source | Language pair | Split size | Paper section |
|---|---|---|---|---|---|
| `data/evaluation/amharic/test.{en,am}` | held-out MT test, in-language | OPUS / Tatoeba (Tiedemann, 2012); 100 of 213 raw lines | en→am | 100 pairs | §4.3, Table 3 |
| `data/evaluation/tigrinya/test.{en,ti}` | held-out MT test, in-language | OPUS / Tatoeba (Tiedemann, 2012); 71 of 74 raw lines | en→ti | 71 pairs | §4.3, Table 3 |
| `data/zeroshot/en_tig_opus/{source,target}.txt` | zero-shot MT test (untrained language) | OPUS / Tatoeba (Tiedemann, 2012); 43 of 45 raw lines | en→tig | 43 pairs | §4.3, Table 3 |
| `data/zeroshot/en_gz_mermru/{source,target}.txt` | zero-shot MT test (untrained language) | Mermru English–Ge'ez parallel corpus (https://mermru.com/); 100 held out from 2,107 with seed 42 | en→gez | 100 pairs | §4.2 / §4.3 (V2 probe; not a reproduction of the published Ge'ez block) |
| `data/evaluation/flores200.zip` | FLORES-200 devtest, MT evaluation | Goyal et al. (2022); Costa-Jussà et al. (2022) | en→am, en→ti | devtest | §4.3, Table 3 |

`data/zeroshot/en_tig_opus/` and `en_gz_mermru/` are copies of
`data/evaluation/{tigre,geez}/test.*`; the scripts read the `data/evaluation/`
paths. Zero-shot: no Tigre or Ge'ez text enters MT training, tokenizer training,
or vocabulary construction.

## Intrinsic morpheme datasets (Table 2 — MorphScore; Table 4 — boundary precision, Rényi entropy)

| Dataset | Purpose | Source | Language | Split sizes (annotations → scored gold set) | Paper section |
|---|---|---|---|---|---|
| `data/intrinsic/amharic/` | gold morpheme boundaries | HornMorpho analysis + human post-editing | Amharic (amh) | 153,759 records → 81,224 gold words | §5, Table 2, Table 4 |
| `data/intrinsic/tigrinya/` | gold morpheme boundaries | manual gold (held out) + HornMorpho post-editing | Tigrinya (tir) | 206 gold + 7,531 post-edited → 5,224 gold words | §5, Table 2, Table 4 |
| `data/intrinsic/tigre/` | gold morpheme boundaries | manual annotation | Tigre (tig) | 8,117 records → 1,974 gold words | §5, Table 2, Table 4 |
| `data/intrinsic/geez/` | gold morpheme boundaries | manual annotation | Ge'ez (gez) | 193 records → 172 gold words | §5, Table 2, Table 4 |

Each `data/intrinsic/<lang>/` holds the annotation JSON (`*_morphemes.json`) plus
the scored gold set (`<lang>_gold.tsv`) and its per-word provenance
(`<lang>_provenance.tsv`). These are copies; the scripts read
`data/annotations/<lang>/` and `evaluation/data/<lang>_gold.tsv`. Gold-set
construction and exclusion counts: `evaluation/data/manifest.json`. Ge'ez and
Tigre morpheme data is evaluation-only (paper §4.1).

## Vocabulary and corpus resources

| Dataset | Purpose | Source | Language | Size | Paper section |
|---|---|---|---|---|---|
| `data/vocabulary/vocab_movoc.txt` | released MoVoC hybrid vocabulary | built by `train.py` from Amharic + Tigrinya corpora | amh + tir | 114,553 entries | §3.2 |
| `data/vocabulary/bpe_{amharic,tigrinya,tigre,geez}.json` | released BPE baselines | `train.py` | per language | 32k each (geez 15k) | §4.3 |
| `data/vocabulary/wordpiece_{amharic,tigrinya}.json` | released WordPiece baselines | `train.py` | amh, tir | 32k each | §4.3 |
| `data/raw/hornmt/{amh,eng,tir}.txt` | HornMT parallel source corpora | HornMT | amh, eng, tir | 2,030 lines each | §3.2 |
| `data/raw/geez_words.txt`, `data/raw/extended/{geez,tigre}_words.txt` | Ge'ez / Tigre word lists for the cross-lingual verification arms | user-supplied corpora (not part of MoVoC; see `v2/tokenizers/extended_arms_build_reconstruction_v2.json`) | gez, tig | 341 / 2,039 / 419,626 words | §5 (V2 arms) |

## Released tokenizers

| Artifact | Purpose | Language | Paper section |
|---|---|---|---|
| `tokenizers/amharic_movoc_tok_32k/` | released MoVoC-Tok tokenizer | Amharic | §3.3, Tables 2–4 |
| `tokenizers/tigrinya_movoc_tok_32k/` | released MoVoC-Tok tokenizer | Tigrinya | §3.3, Tables 2–4 |
| `tokenizers/bpe_32k/`, `tokenizers/wordpiece_32k/` | released baseline tokenizers | Amharic / Tigrinya | §4.3, Tables 2–4 |
| `models/movoc_tok_merges_{geez,tigre}.txt` | post-publication cross-lingual MoVoC-Tok merge tables | Ge'ez, Tigre | §5 (cross-lingual assumption; see `v2/table4/`) |
