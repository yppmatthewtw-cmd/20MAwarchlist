#!/usr/bin/env python3
"""Independent recomputation of flow3.json from the raw sources (natezone CSVs + series10.pkl).
Re-implements the documented formulas without importing flow3.py; reports PROBLEMS."""
import csv, json, math, os, pickle, statistics, collections, re, gzip, glob
SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"
F = json.load(open(f"{SCR}/ai5/flow5.json")); M = F["meta"]; DAYS = M["days"]; live = [r for r in F["rows"] if r.get("days")]
S = pickle.load(open(f"{SCR}/series10.pkl", "rb")); CAL = S["cal"]; SER = S["series"]
EST = S["meta8"]["estimated"]; M10 = S["meta10"]
P = []
def bad(m): P.append(m)

# ---- Yahoo bars: own loader + own merge rule ----
YFILES = ["/home/user/yppmatthewtw-cmd/10ma-watchlist/data/yahoo/eod_2025-12-26_2026-09-05.csv.gz"] + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz"))
YH = {}
for p in YFILES:
    with gzip.open(p, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try: o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError): continue
            if c > 0: YH.setdefault(r["symbol"].replace("/", ".").replace("-", "."), {})[r["date"]] = (o, h, l, c, v)
def yh(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))
def nzraw(sym):
    p = f"{NZ}/{sym.replace('.', '-')}.csv"
    if not os.path.exists(p): return None
    out = {}
    for row in csv.DictReader(open(p)):
        try: o, h, l, c, v = (float(row[k]) for k in ("Open", "High", "Low", "Close", "Volume"))
        except (ValueError, KeyError, TypeError): continue
        if c > 0: out[row["Date"][:10]] = (o, h, l, c, v)
    return out or None
def merged(sym):
    a, b = nzraw(sym), yh(sym)
    if not a and not b: return None, None
    if not b: return a, "real"
    if not a: return dict(b), "yahoo"
    com = sorted(set(a) & set(b))[-15:]
    dev = [abs(a[d][3] - b[d][3]) / b[d][3] for d in com if b[d][3] > 0]
    if dev and statistics.median(dev) <= 0.005:
        m = dict(b); m.update(a); return m, "real"
    return dict(b), "yahoo"
# calendar around the window: sessions covered by >=80% of the scored names' merged bars
cov = collections.Counter()
NB = {}
for r in live:
    for t in r["basket"]:
        if t not in NB:
            NB[t] = merged(t)[0]
            for d in (NB[t] or {}): cov[d] += 1
full = sorted(d for d, n in cov.items() if n >= 0.8 * len(NB))
if DAYS[-1] not in full or DAYS[0] not in full: bad("window days not in bar calendar")
i1 = full.index(DAYS[-1]); LAST = full[i1 - 25:i1 + 1]
BASE = LAST[:21]; PREV = {d: LAST[LAST.index(d) - 1] for d in DAYS}
if [BASE[0], BASE[-1]] != M["base"]: bad(f"base window {BASE[0]}..{BASE[-1]} != {M['base']}")
if M["n_base"] != 21: bad("n_base")

def nz(sym):
    p = f"{NZ}/{sym.replace('.', '-')}.csv"
    if not os.path.exists(p): return None
    out = {}
    for row in csv.DictReader(open(p)):
        try: o, h, l, c, v = (float(row[k]) for k in ("Open", "High", "Low", "Close", "Volume"))
        except (ValueError, KeyError, TypeError): continue
        if c > 0: out[row["Date"][:10]] = (o, h, l, c, v)
    return out or None

# market median from every natezone file
allret = {d: [] for d in DAYS}
UNI = {}
for f in os.listdir(NZ):
    if f.endswith(".csv"): UNI[f[:-4].replace("-", ".")] = merged(f[:-4].replace("-", "."))[0]
for sym in YH:
    if sym not in UNI: UNI[sym] = YH[sym]
for t in NB: UNI[t] = NB[t]
for d in UNI.values():
    if not d: continue
    for day in DAYS:
        if day in d and PREV[day] in d and d[PREV[day]][3] > 0: allret[day].append(d[day][3] / d[PREV[day]][3] - 1)
MKT = {d: statistics.median(allret[d]) for d in DAYS}
for d in DAYS:
    if abs(MKT[d] - M["mkt_med"][d]) > 1e-12: bad(f"mkt median {d}: {MKT[d]} vs {M['mkt_med'][d]}")
    if len(allret[d]) != M["mkt_n"][d]: bad(f"mkt n {d}")

NOVOL = collections.defaultdict(set)
for d, syms in M10["novol_by_date"].items(): NOVOL[d] |= set(syms)
for sym, e in EST.items():
    for d, how in e.items():
        if how in ("official", "interp", "edge"): NOVOL[d].add(sym)

def snapdata(sym):
    if sym not in SER: return None
    fi, cs, vs, ff = SER[sym]; idx = {CAL[fi + i]: i for i in range(len(cs))}
    out = {}
    for d in LAST:
        if d in idx:
            v = None if sym in NOVOL[d] or vs[idx[d]] <= 0 else vs[idx[d]]
            out[d] = (None, None, None, cs[idx[d]], v)
    return out

