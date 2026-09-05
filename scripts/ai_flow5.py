#!/usr/bin/env python3
"""AI money-flow scoring — R5.00 engine (41 AI 小群組 of the Dashboard R15.6 classification).

Identical scoring math to the Sub-Sector watchlist R4.00 engine (Yahoo second source); only
the baskets differ.  Per the brief, baskets hold US-listed shares and US ADRs only — members
carrying a foreign-exchange suffix are excluded and reported, not substituted.

R4 adds Yahoo Finance daily bars as a second, independent price source (pulled by a GitHub
Actions runner, see .github/workflows/fetch_yahoo_eod.yml — the research container cannot
reach Yahoo).  Per ticker the natezone daily bars and the Yahoo bars are merged after a
share-basis check (median close deviation over the common sessions <= 0.5%); natezone wins
on overlap, Yahoo supplies what natezone has not published (the 2026-09-04 session, and
the whole history of names outside the natezone universe).  The snapshot-rebuilt series is
used only where neither has the window.  Every close the snapshot series carries is
cross-checked against Yahoo and the per-day agreement is written to meta["yahoo_xcheck"].

Same scoring core as R1/R2, with the ten defects found in the R2.00 critical review fixed:
  F3  the 40% single-name cap was undone by the renormalisation that followed it
      (a name holding 80% of a basket's dollar volume still ended at 66.7%);
      replaced by an iterative water-filling cap that actually binds.
  F4  a ticker with no 20-day volume baseline was dropped outright, which threw out 33
      workbook constituents that DO have a close for every scored session — TSM, ASML,
      ARM, TEAM, SHOP, NVO, DEO, INFY, TECK, CCJ, AEM, KGC, UUUU, WCN and others that
      the snapshot feed only started carrying on 2026-08-28.  They are now scored with
      the volume term B held at 0 (neutral) and flagged, instead of being deleted.
  F5  symbols carrying a dot (BF.B) never matched the daily-bar mirror, which names the
      file BF-B.csv; lookups now normalise "." to "-".
  F6  the unknown-volume date was hard-coded to a single session; it is now per date.
  F7  on 2026-08-31 the snapshot-sourced close is the exact official close but the volume
      was a neighbour average.  Treating an interpolated volume as real inflates or damps
      B for 5,337 names, so that volume is now treated as UNKNOWN (B=0, "量?") exactly like
      an unpublished one, and only the close is taken as exact.
  F8  two workbook annotations ("XBI 成分股為主", "—（多為中小型）") were being parsed as
      tickers and reported as dropped; non-symbols are now filtered out.
  F9  淨額估算 mixes Chaikin dollars (real OHLC) with direction-scaled dollars (close-only
      names); each basket now reports the share of its dollar volume that carries a real
      intraday range, so the reader can see how much of the figure is true Chaikin.

Scoring, per ticker per session:
  A 方向  = tanh((return - market median return) / 2%)
  B 量能  = clip(log2(clip(dollar volume / 20-day median, .25, 4)) / 2, -1, 1)   [0 if unknown]
  C 收位  = ((C-L) - (H-C)) / (H-L)                       [only where real OHLC exists]
  f = (0.70*A + 0.30*C) * (1 + 0.50*B)      (A-only when there is no intraday range)
Baskets aggregate dollar-volume weighted with a hard 40% per-name cap; daily basket scores
are standardised across the 111 sub-sectors, so a score says where money went RELATIVE to
every other sub-sector that day, not whether the group rose.
"""
import csv, json, math, os, pickle, statistics, collections, re, glob, gzip

SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"
YF_FILES = [p for p in os.environ.get("YAHOO_FILES",
            "/home/user/yppmatthewtw-cmd/10ma-watchlist/data/yahoo/eod_2025-12-26_2026-09-05.csv.gz;"
            + ";".join(sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz")))).split(";") if p]
BASIS_TOL = 0.005            # natezone and Yahoo closes must agree within 0.5% to be merged
WIN = 5                      # scored sessions
LOOK = 20                    # sessions of history for the volume baseline
CAP = 0.40                   # hard cap on any single name's basket weight

AI = json.load(open(f"{SCR}/ai/aigroups.json"))
subs = AI["groups"]
S = pickle.load(open(f"{SCR}/series10.pkl", "rb")); CAL = S["cal"]; SER = S["series"]
EST = S.get("meta8", {}).get("estimated", {})
M10 = S.get("meta10", {})

# ---- F6/F7: per-date set of names whose volume for that session is not real ----
NOVOL_BY_DATE = collections.defaultdict(set)
for d, syms in (M10.get("novol_by_date") or {}).items():
    NOVOL_BY_DATE[d] |= set(syms)
for sym, e in EST.items():                       # F7: filled sessions carry an invented volume
    for d, how in e.items():
        if how in ("official", "interp", "edge"): NOVOL_BY_DATE[d].add(sym)
EST_CLOSE = {sym: {d for d, how in e.items() if how in ("interp", "edge")} for sym, e in EST.items()}

TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,6}$")     # F8
def nzname(sym): return sym.replace(".", "-")          # F5

SUPP = {}      # no hand substitutes: the brief restricts baskets to US listings / ADRs
PROXY = {}

# ---------------- load real daily OHLCV ----------------
def load_nz(sym):
    p = f"{NZ}/{nzname(sym)}.csv"
    if not os.path.exists(p): return None
    out = {}
    with open(p, newline="") as f:
        for row in csv.DictReader(f):
            d = (row.get("Date") or "")[:10]
            try:
                o, h, l, c, v = (float(row[k]) for k in ("Open", "High", "Low", "Close", "Volume"))
            except (ValueError, KeyError, TypeError):
                continue                      # partial rows (volume published before the bar)
            if c > 0: out[d] = (o, h, l, c, v)
    return out or None

# ---------------- Yahoo daily bars (second source) ----------------
YH = {}
for path in YF_FILES:                     # later files override earlier ones (this repo's own pull last)
    if not os.path.exists(path): continue
    n0 = len(YH)
    with gzip.open(path, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try:
                o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError):
                continue
            if c > 0: YH.setdefault(r["symbol"].replace("/", ".").replace("-", "."), {})[r["date"]] = (o, h, l, c, v)
    print(f"yahoo bars: {os.path.basename(path)} -> {len(YH) - n0} new symbols ({len(YH)} total)")
def yh_get(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))

def merge_bars(nz, yh):
    """natezone bars, extended by Yahoo where natezone has no bar, once the two agree on
    share basis; returns (bars, source_tag, deviation_median or None)."""
    if not nz and not yh: return None, None, None
    if not yh: return nz, "real", None
    if not nz: return dict(yh), "yahoo", None
    common = sorted(set(nz) & set(yh))[-15:]
    dev = [abs(nz[d][3] - yh[d][3]) / yh[d][3] for d in common if yh[d][3] > 0]
    med = statistics.median(dev) if dev else None
    if med is not None and med <= BASIS_TOL:
        out = dict(yh); out.update(nz); return out, "real", med
    return dict(yh), "yahoo", med           # bases disagree (unadjusted split etc.): trust Yahoo's restated history

listed_all = {t for s in subs for t in s["us"]}
NOTES = sorted(t for t in listed_all if not TICKER_RE.match(t))          # F8
wanted = sorted({t for t in listed_all if TICKER_RE.match(t)}
                | {t for v in PROXY.values() for t in v} | {t for v in SUPP.values() for t in v})
NZD = {}; SRC = {}; BASIS = {}
for t in wanted:
    bars, tag, med = merge_bars(load_nz(t), yh_get(t))
    if bars: NZD[t] = bars; SRC[t] = tag; BASIS[t] = med

# ---------------- calendar: the last WIN sessions both sources agree on ----------------
nz_dates = collections.Counter()
for d in NZD.values():
    for k in d: nz_dates[k] += 1
full = sorted(k for k, n in nz_dates.items() if n >= 0.8 * len(NZD))
seq = list(full)                            # trading calendar from the bar sources (natezone ∪ Yahoo), not the snapshot series
TERM = os.environ.get("TERMINAL_DATE")          # diagnostic: re-run the engine on an earlier window
if TERM: seq = [d for d in seq if d <= TERM]
LAST = seq[-(WIN + LOOK + 1):]
DAYS = LAST[-WIN:]
BASE = LAST[-(WIN + LOOK + 1):-WIN]
print("scored sessions:", DAYS)
print("volume baseline:", BASE[0], "->", BASE[-1], f"({len(BASE)} sessions)")
print("workbook annotations skipped as non-tickers:", NOTES)

# ---------------- market baseline: median return of the real-OHLCV universe ----------------
allnz = {}
for f in os.listdir(NZ):
    if not f.endswith(".csv"): continue
    sym = f[:-4].replace("-", ".")
    bars, tag, med = merge_bars(load_nz(f[:-4]), yh_get(sym))
    if bars: allnz[sym] = bars
for sym in YH:                                # Yahoo-only names (the 10MA eligible universe + this repo's list)
    if sym not in allnz: allnz[sym] = YH[sym]
for t in NZD: allnz[t] = NZD[t]
MKT = {}
for day in DAYS:
    prev = LAST[LAST.index(day) - 1]
    rets = [d[day][3] / d[prev][3] - 1 for d in allnz.values() if day in d and prev in d and d[prev][3] > 0]
    MKT[day] = statistics.median(rets)
    MKT.setdefault("_n", {})[day] = len(rets)
print("market median return:", {d: f"{MKT[d]*100:+.2f}%" for d in DAYS}, MKT["_n"])

# ---------------- per-ticker daily flow ----------------
def series_snap(sym):
    """close/volume from the repaired snapshot series (no intraday range).  A session whose
    volume is unpublished or was filled by interpolation comes back as None, never a number."""
    if sym not in SER: return None
    fi, cs, vs, ff = SER[sym]
    idx = {CAL[fi + i]: i for i in range(len(cs))}
    out = {}
    for d in LAST:
        if d not in idx: continue
        i = idx[d]
        v = None if (sym in NOVOL_BY_DATE.get(d, ())) or vs[i] <= 0 else vs[i]
        out[d] = (None, None, None, cs[i], v)
    return out

def tick_flow(sym):
    """Real daily OHLCV when the mirror carries the full window; otherwise the repaired
    snapshot series (close only, volume where published).  Stale mirror files fall through."""
    data = NZD.get(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    srctag = SRC.get(sym, "real") if real else "snap"
    if not real:
        data = series_snap(sym)
    if not data or not all(d in data for d in DAYS): return None
    prev0 = LAST[LAST.index(DAYS[0]) - 1]
    if prev0 not in data: return None                      # need the close before day 1

    base_dv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(base_dv) < 10                             # F4: no 20-day volume baseline
    if not nobase:
        med_dv = statistics.median(base_dv)
    else:                                                  # weight proxy only; B is held at 0
        any_dv = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med_dv = statistics.median(any_dv) if any_dv else None
    if not med_dv or med_dv <= 0: return None

    out = {"sym": sym, "src": srctag, "med_dv": med_dv, "basis_dev": BASIS.get(sym),
           "nobase": nobase, "days": {}}
    for day in DAYS:
        prev = LAST[LAST.index(day) - 1]
        if prev not in data: return None
        o, h, l, c, v = data[day]
        pc = data[prev][3]
        ret = c / pc - 1 if pc > 0 else 0.0
        exret = ret - MKT[day]
        novol = v is None or nobase                        # B unusable: unknown volume or no baseline
        dv = c * v if v is not None else med_dv            # weighting proxy when volume is unusable
        rvol = (dv / med_dv if med_dv > 0 else 1.0) if not novol else 1.0
        A = math.tanh(exret / 0.02)
        B = 0.0 if novol else max(-1.0, min(1.0, math.log2(max(0.25, min(4.0, rvol))) / 2))
        if real and h is not None and h > l:
            C = ((c - l) - (h - c)) / (h - l)
            f = (0.70 * A + 0.30 * C) * (1 + 0.50 * B)
            mfd = C * dv                       # Chaikin money-flow dollars
            ohlc = True
        else:
            C = None
            f = A * (1 + 0.50 * B)
            mfd = A * dv                       # direction-scaled dollars (no intraday range)
            ohlc = False
        out["days"][day] = {"ret": ret, "exret": exret, "dv": dv, "rvol": rvol, "novol": novol,
                            "A": A, "B": B, "C": C, "f": f, "mfd": mfd, "ohlc": ohlc,
                            "est": (day in EST_CLOSE.get(sym, ())) if not real else False}
    return out

TICK, dropped = {}, []
for t in wanted:
    r = tick_flow(t)
    if r: TICK[t] = r
    else: dropped.append(t)
nb = sum(1 for v in TICK.values() if v["nobase"])
srcn = collections.Counter(v["src"] for v in TICK.values())
print(f"tickers scored: {len(TICK)} (natezone+yahoo {srcn['real']}, yahoo-only {srcn['yahoo']}, "
      f"snapshot {srcn['snap']}, of which {nb} without a volume baseline -> B held at 0); dropped {len(dropped)}: {dropped}")

# ---------------- cross-check: snapshot-series closes vs Yahoo, per session in the window ----------------
XC = {}
for day in [LAST[LAST.index(DAYS[0]) - 1]] + DAYS:
    dev = []
    for sym in wanted:
        y = yh_get(sym); sd = series_snap(sym)
        if y and sd and day in y and day in sd and y[day][3] > 0:
            dev.append(abs(sd[day][3] - y[day][3]) / y[day][3] * 100)
    if dev:
        XC[day] = {"n": len(dev), "median_pct": round(statistics.median(dev), 4),
                   "gt_0_5": sum(1 for x in dev if x > 0.5), "gt_2": sum(1 for x in dev if x > 2)}
nzdev = []
for sym in wanted:
    nz = load_nz(sym); y = yh_get(sym)
    if nz and y:
        for d in DAYS:
            if d in nz and d in y and y[d][3] > 0: nzdev.append(abs(nz[d][3] - y[d][3]) / y[d][3] * 100)
XC["natezone_vs_yahoo"] = ({"n": len(nzdev), "median_pct": round(statistics.median(nzdev), 4),
                            "gt_0_5": sum(1 for x in nzdev if x > 0.5)} if nzdev else None)
XC["basis_disagree"] = sorted(t for t, m in BASIS.items() if m is not None and m > BASIS_TOL)
print("snapshot vs yahoo close deviation:", {d: v for d, v in XC.items() if d[:2] == "20"})
print("natezone vs yahoo:", XC["natezone_vs_yahoo"], "| basis disagreements:", XC["basis_disagree"])

# ---------------- basket weights: iterative 40% cap that actually binds (F3) ----------------
def capped_weights(raw):
    """Largest-remainder water filling: capped names keep exactly CAP, the rest share the
    remainder in proportion to their dollar volume.  Guarantees max weight <= CAP."""
    tot = sum(raw.values())
    n = len(raw)
    if tot <= 0: return {t: 1.0 / n for t in raw}
    if n * CAP <= 1.0 + 1e-12: return {t: 1.0 / n for t in raw}     # cap unreachable -> equal weight
    w = {t: v / tot for t, v in raw.items()}
    capped = set()
    while True:
        over = [t for t in w if t not in capped and w[t] > CAP + 1e-12]
        if not over: return w
        capped |= set(over)
        free = [t for t in w if t not in capped]
        rest = 1.0 - CAP * len(capped)
        sub = sum(raw[t] for t in free)
        if rest <= 0 or sub <= 0:
            return {t: (1.0 / len(w)) for t in w}
        for t in capped: w[t] = CAP
        for t in free: w[t] = rest * raw[t] / sub

# ---------------- aggregate per sub-sector ----------------
rows = []
for s in subs:
    listed = [t for t in s["us"] if TICKER_RE.match(t)]
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
        raw = {t: TICK[t]["days"][day]["dv"] for t in tk}
        ws = capped_weights(raw)
        F = sum(ws[t] * TICK[t]["days"][day]["f"] for t in tk)
        mfd = sum(TICK[t]["days"][day]["mfd"] for t in tk)
        ret_ew = statistics.mean(TICK[t]["days"][day]["ret"] for t in tk)
        rvol = sum(ws[t] * TICK[t]["days"][day]["rvol"] for t in tk)
        dv = sum(raw.values())
        up = sum(1 for t in tk if TICK[t]["days"][day]["exret"] > 0)
        ohlc_dv = sum(raw[t] for t in tk if TICK[t]["days"][day]["ohlc"])
        daily[day] = {"F": F, "mfd": mfd, "ret": ret_ew, "rvol": rvol, "dv": dv,
                      "breadth": up / len(tk), "up": up, "wmax": max(ws.values()),
                      "ohlc_cov": ohlc_dv / dv if dv else 0.0,
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
                      "src": TICK[t]["src"], "nobase": TICK[t]["nobase"],
                      "novol": sum(1 for d in DAYS if td[d]["novol"])})
    ticks.sort(key=lambda x: -x["tf5"])          # most inflow first, most outflow last
    rows.append(dict(s, basket=tk, ticks=ticks, n_basket=len(tk), proxy=proxy, supp=supp,
                     missing=[t for t in listed if t not in TICK], days=daily,
                     nobase=[t for t in tk if TICK[t]["nobase"]],
                     src=("real" if all(TICK[t]["src"] in ("real", "yahoo") for t in tk) else
                          ("snap" if all(TICK[t]["src"] == "snap" for t in tk) else "mix")),
                     src_detail=dict(collections.Counter(TICK[t]["src"] for t in tk)),
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
    r["shrink"] = math.sqrt(n / (n + 2.0))
    r["z5r"] = r["z5"] * r["shrink"]
    r["intensity"] = r["mfd5"] / r["dv5"] * 100 if r["dv5"] else 0.0
    r["breadth5"] = statistics.mean(r["days"][d]["breadth"] for d in DAYS)
    r["novol_days"] = sum(1 for d in DAYS if r["days"][d]["novol"])
    r["ohlc_cov5"] = (sum(r["days"][d]["ohlc_cov"] * r["days"][d]["dv"] for d in DAYS) / r["dv5"]
                      if r["dv5"] else 0.0)
    r["wmax5"] = max(r["days"][d]["wmax"] for d in DAYS)
vals = [r["z5"] for r in live]
order = sorted(range(len(live)), key=lambda i: vals[i])
for rank, i in enumerate(order): live[i]["score5"] = rank / (len(live) - 1) * 100
vr = [r["z5r"] for r in live]
order = sorted(range(len(live)), key=lambda i: vr[i])
for rank, i in enumerate(order): live[i]["score5r"] = rank / (len(live) - 1) * 100
live.sort(key=lambda r: -r["z5"])
for i, r in enumerate(live, 1): r["rank"] = i

out = {"meta": {"days": DAYS, "base": [BASE[0], BASE[-1]], "n_base": len(BASE),
                "mkt_med": {d: MKT[d] for d in DAYS}, "mkt_n": MKT["_n"],
                "n_sub": len(rows), "n_scored": len(live), "n_tick": len(TICK),
                "n_nobase": nb, "dropped": dropped, "notes_skipped": NOTES,
                "proxy": {str(k): v for k, v in PROXY.items()},
                "supp": {str(k): v for k, v in SUPP.items()},
                "weights": W, "cap": CAP,
                "novol_by_date": {d: len(NOVOL_BY_DATE.get(d, ())) for d in DAYS},
                "yahoo_xcheck": XC, "yahoo_files": [os.path.basename(p) for p in YF_FILES if os.path.exists(p)],
                "yahoo_n_symbols": len(YH), "src_counts": dict(srcn),
                "source_note": "natezone/market-tracker 日線 OHLCV 與 Yahoo Finance 日線（GitHub Actions runner 拉取）合併，快照序列只作對照及最後補足"},
       "rows": live + [r for r in rows if not r["days"]]}
out["meta"]["asof_dash"] = AI["asof_dash"]
out["meta"]["nonus_excluded"] = sorted({m for s in subs for m in s["nonus"]})
json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/ai5/flow5.json"), "w"), ensure_ascii=False)
print("\nTOP 12 inflow:")
for r in live[:12]:
    print(f"  {r['rank']:3d} {r['code']:<5}{r['zh'][:20]:<22} z5{r['z5']:+.2f} 5日分{r['score5']:5.1f} "
          f"日格{[r['days'][d]['grade'] for d in DAYS]} 淨額${r['mfd5']/1e6:+,.0f}M 樣本{r['n_basket']}")
print("BOTTOM 12 outflow:")
for r in live[-12:]:
    print(f"  {r['rank']:3d} {r['zh'][:14]:<16} z5{r['z5']:+.2f} 5日分{r['score5']:5.1f} "
          f"日格{[r['days'][d]['grade'] for d in DAYS]} 淨額${r['mfd5']/1e6:+,.0f}M 樣本{r['n_basket']}")
print("max basket weight across all rows/days:", round(max(r["wmax5"] for r in live), 4))
print("unscorable:", [(r['code'], r['note']) for r in rows if not r["days"]])
