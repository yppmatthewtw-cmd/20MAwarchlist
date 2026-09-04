#!/usr/bin/env python3
"""AI money-flow scoring for the 41 AI 小群組 of the Dashboard R15.6 classification.

Identical scoring math to the Sub-Sector watchlist R1.01 engine; only the baskets differ.
Per the brief, baskets hold US-listed shares and US ADRs only — the dashboard already
carries the ADR line where one exists (TSM for 2330.TW, ASML for the Dutch listing), so
members carrying a foreign-exchange suffix are excluded and reported, not substituted.

For each sub-sector and each of the last 5 trading sessions we score how strongly money
moved INTO or OUT OF its representative basket, from price + volume alone:
  A 方向  = tanh(excess return / 2%)              (return minus the market median that day)
  B 量能  = log2(dollar volume / 20-day median), clipped to +-1   (volume surge / drought)
  C 收位  = Chaikin money-flow multiplier ((C-L)-(H-C))/(H-L)     (where real OHLC exists)
  f = (0.70*A + 0.30*C) * (1 + 0.50*B)        [A only, when no intraday range is available]
Basket aggregation is dollar-volume weighted (money-weighted), each name capped at 40%.
Daily scores are standardised across the 111 sub-sectors, so a score answers
"where did the money go TODAY relative to every other sub-sector", not "did it go up".
"""
import csv, json, math, os, pickle, statistics, collections

SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"
WIN = 5                      # scored sessions
LOOK = 20                    # sessions of history for the volume baseline

AI = json.load(open(f"{SCR}/ai/aigroups.json"))
subs = AI["groups"]
S8 = pickle.load(open(f"{SCR}/series9.pkl", "rb")); CAL = S8["cal"]; SER = S8["series"]
EST = S8.get("meta8", {}).get("estimated", {})
M9 = S8.get("meta9", {})
NOVOL = set(M9.get("no_volume", []))          # 09-02: close known, volume not published yet
NOVOL_DATE = M9.get("added_date")

SUPP = {}      # no hand substitutes: the brief restricts baskets to US listings / ADRs
PROXY = {}

# ---------------- load real daily OHLCV ----------------
def load_nz(sym):
    p = f"{NZ}/{sym}.csv"
    if not os.path.exists(p): return None
    out = {}
    with open(p, newline="") as f:
        for row in csv.DictReader(f):
            d = (row.get("Date") or "")[:10]
            try:
                o, h, l, c, v = (float(row[k]) for k in ("Open", "High", "Low", "Close", "Volume"))
            except (ValueError, KeyError, TypeError):
                continue                      # partial rows (e.g. the volume-only 09-02 row)
            if c > 0: out[d] = (o, h, l, c, v)
    return out or None

wanted = sorted({t for s in subs for t in s["us"]})
NZD = {}
for t in wanted:
    d = load_nz(t)
    if d: NZD[t] = d

# ---------------- calendar: the last WIN sessions both sources agree on ----------------
nz_dates = collections.Counter()
for d in NZD.values():
    for k in d: nz_dates[k] += 1
full = sorted(k for k, n in nz_dates.items() if n >= 0.8 * len(NZD))
LAST = [d for d in CAL if d in set(full)][-(WIN + LOOK + 1):]
DAYS = LAST[-WIN:]
BASE = LAST[-(WIN + LOOK + 1):-WIN]
print("scored sessions:", DAYS)
print("volume baseline:", BASE[0], "->", BASE[-1], f"({len(BASE)} sessions)")

# ---------------- market baseline: median return of the real-OHLCV universe ----------------
allnz = {}
for f in os.listdir(NZ):
    sym = f[:-4]
    if sym in NZD: allnz[sym] = NZD[sym]
    else:
        d = load_nz(sym)
        if d: allnz[sym] = d
MKT = {}
for i, day in enumerate(DAYS):
    prev = LAST[LAST.index(day) - 1]
    rets = [d[day][3] / d[prev][3] - 1 for d in allnz.values() if day in d and prev in d and d[prev][3] > 0]
    MKT[day] = statistics.median(rets)
print("market median return:", {d: f"{MKT[d]*100:+.2f}%" for d in DAYS}, f"(n={len(rets)})")

# ---------------- per-ticker daily flow ----------------
def series_snap(sym):
    """close/volume fallback from the repaired snapshot series (no intraday range)."""
    if sym not in SER: return None
    fi, cs, vs, ff = SER[sym]
    idx = {CAL[fi + i]: i for i in range(len(cs))}
    return {d: (None, None, None, cs[idx[d]], (None if (sym in NOVOL and d == NOVOL_DATE) else vs[idx[d]]))
            for d in LAST if d in idx}