def tick(sym):
    data, tag = merged(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    if not real:
        bad(f"{sym} fell back to snapshot"); data = snapdata(sym)
    if not data or not all(d in data for d in DAYS) or PREV[DAYS[0]] not in data: return None
    bdv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(bdv) < 10
    if not nobase: med = statistics.median(bdv)
    else:
        a = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med = statistics.median(a) if a else None
    if not med: return None
    out = {"real": real, "nobase": nobase, "days": {}}
    for d in DAYS:
        o, h, l, c, v = data[d]; pc = data[PREV[d]][3]
        ret = c / pc - 1; ex = ret - MKT[d]
        novol = v is None or nobase
        dv = c * v if v is not None else med
        rv = 1.0 if novol else dv / med
        A = math.tanh(ex / 0.02)
        Bv = 0.0 if novol else max(-1, min(1, math.log2(max(0.25, min(4.0, rv))) / 2))
        if real and h is not None and h > l:
            C = ((c - l) - (h - c)) / (h - l); f = (0.7 * A + 0.3 * C) * (1 + 0.5 * Bv); mfd = C * dv; ohlc = True
        else:
            f = A * (1 + 0.5 * Bv); mfd = A * dv; ohlc = False
        out["days"][d] = dict(ret=ret, ex=ex, dv=dv, rv=rv, novol=novol, A=A, B=Bv, f=f, mfd=mfd, ohlc=ohlc)
    return out

def weights(raw, cap=0.40):
    n = len(raw); tot = sum(raw.values())
    if n * cap <= 1 + 1e-12 or tot <= 0: return {t: 1 / n for t in raw}
    w = {t: v / tot for t, v in raw.items()}; capped = set()
    while True:
        over = [t for t in w if t not in capped and w[t] > cap + 1e-12]
        if not over: return w
        capped |= set(over); free = [t for t in w if t not in capped]
        rest = 1 - cap * len(capped); sub = sum(raw[t] for t in free)
        for t in capped: w[t] = cap
        for t in free: w[t] = rest * raw[t] / sub

TK = {}
Fday = {d: {} for d in DAYS}
TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,6}$")
for r in live:
    for t in r["basket"]:
        if t not in TK:
            TK[t] = tick(t)
            if TK[t] is None: bad(f"{t} in basket but unscorable")
    if any(t in M["dropped"] for t in r["basket"]): bad(f"{r['code']} contains a dropped ticker")
    if r["n_basket"] != len(r["basket"]): bad(f"{r['code']} n_basket")
    nb = [t for t in r["basket"] if TK[t] and TK[t]["nobase"]]
    if sorted(nb) != sorted(r.get("nobase") or []): bad(f"{r['code']} nobase list {nb} vs {r.get('nobase')}")
    for d in DAYS:
        raw = {t: TK[t]["days"][d]["dv"] for t in r["basket"]}
        w = weights(raw)
        if len(raw) >= 3 and max(w.values()) > 0.4 + 1e-9: bad(f"{r['code']} {d} weight cap broken {max(w.values())}")
        if abs(sum(w.values()) - 1) > 1e-9: bad(f"{r['code']} {d} weights sum")
        Fv = sum(w[t] * TK[t]["days"][d]["f"] for t in raw)
        x = r["days"][d]
        if abs(Fv - x["F"]) > 1e-9: bad(f"{r['code']} {d} F {Fv} vs {x['F']}")
        if abs(sum(TK[t]["days"][d]["mfd"] for t in raw) - x["mfd"]) > 1e-3: bad(f"{r['code']} {d} mfd")
        if abs(sum(raw.values()) - x["dv"]) > 1e-3: bad(f"{r['code']} {d} dv")
        if sum(1 for t in raw if TK[t]["days"][d]["novol"]) != x["novol"]: bad(f"{r['code']} {d} novol count")
        if abs(max(w.values()) - x["wmax"]) > 1e-9: bad(f"{r['code']} {d} wmax")
        cov = sum(raw[t] for t in raw if TK[t]["days"][d]["ohlc"]) / sum(raw.values())
        if abs(cov - x["ohlc_cov"]) > 1e-9: bad(f"{r['code']} {d} ohlc_cov")
        up = sum(1 for t in raw if TK[t]["days"][d]["ex"] > 0)
        if up != x["up"] or abs(up / len(raw) - x["breadth"]) > 1e-9: bad(f"{r['code']} {d} breadth")
        Fday[d][r["zh"]] = Fv
        for t in raw:
            if TK[t]["days"][d]["novol"] and abs(TK[t]["days"][d]["B"]) > 0: bad(f"{t} {d} B nonzero while novol")

