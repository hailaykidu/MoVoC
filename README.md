# MoVoC: Morphology-Aware Subword Vocabulary Construction

Official repository for *"MoVoC: Morphology-Aware Subword Construction for
Ge'ez Script Languages"* (arXiv:[2509.08812](https://arxiv.org/abs/2509.08812),
Teklehaymanot, Fazlija, Nejdl).

MoVoC builds a hybrid morpheme + BPE subword vocabulary for four Ge'ez-script
languages — Amharic, Tigrinya, Tigre, and Ge'ez — and evaluates it against
plain BPE both intrinsically (MorphScore, Boundary Precision) and
extrinsically (downstream machine translation). See Evaluation below.

## Pipeline

```
Raw corpus  ->  Text preprocessing  ->  Morphological analysis
    ->  Morpheme annotation  ->  Hybrid vocabulary construction (MoVoC)
    ->  Tokenizer training  ->  Intrinsic evaluation  ->  Extrinsic evaluation
```

## Repository layout

```
train.py                    Algorithm 1 end to end (Steps 2-7)
evaluate.py                 intrinsic evaluation
segment.py                  segment text with a trained MoVoC-Tok model
requirements.txt

configs/                    bpe_config.json, movoc_config.json

evaluation/
  finetune_marianmt.py      MarianMT fine-tuning (Sec 4.3)
  translate_eval.py         BLEU and chrF++ scoring (Sec 5.1)
  results/                  evaluation output
scripts/
  submit_marianmt.sh        Slurm wrapper (1 GPU, 6 CPU, 32 GB, 24 h)
  submit_translate_eval.sh  Slurm wrapper for MT scoring

movoc/
  preprocessing.py          corpus preparation
  hornmorph.py              interface to HornMorpho
  annotation.py             loading/validating the three annotation kinds
  vocabulary.py             Algorithm 1: sizes, extract_morphemes, merge
  tokenizer.py              Train_BPE and MoVoC-Tok constrained merges
  metrics.py                Boundary Precision, MorphScore, Renyi entropy
  utils.py                  fidel-fusion surface alignment
  io.py                     config and vocabulary I/O

data/
  raw/                      HornMT parallel corpus; unannotated word lists
  annotations/
    amharic/postedited_morphemes.json    HornMorpho + human post-editing
    tigrinya/postedited_morphemes.json   HornMorpho + human post-editing
    tigrinya/gold_morphemes.json         manual gold standard (held out)
    geez/manual_morphemes.json           fully manual annotation
    tigre/manual_morphemes.json          fully manual annotation
  vocabulary/               trained BPE tokenizers, vocab_movoc.txt

models/                     MoVoC-Tok merge tables
evaluation/results/         evaluation output
```

## Morpheme data provenance

Morpheme annotations reach their final form by one of two routes, depending on
whether a morphological analyzer covers the language:

| Language | Initial analysis | Human post-editing | Final annotation | Entries |
|---|---|---|---|---|
| Amharic  | HornMorpho | yes | Curated | 153,759 |
| Tigrinya | HornMorpho | yes | Curated + gold standard | 7,531 curated + 206 gold |
| Ge'ez    | — | manual | Gold standard | 193 |
| Tigre    | — | manual | Gold standard | 8,117 |

For **Amharic and Tigrinya**, HornMorpho provides the initial morphological
analysis, which is then manually post-edited for consistency. Post-editing is
essential rather than cosmetic, particularly for Tigrinya.

Tigrinya has two sets, kept deliberately apart: `tigrinya/postedited_morphemes.json`
(7,531 entries, 7,125 distinct morphemes) is the curated set that feeds
vocabulary construction, while `tigrinya/gold_morphemes.json` (206 entries) is the
gold standard **held out** for evaluation. The two are largely independent —
only 23 of the gold set's 192 words appear in the curated set — so intrinsic
scores are not measured against the vocabulary's own training material.

### Annotated resource totals

The table below reports the **combined annotated resource** per language:
every morpheme in the curated and gold sets together. This is a description
of the annotation effort, and is deliberately *not* the same thing as the
vocabulary input — for Tigrinya the gold set is held out of vocabulary
construction, so 7,125 of its 7,272 morphemes reach `V_MoVoC`.

| Language | Entries | Distinct morphemes |
|---|---|---|
| Amharic  | 153,759 | 50,978 |
| Tigrinya |   7,737 |  7,272 |
| Ge'ez    |     193 |     69 |
| Tigre    |   8,117 |  3,950 |
| **Total distinct** | | **60,128** |

Tigrinya's figure combines both sets: 7,125 curated plus 231 gold, less 84
shared between them.

