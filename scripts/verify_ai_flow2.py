#!/usr/bin/env python3
"""Independent re-computation of the sub-sector flow numbers, straight from the raw sources."""
import csv, json, math, os, pickle, statistics, glob, re
SCR="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
NZ="/home/user/natezone/market-tracker/data/UNIFIED/history"
F=json.load(open(f"{SCR}/ai/flow2.json")); M=F["meta"]; DAYS=M["days"]; rows=[r for r in F["rows"] if r.get("days")]
S8=pickle.load(open(f"{SCR}/series9.pkl","rb")); CAL=S8["cal"]; SER=S8["series"]
bad=[]
# 1) structural
if len(F["rows"])!=41: bad.append(("row count", len(F["rows"])))

subs=json.load(open(f"{SCR}/ai/aigroups.json"))["groups"]
if len(rows)+len([r for r in F["rows"] if not r.get("days")])!=41: bad.append(("scored+unscored != 41",))
# 2) grades match z thresholds; scores are a valid percentile set; ranks consistent
for day in DAYS:
    zs=[r["days"][day]["z"] for r in rows]
    if abs(statistics.mean(zs))>1e-9 or abs(statistics.pstdev(zs)-1)>1e-9: bad.append(("z not standardised",day,statistics.mean(zs),statistics.pstdev(zs)))
    sc=sorted(round(r["days"][day]["score"],4) for r in rows)
    exp=sorted(round(i/(len(rows)-1)*100,4) for i in range(len(rows)))
    if sc!=exp: bad.append(("percentile set",day))
    # score order must follow z order
    if [r["sym"] if False else r["n"] for r in sorted(rows,key=lambda r:-r["days"][day]["z"])]!=[r["n"] for r in sorted(rows,key=lambda r:-r["days"][day]["score"])]:
        bad.append(("score/z order",day))
    for r in rows:
        z=r["days"][day]["z"]; g=r["days"][day]["grade"]
        exp_g=(3 if z>=1.5 else 2 if z>=0.75 else 1 if z>=0.25 else 0 if z>-0.25 else -1 if z>-0.75 else -2 if z>-1.5 else -3)
        if g!=exp_g: bad.append(("grade",r["n"],day,z,g))
if [r["rank"] for r in sorted(rows,key=lambda r:-r["z5"])]!=list(range(1,len(rows)+1)): bad.append(("rank order",))
for r in rows:
    W=M["weights"]; z5=sum(w*r["days"][d]["z"] for w,d in zip(W,DAYS))/sum(W)
    if abs(z5-r["z5"])>1e-9: bad.append(("z5",r["n"],z5,r["z5"]))
    if r["pos"]!=sum(1 for d in DAYS if r["days"][d]["grade"]>=1): bad.append(("pos",r["n"]))
    if r["neg"]!=sum(1 for d in DAYS if r["days"][d]["grade"]<=-1): bad.append(("neg",r["n"]))
# 3) full independent recompute of two baskets straight from the CSVs
def nz(sym):
    p=f"{NZ}/{sym}.csv"
    if not os.path.exists(p): return None
    d={}
    for row in csv.DictReader(open(p)):
        try: d[row["Date"][:10]]=tuple(float(row[k]) for k in ("Open","High","Low","Close","Volume"))
        except (ValueError,KeyError): pass
    return d
