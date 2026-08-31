# MoVoC-Tok: Morpheme-Aware BPE — Training Report

Two independent tokenizers trained by BPE learning under morpheme-boundary
constraints. No vocabulary slots were manually allocated; the composition
emerged from constrained merge learning.

---

## Method and implementation — kept separate

**Published MoVoC-Tok method.** BPE vocabulary learning in which merge
operations are restricted by morpheme boundaries, optimising

```
max_V  Σ_i log P(BPE(w_i; V, M_i))
subject to: no subword s_j crosses a morpheme boundary in M_i
```

**Implementation procedures (this work, not attributed to the paper).** The
paper specifies the constraint but not how to obtain surface boundaries from a
morphological analyser whose output is in citation form. The following are
this implementation's decisions:

1. **Surface boundary projection.** HornMorpho returns citation forms, so
   morphemes generally do not concatenate to the surface word — only 18.5% of
   Amharic records do. Boundaries are projected onto the surface by aligning
   morphemes left to right, matching each against the remaining suffix, and
   falling back to the longest shared contiguous block
   (`difflib.SequenceMatcher`) when the citation form differs.
2. **Morpheme ordering by surface position.** The datasets store morphemes by
   grammatical slot, so a proclitic (e.g. የ) appears in the `clitic` field
   after the root. Clitics are repositioned by where they attach, which
   corrects የግብፅ from `የግብ|ፅ` to `የ|ግብፅ` and nearly doubled usable
   constraints (2,239 → 4,439 for Amharic).
3. **Unalignable words are unconstrained.** When projection fails the word
   contributes no constraint rather than a guessed boundary. No boundary is
   invented.
4. **Encoding-time constraint enforcement.** Training-time restriction alone
   is *insufficient*. A merge is learned if legal anywhere in the corpus, so a
   pair with no boundary between it in one word may straddle a boundary in
   another. Measured directly: with training-time constraints only, boundary
   compliance was **69.05%** (ማላሽ segmented as `▁ማ ላሽ`, with `ላሽ` spanning
   ማላ|ሽ). Re-applying the per-word constraint during encoding raises this to
   **100%**.

---

## Training

| | Amharic | Tigrinya |
|---|---|---|
| Corpus | `NLLB.am-en.am` | `NLLB.en-ti.ti` |
| Corpus lines read | 400,000 | 400,000 |
| Word types (min freq 2) | 158,504 | 169,373 |
| Alphabet size | 1,041 | 1,156 |
| **Vocabulary size** | **32,000** | **32,000** |
| **BPE merges** | **30,955** | **30,840** |
| Training time | 12.6 min | 13.9 min |

**Random seed:** none required. Constrained BPE is fully deterministic — at
each step the highest-frequency legal pair is selected, ties broken on the pair
itself. No sampling or shuffling occurs, so the same inputs always produce the
same vocabulary.

**Software:** Python 3.13.11; HornMorpho 5.3.6 (segmentation, upstream);
no external tokenizer library — the constrained BPE learner is implemented
directly in `scripts/train_movoc_tok_bpe.py`, since SentencePiece exposes no
merge-level constraint hook.

---

## Boundary constraints

| | Amharic | Tigrinya |
|---|---:|---:|
| Analysed word records | 10,293 | 6,692 |
| Single-morpheme (no boundary to project) | 2,172 | 1,828 |
| **Words with projected boundaries** | **4,439** | **2,291** |
| Projection failed (left unconstrained) | 3,655 | 2,534 |
| Projection success rate (multi-morpheme words) | 54.8% | 47.5% |
| Corpus word types carrying a constraint | 3,372 | 1,470 |
| Corpus constraint coverage | 2.13% | 0.87% |
| **Rejected boundary-crossing merges** | **335,638** | **104,964** |
| **Accepted merges** | **30,955** | **30,840** |

---

## Verification

| Check | Amharic | Tigrinya | Required |
|---|---|---|---|
| Vocabulary size | 32,000 ✅ | 32,000 ✅ | 32,000 |
| **Boundary violation rate** | **0.00%** ✅ | **0.00%** ✅ | **0%** |
| Constrained words respected | 4,439/4,439 | 2,291/2,291 | all |
| Decode round-trip accuracy | 100.00% ✅ | 100.00% ✅ | lossless |
| UNK rate | 0.2281% | 0.1309% | — |
| Fertility (tokens/word) | 1.79 | 1.65 | — |

UNK rate and fertility measured over the full HornMT corpora (39,102 Amharic
and 43,511 Tigrinya word tokens). Round-trip verified on every word.

---

## Segmentation examples

### Amharic

```
Original:       የእስራኤል          ማላሽ            ክርስቶስን
MoVoC boundary: የ|እስራኤል         ማላ|ሽ           ክርስቶስ|ን
MoVoC-Tok:      ▁የ እስራኤል        ▁ማላ ሽ          ▁ክርስቶስ ን

Original:       በጋዛ             የኢየሱስ
MoVoC boundary: በ|ጋዛ            የ|ኢየሱስ
MoVoC-Tok:      ▁በ ጋ ዛ          ▁የ ኢየሱስ
```

### Tigrinya

```
Original:       ሞርታርን           ውሽጣ            ፈንዩ
MoVoC boundary: ሞርታር|ን          ውሽ|ጣ           ፈን|ዩ
MoVoC-Tok:      ▁ሞ ርታ ር ን       ▁ውሽ ጣ          ▁ፈን ዩ

Original:       ብህላወ            ጋዛ
MoVoC boundary: ብ|ህላወ           ጋ|ዛ
MoVoC-Tok:      ▁ብ ህ ላወ         ▁ጋ ዛ
```

In every case the tokenizer's output boundaries are a superset of the morpheme
boundaries: it may split *within* a morpheme (▁ሞ ርታ ር), but never *across*
one.

---

## Artifacts

```
tokenizers/amharic_movoc_tok_32k/    tokenizer.model  tokenizer.vocab
                                     config.json      training_config.json
tokenizers/tigrinya_movoc_tok_32k/   tokenizer.model  tokenizer.vocab
                                     config.json      training_config.json
```

The two vocabularies are independent: each was trained on its own language
corpus with its own morpheme constraints, and neither was merged with the
other.

---

## Limitation

Constraint coverage over the corpus is low — 2.13% of Amharic and 0.87% of
Tigrinya word types carry a boundary constraint. This follows from the
morphological analysis covering ~14,000 words per language while the training
corpus holds ~160,000 word types, compounded by projection failures on 45–53%
of multi-morpheme words.

The constraint is therefore satisfied absolutely (0% violations on every word
where boundaries are known) but shapes a minority of merge decisions. Wider
morphological coverage — analysing more of the corpus with HornMorpho, or
improving citation-to-surface alignment — would strengthen the effect of the
constraint on the learned vocabulary. This is a property of the available
morphological resources, not of the algorithm.
