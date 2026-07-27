# MoVoC: Morphology-Aware Subword Vocabulary Construction

Official repository for *"MoVoC: Morphology-Aware Subword Construction for
Ge'ez Script Languages"* (arXiv:[2509.08812](https://arxiv.org/abs/2509.08812),
Teklehaymanot, Fazlija, Nejdl).

MoVoC builds a hybrid morpheme + BPE subword vocabulary for four Ge'ez-script
languages — Amharic, Tigrinya, Tigre, and Ge'ez — and evaluates it against
plain BPE using MorphScore and Boundary Precision.

## Repository layout

```
movoc/                      segmentation and evaluation code
  __init__.py
  segmenter.py              rule-based prefix/suffix segmenter
  metrics.py                MorphScore / Boundary Precision
data/
  morphemes/                morpheme annotation sets (see below)
    amharic_morphemes.json    153,759 entries
    Tigriyna_Morphem.json         206 entries  (gold standard)
    tigre_morphems.json         8,117 entries  (gold standard)
    Geez_Morphem.json             193 entries  (gold standard)
  raw/
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
| Tigrinya | HornMorpho | yes | Curated + gold standard | 206 (gold) |
| Ge'ez    | — | manual | Gold standard | 193 |
| Tigre    | — | manual | Gold standard | 8,117 |

For **Amharic and Tigrinya**, HornMorpho provides the initial morphological
analysis, which is then manually post-edited for consistency. Post-editing is
essential rather than cosmetic, particularly for Tigrinya.

For **Ge'ez and Tigre**, no morphological analyzer offers usable coverage, so
both sets are human-annotated end to end under linguistic supervision.

Annotation depth differs by language. Amharic and Tigre carry the full
five-way `prefix / root / suffix / infix / clitic` scheme; Ge'ez carries four
(`prefix / root / infix / suffix`); Tigrinya carries three
(`prefix / root / suffix`).

### Raw word lists

`data/raw/` holds unannotated word lists — **corpus material only**, carrying
no morpheme annotation and forming no part of the annotated sets above.

`amh_hornmt_words.txt` and `tir_hornmt_words.txt` (13,992 Amharic and 13,327
Tigrinya unique Ge'ez-script forms) are the words submitted for morphological
analysis, taken from the HornMT parallel corpus. Both derive from the word
column of `amharic_segmentation_output.txt` and `Tigr_segmentation_output.txt`
respectively; those files' analysis columns are discarded, since the
HornMorpho pass they record returned no usable segmentation — every line
either echoed the surface form or reported `NO_SEGMENTATION`. Only the input
words are retained.

`amh_cleaned_words.txt` (13,563 words) is a separate, earlier Amharic list;
it overlaps the HornMT-derived one substantially but is not identical.

`data/morphemes/amharic_morphemes.json` is the largest resource here by an
order of magnitude: 153,759 entries covering 150,918 unique words, with a
consistent key set throughout. Field coverage is root 99.9%, prefix 60.5%,
suffix 54.8%, infix 14.3%, clitic 13.7%; 80.5% of entries carry at least one
affix, and the remaining 19.5% are root-only surface forms.

## Data

Amharic and Tigrinya data come from the **No Language Left Behind (NLLB)**
project (Costa-Jussà et al., 2022), used in two places:

1. **Vocabulary construction** — BPE training for the Amharic and Tigrinya
   vocabularies.
2. **Downstream MT** — the English–Tigrinya and English–Amharic parallel
   corpora mined and released by Meta AI as part of NLLB, used to fine-tune
   MarianMT for the translation evaluation.

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
- HornMorpho — morphological analyzer for Horn of Africa languages,
  <https://github.com/hltdi/HornMorpho>.