NOVOL=set(S8.get("meta9",{}).get("no_volume",[])); NOVOLD=S8.get("meta9",{}).get("added_date")
LAST=[d for d in CAL if d<=DAYS[-1]][-27:]
BASE=[d for d in CAL if M["base"][0]<=d<=M["base"][1]]      # exactly the engine's volume baseline
mkt=M["mkt_med"]
for target in [r["n"] for r in rows[:2]] + [rows[-1]["n"]]:
    r=[x for x in rows if x["n"]==target][0]
    for day in DAYS:
        prev=LAST[LAST.index(day)-1]; num=0.0; W={}
        vals={}
        for t in r["basket"]:
            data=nz(t)
            real = data and all(x in data for x in LAST[-6:])
            if not real:
                fi,cs,vs,ff=SER[t]; idx={CAL[fi+i]:i for i in range(len(cs))}
                data={d:(None,None,None,cs[idx[d]],vs[idx[d]]) for d in LAST if d in idx}
            o,h,l,c,v=data[day]; pc=data[prev][3]
            novol = (not real) and (t in NOVOL) and day==NOVOLD
            base=statistics.median(data[d][3]*data[d][4] for d in BASE if d in data and not ((not real) and t in NOVOL and d==NOVOLD))
            dv=(c*v) if not novol else base; rvol=(dv/base) if not novol else 1.0
            A=math.tanh((c/pc-1-mkt[day])/0.02); B=0.0 if novol else max(-1,min(1,math.log2(max(.25,min(4,rvol)))/2))
            if real and h and h>l:
                C=((c-l)-(h-c))/(h-l); f=(0.7*A+0.3*C)*(1+0.5*B)
            else: f=A*(1+0.5*B)
            vals[t]=(f,dv)
        tot=sum(x[1] for x in vals.values()); w={t:min(0.4,x[1]/tot) for t,x in vals.items()}
        z=sum(w.values()); w={t:x/z for t,x in w.items()}
        Fv=sum(w[t]*vals[t][0] for t in vals)
        if abs(Fv-r["days"][day]["F"])>1e-6: bad.append(("F recompute",target,day,Fv,r["days"][day]["F"]))
# 4) HTML matches the JSON
htmlf=sorted(glob.glob(f"{SCR}/AI_Sector_watchlist_R2.00_*.html"))[-1]
H=open(htmlf,encoding="utf-8").read()
for r in rows:
    for i,d in enumerate(DAYS,1):
        if f'data-d{i}="{r["days"][d]["score"]:.2f}"' not in H: bad.append(("html day attr",r["n"],d))
    if f'data-score5="{r["score5"]:.2f}"' not in H: bad.append(("html score5",r["n"]))
if H.count('<tr data-z5=')+H.count('"><td class="rk">')<111: pass
import collections
print("rows:",len(rows),"| days:",DAYS,"| tickers:",M["n_tick"])
print("basket size: min %d, median %.0f, max %d | n<=2: %d | unscorable: %d" % (min(r["n_basket"] for r in rows),
      statistics.median(r["n_basket"] for r in rows), max(r["n_basket"] for r in rows),
      sum(1 for r in rows if r["n_basket"]<=2), len([x for x in F["rows"] if not x.get("days")])))
# US-only rule: no basket member may carry a foreign-exchange suffix
for r in rows:
    for t in r["basket"]:
        if "." in t: bad.append(("non-US ticker in basket", r["code"], t))
    if set(r["basket"]) - set(r["us"]): bad.append(("basket not subset of US members", r["code"]))
import math as _m
for r in rows:
    n=r["n_basket"]
    if abs(r["shrink"]-_m.sqrt(n/(n+2.0)))>1e-9: bad.append(("shrink",r["code"]))
    if abs(r["z5r"]-r["z5"]*r["shrink"])>1e-9: bad.append(("z5r",r["code"]))
    if r["dv5"] and abs(r["intensity"]-r["mfd5"]/r["dv5"]*100)>1e-6: bad.append(("intensity",r["code"]))
    if abs(r["breadth5"]-statistics.mean(r["days"][d]["breadth"] for d in DAYS))>1e-9: bad.append(("breadth5",r["code"]))
    for d in DAYS:
        if not (0<=r["days"][d]["breadth"]<=1): bad.append(("breadth range",r["code"],d))
sc=sorted(round(r["score5r"],4) for r in rows)
exp=sorted(round(i/(len(rows)-1)*100,4) for i in range(len(rows)))
if sc!=exp: bad.append(("score5r percentile set",))
print("PROBLEMS:", len(bad))
for b in bad[:20]: print("  ", b)
