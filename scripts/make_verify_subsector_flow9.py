S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub8/verify8.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:90]); src = src.replace(a, b, 1)

rep('F = json.load(open(f"{SCR}/sub8/flow8.json"))', 'F = json.load(open(f"{SCR}/sub9/flow9.json"))')

# D1 re-derived here: screen each source's sessions by turnover, independently of the engine
rep('''def nzraw(sym):
    p = f"{NZ}/{sym.replace('.', '-')}.csv"
    if not os.path.exists(p): return None
    out = {}
    for row in csv.DictReader(open(p)):
        try: o, h, l, c, v = (float(row[k]) for k in ("Open", "High", "Low", "Close", "Volume"))
        except (ValueError, KeyError, TypeError): continue
        if c > 0: out[row["Date"][:10]] = (o, h, l, c, v)
    return out or None''',
'''def nzraw0(sym):
    p = f"{NZ}/{sym.replace('.', '-')}.csv"
    if not os.path.exists(p): return None
    out = {}
    for row in csv.DictReader(open(p)):
        try: o, h, l, c, v = (float(row[k]) for k in ("Open", "High", "Low", "Close", "Volume"))
        except (ValueError, KeyError, TypeError): continue
        if c > 0: out[row["Date"][:10]] = (o, h, l, c, v)
    return out or None

RELVOL_MIN = 0.80
def relvol_median(bars_by_sym, day, lookback=20):
    """Cross-sectional median of a session's volume over each name's own 20-day median volume:
    near 1.0 on a closed session, far below it on a mid-session snapshot."""
    rat = []
    for sym, bars in bars_by_sym.items():
        b = bars.get(day)
        if not b or not b[4]: continue
        prev = sorted(d for d in bars if d < day)[-lookback:]
        base = [bars[d][4] for d in prev if bars[d][4]]
        if len(base) < 10: continue
        m = statistics.median(base)
        if m > 0: rat.append(b[4] / m)
    return statistics.median(rat) if len(rat) >= 25 else None

_nzall = {}
for _f in os.listdir(NZ):
    if _f.endswith(".csv"):
        _b = nzraw0(_f[:-4].replace("-", "."))
        if _b: _nzall[_f[:-4]] = _b
MID = {"mirror": set(), "yahoo": set()}
_nzrel = {}
for _d in sorted({d for m in _nzall.values() for d in m})[-8:]:
    _m = relvol_median(_nzall, _d)
    if _m is not None:
        _nzrel[_d] = round(_m, 3)
        if _m < RELVOL_MIN: MID["mirror"].add(_d)
_yrel = {}
for _d in sorted({d for m in YH.values() for d in m})[-8:]:
    _m = relvol_median(YH, _d)
    if _m is not None:
        _yrel[_d] = round(_m, 3)
        if _m < RELVOL_MIN: MID["yahoo"].add(_d)
for _sym in YH:
    for _d in MID["yahoo"]: YH[_sym].pop(_d, None)
del _nzall
if {k: sorted(v) for k, v in MID.items()} != (M.get("mid_session_dropped") or {}):
    bad(f"mid-session sets {({k: sorted(v) for k, v in MID.items()})} != {M.get('mid_session_dropped')}")
for _src, _rel in (("mirror", _nzrel), ("yahoo", _yrel)):
    for _d, _v in _rel.items():
        _e = (M.get("relvol_by_source", {}).get(_src) or {}).get(_d)
        if _e is not None and abs(_e - _v) > 0.002: bad(f"relvol {_src} {_d}: {_v} vs {_e}")
print(f"turnover screen — mirror {_nzrel}")
print(f"turnover screen — yahoo  {_yrel}")
print(f"mid-session dropped: {({k: sorted(v) for k, v in MID.items()})}")

def nzraw(sym):
    out = nzraw0(sym)
    if not out: return None
    if MID["mirror"]: out = {d: b for d, b in out.items() if d not in MID["mirror"]}
    return out or None''')

# no scored session may be one this side judged mid-session in every source
rep('''print("PROBLEMS:", len(P))''',
'''for d in DAYS:
    if d in MID["mirror"] and d in MID["yahoo"]:
        bad(f"{d} is mid-session in both sources but was scored")
print("PROBLEMS:", len(P))''')
open(f"{S}/sub9/verify9.py", "w", encoding="utf-8").write(src); print("sub9/verify9.py written")
