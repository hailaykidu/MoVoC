# Instructions for the coding agent: corrected version of MoVoC (Findings of EMNLP 2025)

You are preparing a **corrected version (ACL Anthology revision)** of:

> Hailay Kidu Teklehaymanot, Dren Fazlija, Wolfgang Nejdl. 2025. *MoVoC: Morphology-Aware
> Subword Construction for Ge'ez Script Languages.* Findings of EMNLP 2025, pp. 13131–13144.
> https://aclanthology.org/2025.findings-emnlp.706/ — DOI 10.18653/v1/2025.findings-emnlp.706

The EMNLP 2025 programme chairs advised publishing a corrected version. **Every result must
come from the reconstructed results in the public repository
<https://github.com/hailaykidu/MoVoC>**, because the artifacts behind the published figures
were never recovered and those figures cannot be reproduced.

Deliverable: a compiled PDF in ACL *final* format, its LaTeX source, and a neutral change
summary for the Anthology. A complete reference build accompanies these instructions
(`main.tex`, `main.pdf`, `tables/`, `scripts/`). Your job is to reproduce it from scratch,
verify it, and, if the original camera-ready source is available, carry the corrections into
that source (see §4).

---

## 1. Hard rules (read before doing anything)

1. **Only repository results.** Every result number, segmentation or example must come from a
   file in the MoVoC repository, or be computed from one by a script. Never type a result
   number by hand.
2. **Use only these result sources.**

   | Result | Source in the repository |
   |---|---|
   | Table 2 (MorphScore) | `v2/paper/manuscript/tables/table2_final.tex` (= `v2/table2/table2_final.csv`) |
   | Table 3 (MT, FLORES-200) | `v2/archive/table3_intrinsic_v1_original/table3_final.tex` |
   | Table 4 (precision, Rényi) | `v2/paper/manuscript/tables/table4_final.tex` (= `v2/table4/table4_final.csv`) |
   | Table 7 (MT, OPUS + zero-shot) | `per_run` records in `v2/archive/table3_intrinsic_v1_original/table3_multiseed.json` |
   | Table 1 (segmentations) | output of the released tokenizers in `tokenizers/` |
   | Table 5 (vocabulary) | `configs/movoc_config.json` |
   | Table 6 (annotation examples) | `data/annotations/*/*.json` |
   | Setup facts | `table3_multiseed.json` (`experimental_design`, `metrics`), `tokenizers/*/training_config.json`, `data/README.md`, `data/evaluation/manifest.json`, `data/evaluation/geez/manifest.json` |

3. **Do NOT use the September 2026 Table 3 figures.** The files `v2/table3/*.md` and the
   "Results at a glance" table in `v2/README.md` report MoVoC-Tok winning EN→Amharic
   (0.8987 BLEU). **They must not appear anywhere in the paper**, because:
   - the seed-43 zero-shot values are marked "estimated/interpolated", so they were never measured;
   - MoVoC-Tok seed 44 (BLEU 0.0127) was excluded after the results were seen;
   - BPE EN→Amharic seed 42 is listed as "PENDING", although the table claims 36/36 runs;
   - there are no per-run records for any of these runs in the repository.

   Table 3 uses the August 2026 run set instead. That set has 9 runs, all three seeds, nothing
   excluded, and 54 per-run records.
4. **Tables 2, 3 and 4 are copied verbatim** from the repository by the generator. Do not
   change their structure, rows, columns or values. Do not change the structure of any other
   table beyond what is listed here.
5. **Keep the published table numbering** (Tables 1–6 as published, plus a new Table 7 in the
   appendix). The order of the floats in the source determines the numbering. The MT table
   (Table 3) must come before the precision table (Table 4).