`extract_morphemes` selects the top-`k` morphemes by frequency, bounded by
`s_morpheme`. Amharic contributes 50,978 morphemes and Tigrinya 7,125 to the
vocabulary.

For **Ge'ez and Tigre**, no morphological analyzer offers usable coverage, so
both sets are human-annotated end to end under linguistic supervision.

Annotation depth differs by language. Amharic and Tigre carry the full
five-way `prefix / root / suffix / infix / clitic` scheme; Ge'ez carries four
(`prefix / root / infix / suffix`); Tigrinya carries three
(`prefix / root / suffix`).

### Raw word lists

`data/raw/` holds unannotated word lists — **corpus material only**, carrying
no morpheme annotation and forming no part of the annotated sets above.

`raw/hornmt/` is the **HornMT parallel corpus** at sentence level: 2,030
English–Amharic–Tigrinya aligned sentences, the origin of all Amharic and
Tigrinya material submitted for morphological analysis. Whitespace-tokenizing
`amh.txt` and `tir.txt` yields exactly 39,102 and 43,511 tokens.

`geez_words.txt` holds 341 Ge'ez surface forms — verb paradigms (`ሐዘን`,
`አብርሃ`, `ሰፍሐ`, `በልዐ` conjugations) and triliteral roots — supplied as a word
list with no prefix/root/suffix annotation. Deduplicated, and disjoint from
`geez/manual_morphemes.json`: none of the 341 already appears there. They are **not**
part of the Ge'ez gold standard and do not feed morpheme extraction; they are
staged here as candidates for future annotation.

`data/annotations/amharic/postedited_morphemes.json` is the largest resource here by an
order of magnitude: 153,759 entries covering 150,918 unique words, with a
consistent key set throughout. Field coverage is root 99.9%, prefix 60.5%,
suffix 54.8%, infix 14.3%, clitic 13.7%; 80.5% of entries carry at least one
affix, and the remaining 19.5% are root-only surface forms.

## Vocabulary construction (Algorithm 1)

Parameters follow the paper's Table 5: 32,000 BPE + 80,000 morpheme tokens
per language, i.e. `s = 224,000` and `r = 5/7`.

| Step | Result |
|---|---|
| 2. Vocabulary sizes | `s_lang` 112,000 · `s_BPE` 32,000 · `s_morpheme` 80,000 |
| 3. `Train_BPE(P, s_BPE)` | 32,000 tokens each, over the full NLLB corpora (Amharic 16,137,053 lines; Tigrinya 1,398,173) |
| 4. `extract_morphemes(P, s_morpheme)` | Amharic 50,978 · Tigrinya 7,125 |
| 5. Merge | `V_MoVoC` = **114,553** (122,103 before collapsing 7,550 shared tokens) |
| 6. `Train_MoVoC_Model` | constrained-merge BPE, 32,000 merges per language — see below |

### Step 6: MoVoC-Tok constrained merges

Step 6 is not the Step 5 vocabulary handed to a stock BPE tokenizer. Per the
paper's Sec 3.3, the merge process itself is constrained:

```
max_V  sum_i log P(BPE(w_i; V, M_i))    s.t. no merge unit crosses M_i
```

Each word carries the morpheme boundary offsets implied by its annotation,
and a merge candidate is counted only when both symbols fall inside the same
morpheme. Pairs straddling a boundary are never counted and never enter the
merge table, so the learned merges cannot fuse across a morpheme boundary.

Words whose annotated morphemes do not concatenate back to the surface form
(templatic morphology, fidel fusion at a boundary) contribute no constraint
rather than a guessed one.

## Data

Amharic and Tigrinya data come from the **No Language Left Behind (NLLB)**
project (Costa-Jussà et al., 2022), used in two places:

1. **Vocabulary construction** — BPE training for the Amharic and Tigrinya
   vocabularies.
2. **Downstream MT** — the English–Tigrinya and English–Amharic parallel
   corpora mined and released by Meta AI as part of NLLB, used to fine-tune
   MarianMT for the translation evaluation.

## Evaluation

MoVoC is evaluated two ways: **intrinsically**, on segmentation quality, and
**extrinsically**, on downstream machine translation.

### Intrinsic

For all four languages, intrinsic evaluation uses the annotated morpheme test
sets in `data/annotations/`, designed specifically to assess segmentation
quality, and scored with MorphScore and Boundary Precision (`movoc/metrics.py`).

Ge'ez is evaluated **intrinsically only**, as no parallel data is available
for it.

### Extrinsic

Extrinsic evaluation runs on an unseen subset of the first 100 sentence pairs
from the **OPUS** parallel corpus (Tiedemann, 2012), for each target language.
Each language pair is capped at 100 sentence pairs to keep the evaluation
balanced across languages:

