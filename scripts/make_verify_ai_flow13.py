# -*- coding: utf-8 -*-
"""Derive verify_ai_flow13.py from verify_ai_flow12.py.

Applies exactly the patch set make_verify_subsector_flow12.py applies to the sub-sector
verifier. Deriving the AI verifier from the previous AI verifier is what let R8 ship a
verifier a revision behind its engine, so the two are generated from one patch set.

ORIGINAL NOTE ---

The verifier is an independent reimplementation, so it has to take the same inputs the
engine takes or its market panel differs and every F disagrees. R12's G2 lets the engine
read every data/yahoo/tail*.csv.gz; the verifier follows, and additionally re-derives the
G1 price-less-mirror counter from the raw CSVs and asserts the engine's figure.
"""
src = open("scripts/verify_ai_flow12.py").read()

def rep(a, b):
    global src
    assert src.count(a) == 1, "anchor not unique: " + a[:70]
    src = src.replace(a, b)

rep('''TAILP = "/home/user/20MAwarchlist/data/yahoo/tail.csv.gz"
SOFTVOL = set(); TAILN = collections.Counter()
if os.path.exists(TAILP):
    with gzip.open(TAILP, "rt", newline="") as f:''',
'''TAILPS = sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/tail*.csv.gz"))
SOFTVOL = set(); TAILN = collections.Counter()
for TAILP in TAILPS:                      # G2: the engine merges every tail pull, so do the same
    with gzip.open(TAILP, "rt", newline="") as f:''')
rep('''print(f"tail bars merged: {dict(TAILN)}, soft-volume pairs {len(SOFTVOL)}")''',
'''print(f"tail bars merged from {[os.path.basename(p) for p in TAILPS]}: {dict(TAILN)}, "
      f"soft-volume pairs {len(SOFTVOL)}")''')

# G1: rebuild the price-less counter straight from the mirror CSVs and check the engine's
rep('''print("PROBLEMS:", len(P))''',
'''_pl = collections.Counter()
for _p in glob.glob(NZ + "/*.csv"):
    with open(_p, newline="") as _f:
        for _row in csv.DictReader(_f):
            _d = (_row.get("Date") or "")[:10]
            try:
                float(_row["Close"])
            except (ValueError, KeyError, TypeError):
                if _d and (_row.get("Volume") or "").strip(): _pl[_d] += 1
_exp = {d: n for d, n in sorted(_pl.items()) if d >= DAYS[0]}
if _exp != (M.get("mirror_priceless") or {}):
    bad(f"mirror_priceless {M.get('mirror_priceless')} != {_exp}")
print(f"mirror rows with a volume but no OHLC: {_exp}")
_tf = [os.path.basename(p) for p in TAILPS]
if _tf != (M.get("tail_files") or []):
    bad(f"tail_files {M.get('tail_files')} != {_tf}")
print("PROBLEMS:", len(P))''')

# G3: the same corporate-action guard the engine applies. Without it the verifier's bars
# differ from the engine's and every downstream F disagrees.
rep("""YH = {}
for p in YFILES:""", """YH = {}
ADJ = {}
for p in YFILES:""")
rep("""            if c > 0: YH.setdefault(r["symbol"].replace("/", ".").replace("-", "."), {})[r["date"]] = (o, h, l, c, v)""",
"""            if c > 0:
                _s = r["symbol"].replace("/", ".").replace("-", ".")
                YH.setdefault(_s, {})[r["date"]] = (o, h, l, c, v)
                try:
                    _a = float(r.get("adj_close") or 0)
                    if _a > 0: ADJ.setdefault(_s, {})[r["date"]] = _a
                except (ValueError, TypeError): pass""")
rep("""            YH.setdefault(sym, {})[r["date"]] = (o, h, l, c, v)
            TAILN[r["date"]] += 1""",
"""            YH.setdefault(sym, {})[r["date"]] = (o, h, l, c, v)
            try:
                _a = float(r.get("adj_close") or 0)
                if _a > 0: ADJ.setdefault(sym, {})[r["date"]] = _a
            except (ValueError, TypeError): pass
            TAILN[r["date"]] += 1""")
rep("""def yh(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))""",
"""SPLIT_DROPPED = {}
def _drop_unadjusted(tol=1.25, hard=4.0):
    for sym, bars in YH.items():
        adj = ADJ.get(sym) or {}
        ds = sorted(bars); hit = None
        for prev, cur in zip(ds, ds[1:]):
            c0, c1 = bars[prev][3], bars[cur][3]
            if min(c0, c1) <= 0: continue
            rc = c1 / c0
            if rc > hard or rc < 1 / hard:
                hit = cur; continue
            a0, a1 = adj.get(prev), adj.get(cur)
            if a0 and a1 and a0 > 0 and a1 > 0:
                ratio = rc / (a1 / a0)
                if ratio > tol or ratio < 1 / tol: hit = cur
        if hit:
            SPLIT_DROPPED.setdefault(hit, []).append(sym)
            for d in [d for d in ds if d <= hit]: bars.pop(d, None)
_drop_unadjusted()
print(f"corporate-action bars dropped over {len(SPLIT_DROPPED)} sessions")

def yh(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))""")
rep("""_tf = [os.path.basename(p) for p in TAILPS]""",
"""_sd = {d: sorted(v) for d, v in sorted(SPLIT_DROPPED.items()) if d >= DAYS[0]}
if _sd != (M.get("split_dropped") or {}):
    bad(f"split_dropped {M.get('split_dropped')} != {_sd}")
print(f"corporate-action drops inside the window: {_sd}")
_tf = [os.path.basename(p) for p in TAILPS]""")

# A settled-print share of exactly 0.0 is falsy, so `(rounded_share(d) or 1.0)` fell back to
# 1.0 and judged the session settled -- the opposite of the truth. It never showed until
# 2026-09-17, where the share over the AI universe is exactly zero (previous unsettled
# sessions read 0.006-0.010, which are truthy).
rep("""mine = sorted(d for d in DAYS if (rounded_share(d) or 1.0) < 0.5)""",
"""def _share_or_settled(d):
    sh = rounded_share(d)
    return 1.0 if sh is None else sh        # None = too few names to judge, not "zero"
mine = sorted(d for d in DAYS if _share_or_settled(d) < 0.5)""")

src = src.replace('f"{SCR}/ai12/flow12.json"', 'f"{SCR}/ai13/flow13.json"', 1)
open("scripts/verify_ai_flow13.py", "w").write(src)
print("wrote scripts/verify_ai_flow13.py")
