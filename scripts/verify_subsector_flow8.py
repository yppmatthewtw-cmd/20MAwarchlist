#!/usr/bin/env python3
"""Independent recomputation of flow3.json from the raw sources (natezone CSVs + series10.pkl).
Re-implements the documented formulas without importing flow3.py; reports PROBLEMS."""
import csv, json, math, os, pickle, statistics, collections, re, gzip, glob
SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"
F = json.load(open(f"{SCR}/sub8/flow8.json")); M = F["meta"]; DAYS = M["days"]; live = [r for r in F["rows"] if r.get("days")]
S = pickle.load(open(f"{SCR}/series10.pkl", "rb")); CAL = S["cal"]; SER = S["series"]
EST = S["meta8"]["estimated"]; M10 = S["meta10"]
P = []
def bad(m): P.append(m)

# ---- Yahoo bars: own loader + own merge rule ----
YFILES = (["/home/user/yppmatthewtw-cmd/10ma-watchlist/data/yahoo/eod_2025-12-26_2026-09-05.csv.gz"]
          + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz"))
          + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/broad_*.csv.gz")))
YH = {}
for p in YFILES:
    with gzip.open(p, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try: o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError): continue
            if c > 0: YH.setdefault(r["symbol"].replace("/", ".").replace("-", "."), {})[r["date"]] = (o, h, l, c, v)
TAILP = "/home/user/20MAwarchlist/data/yahoo/tail.csv.gz"
SOFTVOL = set(); TAILN = collections.Counter()
if os.path.exists(TAILP):
    with gzip.open(TAILP, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try: o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError): continue
            if c <= 0: continue
            sym = r["symbol"].replace("/", ".").replace("-", ".")
            if r["date"] in YH.get(sym, {}): continue
            YH.setdefault(sym, {})[r["date"]] = (o, h, l, c, v)
            TAILN[r["date"]] += 1
            if r.get("route") != "hist5d": SOFTVOL.add((sym, r["date"]))
print(f"tail bars merged: {dict(TAILN)}, soft-volume pairs {len(SOFTVOL)}")
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
SINCE = M.get("merge_since")
# C2 re-derived: a mirror session is "not settled" when its volumes are not vendor-rounded, or
# when the mirror is mid-repopulation and carries a fraction of its usual names.
_mv = collections.defaultdict(lambda: [0, 0])
for _f in os.listdir(NZ):
    if not _f.endswith(".csv"): continue
    for _d, _b in (nzraw(_f[:-4].replace("-", ".")) or {}).items():
        if _d < "2026-08-01" or not _b[4]: continue
        _mv[_d][0] += 1
        if abs(_b[4] - round(_b[4] / 100.0) * 100.0) < 1e-6: _mv[_d][1] += 1
_typ = statistics.median(sorted(t for t, _ in _mv.values())) if _mv else 0
NZ_UNSETTLED = {d for d, (tot, rnd) in _mv.items()
                if (tot >= 25 and rnd / tot < 0.5) or (_typ and tot < 0.5 * _typ)}
if sorted(NZ_UNSETTLED) != sorted(M.get("mirror_unsettled") or []):
    bad(f"mirror-unsettled {sorted(NZ_UNSETTLED)} != {M.get('mirror_unsettled')}")
print(f"mirror sessions published but not settled: {sorted(NZ_UNSETTLED) or 'none'} (typical {_typ:.0f})")

def merged(sym):
    a, b = nzraw(sym), yh(sym)
    if not a and not b: return None, None
    if not b: return a, "real"
    if not a: return dict(b), "yahoo"
    if SINCE and not any(d >= SINCE for d in a): return dict(b), "yahoo"
    com = sorted(set(a) & set(b))
    if SINCE:
        rec = [d for d in com if d >= SINCE]
        com = rec if rec else com
    com = com[-15:]
    dev = [abs(a[d][3] - b[d][3]) / b[d][3] for d in com if b[d][3] > 0]
    if dev and statistics.median(dev) <= 0.005:
        m = dict(b); m.update(a)
        for d in NZ_UNSETTLED:                  # C2: a settled second-source bar wins there
            if d in b: m[d] = b[d]
        return m, "real"
    return dict(b), "yahoo"
# calendar: each source measured against its OWN universe; a session counts when either is complete
NB = {}
nzc = collections.Counter(); yhc = collections.Counter(); nzu = yhu = 0
for r in live:
    for t in r["basket"]:
        if t in NB: continue
        NB[t] = merged(t)[0]
        a = nzraw(t); b = yh(t)
        if a:
            nzu += 1
            for d in a: nzc[d] += 1
        if b:
            yhu += 1
            for d in b: yhc[d] += 1
full = sorted({d for d in set(nzc) | set(yhc)
               if (nzu and nzc[d] >= 0.8 * nzu) or (yhu and yhc[d] >= 0.8 * yhu)})
print(f"calendar: mirror {nzu} names, yahoo {yhu} names, {len(full)} sessions")
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
NEEDD = set(DAYS) | {PREV[d] for d in DAYS}
PANEL = {s2: d for s2, d in UNI.items() if d and NEEDD <= set(d)}
for d in PANEL.values():
    for day in DAYS:
        if d[PREV[day]][3] > 0: allret[day].append(d[day][3] / d[PREV[day]][3] - 1)
if len({len(v) for v in allret.values()}) != 1: bad("market panel not balanced across days")
print(f"balanced market panel: {len(PANEL)} names")
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
    bsv = [data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(bdv) < 10
    if not nobase:
        med = statistics.median(bdv); medsv = statistics.median(bsv)   # R7: activity in SHARES
    else:
        a = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med = statistics.median(a) if a else None; medsv = None
    if not med: return None
    out = {"real": real, "nobase": nobase, "days": {}}
    for d in DAYS:
        o, h, l, c, v = data[d]; pc = data[PREV[d]][3]
        if (sym, d) in SOFTVOL and d not in (nzraw(sym) or {}): v = None   # tail-only bar
        ret = c / pc - 1; ex = ret - MKT[d]
        novol = v is None or nobase
        dv = c * v if v is not None else med
        rv = 1.0 if novol else (v / medsv if medsv else 1.0)
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
    if any(t in M["dropped"] for t in r["basket"]): bad(f"{r['zh']} contains a dropped ticker")
    if r["n_basket"] != len(r["basket"]): bad(f"{r['zh']} n_basket")
    nb = [t for t in r["basket"] if TK[t] and TK[t]["nobase"]]
    if sorted(nb) != sorted(r.get("nobase") or []): bad(f"{r['zh']} nobase list {nb} vs {r.get('nobase')}")
    for d in DAYS:
        raw = {t: TK[t]["days"][d]["dv"] for t in r["basket"]}
        w = weights(raw)
        if len(raw) >= 3 and max(w.values()) > 0.4 + 1e-9: bad(f"{r['zh']} {d} weight cap broken {max(w.values())}")
        if abs(sum(w.values()) - 1) > 1e-9: bad(f"{r['zh']} {d} weights sum")
        Fv = sum(w[t] * TK[t]["days"][d]["f"] for t in raw)
        x = r["days"][d]
        if abs(Fv - x["F"]) > 1e-9: bad(f"{r['zh']} {d} F {Fv} vs {x['F']}")
        if abs(sum(TK[t]["days"][d]["mfd"] for t in raw) - x["mfd"]) > 1e-3: bad(f"{r['zh']} {d} mfd")
        if abs(sum(raw.values()) - x["dv"]) > 1e-3: bad(f"{r['zh']} {d} dv")
        if sum(1 for t in raw if TK[t]["days"][d]["novol"]) != x["novol"]: bad(f"{r['zh']} {d} novol count")
        if abs(max(w.values()) - x["wmax"]) > 1e-9: bad(f"{r['zh']} {d} wmax")
        cov = sum(raw[t] for t in raw if TK[t]["days"][d]["ohlc"]) / sum(raw.values())
        if abs(cov - x["ohlc_cov"]) > 1e-9: bad(f"{r['zh']} {d} ohlc_cov")
        up = sum(1 for t in raw if TK[t]["days"][d]["ex"] > 0)
        if up != x["up"] or abs(up / len(raw) - x["breadth"]) > 1e-9: bad(f"{r['zh']} {d} breadth")
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
        if abs(z - x["z"]) > 1e-9: bad(f"{r['zh']} {d} z")
        if abs(rank / (len(live) - 1) * 100 - x["score"]) > 1e-9: bad(f"{r['zh']} {d} score")
        g = 3 if z >= 1.5 else 2 if z >= .75 else 1 if z >= .25 else 0 if z > -.25 else -1 if z > -.75 else -2 if z > -1.5 else -3
        if g != x["grade"]: bad(f"{r['zh']} {d} grade")
        Z.setdefault(r["zh"], []).append(z)
z5 = {}
for r in live:
    zs = Z[r["zh"]]; v = sum(w * z for w, z in zip(W, zs)) / sum(W); z5[r["zh"]] = v
    if abs(v - r["z5"]) > 1e-9: bad(f"{r['zh']} z5")
    n = r["n_basket"]
    if abs(v * math.sqrt(n / (n + 2)) - r["z5r"]) > 1e-9: bad(f"{r['zh']} z5r")
    mfd5 = sum(r["days"][d]["mfd"] for d in DAYS); dv5 = sum(r["days"][d]["dv"] for d in DAYS)
    if abs(mfd5 / dv5 * 100 - r["intensity"]) > 1e-6: bad(f"{r['zh']} intensity")
    xb = 2; yb = sum(zs) / 5
    slope = sum((i - xb) * (z - yb) for i, z in enumerate(zs)) / 10
    if abs(slope - r["slope"]) > 1e-9: bad(f"{r['zh']} slope")
    if abs(statistics.mean(r["days"][d]["breadth"] for d in DAYS) - r["breadth5"]) > 1e-9: bad(f"{r['zh']} breadth5")
    if sum(1 for d in DAYS if r["days"][d]["grade"] >= 1) != r["pos"] or sum(1 for d in DAYS if r["days"][d]["grade"] <= -1) != r["neg"]: bad(f"{r['zh']} pos/neg")
order = sorted(live, key=lambda r: z5[r["zh"]])
for rank, r in enumerate(order):
    if abs(rank / (len(live) - 1) * 100 - r["score5"]) > 1e-9: bad(f"{r['zh']} score5")
ranks = [r["rank"] for r in sorted(live, key=lambda r: -z5[r["zh"]])]
if ranks != list(range(1, len(live) + 1)): bad("rank order")
if len(live) != 111 or M["n_scored"] != 111: bad("not 111 live rows")
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
if set(M["notes_skipped"]) != {"XBI 成分股為主", "—（多為中小型）"}: bad("notes skipped")
# every dropped ticker really has no usable data
# (dropped tickers are checked against the merged bars above)
# terminal date is the newest session with a close in either source
print("verified", len(live), "rows,", len(TK), "tickers, window", DAYS)
stale_exp = sorted(t for t in {x for r in live for x in r["basket"]}
                   if nzraw(t) and SINCE and not any(d >= SINCE for d in nzraw(t)))
if stale_exp != sorted(M.get("stale_mirror", [])):
    bad(f"stale list {sorted(M.get('stale_mirror', []))} != {stale_exp}")
for t in stale_exp:
    if TK.get(t) and TK[t]["real"]:
        m, tag = merged(t)
        if tag != "yahoo": bad(f"{t} stale mirror but merged as {tag}")
print(f"stale-mirror names verified (Yahoo alone): {len(stale_exp)} {stale_exp}")
nzc = collections.Counter()
for t in sorted({x for r in live for x in r["basket"]}):
    for d in (nzraw(t) or {}): nzc[d] += 1
typ = statistics.median([nzc[d] for d in sorted(nzc)[-30:] if nzc[d]]) if nzc else 0
prov = [d for d in DAYS if nzc[d] < 0.5 * typ]      # coverage test only: kept as a diagnostic,
# superseded below by the settled-print test, which is what the engine now claims
print(f"mirror-coverage diagnostic (not the verdict): {prov or 'none'} (coverage {[nzc[d] for d in DAYS]}, typical {typ:.0f})")
# ---- R7 data-integrity claims, re-measured here ----
def rounded_share(day):
    """C1: measured on the bars actually scored, not on the mirror's copy."""
    tot = rnd = 0
    for t in NB:
        b = (NB[t] or {}).get(day)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    return rnd / tot if tot >= 25 else None
mine = sorted(d for d in DAYS if (rounded_share(d) or 1.0) < 0.5)
if mine != sorted(M.get("provisional_vol_days") or []):
    bad(f"provisional days {mine} != {M.get('provisional_vol_days')}")
for d in DAYS:
    sh = rounded_share(d)
    if sh is not None and abs(sh - M.get("settled_print_share", {}).get(d, -1)) > 0.002:
        bad(f"settled-print share {d}: {sh:.4f} vs {M.get('settled_print_share', {}).get(d)}")
# every tail-sourced day must be scored with B = 0
for t, td in TK.items():
    for d in DAYS:
        if (t, d) in SOFTVOL and d not in (nzraw(t) or {}) and abs(td["days"][d]["B"]) > 0:
            bad(f"{t} {d} B nonzero on a tail-only bar")
# the newest session must actually be the newest one either source has
newest = max(d for d in full)
if DAYS[-1] != newest: bad(f"window ends {DAYS[-1]} but the sources carry {newest}")
print(f"newest session available {newest}, scored {DAYS[-1]}; provisional {mine}")
if len(PANEL) < 1000:
    bad(f"market panel collapsed to {len(PANEL)} names — the broad Yahoo pull is missing a session")
print("PROBLEMS:", len(P))
for m in P[:30]: print("  -", m)
