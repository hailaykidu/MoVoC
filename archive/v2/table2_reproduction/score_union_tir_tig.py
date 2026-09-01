"""Tigrinya and Tigre: maximal scorable pool = union of official + AMSEG data.

Union is taken over surface-aligned, multi-morpheme entries, deduplicated by
surface word with official sources taking precedence (gold before post-edited
before HornMorpho-segmented, then AMSEG evaluation data).

Scoring is unchanged: movoc/metrics.py::morphscore over cumulative-length
projection with the released MoVoC-Tok merges.
"""
import sys, json, csv, unicodedata
from pathlib import Path
A=Path("/homes/neumann/teklehaymanot/amseg")
MV=Path("/homes/neumann/teklehaymanot/TigrinyaTokenizer/MPETokenization/Paralleldata/MoVoC/movoc")
sys.path.insert(0,str(MV))
from movoc import tokenizer as mvtok
OUT=Path(__file__).parent/"results"; OUT.mkdir(parents=True,exist_ok=True)
END="</w>"; PH={"-","–","—","","None","null"}
def clean(v):
    if v is None: return ""
    v=unicodedata.normalize("NFC",str(v)).strip().strip("-").strip("–").strip()
    return "" if v in PH else v
def norm(s): return unicodedata.normalize("NFC",str(s)).strip()
K4=("prefix","root","infix","suffix"); K5=K4+("clitic",)
SRC={"tigrinya":[("data/annotations/tigrinya/gold_morphemes.json",K4,"official:gold"),
                 ("data/annotations/tigrinya/postedited_morphemes.json",K4,"official:postedited"),
                 ("data/segmented/tigrinya_morpheme_segmented.json",K5,"official:hornmorpho")],
     "tigre":[("data/annotations/tigre/manual_morphemes.json",K5,"official:manual"),
              ("data/segmented/tigre_morpheme_segmented.json",K5,"official:hornmorpho")]}
MERGES={"tigrinya":"movoc_tok_merges_tigrinya.txt","tigre":"movoc_tok_merges_tigre.txt"}
LABEL={"tigrinya":("Tigrinya","tir",80000,0.731),"tigre":("Tigre","tig",32000,0.654)}
def cuts(parts):
    c,pos=set(),0
    for p in parts[:-1]: pos+=len(p); c.add(pos)
    return c
def official_morphscore(pred,gold):
    hit=tot=0
    for p,g in zip(pred,gold):
        if not p: continue
        tot+=len(g); hit+=len(p&g)
    return hit/tot if tot else 0.0
rows=[]
for L in ("tigrinya","tigre"):
    union={}; prov={}; dup=0; unal=0
    for path,keys,tag in SRC[L]:
        for e in json.load(open(A/path,encoding="utf-8")):
            w=norm(e.get("word",""))
            if not w: continue
            parts=[clean(e.get(k)) for k in keys]; parts=[p for p in parts if p]
            if len(parts)<2: continue
            if "".join(parts)!=w: unal+=1; continue
            if w in union: dup+=1; continue
            union[w]=parts; prov[w]=tag
    for l in open(A/f"evaluation/data/{L}_gold.tsv",encoding="utf-8"):
        p=l.rstrip("\n").split("\t")
        if len(p)<2: continue
        w,seg=p[0],p[1].split("+")
        if "".join(seg)!=w or len(seg)<2: continue
        if w in union: dup+=1; continue
        union[w]=seg; prov[w]="amseg:evaluation_data"
    items=sorted(union.items())
    ranks=mvtok.load_merges(MV/"models"/MERGES[L])
    gold=[cuts(p) for _,p in items]
    pred=[cuts([x[:-len(END)] if x.endswith(END) else x for x in mvtok.encode(w,ranks)]) for w,_ in items]
    ms=100*official_morphscore(pred,gold)
    n_off=sum(1 for w,_ in items if prov[w].startswith("official"))
    n_ams=len(items)-n_off
    name,iso,t,ps=LABEL[L]
    rows.append(dict(language=name,iso=iso,final_items_evaluated=len(items),morphscore=round(ms,1),
        official_items_used=n_off,amseg_items_used=n_ams,duplicates_removed=dup,
        excluded_unaligned=unal,paper_items=t,paper_morphscore=ps,shortfall=t-len(items),
        pct_official=round(100*n_off/len(items),1),pct_amseg=round(100*n_ams/len(items),1),
        segmented_words=sum(1 for p in pred if p)))
    print(f"{name:10} union={len(items):>6,} off={n_off:>6,} amseg={n_ams:>6,} "
          f"dup_removed={dup:>6,} unaligned={unal:>6,} MorphScore={ms:>5.1f}")
json.dump(rows,open(OUT/"table2_union_tir_tig.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
with open(OUT/"morphscore_union_tir_tig.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
