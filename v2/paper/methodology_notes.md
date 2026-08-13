# Methodology — notes

Source: `docs/methodology.md`, `movoc/` implementation.

## 1. Pre-tokenization and morphological analysis

Words are analysed into `(prefix, root, infix, suffix, clitic)` slots by
supervised morphological analysis (HornMorpho), with human post-editing for
Amharic and Tigrinya and manual annotation for Tigre and Ge'ez.

Implementation: `movoc/hornmorph.py`, `movoc/annotation.py`.

## 2. MoVoC vocabulary construction

The budget is split evenly between morpheme types and BPE merges:

```
s_lang     = s / 2
s_morpheme = s_lang × r
s_BPE      = s_lang × (1 − r)
```

`s` is the total vocabulary size and `r` the morpheme ratio. Morphemes enter the
vocabulary as first-class units rather than being discovered statistically, so
frequent affixes and roots survive as whole tokens.

```bash
python train.py --lang amharic -s 224000 -r 0.7142857142857143
```

Implementation: `movoc/vocabulary.py`.

## 3. MoVoC-Tok

Constrained-merge BPE: **a merge may never cross a morpheme boundary.**
Segmentation therefore stays inside morphemes and a token cannot straddle a
prefix–root or root–suffix join.

```bash
python segment.py --lang amharic --text "ዝወደቐ"
```

Implementation: `movoc/tokenizer.py`.

## 4. Datasets

Morpheme annotations for four Ge'ez-script languages (`data/README.md`):

| Language | ISO 639-3 | Records | Multi-morpheme | Source |
|---|---|---:|---:|---|
| Amharic | amh | 153,759 | 123,761 | HornMorpho + human post-editing |
| Tigrinya | tir | 7,737 | 2,870 | gold (206) + post-edited (7,531) |
| Tigre | tig | 8,117 | 2,457 | manual annotation |
| Ge'ez | gez | 193 | 173 | manual annotation |

**Total: 169,806 annotated records, 129,261 carrying at least one morpheme
boundary.**

Format — JSON array, one object per word, `-` marking an empty slot:

```json
{"no": 3, "word": "ዝወደቐ", "prefix": "ዝ-", "root": "ወደቐ", "suffix": "-"}
```

Ge'ez and Tigre annotations are reserved for evaluation; the paper (Sec. 4.1)
states no separate training morpheme data was obtained for them.

Parallel evaluation sets: `data/evaluation/{lang}/` plus FLORES-200.

## 5. Intrinsic evaluation

Three metrics over the annotated morpheme sets (`movoc/metrics.py`, run by
`evaluate.py`):

- **Morpheme boundary precision** — predicted boundaries against gold, exact
  character-offset match, micro-averaged.
- **MorphScore** — recall of gold boundaries; unsegmented words excluded rather
  than scored zero.
- **Rényi entropy** (α = 2), normalized as `H_α / log(support)`; lower is
  sharper.

Gold boundaries are derived as cumulative morpheme lengths
(`boundaries_from_triple`).

```bash
python evaluate.py --alpha 2.0
```

## 6. Extrinsic evaluation

English→X MarianMT (6+6 layers, 8 heads, d_model 512, FFN 2048, tied
embeddings), one multilingual model per tokenizer, three seeds (42/43/44).
Scored with sacreBLEU (BLEU, chrF++) on FLORES-200 devtest.

```bash
bash scripts/submit_marianmt.sh
```

Implementation: `evaluation/finetune_marianmt.py`, `evaluation/translate_eval.py`.
