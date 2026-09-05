# verifiers for the Yahoo-layer engines, derived from the R3/R4 verifiers with an independent merge implementation
S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
for base, out, flow in (("sub3/verify3.py", "sub4/verify4.py", "sub4/flow4.json"), ("ai4/verify4.py", "ai5/verify5.py", "ai5/flow5.json")):
    s = open(f"{S}/{base}", encoding="utf-8").read()
    def rep(old, new):
        global s
        assert old in s, (base, old[:70]); s = s.replace(old, new, 1)
    rep('import csv, json, math, os, pickle, statistics, collections, re', 'import csv, json, math, os, pickle, statistics, collections, re, gzip, glob')
    rep(f'F = json.load(open(f"{{SCR}}/{base.split("/")[0]}/{"flow3" if "sub" in base else "flow4"}.json"))', f'F = json.load(open(f"{{SCR}}/{flow}"))')
    # calendar: derive from bar sources instead of the snapshot CAL
    rep('''# calendar around the window
i0 = CAL.index(DAYS[0]); LASTI = list(range(i0 - 21, CAL.index(DAYS[-1]) + 1))
LAST = [CAL[i] for i in LASTI]''',
'''# ---- Yahoo bars: own loader + own merge rule ----
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
i1 = full.index(DAYS[-1]); LAST = full[i1 - 25:i1 + 1]''')
    # market median over merged union universe
    rep('''allret = {d: [] for d in DAYS}
for f in os.listdir(NZ):
    if not f.endswith(".csv"): continue
    d = nz(f[:-4])
    if not d: continue
    for day in DAYS:
        if day in d and PREV[day] in d and d[PREV[day]][3] > 0: allret[day].append(d[day][3] / d[PREV[day]][3] - 1)''',
'''allret = {d: [] for d in DAYS}
UNI = {}
for f in os.listdir(NZ):
    if f.endswith(".csv"): UNI[f[:-4].replace("-", ".")] = merged(f[:-4])[0]
for sym in YH:
    if sym not in UNI: UNI[sym] = YH[sym]
for t in NB: UNI[t] = NB[t]
for d in UNI.values():
    if not d: continue
    for day in DAYS:
        if day in d and PREV[day] in d and d[PREV[day]][3] > 0: allret[day].append(d[day][3] / d[PREV[day]][3] - 1)''')
    # tick(): merged bars replace natezone-only; no snapshot fallback expected
    rep('''def tick(sym):
    data = nz(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    if not real: data = snapdata(sym)''',
'''def tick(sym):
    data, tag = merged(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    if not real:
        bad(f"{sym} fell back to snapshot"); data = snapdata(sym)''')
    rep('''if set(M["notes_skipped"])''' if "sub" in base else '''if M["notes_skipped"]: bad("notes skipped")''',
        ('''# every dropped ticker really has no bars in the window
for t in M["dropped"]:
    m, _ = merged(t)
    if m and all(d in m for d in DAYS) and PREV[DAYS[0]] in m: bad(f"dropped {t} has full bars")
# cross-check stats: recompute the natezone-vs-yahoo figure
nzd = []
for r in live:
    for t in r["basket"]:
        a, b = nzraw(t), yh(t)
        if a and b:
            for d in DAYS:
                if d in a and d in b and b[d][3] > 0: nzd.append(abs(a[d][3] - b[d][3]) / b[d][3] * 100)
xn = M["yahoo_xcheck"]["natezone_vs_yahoo"]
if xn and (xn["n"] != len(set()) + len(nzd) or abs(xn["median_pct"] - round(statistics.median(nzd), 4)) > 1e-9): bad(f"natezone_vs_yahoo stats {xn} vs n={len(nzd)}")
''') + ('''if set(M["notes_skipped"])''' if "sub" in base else '''if M["notes_skipped"]: bad("notes skipped")'''))
    open(f"{S}/{out}", "w", encoding="utf-8").write(s); print(out, "written")