6. **Published figures may appear only as quoted corrections** ("the published version
   reported X"). They must never be placed in a table beside reconstructed values.
7. **Do not commit or push** anything to any repository unless the author asks. Never add
   "Co-Authored-By: Claude" or any other AI attribution to commit messages.
8. **Unchanged sections stay unchanged.** If the original camera-ready source is available,
   keep its Introduction, Background (§2), method description (§3, except the edits listed
   in §4) and bibliography verbatim.

---

## 2. Environment

```bash
# Repository, pinned to the commit the reference build was made from
git clone https://github.com/hailaykidu/MoVoC.git
cd MoVoC && git checkout b115debf6f6cbfab0ef151959ba1d10cc780f3e5 && cd ..

python3 -m pip install -r MoVoC/requirements.txt sacrebleu

# LaTeX: XeLaTeX is required (Ethiopic script). Needs fontspec, booktabs,
# algorithm/algpseudocode, TeX Gyre Termes.
# ACL style files:
git clone --depth 1 https://github.com/acl-org/acl-style-files.git
# Ethiopic font: fonts/NotoSerifEthiopic-{Regular,Bold}.ttf (shipped in the package;
# source: https://github.com/notofonts/ethiopic, SIL Open Font License)
```

---

## 3. Procedure (reference build)

Run every step and stop at the first failure.

**Step 1: Reproduce the intrinsic results.**
```bash
cd MoVoC
python scripts/evaluate_intrinsic.py --datadir evaluation/data \
       --outdir /tmp/intr --tokenizers tokenizers
```
Compare `/tmp/intr/intrinsic_tokenizer_table.md` with `v2/table2/table2_final.csv` and
`v2/table4/table4_final.csv`. All 36 values (12 rows × MorphScore, precision, Rényi) must
match exactly. Expected word counts: Amharic 81,224, Tigrinya 5,224, Tigre 1,974,
Ge'ez 172.

**Step 2: Generate the tables.**
```bash
python paper/scripts/make_correction_tables.py --repo MoVoC --out paper/tables
```
This copies Tables 2–4 verbatim and generates Tables 1, 5, 6 and 7. It writes
`tables/provenance.json`; keep that file with the paper source.

**Step 3: Check the Table 3 aggregates.** Recompute the mean and sample SD (ddof=1) per
(dataset, direction, tokenizer) from `per_run` in `table3_multiseed.json`. All 18 FLORES
values in `table3_final.tex` must match to 4 decimals. Every cell must have seeds 42, 43
and 44 with status `complete`.

**Step 4: Compile.**
```bash
cd paper && latexmk -xelatex -interaction=nonstopmode main.tex
```
The log must contain no `undefined` references, no `Missing character` and no Overfull
boxes. If an Ethiopic character falls back to the Latin font, wrap it in `\eth{...}`. The
generator does this automatically for the tables.

**Step 5: Check the numbers.**
```bash
python scripts/check_numbers.py --repo ../MoVoC --paper .
```
The exit status must be 0, meaning 0 unaccounted numbers. If you add any number to the
prose, it must be found in a repository file. Otherwise, add it to `derived()` in the script
together with the computation that produces it. A matching value is not enough: also confirm
by reading that each number is attached to the right claim (language, tokenizer, metric).

**Step 6: Check visually.** Render each page. Check that:
- the Ethiopic text renders;
- the table numbering is 1–7 in the published order;
- the correction notice is on page 1;
- no table overflows.

**Step 7: Produce the deliverables.** These are `main.pdf`, a zip of the source (`main.tex`,
`custom.bib`, `acl.sty`, `acl_natbib.bst`, `fonts/`, `tables/`, `scripts/`) and
`ANTHOLOGY_CHANGE_SUMMARY.txt`.

---

## 4. Section-by-section corrections

Apply these edits to the original camera-ready source if you have it. Otherwise use the
reference `main.tex`, which already contains all of them. The "Published" column describes
what is wrong. The "Corrected" column is what must replace it.

| Location | Published (wrong) | Corrected | Source |
|---|---|---|---|
| Title block | — | Add "Corrected version" under the title | — |
| Abstract | "consistent improvements in intrinsic metrics"; "manually annotated morpheme data" | MoVoC-Tok highest of three tokenizers on precision and MorphScore in 3 of 4 languages, small margins; BPE narrowly ahead on Ge'ez; MT: BPE highest, models undertrained, no ranking; 169,806 records | Tables 2, 3, 4 |
| New: Correction Notice (after the abstract) | — | States that published results could not be reproduced, that all results are replaced by repository reconstructions on the chairs' advice, the main corrections, and a pointer to Appendix D | — |
| §1 Contribution (iii) | "thorough intrinsic and extrinsic evaluations" | "…and report where it helps and where it does not" | — |
| §2.3 last sentence | "MoVoC contributes as a successful example…" | Remove; say the corrected results are consistent with the mixed literature | — |
| §3.1 / Table 1 | BPE splits አልሰበሩም as አል-ሰ-በሩ-ም | Table 1 = real BPE / WordPiece / MoVoC-Tok output for አልሰበሩም, ኣይትከውንን, መምህርነት (generated). Text: no tokenizer consistently recovers morphemes; MoVoC-Tok = BPE on መምህርነት; WordPiece separates -ነት | tokenizers/ |
| §3.2 formula | BPE trained with size s(1−r) | s_BPE = s_lang(1−r); released config s=224,000, r=5/7, s_BPE=32,000, morpheme budget 80,000 per language, realised vocabulary 114,553 | configs/movoc_config.json |
| §3.3 | — | Add: released tokenizers are per-language with 32,000 entries, trained on 400,000 NLLB lines; constraint data 10,293 (am) / 6,692 (ti) records; rejected merges 335,638 / 104,964; no gold boundaries at encoding time | tokenizers/*/training_config.json |
| §4.1 | Ge'ez/Tigre "for testing only" | Keep; add that the Tigrinya MoVoC-Tok is applied to them cross-lingually | v2/table2 |
| §4.2 annotations | 80k / 80k / 20k / 32k items | 153,759 am; 7,531 + 206 ti; 8,117 tig; 193 gez (total 169,806). Evaluation sets: 81,224 / 5,224 / 1,974 / 172 words | data/README.md, Table 2 |
| §4.2 MT data | Tigrinya 74 + 26 human-validated; Tigre 45 + 55; Ge'ez "newly created" and also "evaluated only intrinsically" | FLORES-200 devtest (n=1,012) for am/ti; OPUS/Tatoeba 100 am, 71 ti, 43 tig; Ge'ez 100 pairs held out (seed 42) from the 2,107-pair Mermru corpus; Tigre and Ge'ez zero-shot. Training: 800,000-pair NLLB sample, 100,000 validation | data/evaluation/manifest.json, table3_multiseed.json |
| §4.3 | lr 1.44e-7, batch 8, loss 0.443–0.438, 12 h, 96.7 samples/s, vocab 63,050, single GPU | 3 epochs, batch 32, lr 3e-4, 10% warmup, max len 128, fp16, 75,000 steps, A100 40 GB, seeds 42/43/44, 9/9 runs completed, final loss 3.00–3.59, vocab 63,051 for all arms. Tokenizers: HF tokenizers 0.21.4, 32,000 entries, 2,796,346 sentences | table3_multiseed.json, tokenizers/bpe_32k/training_config.json |
| §5.1 | Swish activation, static positional encodings | Omit. These come from `evaluation/finetune_marianmt.py`, which the repository says is NOT the source of the reconstructed runs | v2/archive/.../README.md |
| §5.2 metrics | MorphScore "mean across test set" | Precision = matched/predicted boundaries, pooled. MorphScore = recovered/gold boundaries pooled over segmented words, unsegmented words excluded. Rényi H₂ = −log Σp², raw nats, over tokens produced on the evaluation words | scripts/evaluate_intrinsic.py |
| §6 / Table 2 | MorphScore 0.654–0.731, all above the fusional mean 0.533; "does not beat all SentencePiece variants" | Table 2 from the repository. MoVoC-Tok highest in am/ti/tig (0.4139/0.4366/0.5278); BPE ahead on Ge'ez (0.6667 vs 0.6561). Fusional-mean comparison **withdrawn**. Remove the SentencePiece sentence (no such results exist) | Table 2 |
| §6 / Table 4 | Precision 73.9–88.3, MoVoC-Tok best in all four, largest gains on Tigre/Ge'ez; entropy best everywhere | Table 4 from the repository. Precision: MoVoC-Tok highest in am/ti/tig, margins 0.0038–0.0249; BPE marginally ahead on Ge'ez (0.4326 vs 0.4301). Entropy: MoVoC-Tok < BPE in am/ti/tig, but WordPiece lowest in am/ti/tig and BPE lowest on Ge'ez; raw values, not comparable to the published normalized ones | Table 4 |
| §6 / Table 3 | MoVoC-Tok best in every direction | **Withdrawn.** Table 3 = FLORES-200 reconstruction: BPE highest, MoVoC-Tok second, WordPiece last; BLEU < 2 in every cell; 75,000 vs ~416,000 steps; no ranking supported. OPUS and zero-shot results in new Table 7 (BPE highest everywhere) | table3_final.tex, per_run |
| §7 Qualitative | ኣይ-ትከውን-ን, መምህር-ነት; translation of ቤቱን አላየሁም | Replace with actual output (Table 1). The translation example is **withdrawn**: both words are single tokens for every tokenizer, and the models translate only from English. Explain that the constraint acts on 3,372 (am) / 1,470 (ti) corpus words during training and is absent at encoding time | tokenizers/, training_config.json |
| §8 Conclusion | "improving tokenization quality" | 3 of 4 languages, small margins; MT inconclusive | — |
| Limitations | — | Add: undertrained MT; evaluation-set size range (81,224 vs 172; OPUS 43–100 pairs); cross-lingual Tigre/Ge'ez; published artifacts not recovered | — |
| Ethics | — | Add FLORES-200 and Mermru to the data list; disclose AI assistance in preparing the correction (author to confirm wording) | — |
| Table 5 | 80k / 32k / 80k / 32k / 152k | Budget vs realised: 80,000/50,978; 32,000/32,000; 80,000/7,125; 32,000/32,000; 224,000/114,553 (generated) | configs/movoc_config.json |
| Table 6 | ምሕዳራት (ti), እምነት (gez), ኣብይና (tig) | Those words are not in the released files for those languages. Use the generated table: መምህርነት for Amharic (present), and the first multi-morpheme record of each other file | data/annotations |
| New Appendix C / Table 7 | — | OPUS + Mermru results, mean ± SD over three seeds, recomputed from per_run | table3_multiseed.json |
| New Appendix D | — | Numbered list of every correction | — |
| Bibliography | — | Add the Anthology entry `teklehaymanot-etal-2025-movoc` (BibTeX from the Anthology page). Keep the original 62 entries | — |

---

## 5. Acceptance checklist

- [ ] Step 1: all 36 intrinsic values match the repository exactly.
- [ ] Step 3: all 18 FLORES aggregates recompute from `per_run`; 9/9 runs, no exclusions.
- [ ] No value from `v2/table3/*.md` or the `v2/README.md` "at a glance" table appears in the paper.
- [ ] `check_numbers.py` exits 0.
- [ ] Every claim of "highest" or "lowest" checked against the table it cites (language, tokenizer and metric).
- [ ] The published figures appear only as quoted corrections.
- [ ] Tables 2–4 are byte-identical to the repository files; `tables/provenance.json` is present.
- [ ] XeLaTeX log is clean: no undefined references, no missing characters, no overfull boxes.
- [ ] Table numbering is 1–7 in the published order; the correction notice is visible on page 1.
- [ ] Authors and affiliation match the Anthology record: Teklehaymanot, Fazlija, Nejdl; L3S Research Center, Leibniz University Hannover.
- [ ] Nothing was committed or pushed.

---

## 6. Open items: ask the author, do not decide

1. **Decoding settings.** `table3_multiseed.json` says 5 beams, but the archive README says
   greedy decoding. Both are omitted from the paper until the job logs settle it.
2. **Initialisation of the MT models.** It is not stated whether they started from a
   pretrained MarianMT or were trained from scratch. The paper says "train" and makes no claim
   either way.
3. **AI-assistance disclosure** in the Ethics section: the author must approve the wording.
4. **Multi-morpheme count.** `data/README.md` gives 129,261. An independent recount gives
   129,262, a one-record difference in how a boundary is defined. The corrected paper uses
   only the record total (169,806), which is exact.
5. **Rényi scale.** The frozen Table 4 is in raw nats. The evaluation script also outputs a
   normalized version. Under normalization MoVoC-Tok has the lowest entropy in Amharic only.
   Keep raw unless the author decides otherwise; the table structure must not change.
6. **Wording of Sections 1–2.** The reference build paraphrases them from the published PDF.
   If the original source is available, use its wording verbatim. Two related-work citations
   (Dewangan et al. 2025; Mikaberidze et al. 2024) were left out of the reference build
   because their entries could not be verified; restore them from the original bibliography.

---

## 7. Submitting to the ACL Anthology

- **Type: revision** (a full replacement PDF), not an erratum. The changes affect the main
  results. A retraction is only for unrecoverable findings; the authors and chairs decide.
- **How:** use the yellow "Fix data" button on
  https://aclanthology.org/2025.findings-emnlp.706/. This opens a GitHub issue. Choose the
  revision type, attach `main.pdf`, and paste `ANTHOLOGY_CHANGE_SUMMARY.txt`. Reference the
  programme chairs' advice to publish a corrected version.
- **Header and footer:** add the proceedings header and footer with the Anthology's watermark
  service before attaching the PDF.
- **Expectations:** processing takes about four weeks, and the original PDF remains available.
- **The author files the issue.** The agent prepares the files only.