| Language | Sentence pairs | Composition |
|---|---|---|
| Amharic  | 100 | 100 of 213 available from OPUS |
| Tigrinya | 100 | 74 from OPUS + 26 human-validated |
| Tigre    | 100 | 45 from OPUS + 55 human-validated |
| Ge'ez    | 100 | 100 newly created and validated (intrinsic evaluation only) |

Where OPUS coverage falls short — as it does for Tigrinya and Tigre — the
remainder is made up with human-validated pairs, so every language is scored
on an equally sized set.

#### MarianMT fine-tuning (Sec 4.3)

Downstream translation quality is measured by fine-tuning **MarianMT**
(Junczys-Dowmunt et al., 2018) on the English–Amharic and English–Tigrinya
parallel corpora from NLLB, then comparing the MoVoC vocabulary against the
BPE and WordPiece baselines.

| Setting | Value |
|---|---|
| Epochs | 3 |
| Batch size | 8 |
| Max sequence length | 128 tokens |
| Learning rate | 1.44e-07, decayed through training |
| transformers | 4.51.3 |
| Hardware | 1 GPU, 6 CPU cores, 32 GB RAM (Slurm) |
| Max runtime | 24 hours |
| Environment | Conda-managed |

Reported run: gradient norms 1.14 → 1.06, training loss 0.443 → 0.438,
approximately 12 hours at ~96.7 samples/second.

Model architecture (verified field-for-field against the reported run's
`config.json`):

| Field | Value |
|---|---|
| Encoder / decoder layers | 6 / 6 |
| Attention heads | 8 |
| Hidden size (`d_model`) | 512 |
| Feedforward dimension | 2048 |
| Activation | Swish |
| Embeddings | shared encoder–decoder |
| Positional encoding | static |
| Vocabulary size | 63,050 |

Training covers **English–Amharic** and **English–Tigrinya** only. **Tigre is
excluded from training entirely** and appears at evaluation to measure
zero-shot translation between Ge'ez-script languages.

Translation quality is scored with **BLEU** and **chrF++** (sacrebleu),
measuring n-gram and character-level overlap. Because these can overlook
morphological improvements, they are complemented by the intrinsic metrics
above.

**COMET is deliberately not used.** It depends on pretrained models and
reference corpora available only for high-resource languages; no reliable
COMET-compatible model exists for Tigrinya, Tigre, or Ge'ez, which would make
its use inappropriate or misleading.

Directions: `en-am`, `am-en`, `en-ti`, `ti-en` from training, plus `en-tig`
and `tig-en` **zero-shot**, Tigre having been excluded from training.

`evaluation/translate_eval.py` performs this scoring.
`evaluation/finetune_marianmt.py` builds this configuration;
`scripts/submit_marianmt.sh` is the Slurm wrapper requesting exactly those
resources. Both require a GPU and the NLLB corpora — **this fine-tuning has
not been run from this repository**, and no downstream results are reported
here yet.

## Usage

```bash
pip install -r requirements.txt

# Algorithm 1, Steps 2-7: vocabulary sizes, BPE, morphemes, merge,
# and MoVoC-Tok constrained-merge training
python train.py \
    --amharic-corpus  NLLB.am-en.am \
    --tigrinya-corpus NLLB.en-ti.ti \
    -s 224000 -r 0.7142857142857143

# Intrinsic evaluation
python evaluate.py

# Segment text with the trained tokenizer
python segment.py tigrinya "ኣይመፀን"
```

## Citation

```bibtex
@article{teklehaymanot2025movoc,
  title  = {MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages},
  author = {Teklehaymanot, Hailay and Fazlija, Bes and Nejdl, Wolfgang},
  journal = {arXiv preprint arXiv:2509.08812},
  year   = {2025}
}
```

## References

- Costa-Jussà, M. R., Cross, J., Çelebi, O., Elbayad, M., Heafield, K.,
  Heffernan, K., et al. (2022). *No Language Left Behind: Scaling
  Human-Centered Machine Translation.* arXiv:2207.04672.
- Junczys-Dowmunt, M., Grundkiewicz, R., Dwojak, T., Hoang, H., Heafield, K.,
  Neckermann, T., et al. (2018). *Marian: Fast Neural Machine Translation in
  C++.* In Proceedings of ACL 2018, System Demonstrations. — MarianMT, the
  model fine-tuned for extrinsic evaluation.
- Tiedemann, J. (2012). *Parallel Data, Tools and Interfaces in OPUS.*
  In Proceedings of the 8th International Conference on Language Resources
  and Evaluation (LREC 2012). — Source of the extrinsic evaluation sentence
  pairs.
- HornMorpho — morphological analyzer for Horn of Africa languages,
  <https://github.com/hltdi/HornMorpho>.
