S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/ai10/verify10.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:90]); src = src.replace(a, b, 1)

rep('F = json.load(open(f"{SCR}/ai10/flow10.json"))', 'F = json.load(open(f"{SCR}/ai11/flow11.json"))')

# E1 re-derived: adjudicate a light session by cross-source disagreement, not by its level
rep('''MID = {"mirror": set(), "yahoo": set()}
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
    for _d in MID["yahoo"]: YH[_sym].pop(_d, None)''',
'''MID = {"mirror": set(), "yahoo": set()}
UNADJ = set()
CROSS_TOL, LIGHT = 0.75, 0.80
_nzrel = {}
for _d in sorted({d for m in _nzall.values() for d in m})[-8:]:
    _m = relvol_median(_nzall, _d)
    if _m is not None: _nzrel[_d] = round(_m, 3)
_yrel = {}
for _d in sorted({d for m in YH.values() for d in m})[-8:]:
    _m = relvol_median(YH, _d)
    if _m is not None: _yrel[_d] = round(_m, 3)
# a light session is only a bad bar when the sources DISAGREE; a half session is light for all
for _d in sorted(set(_nzrel) | set(_yrel)):
    _vals = {k: v for k, v in (("mirror", _nzrel.get(_d)), ("yahoo", _yrel.get(_d))) if v is not None}
    if not _vals or not any(v < LIGHT for v in _vals.values()): continue
    if len(_vals) < 2:
        UNADJ.add(_d); continue
    _best = max(_vals.values())
    for _k, _v in _vals.items():
        if _v / _best < CROSS_TOL: MID[_k].add(_d)
for _sym in YH:
    for _d in MID["yahoo"] | UNADJ: YH[_sym].pop(_d, None)
if sorted(UNADJ) != sorted(M.get("unadjudicated_sessions") or []):
    bad(f"unadjudicated {sorted(UNADJ)} != {M.get('unadjudicated_sessions')}")''')

rep('''RELVOL_MIN = 0.80
def relvol_median''', '''def relvol_median''')

rep('''    if MID["mirror"]: out = {d: b for d, b in out.items() if d not in MID["mirror"]}''',
    '''    drop = MID["mirror"] | UNADJ
    if drop: out = {d: b for d, b in out.items() if d not in drop}''')

# a session both sources call light must NOT have been dropped (it is a real half session)
rep('''for d in DAYS:
    if d in MID["mirror"] and d in MID["yahoo"]:
        bad(f"{d} is mid-session in both sources but was scored")''',
'''for d in DAYS:
    if d in MID["mirror"] and d in MID["yahoo"]:
        bad(f"{d} is mid-session in both sources but was scored")
# a light session the sources AGREE on is a real short session and must survive the screen
for d, v in _nzrel.items():
    y = _yrel.get(d)
    if v < LIGHT and y is not None and min(v, y) / max(v, y) >= CROSS_TOL:
        if d in MID["mirror"] or d in MID["yahoo"] or d in UNADJ:
            bad(f"{d} is light in both sources (mirror {v}, yahoo {y}) but was dropped")
print(f"light-but-agreeing sessions kept: "
      f"{[d for d, v in _nzrel.items() if v < LIGHT and _yrel.get(d) and min(v, _yrel[d]) / max(v, _yrel[d]) >= CROSS_TOL] or 'none'}")''')
open(f"{S}/ai11/verify11.py", "w", encoding="utf-8").write(src); print("ai11/verify11.py written")
