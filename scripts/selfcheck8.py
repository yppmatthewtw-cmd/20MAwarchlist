import json, pickle, statistics, collections
SCR="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
o=json.load(open(f"{SCR}/screen_results8.json")); d=pickle.load(open(f"{SCR}/series8.pkl","rb")); cal=d["cal"]; S=d["series"]
src=open(f"{SCR}/screener8.py").read()
ns={}
exec(src[src.index("def sma_series"):src.index("# ---------------- eligibility")], ns)
sma_series, find_bottoms, higher_lows, ma_uptrend = ns["sma_series"], ns["find_bottoms"], ns["higher_lows"], ns["ma_uptrend"]
PIDS=o["meta"]["page_ids"]; TIERS={"a":(10e9,float("inf")),"b":(2e9,10e9),"c":(0,2e9)}
bad=[]
deal=set(o["meta"]["deal_pinned"]["symbols"]); funds=set(o["meta"]["unknown_cap"]["funds"]); dupes={x["dropped"] for x in o["meta"]["class_dupes"]}
# 1 conservation + tier assignment + sort + leakage + per-row recomputation
for pid in PIDS:
    pg=o["pages"][pid]; p=int(pid[0]); L,W=pg["L"],pg["W"]
    prev=None
    for i,r in enumerate(pg["rows"],1):
        if r["sym"] in deal or r["sym"] in funds or r["sym"] in dupes: bad.append((pid,r["sym"],"excluded name listed"))
        lo,hi=TIERS[pid[1]]
        if not (lo<=r["mcap"]<hi): bad.append((pid,r["sym"],"tier mismatch",r["mcap"]))
        if any(k.startswith("_") for k in r): bad.append((pid,r["sym"],"underscore leak"))
        if prev is not None and r["combo"]>prev+0.05: bad.append((pid,r["sym"],"sort order",prev,r["combo"]))
        prev=r["combo"]
        fi,cs,vs,ff=S[r["sym"]]
        ma=sma_series(cs,L); slope=ma_uptrend(ma,W)
        if slope is None: bad.append((pid,r["sym"],"MA uptrend fails on recompute")); continue
        if abs(slope-r["slope"])>0.011: bad.append((pid,r["sym"],"slope",slope,r["slope"]))
        if abs(ma[-1]-r["ma"])>0.006: bad.append((pid,r["sym"],"ma",ma[-1],r["ma"]))
        if abs(cs[-1]-r["close"])>0.006: bad.append((pid,r["sym"],"close",cs[-1],r["close"]))
        hl=higher_lows(find_bottoms(cs),len(cs))
        if hl is None: bad.append((pid,r["sym"],"no higher lows on recompute")); continue
        hl2=[[cal[fi+j],round(c,4)] for j,c in hl]
        if hl2!=r["hl"]: bad.append((pid,r["sym"],"hl mismatch",hl2[-2:],r["hl"][-2:]))
        if (cs[-1]<ma[-1])!=r["below_ma"]: bad.append((pid,r["sym"],"below_ma flag"))
        if cs[-1] < hl[-1][1]: bad.append((pid,r["sym"],"close below last low (gate)"))
        if r["cert_c"]["retrace_pct"]>100: bad.append((pid,r["sym"],"retrace uncapped"))
    # all_ranks consistency
    ar=pg["all_ranks"]; 
    if len(ar)!=pg["qualified"]: bad.append((pid,"all_ranks size",len(ar),pg["qualified"]))
    for i,r in enumerate(pg["rows"],1):
        if ar.get(r["sym"])!=i: bad.append((pid,r["sym"],"all_ranks rank",ar.get(r["sym"]),i))
# 2 page1 union / ranks / score / sort  (coverage = qualifying timeframes, as documented)
q=o["meta"]["diag"]["qual"]
union={}
for pid in PIDS:
    for i,r in enumerate(o["pages"][pid]["rows"],1): union.setdefault(r["sym"],{})[pid]=i
p1={r["sym"]:r for r in o["page1"]}
if set(p1)!=set(union): bad.append(("page1","union mismatch",set(p1)^set(union)))
for s,r in p1.items():
    if r["ranks"]!=union.get(s): bad.append(("page1",s,"ranks",r["ranks"],union.get(s)))
    hits=sum(1 for p in "2345" if s in set(q[p]))
    if r["hits"]!=hits: bad.append(("page1",s,"hits",r["hits"],hits))
    sc=0.4*r["vcp"]+0.4*r["cert"]+0.2*(hits/4*100)
    if abs(sc-r["score"])>0.11: bad.append(("page1",s,"score",sc,r["score"]))
prev=None
for r in o["page1"]:
    if prev is not None and r["score"]>prev+0.05: bad.append(("page1",r["sym"],"sort"))
    prev=r["score"]
# 3 tier conservation: tiers + unknown(x,f) + deals = timeframe total (all struct syms qualifying)
q=o["meta"]["diag"]["qual"]
for p in "2345":
    tot=sum(o["pages"][f"{p}{k}"]["qualified"] for k in "abc")+o["meta"]["unknown_cap"]["per_timeframe"][p]+o["meta"]["deal_pinned"]["per_timeframe"][p]
    if tot!=len(q[p]): bad.append(("conservation",p,tot,len(q[p])))
# 4 estimated-bar bottoms
eb=[(r["sym"],r["est_bottom"]) for r in o["page1"] if r["est_bottom"]]
print("rows with a bottom on an estimated bar:", len(eb), eb[:10])
print("below_ma rows:", sum(1 for r in o["page1"] if r["below_ma"]))
print("undercut rows:", [r["sym"] for r in o["page1"] if r["cert_c"]["undercut"]][:20])
print("PROBLEMS:", len(bad)); [print("  ",b) for b in bad[:30]]