# cross-sectional z / percentile / grades / composites
W = M["weights"]; Z = {}
for d in DAYS:
    vals = [Fday[d][r["zh"]] for r in live]; mu = statistics.mean(vals); sd = statistics.pstdev(vals)
    order = sorted(live, key=lambda r: Fday[d][r["zh"]])
    for rank, r in enumerate(order):
        z = (Fday[d][r["zh"]] - mu) / sd; x = r["days"][d]
        if abs(z - x["z"]) > 1e-9: bad(f"{r['code']} {d} z")
        if abs(rank / (len(live) - 1) * 100 - x["score"]) > 1e-9: bad(f"{r['code']} {d} score")
        g = 3 if z >= 1.5 else 2 if z >= .75 else 1 if z >= .25 else 0 if z > -.25 else -1 if z > -.75 else -2 if z > -1.5 else -3
        if g != x["grade"]: bad(f"{r['code']} {d} grade")
        Z.setdefault(r["zh"], []).append(z)
z5 = {}
for r in live:
    zs = Z[r["zh"]]; v = sum(w * z for w, z in zip(W, zs)) / sum(W); z5[r["zh"]] = v
    if abs(v - r["z5"]) > 1e-9: bad(f"{r['code']} z5")
    n = r["n_basket"]
    if abs(v * math.sqrt(n / (n + 2)) - r["z5r"]) > 1e-9: bad(f"{r['code']} z5r")
    mfd5 = sum(r["days"][d]["mfd"] for d in DAYS); dv5 = sum(r["days"][d]["dv"] for d in DAYS)
    if abs(mfd5 / dv5 * 100 - r["intensity"]) > 1e-6: bad(f"{r['code']} intensity")
    xb = 2; yb = sum(zs) / 5
    slope = sum((i - xb) * (z - yb) for i, z in enumerate(zs)) / 10
    if abs(slope - r["slope"]) > 1e-9: bad(f"{r['code']} slope")
    if abs(statistics.mean(r["days"][d]["breadth"] for d in DAYS) - r["breadth5"]) > 1e-9: bad(f"{r['code']} breadth5")
    if sum(1 for d in DAYS if r["days"][d]["grade"] >= 1) != r["pos"] or sum(1 for d in DAYS if r["days"][d]["grade"] <= -1) != r["neg"]: bad(f"{r['code']} pos/neg")
order = sorted(live, key=lambda r: z5[r["zh"]])
for rank, r in enumerate(order):
    if abs(rank / (len(live) - 1) * 100 - r["score5"]) > 1e-9: bad(f"{r['code']} score5")
ranks = [r["rank"] for r in sorted(live, key=lambda r: -z5[r["zh"]])]
if ranks != list(range(1, len(live) + 1)): bad("rank order")
if len(F["rows"]) != 41 or M["n_scored"] != len(live): bad("row counts")
for r in F["rows"]:
    if not r.get("days") and r["us"] and r["note"] != "美股成分股數據不足": bad(f"{r['code']} note")
    if not r.get("days") and not r["us"] and r["note"] != "成分股全部非美股上市／無 US ADR": bad(f"{r['code']} note")
# per-ticker column: tf5 recomputed, sorted desc
for r in live:
    tf = {t: sum(w * TK[t]["days"][d]["f"] for w, d in zip(W, DAYS)) / sum(W) for t in r["basket"]}
    syms = [x["sym"] for x in r["ticks"]]
    if sorted(syms) != sorted(r["basket"]): bad(f"{r['code']} ticks membership")
    if syms != sorted(syms, key=lambda t: -tf[t]) and any(abs(tf[a]-tf[b])>1e-6 for a,b in zip(syms,syms[1:]) if tf[a]<tf[b]): bad(f"{r['code']} ticks order")
    for x in r["ticks"]:
        if abs(x["tf5"] - tf[x["sym"]]) > 6e-5: bad(f"{r['code']} {x['sym']} tf5")
        if x["nobase"] != TK[x["sym"]]["nobase"]: bad(f"{x['sym']} tick nobase")
if M["n_tick"] != len(TK): bad(f"n_tick {M['n_tick']} vs {len(TK)}")
if M["n_nobase"] != sum(1 for t in TK.values() if t and t["nobase"]): bad("n_nobase")
# every dropped ticker really has no bars in the window
for t in M["dropped"]:
    m, _ = merged(t)
    if m and all(d in m for d in DAYS) and PREV[DAYS[0]] in m: bad(f"dropped {t} has full bars")
# cross-check stats: recompute the natezone-vs-yahoo figure
nzd = []
for t in sorted({t for r in live for t in r["basket"]} | set(M["dropped"])):
    if True:
        a, b = nzraw(t), yh(t)
        if a and b:
            for d in DAYS:
                if d in a and d in b and b[d][3] > 0: nzd.append(abs(a[d][3] - b[d][3]) / b[d][3] * 100)
xn = M["yahoo_xcheck"]["natezone_vs_yahoo"]
if xn and (xn["n"] != len(nzd) or abs(xn["median_pct"] - round(statistics.median(nzd), 4)) > 1e-9): bad(f"natezone_vs_yahoo stats {xn} vs n={len(nzd)}")
if M["notes_skipped"]: bad("notes skipped")
# every dropped ticker really has no usable data
# (dropped tickers are checked against the merged bars above)
# terminal date is the newest session with a close in either source
print("verified", len(live), "rows,", len(TK), "tickers, window", DAYS)
print("PROBLEMS:", len(P))
for m in P[:30]: print("  -", m)
