#!/usr/bin/env python3
"""sub8/flow8.py -> sub9/flow9.py : refuse a bar that is not a closed session.

Everything up to R8 assumed that a bar carrying a date is that date's CLOSE, and treated
"unsettled" as a volume-only problem.  2026-09-14 broke the assumption: the daily-bar mirror
committed its 09-14 bars at 19:21 UTC — 15:21 ET, forty minutes BEFORE the 16:00 close — so
1,503 names carried a mid-session snapshot with a date on it and nothing in the R8 engine
would have said the close was wrong.  Measured against Yahoo's post-close bar for the same
session over the 403 names both carry: the mirror's close is off by a median of 0.29%, p95
1.38%, max 2.83%, with 29.5% of names more than 0.5% out.  A 0.29% median error on a term
that saturates at 2% excess return is not a rounding difference; it is a different price.

The tell is turnover, and it does not need a second source.  Scale each name's volume for a
session by its own 20-day median volume and take the cross-sectional median: a real session
lands near 1.0 and a mid-session snapshot lands far below, because only part of the day has
traded.  Measured on the mirror: 1.099 / 1.059 / 1.059 / 0.992 for 09-08 through 09-11, and
0.596 for the mid-session 09-14 (87.6% of names below 0.9x, against 23-37% on real sessions).
Yahoo's post-close 09-14, pulled at 18:15 ET, sits at 1.089 — a full session, merely not yet
vendor-rounded.

So each source's bars are now screened per session at load time and a session judged
mid-session is DROPPED from that source.  A session no source has closed never enters the
calendar; where one source has closed it and another has not, the closed one is what gets
merged.  This subsumes R8's "mirror published but not settled loses the overlap" rule, which
kept the same day's prices whenever Yahoo happened to lack the ticker.
"""
SRC = "sub8/flow8.py"; DST = "sub9/flow9.py"
s = open(SRC).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, f"anchor x{s.count(a)} (want {n}): {a[:90]!r}"
    s = s.replace(a, b)

RELVOL_MIN = "0.80"

# ---- raw loaders kept separate from the screened ones ----
rep('''def load_nz(sym):
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
    return out or None''',
'''MID_SESSION = {"mirror": set(), "yahoo": set()}   # sessions a source has not closed yet
RELVOL_MIN = ''' + RELVOL_MIN + '''   # cross-sectional median turnover below this = mid-session

def relvol_median(bars_by_sym, day, lookback=20):
    """Cross-sectional median of (that session's volume / the name's own 20-day median volume).

    A closed session sits near 1.0 by construction; a mid-session snapshot sits far below it
    because only part of the day has traded. Needs no second source."""
    rat = []
    for sym, bars in bars_by_sym.items():
        b = bars.get(day)
        if not b or not b[4]: continue
        prev = sorted(d for d in bars if d < day)[-lookback:]
        base = [bars[d][4] for d in prev if bars[d][4]]
        if len(base) < 10: continue
        m = statistics.median(base)
        if m > 0: rat.append(b[4] / m)
    return (statistics.median(rat), len(rat)) if len(rat) >= 25 else (None, len(rat))

def load_nz_raw(sym):
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

def load_nz(sym):
    """Mirror bars with any session the mirror has not closed yet removed."""
    out = load_nz_raw(sym)
    if not out: return None
    if MID_SESSION["mirror"]:
        out = {d: b for d, b in out.items() if d not in MID_SESSION["mirror"]}
    return out or None''')

# ---- screen the mirror in the pass that already reads every file ----
rep('''_mv = collections.defaultdict(lambda: [0, 0])
for _f in os.listdir(NZ):
    if not _f.endswith(".csv"): continue
    for _d, _b in (load_nz(_f[:-4]) or {}).items():
        if _d < "2026-08-01" or not _b[4]: continue
        _mv[_d][0] += 1
        if abs(_b[4] - round(_b[4] / 100.0) * 100.0) < 1e-6: _mv[_d][1] += 1''',
'''_mv = collections.defaultdict(lambda: [0, 0])
_nzall = {}
for _f in os.listdir(NZ):
    if not _f.endswith(".csv"): continue
    _b0 = load_nz_raw(_f[:-4])
    if not _b0: continue
    _nzall[_f[:-4]] = _b0
    for _d, _b in _b0.items():
        if _d < "2026-08-01" or not _b[4]: continue
        _mv[_d][0] += 1
        if abs(_b[4] - round(_b[4] / 100.0) * 100.0) < 1e-6: _mv[_d][1] += 1
# D1: drop any session the mirror has published but not yet closed.
_recent = sorted(_mv)[-8:]
_nzrel = {}
for _d in _recent:
    _m, _n = relvol_median(_nzall, _d)
    if _m is not None:
        _nzrel[_d] = round(_m, 3)
        if _m < RELVOL_MIN: MID_SESSION["mirror"].add(_d)
print(f"mirror turnover vs 20-day median, by session: {_nzrel}")
print(f"mirror sessions NOT closed yet (dropped): {sorted(MID_SESSION['mirror']) or 'none'}")
RELVOL = {"mirror": _nzrel, "yahoo": _yrel}
del _nzall''')