def tick_flow(sym):
    """Real daily OHLCV when the mirror carries the full window; otherwise the repaired
    snapshot series (close/volume only). Stale mirror files fall through to the snapshot."""
    data = NZD.get(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    if not real:
        data = series_snap(sym)
    if not data: return None
    if not all(d in data for d in DAYS): return None
    base_dv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4] is not None]
    if len(base_dv) < 10: return None
    med_dv = statistics.median(base_dv)
    if med_dv <= 0: return None
    out = {"sym": sym, "src": "real" if real else "snap", "med_dv": med_dv, "days": {}}
    for day in DAYS:
        prev = LAST[LAST.index(day) - 1]
        if prev not in data: return None
        o, h, l, c, v = data[day]
        pc = data[prev][3]
        ret = c / pc - 1 if pc > 0 else 0.0
        exret = ret - MKT[day]
        novol = v is None
        dv = c * v if not novol else med_dv          # weighting proxy when volume is unpublished
        rvol = (dv / med_dv if med_dv > 0 else 1.0) if not novol else 1.0
        A = math.tanh(exret / 0.02)
        B = 0.0 if novol else max(-1.0, min(1.0, math.log2(max(0.25, min(4.0, rvol))) / 2))
        if real and h is not None and h > l:
            C = ((c - l) - (h - c)) / (h - l)
            f = (0.70 * A + 0.30 * C) * (1 + 0.50 * B)
            mfd = C * dv                       # Chaikin money-flow dollars
        else:
            C = None
            f = A * (1 + 0.50 * B)
            mfd = A * dv                       # direction-scaled dollars (no intraday range)
        est = EST.get(sym, {}).get(day) in ("official", "interp") if not real else False
        out["days"][day] = {"ret": ret, "exret": exret, "dv": dv, "rvol": rvol, "novol": novol,
                            "A": A, "B": B, "C": C, "f": f, "mfd": mfd, "est": est}
    return out

TICK, dropped = {}, []
for t in wanted:
    r = tick_flow(t)
    if r: TICK[t] = r
    else: dropped.append(t)
print(f"tickers scored: {len(TICK)} (real OHLCV {sum(1 for v in TICK.values() if v['src']=='real')}, "
      f"snapshot {sum(1 for v in TICK.values() if v['src']=='snap')}); dropped {len(dropped)}: {dropped}")

# ---------------- aggregate per sub-sector ----------------
rows = []
for s in subs:
    listed = s["us"]
    tk = [t for t in listed if t in TICK]
    supp = [t for t in SUPP.get(s["n"], []) if t in TICK and t not in tk]
    tk = tk + supp
    proxy = s["n"] in PROXY
    if not tk:
        rows.append(dict(s, basket=[], n_basket=0, proxy=proxy, days=None,
                         note=("成分股全部非美股上市／無 US ADR" if not s["us"] else "美股成分股數據不足")))
        continue
    daily = {}
    for day in DAYS:
        w = {t: TICK[t]["days"][day]["dv"] for t in tk}
        tot = sum(w.values()) or 1.0
        ws = {t: min(0.40, w[t] / tot) for t in tk}          # cap any single name at 40%
        z = sum(ws.values()); ws = {t: v / z for t, v in ws.items()}
        F = sum(ws[t] * TICK[t]["days"][day]["f"] for t in tk)
        mfd = sum(TICK[t]["days"][day]["mfd"] for t in tk)
        ret_ew = statistics.mean(TICK[t]["days"][day]["ret"] for t in tk)
        rvol = sum(ws[t] * TICK[t]["days"][day]["rvol"] for t in tk)
        dv = sum(TICK[t]["days"][day]["dv"] for t in tk)
        up = sum(1 for t in tk if TICK[t]["days"][day]["exret"] > 0)
        daily[day] = {"F": F, "mfd": mfd, "ret": ret_ew, "rvol": rvol, "dv": dv,
                      "breadth": up / len(tk), "up": up,
                      "novol": sum(1 for t in tk if TICK[t]["days"][day]["novol"])}
    # per-ticker 5-day flow, same recency weights as the group score, for the ticker column
    W5 = [1.0, 1.15, 1.35, 1.6, 1.9]
    ticks = []
    for t in tk:
        td = TICK[t]["days"]
        tf5 = sum(w * td[d]["f"] for w, d in zip(W5, DAYS)) / sum(W5)
        ticks.append({"sym": t, "tf5": round(tf5, 4),
                      "mfd5": sum(td[d]["mfd"] for d in DAYS),
                      "dv5": sum(td[d]["dv"] for d in DAYS),
                      "ret5": round(math.prod(1 + td[d]["ret"] for d in DAYS) - 1, 5),
                      "src": TICK[t]["src"],
                      "novol": sum(1 for d in DAYS if td[d]["novol"])})
    ticks.sort(key=lambda x: -x["tf5"])          # most inflow first, most outflow last
    rows.append(dict(s, basket=tk, ticks=ticks, n_basket=len(tk), proxy=proxy, supp=supp,
                     missing=[t for t in listed if t not in TICK], days=daily,
                     src=("real" if all(TICK[t]["src"] == "real" for t in tk) else
                          ("snap" if all(TICK[t]["src"] == "snap" for t in tk) else "mix")),
                     est_days=sorted({d for t in tk for d in DAYS if TICK[t]["days"][d]["est"]})))

