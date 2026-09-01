"""Table 2: official MoVoC data first, AMSEG evaluation data only for the deficit.

Scoring is the official implementation, unmodified: movoc/metrics.py::morphscore
(recall of gold boundaries, micro-averaged, unsegmented words excluded) over
cumulative-length boundary projection, with the released MoVoC-Tok merges.

Only surface-aligned entries are evaluable: gold boundaries are character offsets
into the surface word, so an annotation whose parts do not concatenate back to the
word yields offsets that do not correspond to real positions. Citation-form
annotations (normalised roots) are therefore excluded, not scored.
"""
import sys, json, csv, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
MV=Path("/homes/neumann/teklehaymanot/TigrinyaTokenizer/MPETokenization/Paralleldata/MoVoC/movoc")
sys.path.insert(0,str(MV))
from movoc import tokenizer as mvtok
from build_official import official_pool, amseg_pool
OUT=Path(__file__).parent/"results"; OUT.mkdir(parents=True,exist_ok=True)
END="</w>"
TARGET={"amharic":80000,"tigrinya":80000,"geez":20000,"tigre":32000}
MERGES={"amharic":"movoc_tok_merges_amharic.txt","tigrinya":"movoc_tok_merges_tigrinya.txt",
        "geez":"movoc_tok_merges_geez.txt","tigre":"movoc_tok_merges_tigre.txt"}
LABEL={"amharic":("Amharic","amh",0.710),"tigrinya":("Tigrinya","tir",0.731),
       "geez":("Ge'ez","gez",0.670),"tigre":("Tigre","tig",0.654)}
def cuts(parts):
    c,pos=set(),0
    for p in parts[:-1]: pos+=len(p); c.add(pos)
    return c
def official_morphscore(pred,gold):
    hit=tot=0
    for p,g in zip(pred,gold):
        if not p: continue          # unsegmented: excluded, not scored 0
        tot+=len(g); hit+=len(p&g)
    return hit/tot if tot else 0.0
rows=[]
for L,t in TARGET.items():
    off,off_dup,off_unal=official_pool(L,aligned_only=True)
    items=[(w,parts) for w,(parts,_) in sorted(off.items())]
    if len(items)>t:
        random.Random(42).shuffle(items); items=sorted(items[:t])
    n_off=len(items); n_amseg=0; amseg_dup=0
    if len(items)<t:                                   # fallback only for deficit
        have={w for w,_ in items}
        extra=[(w,s) for w,(s,_) in sorted(amseg_pool(L).items()) if w not in have]
        amseg_dup=len(amseg_pool(L))-len(extra)-0
        need=t-len(items)
        items+=extra[:need]; n_amseg=min(need,len(extra))
    ranks=mvtok.load_merges(MV/"models"/MERGES[L])
    gold=[cuts(p) for _,p in items]
    pred=[cuts([x[:-len(END)] if x.endswith(END) else x for x in mvtok.encode(w,ranks)]) for w,_ in items]
    ms=100*official_morphscore(pred,gold)
    name,iso,ps=LABEL[L]
    rows.append(dict(language=name,iso=iso,official_items_used=n_off,
        amseg_fallback_items_used=n_amseg,duplicates_removed=off_dup+amseg_dup,
        final_items_evaluated=len(items),morphscore=round(ms,1),
        paper_items=t,paper_morphscore=ps,shortfall=max(0,t-len(items)),
        pct_official=round(100*n_off/len(items),1),pct_amseg=round(100*n_amseg/len(items),1),
        excluded_unaligned=off_unal,segmented_words=sum(1 for p in pred if p)))
    print(f"{name:10} off={n_off:>6,} amseg={n_amseg:>6,} final={len(items):>6,} "
          f"MorphScore={ms:>5.1f} (unaligned excluded={off_unal:,})")
with open(OUT/"morphscore_scores.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(OUT/"table2_reproduction.csv","w",newline="",encoding="utf-8") as f:
    k=["language","iso","final_items_evaluated","morphscore","paper_items","paper_morphscore",
       "official_items_used","amseg_fallback_items_used","duplicates_removed","pct_official","pct_amseg","shortfall"]
    w=csv.DictWriter(f,fieldnames=k,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
tex=["% Table 2 reproduction. Official MoVoC data first; AMSEG evaluation data only for the deficit.",
"\\begin{tabular}{lrr}","\\toprule","Language (ISO 639-3) & No. Items & MorphScore $\\uparrow$ \\\\","\\midrule"]
for r in rows: tex.append(f"{r['language']} ({r['iso']}) & {r['final_items_evaluated']:,} & {r['morphscore']} \\\\")
tex+=["\\bottomrule","\\end{tabular}"]
(OUT/"table2_reproduction.tex").write_text("\n".join(tex)+"\n",encoding="utf-8")
json.dump(rows,open(OUT/"table2_rows.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
