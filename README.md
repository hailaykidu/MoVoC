# MoVoC: Morphology-Aware Subword Vocabulary Construction

Official repository for *"MoVoC: Morphology-Aware Subword Construction for
Ge'ez Script Languages"* (arXiv:[2509.08812](https://arxiv.org/abs/2509.08812),
Teklehaymanot, Fazlija, Nejdl).

MoVoC builds a hybrid morpheme + BPE subword vocabulary for four Ge'ez-script
languages — Amharic, Tigrinya, Tigre, and Ge'ez — and evaluates it against
plain BPE both intrinsically (MorphScore, Boundary Precision) and
extrinsically (downstream machine translation). See Evaluation below.

## Repository layout

```
movoc/                      segmentation and evaluation code
  __init__.py
  segmenter.py              rule-based prefix/suffix segmenter
  metrics.py                MorphScore / Boundary Precision
data/
  morphemes/                morpheme annotation sets (see below)
    amharic_morphemes.json    153,759 entries
    tigrinya_morphemes.json     7,531 entries
    Tigriyna_Morphem.json         206 entries  (gold standard, held out)
    tigre_morphems.json         8,117 entries  (gold standard)
    Geez_Morphem.json             193 entries  (gold standard)
  raw/
    hornmt/                   HornMT parallel corpus, 2,030 aligned sentences
      amh.txt                   Amharic  (39,102 tokens)
      tir.txt                   Tigrinya (43,511 tokens)
      eng.txt                   English
    amh_cleaned_words.txt     cleaned Amharic word list   (13,563 words)
    amh_hornmt_words.txt      Amharic words from HornMT   (13,992 words)
    tir_hornmt_words.txt      Tigrinya words from HornMT  (13,327 words)
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

Tigrinya has two sets, kept deliberately apart: `tigrinya_morphemes.json`
(7,531 entries, 7,125 distinct morphemes) is the curated set that feeds
vocabulary construction, while `Tigriyna_Morphem.json` (206 entries) is the
gold standard **held out** for evaluation. The two are largely independent —
only 23 of the gold set's 192 words appear in the curated set — so intrinsic
scores are not measured against the vocabulary's own training material.

### Annotated resource totals

The table below reports the **combined annotated resource** per language:
every morpheme in the curated and gold sets together. This is a description
of the annotation effort, and is deliberately *not* the same thing as the
vocabulary input — for Tigrinya the gold set is held out of vocabulary
construction, so only 7,125 of its 7,272 morphemes reach `V_MoVoC`.

| Language | Entries | Distinct morphemes |
|---|---|---|
| Amharic  | 153,759 | 50,978 |
| Tigrinya |   7,737 |  7,272 |
| Ge'ez    |     193 |     69 |
| Tigre    |   8,117 |  3,950 |
| **Total distinct** | | **60,128** |

Tigrinya's figure combines both sets: 7,125 curated plus 231 gold, less 84
shared between them.

Both Amharic and Tigrinya fall short of the paper's per-language morpheme
budget of 80,000 (Table 5) — Amharic reaches 63.7%, Tigrinya 9.1%. The
morpheme half of the vocabulary is therefore limited by how much annotated
data exists, not by the budget, which is why `V_MoVoC` comes out well below
its nominal size. See Vocabulary construction below.

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

`amh_hornmt_words.txt` and `tir_hornmt_words.txt` (13,992 Amharic and 13,327
Tigrinya unique Ge'ez-script forms) are those same tokens deduplicated to word
type. They come from the word column of `amharic_segmentation_output.txt` and
`Tigr_segmentation_output.txt`; those files' analysis columns are discarded,
since the HornMorpho pass they record returned no usable segmentation — every
line either echoed the surface form or reported `NO_SEGMENTATION`. Only the
input words are retained.

`amh_cleaned_words.txt` (13,563 words) is a separate, earlier Amharic list;
it overlaps the HornMT-derived one substantially but is not identical.

`data/morphemes/amharic_morphemes.json` is the largest resource here by an
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
| 4. `extract_morphemes(P, s_morpheme)` | Amharic 50,978 · Tigrinya 7,125 — both below the 80,000 budget, so Top-k returns every available morpheme |
| 5. Merge | `V_MoVoC` = **114,553** (122,103 before collapsing 7,550 shared tokens) |
| 6. `Train_MoVoC_Model` | constrained-merge BPE, 32,000 merges per language — see below |

`V_MoVoC` lands at 114,553 rather than the nominal 224,000 because the
morpheme half is bounded by the annotated data available (see Annotated
resource totals above), not by `s_morpheme`.

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
sets in `data/morphemes/`, designed specifically to assess segmentation
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

## Usage

```python
from movoc.segmenter import MorphemeSegmenter

seg = MorphemeSegmenter("tigrinya")
seg.segment_word("ኣይመፀን")      # -> Segmentation(prefix='ኣይ-', root='መፀ', suffix='-ን')
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
- Tiedemann, J. (2012). *Parallel Data, Tools and Interfaces in OPUS.*
  In Proceedings of the 8th International Conference on Language Resources
  and Evaluation (LREC 2012). — Source of the extrinsic evaluation sentence
  pairs.
- HornMorpho — morphological analyzer for Horn of Africa languages,
  <https://github.com/hltdi/HornMorpho>.
