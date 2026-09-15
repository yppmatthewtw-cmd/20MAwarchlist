#!/usr/bin/env python3
"""sub9/flow9.py -> sub10/flow10.py : judge a mid-session bar by disagreement, not by level.

R9 added the turnover screen that caught the mirror's mid-session 2026-09-14 bars, and it was
right — but it judged on an ABSOLUTE level (turnover below 0.80 of the name's own 20-day median
= not a closed session), and that level does not separate the two things it has to separate.

Over the mirror's own history since 2025-10, 12 sessions fall below 0.80, and ELEVEN of them are
genuine closed sessions: 2025-12-24 at 0.348 and 2025-11-28 at 0.418 (the Christmas Eve and
day-after-Thanksgiving half sessions), then 2025-12-26 0.507, 2025-12-30 0.664, 2026-07-10 0.694,
2025-12-31 0.709, 2025-12-29 0.718, 2026-04-06 0.719, 2026-08-14 0.744, 2025-12-23 0.762,
2026-04-10 0.799. Only 2026-09-15 (0.472) is a snapshot. The two half sessions sit BELOW the
snapshot, so no absolute threshold can tell them apart — R9 would have silently deleted eleven
real closes, two of them every year on a fixed calendar.

What does separate them is whether the sources AGREE. A half session is short for everybody, so
both sources report the same low turnover; a mid-session snapshot is one source reading the
clock wrong while the other has the whole day. Measured on the four light sessions where both
sources carry 20 days of prior history: 2026-04-06 mirror 0.719 / Yahoo 0.756 (ratio 0.952),
2026-04-10 0.799 / 0.805 (0.993), 2026-07-10 0.694 / 0.705 (0.984), 2026-08-14 0.744 / 0.793
(0.938) — and on a normal session 2026-09-14 1.131 / 1.111 (1.018). Against that, the mirror's
2026-09-15 snapshot reads far below Yahoo's same-session figure.

So a source loses a session only when another source has that session and reads materially
higher (ratio below 0.75). Where a session has just one source and that source reads light,
there is nothing to adjudicate with, so the session is refused outright rather than scored on a
bar that might be a snapshot.
"""
SRC = "sub9/flow9.py"; DST = "sub10/flow10.py"
s = open(SRC).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, f"anchor x{s.count(a)} (want {n}): {a[:90]!r}"
    s = s.replace(a, b)

rep('''MID_SESSION = {"mirror": set(), "yahoo": set()}   # sessions a source has not closed yet
RELVOL_MIN = 0.80   # cross-sectional median turnover below this = mid-session''',
'''MID_SESSION = {"mirror": set(), "yahoo": set()}   # sessions a source has not closed yet
UNADJUDICATED = set()      # sessions carried by one light source only: cannot be judged, refused
CROSS_TOL = 0.75    # a source reading below this fraction of the best source is mid-session
LIGHT = 0.80        # below this a session is "light" and has to be adjudicated at all''')

# the mirror screen no longer decides on its own; it just records the measurement
rep('''# D1: drop any session the mirror has published but not yet closed.
_recent = sorted(_mv)[-8:]
_nzrel = {}
for _d in _recent:
    _m, _n = relvol_median(_nzall, _d)
    if _m is not None:
        _nzrel[_d] = round(_m, 3)
        if _m < RELVOL_MIN: MID_SESSION["mirror"].add(_d)
print(f"mirror turnover vs 20-day median, by session: {_nzrel}")
print(f"mirror sessions NOT closed yet (dropped): {sorted(MID_SESSION['mirror']) or 'none'}")''',
'''# D1/E1: measure the mirror's turnover per session; the verdict is taken below, against Yahoo.
_recent = sorted(_mv)[-8:]
_nzrel = {}
for _d in _recent:
    _m, _n = relvol_median(_nzall, _d)
    if _m is not None: _nzrel[_d] = round(_m, 3)
print(f"mirror turnover vs 20-day median, by session: {_nzrel}")''')

