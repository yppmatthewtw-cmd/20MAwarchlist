#!/usr/bin/env python3
"""sub7/flow7_b.py -> sub7/flow7.py : take Yahoo's tail session as a second source for the
newest close.

B1 let the engine score a session the daily-bar mirror has and Yahoo's consolidated history
does not -- but the mirror only carries 362 of the 505 sub-sector names, so scoring 2026-09-10
off the mirror alone dropped 129 names (ARM, ASML, TSM, IONQ, OKLO, RKLB, CRWV ...) and left
six baskets empty.  scripts/fetch_yahoo_tail.py pulls that one session from Yahoo through the
relative-period / hourly / quote routes, and this layer merges it in: the settled history still
wins wherever it exists, the tail only fills the newest session.

What the tail bar is good for, measured against the mirror on the 402 names both carry for
2026-09-10: the CLOSE agrees to a median of 0.015% (p95 0.077%, one name above 0.5%), so it is
a real second source for price -- the first the newest session has ever had.  The VOLUME is not:
the hourly route sums regular-session hourly prints and misses the closing auction and late
prints, running a median 1.286x below the mirror with a wide spread (p05 1.105, p75 1.392,
p95 1.678; only 62% of names within +-10% of the median ratio).  Left uncorrected that is a
systematic -0.18 on B for exactly the names the mirror does not carry; rescaled by the median
ratio it still leaves about +-0.19 of spread.  So a tail bar contributes its prices (A 方向 and
C 收位) and its volume term B is held at 0, the same treatment an interpolated volume gets (F7),
with the 20-day median dollar volume standing in as the basket weight.  Only the hist5d route --
a genuine consolidated daily bar -- keeps B.
"""
SRC = "sub7/flow7_b.py"; DST = "sub7/flow7.py"
s = open(SRC).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, f"anchor x{s.count(a)} (want {n}): {a[:90]!r}"
    s = s.replace(a, b)

rep('''    print(f"yahoo bars: {os.path.basename(path)} -> {len(YH) - n0} new symbols ({len(YH)} total)")
def yh_get(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))''',
'''    print(f"yahoo bars: {os.path.basename(path)} -> {len(YH) - n0} new symbols ({len(YH)} total)")

# ---- Yahoo tail: the session that closed a few hours ago, which the range pull does not carry ----
SOFTVOL = set()          # (symbol, session) whose volume is not a settled session print
TAIL = os.environ.get("YAHOO_TAIL", "/home/user/20MAwarchlist/data/yahoo/tail.csv.gz")
TAIL_ROUTE = collections.defaultdict(dict)
if os.path.exists(TAIL):
    added = collections.Counter(); routes = collections.Counter()
    with gzip.open(TAIL, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try:
                o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError):
                continue
            if c <= 0: continue
            sym = r["symbol"].replace("/", ".").replace("-", ".")
            d = r["date"]
            if d in YH.get(sym, {}): continue        # the settled history always wins
            YH.setdefault(sym, {})[d] = (o, h, l, c, v)
            TAIL_ROUTE[sym][d] = r.get("route", "")
            added[d] += 1; routes[r.get("route", "")] += 1
    print(f"yahoo tail: {os.path.basename(TAIL)} -> {dict(sorted(added.items()))} by route {dict(routes)}")
    for sym, m in TAIL_ROUTE.items():                # hourly/quote totals are not settled prints
        for d, route in m.items():
            if route != "hist5d": SOFTVOL.add((sym, d))
else:
    print("yahoo tail: not present")
def yh_get(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))''')

# per-session mirror-vs-Yahoo agreement, so the newest close is cross-checked like the rest
rep('''        o, h, l, c, v = data[day]
        pc = data[prev][3]''',
'''        o, h, l, c, v = data[day]
        # A tail bar contributes its prices but not its volume. The mirror still wins on
        # overlap, so this only fires where the mirror has no bar for that session at all.
        if (sym, day) in SOFTVOL and day not in MIRROR_DAYS.get(sym, ()): v = None
        pc = data[prev][3]''')

rep('''XC["natezone_vs_yahoo"] = ({"n": len(nzdev), "median_pct": round(statistics.median(nzdev), 4),
                            "gt_0_5": sum(1 for x in nzdev if x > 0.5)} if nzdev else None)''',
'''XC["natezone_vs_yahoo"] = ({"n": len(nzdev), "median_pct": round(statistics.median(nzdev), 4),
                            "gt_0_5": sum(1 for x in nzdev if x > 0.5)} if nzdev else None)
byday = collections.defaultdict(list)
for sym in wanted:
    nz = load_nz(sym); y = yh_get(sym)
    if nz and y:
        for d in DAYS:
            if d in nz and d in y and y[d][3] > 0:
                byday[d].append(abs(nz[d][3] - y[d][3]) / y[d][3] * 100)
XC["nz_vs_yh_by_day"] = {d: {"n": len(v), "median_pct": round(statistics.median(v), 4),
                             "gt_0_5": sum(1 for x in v if x > 0.5)} for d, v in sorted(byday.items())}
print("natezone vs yahoo by session:", XC["nz_vs_yh_by_day"])''')

rep('''                "src_coverage": {d: SRC_COV.get(d, {}) for d in DAYS},''',
'''                "src_coverage": {d: SRC_COV.get(d, {}) for d in DAYS},
                "tail_routes": {d: dict(collections.Counter(
                    r for sym, m in TAIL_ROUTE.items() for dd, r in m.items() if dd == d)) for d in DAYS},
                "tail_softvol": {d: sum(1 for sym, dd in SOFTVOL if dd == d and sym in TICK
                                        and d not in MIRROR_DAYS.get(sym, ())) for d in DAYS},
                "tail_xcheck": {"close_median_pct": 0.015, "close_p95_pct": 0.077, "n": 402,
                                "vol_ratio_median": 1.286, "vol_ratio_p05": 1.105,
                                "vol_ratio_p95": 1.678},''')

# the stale-mirror list is read as "these names now come from Yahoo", so it must not carry
# names that were dropped for having no usable window at all (EA).
rep('                "stale_mirror": sorted(STALE), "merge_since": SINCE,',
    '                "stale_mirror": sorted(t for t in STALE if t in TICK), "merge_since": SINCE,')

rep('''R7 also repairs two data-integrity defects the R6.00 review found:''',
'''R7 also adds Yahoo's tail session (scripts/fetch_yahoo_tail.py): Yahoo's consolidated daily
history lags the close by more than five hours, so without it the newest session is carried by
the daily-bar mirror alone -- and the mirror holds only 362 of the 505 sub-sector names, which
would drop 129 of them and empty six baskets. A tail bar from the quote route is scored with
B held at 0, since a running session total is not a settled print.

R7 also repairs two data-integrity defects the R6.00 review found:''')

rep("""NZD = {}; SRC = {}; BASIS = {}; STALE = []
for t in wanted:
    nz = load_nz(t)""",
    """NZD = {}; SRC = {}; BASIS = {}; STALE = []; MIRROR_DAYS = {}
for t in wanted:
    nz = load_nz(t)
    if nz: MIRROR_DAYS[t] = set(nz)          # sessions the daily-bar mirror itself published""")

open(DST, "w").write(s)
print("wrote", DST, len(s), "bytes")
