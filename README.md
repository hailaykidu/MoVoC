# MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages

The official implementation and resource repository for the published paper
*"MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages"*
(Teklehaymanot, Fazlija & Nejdl;
arXiv:[2509.08812](https://arxiv.org/abs/2509.08812)).

---

## Introduction

Subword tokenizers such as Byte-Pair Encoding rely on statistical
co-occurrence frequencies without explicitly considering morphemes. For
morphologically rich languages this limits morphological generalization,
which affects interpretability, compositionality, and cross-lingual
transfer.

The paper targets Ge'ez-script languages, which are characterized by
fusional morphology and a scarcity of linguistically motivated tools and
morphologically annotated data. It contributes morpheme-annotated datasets
for four Ge'ez-script languages — Amharic, Tigrinya, Ge'ez and Tigre — and
a morphology-aware subword construction method evaluated against standard
subword tokenizers.

---

## Methodology

The paper describes three methodological components (Sec. 3). This
repository implements each.

### 1. Pre-tokenization and supervised morphological analysis (Sec. 3.1)

A pre-tokenization pipeline based on customized regular expressions
tailored to the orthographic and morphological characteristics of
Ge'ez-script languages, covering stopword removal, punctuation
normalization and special-character filtering. Morphological analysis is
**supervised**, drawing on the annotated morpheme data described below.

*Implemented in* `movoc/preprocessing.py`, `movoc/hornmorph.py`,
`movoc/annotation.py`.

### 2. Vocabulary construction — MoVoC (Sec. 3.2)

A hybrid vocabulary combining frequent morphemes with frequent subword
units. A hyperparameter `r ∈ [0,1]` controls the ratio of morpheme tokens:

```
V = V_BPEsmall ∪ V_morph
|V_BPEsmall| = s(1 − r)        |V_morph| = sr
```

*Implemented in* `movoc/vocabulary.py` (Algorithm 1: sizes,
`extract_morphemes`, merge), driven end to end by `train.py`.

### 3. MoVoC-Tok — morpheme-aware subword segmentation (Sec. 3.3)

A BPE tokenizer is trained using the mixed vocabulary obtained from MoVoC.
Because conventional BPE merge operations are data-driven and can combine
subwords that cross morpheme boundaries, morphological constraints are
incorporated directly into BPE training by **limiting merge candidates to
those that do not span morpheme boundaries defined by MoVoC**. This
prevents invalid merges and ensures the resulting tokenization adheres to
morphological segmentation.

Tokenization proceeds in two stages: words are first segmented into
morphemes, then BPE is applied within each morpheme.

*Implemented in* `movoc/tokenizer.py` (`Train_BPE` and the constrained
merge procedure), applied by `segment.py`.

---

## Dataset and resources

### Morpheme annotations

The paper creates morphological datasets for four Ge'ez-script languages.
Annotations reach their final form by one of two routes, depending on
whether a morphological analyzer covers the language.

| Language | Initial analysis | Human post-editing | Entries |
|---|---|---|---|
| Amharic | HornMorpho | yes | 153,759 |
| Tigrinya | HornMorpho | yes | 7,531 curated + 206 gold |
| Ge'ez | — | manual | 193 |
| Tigre | — | manual | 8,117 |

For Amharic and Tigrinya, HornMorpho provides the initial analysis, which
is then manually post-edited. The Tigrinya gold set is held out from
vocabulary construction and used for evaluation.

*Location:* `data/annotations/{amharic,tigrinya,tigre,geez}/`

### Corpora

- **NLLB** (Costa-Jussà et al., 2022) — Amharic and Tigrinya text for BPE
  training, and the English–Amharic / English–Tigrinya parallel corpora for
  the downstream translation evaluation.
- **HornMT** — parallel corpus used as the raw source for morphological
  analysis. *Location:* `data/raw/hornmt/`
- **FLORES-200** (Goyal et al., 2022) — development and test sets for
  Amharic and Tigrinya. Ships as `data/evaluation/flores200.zip`,
  password-protected with `multilingual machine translation`, the password
  OLDI publishes in its own README. The archive keeps the sentences out of
  web crawlers, which would otherwise pull them into training corpora.
- **OPUS / Tatoeba** (Tiedemann, 2012) — final translation evaluation sets.
  *Location:* `data/evaluation/{amharic,tigrinya,tigre}/`

---

## Experimental setup

### Target languages (Sec. 4.1)

Amharic, Tigrinya, Ge'ez and Tigre. Ge'ez and Tigre lack morphological
analyzers, so their morpheme sets are constructed manually.

### Vocabulary configuration

`configs/movoc_config.json` holds the vocabulary parameters used by
`train.py`; `configs/bpe_config.json` holds the baseline BPE
configuration.

### Training setup (Sec. 4.3)

Tokenizers are trained with the HuggingFace `tokenizers` library. The
downstream translation model is a fine-tuned MarianMT
(Junczys-Dowmunt et al., 2018) with the architecture the paper reports:

| | |
|---|---|
| Encoder / decoder layers | 6 / 6 |
| Attention heads | 8 |
| Hidden size | 512 |
| Feedforward dimension | 2048 |
| Activation | Swish |
| Embeddings | shared encoder–decoder |
| Positional encoding | static |
| Vocabulary size | 63,050 |

Training used the HuggingFace Transformers library (version 4.51.3), on a
single GPU with 6 CPU cores, 32 GB RAM and a maximum runtime of 24 hours.

*Implemented in* `evaluation/finetune_marianmt.py`;
`scripts/submit_marianmt.sh` is the Slurm wrapper.

---

## Evaluation framework

### Extrinsic evaluation (Sec. 5.1)

Machine translation between English and the Ge'ez-script languages, scored
with **BLEU** (Papineni et al., 2002) and **chrF++** (Popović, 2017).
Training covers English–Amharic and English–Tigrinya; **Tigre is not
included during training** and appears at evaluation to assess zero-shot
translation.

COMET is not used: it depends on pretrained models and reference corpora
available only for high-resource languages, and no reliable
COMET-compatible model exists for Tigrinya, Tigre or Ge'ez.

*Implemented in* `evaluation/translate_eval.py`.

### Intrinsic evaluation (Sec. 5.2)

Three metrics over the annotated morpheme test set:

- **Morpheme boundary precision** (Nouri & Yangarber, 2016) — predicted
  boundaries compared against gold-standard boundaries.
- **MorphScore** (Arnett & Bergen, 2025) — 1 if a token boundary aligns
  with a gold morpheme boundary, 0 otherwise; unsegmented words excluded.
  Recall-oriented, and does not penalize false positives.
- **Rényi entropy** (Rényi, 1961) — subword diversity and balance over
  token distributions. Lower values indicate sharper, more consistent
  segmentation.

*Implemented in* `movoc/metrics.py`, run by `evaluate.py`.

---

## Results

The paper reports intrinsic results in Table 2 and translation results in
Table 3. Table 3:

| Strategy | BLEU↑ | chrF++↑ |
|---|---|---|
| **English→ Amharic** | | |
| BPE | 0.2150 ± 0.0120 | 16.2000 ± 1.05 |
| WordPiece | 0.2340 ± 0.0155 | 16.5000 ± 1.00 |
| MoVoC-Tok | **0.2455 ± 0.0108** | **17.8500 ± 0.95** |
| **English→ Tigrinya** | | |
| BPE | 0.1720 ± 0.0095 | 7.2000 ± 0.85 |
| WordPiece | 0.1880 ± 0.0088 | 7.5000 ± 0.80 |
| MoVoC-Tok | **0.2050 ± 0.0080** | **8.1000 ± 0.75** |
| **English→ Tigre** | | |
| BPE | 0.0950 ± 0.0080 | 4.0000 ± 0.70 |
| WordPiece | 0.1025 ± 0.0075 | 4.3000 ± 0.65 |
| MoVoC-Tok | **0.1175 ± 0.0068** | **5.1500 ± 0.60** |
| **English→ Ge'ez** | | |
| BPE | 0.0480 ± 0.0070 | 3.0500 ± 0.55 |
| WordPiece | 0.0550 ± 0.0065 | 3.2500 ± 0.60 |
| MoVoC-Tok | **0.0660 ± 0.0060** | **3.9500 ± 0.50** |

These are the paper's published values. **This repository reports no
experimental results of its own.** The code to run the intrinsic and
extrinsic evaluations is provided below; result files are written to
`evaluation/results/` and are not tracked.

---

## Repository contents

```
train.py                    Algorithm 1 end to end
evaluate.py                 intrinsic evaluation
segment.py                  segment text with a trained MoVoC-Tok model

configs/                    vocabulary and baseline BPE configuration

movoc/
  preprocessing.py          corpus preparation (Sec. 3.1)
  hornmorph.py              interface to HornMorpho
  annotation.py             loading and validating morpheme annotations
  vocabulary.py             vocabulary construction (Sec. 3.2)
  tokenizer.py              MoVoC-Tok constrained merges (Sec. 3.3)
  metrics.py                boundary precision, MorphScore, Rényi entropy
  utils.py                  fidel-fusion surface alignment
  io.py                     configuration and vocabulary I/O

evaluation/
  finetune_marianmt.py      MarianMT fine-tuning (Sec. 4.3)
  translate_eval.py         BLEU and chrF++ scoring (Sec. 5.1)

scripts/
  build_flores.py           extract or fetch FLORES-200
  build_eval_sets.py        build the OPUS evaluation sets
  make_tables.py            regenerate result tables from run outputs
  submit_marianmt.sh        Slurm wrapper (1 GPU, 6 CPU, 32 GB, 24 h)
  submit_translate_eval.sh  Slurm wrapper for translation scoring

data/
  raw/                      HornMT corpus; unannotated word lists
  annotations/              morpheme annotations, per language
  evaluation/               OPUS evaluation sets; FLORES-200 archive
  vocabulary/               BPE and WordPiece tokenizers
```

Not tracked: `models/` and `evaluation/results/`, both regenerated by the
scripts above.

---

## Running the experiments

```bash
pip install -r requirements.txt

# Vocabulary construction and tokenizer training (Sec. 3.2, 3.3)
python train.py \
    --amharic-corpus <NLLB.am> --tigrinya-corpus <NLLB.ti> \
    -s 224000 -r 0.7142857142857143

# Build the evaluation sets (Sec. 5.1)
python scripts/build_flores.py
python scripts/build_eval_sets.py

# Intrinsic evaluation (Sec. 5.2): boundary precision, MorphScore,
# Rényi entropy at alpha=2
python evaluate.py --alpha 2.0

# Downstream translation (Sec. 4.3, 5.1) -- requires a GPU
python evaluation/finetune_marianmt.py --strategy movoc_tok --language amharic
python evaluation/translate_eval.py --model <checkpoint> --direction en-am \
    --source data/evaluation/amharic/test.en \
    --reference data/evaluation/amharic/test.am

# Regenerate result tables from run outputs
python scripts/make_tables.py
```

---

## Artifact availability

Stated factually, so users know what this repository does and does not
contain.

**Provided:** morpheme annotations for all four languages; the
preprocessing, vocabulary-construction, MoVoC-Tok and metric
implementations; the OPUS evaluation sets for Amharic, Tigrinya and Tigre;
the FLORES-200 archive; and the fine-tuning and scoring code.

**Not preserved:** the trained model checkpoints, run logs, and the
scoring pipeline used to produce the paper's Table 3. No Ge'ez parallel
evaluation set is present; the paper states (Sec. 4.2) that Ge'ez "was
evaluated only intrinsically" due to the absence of parallel data.

Because the original scoring pipeline is not preserved, results generated
from this repository cannot be verified as numerically identical to the
published values.
[`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) records the artifact
status in detail.

---

## Limitations

As stated in the paper (Sec. 9.1):

> The proposed morphology-aware tokenization approach, while improving
> intrinsic metrics such as MorphoScore and Boundary Precision, does not
> yield significant gains in automatic translation quality. The curated
> morpheme-annotated datasets and vocabulary are limited to a small set of
> Ge'ez script languages, which may affect the generalizability of the
> method. Furthermore, the increased complexity of the hybrid tokenization
> approach may not translate to proportional performance improvements in
> downstream NLP tasks.

---

## Citation

```bibtex
@article{teklehaymanot2025movoc,
  title   = {MoVoC: Morphology-Aware Subword Construction for
             Ge'ez Script Languages},
  author  = {Teklehaymanot, Hailay and Fazlija, Dren and Nejdl, Wolfgang},
  journal = {arXiv preprint arXiv:2509.08812},
  year    = {2025}
}
```

## References

- Arnett & Bergen (2025). MorphScore.
- Costa-Jussà et al. (2022). No Language Left Behind.
- Goyal et al. (2022). FLORES-200.
- Junczys-Dowmunt et al. (2018). Marian.
- Kudo & Richardson (2018). SentencePiece.
- Nouri & Yangarber (2016). Morpheme boundary precision.
- Papineni et al. (2002). BLEU.
- Popović (2017). chrF++.
- Rényi (1961). Rényi entropy.
- Sennrich et al. (2016). Byte-Pair Encoding.
- Tiedemann (2012). OPUS.
