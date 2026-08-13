# Limitations — notes

Limited to what the final approved V2 result set establishes.

## 1. Annotation coverage varies by two orders of magnitude

| Language | Records | Multi-morpheme |
|---|---:|---:|
| Amharic | 153,759 | 123,761 |
| Tigrinya | 7,737 | 2,870 |
| Tigre | 8,117 | 2,457 |
| Ge'ez | 193 | 173 |

Intrinsic results for Ge'ez rest on a small evaluation set (173 words), so its
values carry wider uncertainty than Amharic's.

## 2. Cross-lingual application for Tigre and Ge'ez

No in-language MoVoC-Tok exists for Tigre or Ge'ez: the paper (Sec. 4.1) states
no separate training morpheme data was obtained for them, and their annotations
are reserved for evaluation. Their Table 4 rows apply the 32k Tigrinya
MoVoC-Tok, and are marked accordingly.

## 3. Translation is trained on two directions only

MarianMT models are trained on English→Amharic and English→Tigrinya. Tigre and
Ge'ez appear only as zero-shot evaluation, so Table 3's supervised comparison
covers two of the four languages.

## 4. Translation scale

BLEU values on FLORES-200 devtest are low in absolute terms for all three
tokenizers, reflecting the training scale and the difficulty of English→X
translation into morphologically rich, low-resource targets. Comparisons are
between tokenizers under identical conditions rather than against
state-of-the-art translation systems.

## 5. Boundary metrics require surface-aligned annotations

Boundary precision and MorphScore locate gold boundaries by character offset, so
they apply to annotations whose morphemes concatenate to the surface form. This
constrains the evaluable subset in the more fusional languages.