# ---- screen Yahoo the same way, right after its bars are loaded ----
rep('''def yh_get(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))''',
'''# D1: the same screen on the Yahoo side, before anything reads YH.
_yrecent = sorted({d for m in YH.values() for d in m})[-8:]
_yrel = {}
for _d in _yrecent:
    _m, _n = relvol_median(YH, _d)
    if _m is not None:
        _yrel[_d] = round(_m, 3)
        if _m < RELVOL_MIN: MID_SESSION["yahoo"].add(_d)
print(f"yahoo turnover vs 20-day median, by session: {_yrel}")
print(f"yahoo sessions NOT closed yet (dropped): {sorted(MID_SESSION['yahoo']) or 'none'}")
for _sym in YH:
    for _d in MID_SESSION["yahoo"]: YH[_sym].pop(_d, None)

def yh_get(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))''')

# ---- R8's unsettled-overlap rule now also covers a mirror session that is merely stale ----
# NZ_UNSETTLED only governs days the mirror still has; a day screened out as mid-session is gone
# from nz altogether, so counting it in both places would double-report the same session.
rep("""NZ_UNSETTLED |= {d for d, (tot, rnd) in _mv.items()
                 if (tot >= 25 and rnd / tot < 0.5) or (_typ and tot < 0.5 * _typ)}""",
    """NZ_UNSETTLED |= {d for d, (tot, rnd) in _mv.items()
                 if d not in MID_SESSION["mirror"]
                 and ((tot >= 25 and rnd / tot < 0.5) or (_typ and tot < 0.5 * _typ))}""")

rep('''        # C2: on a session the mirror has published but not settled, a settled Yahoo bar is the
        # better of the two — the mirror's own figure is still the live feed and will be revised.''',
'''        # C2: on a session the mirror has published but not settled, a settled Yahoo bar is the
        # better of the two — the mirror's own figure is still the live feed and will be revised.
        # (A session the mirror has not CLOSED is already gone from nz, screened out at load.)''')

rep('''                "mirror_unsettled": sorted(NZ_UNSETTLED),
                "settled_basis": "merged_bars",''',
'''                "mirror_unsettled": sorted(NZ_UNSETTLED),
                "settled_basis": "merged_bars",
                "relvol_by_source": RELVOL, "relvol_min": RELVOL_MIN,
                "mid_session_dropped": {k: sorted(v) for k, v in MID_SESSION.items()},''')

rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub8/flow8.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub9/flow9.json"), "w"), ensure_ascii=False)')

rep('''"""Sub-sector money-flow scoring — R8.00 engine (111 sub-sectors of the R2 heat-map workbook).''',
'''"""Sub-sector money-flow scoring — R9.00 engine (111 sub-sectors of the R2 heat-map workbook).

R9 stops trusting that a bar carrying a date is that date's close. On 2026-09-14 the daily-bar
mirror committed 1,503 bars for the session at 15:21 ET — forty minutes before the close — and
nothing in R8 would have caught it: against Yahoo's post-close bar for the same session, those
closes are off by a median of 0.29% (p95 1.38%, max 2.83%; 29.5% of names more than 0.5% out).
Each source's sessions are now screened by turnover — the cross-sectional median of a session's
volume over each name's own 20-day median volume, which sits near 1.0 on a closed session and
far below it mid-session (mirror: 1.099/1.059/1.059/0.992 for 09-08..09-11 against 0.596 for the
mid-session 09-14; Yahoo's post-close 09-14: 1.089). A session below 0.80 is dropped from that
source, so a session no source has closed never enters the calendar.''')
open(DST, "w").write(s)
print("wrote", DST, len(s), "bytes")