# and neither does the Yahoo screen
rep('''# D1: the same screen on the Yahoo side, before anything reads YH.
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
    for _d in MID_SESSION["yahoo"]: YH[_sym].pop(_d, None)''',
'''# E1: measure Yahoo's turnover per session. Both measurements are in hand only after the mirror
# pass below, so the verdict is deferred to adjudicate(); Yahoo's bars are pruned there.
_yrecent = sorted({d for m in YH.values() for d in m})[-8:]
_yrel = {}
for _d in _yrecent:
    _m, _n = relvol_median(YH, _d)
    if _m is not None: _yrel[_d] = round(_m, 3)
print(f"yahoo turnover vs 20-day median, by session: {_yrel}")''')

# the adjudication itself, right after the mirror measurement (both dicts exist there)
rep('''RELVOL = {"mirror": _nzrel, "yahoo": _yrel}
del _nzall''',
'''RELVOL = {"mirror": _nzrel, "yahoo": _yrel}
del _nzall

# ---- E1: a light session is judged by DISAGREEMENT between the sources, never by its level ----
# A half session (Christmas Eve, the day after Thanksgiving) is short for every source and both
# read the same low turnover; a mid-session snapshot is one source reading the clock wrong while
# the other has the whole day. Only the second case is a bad bar.
for _d in sorted(set(_nzrel) | set(_yrel)):
    _vals = {k: v for k, v in (("mirror", _nzrel.get(_d)), ("yahoo", _yrel.get(_d))) if v is not None}
    if not _vals: continue
    _best = max(_vals.values())
    _light = [k for k, v in _vals.items() if v < LIGHT]
    if not _light: continue
    if len(_vals) < 2:
        UNADJUDICATED.add(_d)                      # one light source, nothing to check it against
        continue
    for _k, _v in _vals.items():
        if _v / _best < CROSS_TOL: MID_SESSION[_k].add(_d)
print(f"sessions NOT closed yet, by source: "
      f"{ {k: sorted(v) for k, v in MID_SESSION.items() if v} or 'none'}")
print(f"light sessions with no second source to adjudicate (refused): {sorted(UNADJUDICATED) or 'none'}")
for _sym in YH:
    for _d in MID_SESSION["yahoo"] | UNADJUDICATED: YH[_sym].pop(_d, None)''')

# the mirror loader must also honour UNADJUDICATED
rep('''def load_nz(sym):
    """Mirror bars with any session the mirror has not closed yet removed."""
    out = load_nz_raw(sym)
    if not out: return None
    if MID_SESSION["mirror"]:
        out = {d: b for d, b in out.items() if d not in MID_SESSION["mirror"]}
    return out or None''',
'''def load_nz(sym):
    """Mirror bars with any session the mirror has not closed yet removed."""
    out = load_nz_raw(sym)
    if not out: return None
    drop = MID_SESSION["mirror"] | UNADJUDICATED
    if drop:
        out = {d: b for d, b in out.items() if d not in drop}
    return out or None''')

rep('''                "relvol_by_source": RELVOL, "relvol_min": RELVOL_MIN,
                "mid_session_dropped": {k: sorted(v) for k, v in MID_SESSION.items()},''',
'''                "relvol_by_source": RELVOL, "relvol_light": LIGHT, "relvol_cross_tol": CROSS_TOL,
                "mid_session_dropped": {k: sorted(v) for k, v in MID_SESSION.items()},
                "unadjudicated_sessions": sorted(UNADJUDICATED),''')

rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub9/flow9.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub10/flow10.json"), "w"), ensure_ascii=False)')

rep('''"""Sub-sector money-flow scoring — R9.00 engine (111 sub-sectors of the R2 heat-map workbook).''',
'''"""Sub-sector money-flow scoring — R10.00 engine (111 sub-sectors of the R2 heat-map workbook).

R10 fixes how R9's turnover screen decides. R9 judged on an absolute level — turnover below 0.80
of the name's own 20-day median meant "not a closed session" — and that level cannot separate a
mid-session snapshot from a genuinely short session. Of the 12 sessions below 0.80 in the
mirror's history since 2025-10, eleven are real closes, including Christmas Eve 2025 at 0.348 and
the day after Thanksgiving at 0.418 — both BELOW the 0.472 snapshot R9 was built to catch. R9
would have deleted eleven real sessions, two of them on a fixed calendar every year.
The separator is agreement: a half session is short for every source, a snapshot is one source
reading the clock wrong. A source now loses a session only when another source has it and reads
materially higher; a light session with no second source is refused rather than guessed at.''')
open(DST, "w").write(s)
print("wrote", DST, len(s), "bytes")