# ---------------- cross-sectional standardisation, per day ----------------
live = [r for r in rows if r["days"]]
W = [1.0, 1.15, 1.35, 1.6, 1.9]          # recency weights over the 5 sessions
for day in DAYS:
    vals = [r["days"][day]["F"] for r in live]
    mu = statistics.mean(vals); sd = statistics.pstdev(vals) or 1e-9
    order = sorted(range(len(live)), key=lambda i: vals[i])
    pct = [0.0] * len(live)
    for rank, i in enumerate(order): pct[i] = rank / (len(live) - 1) * 100
    for i, r in enumerate(live):
        d = r["days"][day]
        d["z"] = (d["F"] - mu) / sd
        d["score"] = pct[i]
        d["grade"] = (3 if d["z"] >= 1.5 else 2 if d["z"] >= 0.75 else 1 if d["z"] >= 0.25 else
                      0 if d["z"] > -0.25 else -1 if d["z"] > -0.75 else -2 if d["z"] > -1.5 else -3)
for r in live:
    zs = [r["days"][d]["z"] for d in DAYS]
    r["z5"] = sum(w * z for w, z in zip(W, zs)) / sum(W)
    r["pos"] = sum(1 for d in DAYS if r["days"][d]["grade"] >= 1)
    r["neg"] = sum(1 for d in DAYS if r["days"][d]["grade"] <= -1)
    n = len(zs); xb = (n - 1) / 2; yb = sum(zs) / n
    r["slope"] = sum((i - xb) * (z - yb) for i, z in enumerate(zs)) / sum((i - xb) ** 2 for i in range(n))
    r["mfd5"] = sum(r["days"][d]["mfd"] for d in DAYS)
    r["dv5"] = sum(r["days"][d]["dv"] for d in DAYS)
    r["ret5"] = math.prod(1 + r["days"][d]["ret"] for d in DAYS) - 1
    n = r["n_basket"]
    r["shrink"] = math.sqrt(n / (n + 2.0))                 # reliability weight, n=1 -> .58, n=11 -> .92
    r["z5r"] = r["z5"] * r["shrink"]                        # noise-adjusted composite
    r["intensity"] = r["mfd5"] / r["dv5"] * 100 if r["dv5"] else 0.0   # net flow as % of turnover
    r["breadth5"] = statistics.mean(r["days"][d]["breadth"] for d in DAYS)
    r["novol_days"] = sum(1 for d in DAYS if r["days"][d]["novol"])
vals = [r["z5"] for r in live]
order = sorted(range(len(live)), key=lambda i: vals[i])
for rank, i in enumerate(order): live[i]["score5"] = rank / (len(live) - 1) * 100
vr = [r["z5r"] for r in live]
order = sorted(range(len(live)), key=lambda i: vr[i])
for rank, i in enumerate(order): live[i]["score5r"] = rank / (len(live) - 1) * 100
live.sort(key=lambda r: -r["z5"])
for i, r in enumerate(live, 1): r["rank"] = i

out = {"meta": {"days": DAYS, "base": [BASE[0], BASE[-1]], "mkt_med": MKT,
                "n_sub": len(rows), "n_scored": len(live), "n_tick": len(TICK),
                "dropped": dropped, "proxy": {str(k): v for k, v in PROXY.items()}, "supp": {str(k): v for k, v in SUPP.items()},
                "weights": W, "source_note": "natezone/market-tracker 真實日線 OHLCV 為主，"
                "其餘以快照序列（僅收盤/成交量）補足"},
       "rows": live + [r for r in rows if not r["days"]]}
out["meta"]["asof_dash"] = AI["asof_dash"]
out["meta"]["nonus_excluded"] = sorted({m for s in subs for m in s["nonus"]})
out["meta"]["novol_note"] = {"date": NOVOL_DATE, "n": len(NOVOL),
                                "why": "09-02 收盤已由 09-03 盤中快照嘅 price-price_change 取得，但該快照嘅成交量係 09-03 partial，"
                                       "故非日線鏡像覆蓋嘅股票當日成交量從缺，量能項 B 設為 0（中性），並標示"}
json.dump(out, open(f"{SCR}/ai/flow3.json", "w"), ensure_ascii=False)
print("\nTOP 12 inflow:")
for r in live[:12]:
    print(f"  {r['rank']:3d} {r['code']:<5}{r['zh'][:20]:<22} z5{r['z5']:+.2f} 5日分{r['score5']:5.1f} "
          f"日格{[r['days'][d]['grade'] for d in DAYS]} 淨額${r['mfd5']/1e6:+,.0f}M 樣本{r['n_basket']}")
print("BOTTOM 12 outflow:")
for r in live[-12:]:
    print(f"  {r['rank']:3d} {r['code']:<5}{r['zh'][:20]:<22} z5{r['z5']:+.2f} 5日分{r['score5']:5.1f} "
          f"日格{[r['days'][d]['grade'] for d in DAYS]} 淨額${r['mfd5']/1e6:+,.0f}M 樣本{r['n_basket']}")
print("unscorable:", [(r['code'], r['note']) for r in rows if not r["days"]])
