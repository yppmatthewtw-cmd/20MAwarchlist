# -*- coding: utf-8 -*-
"""Derive verify_subsector_flow12.py from verify_subsector_flow11.py.

The verifier is an independent reimplementation, so it has to take the same inputs the
engine takes or its market panel differs and every F disagrees. R12's G2 lets the engine
read every data/yahoo/tail*.csv.gz; the verifier follows, and additionally re-derives the
G1 price-less-mirror counter from the raw CSVs and asserts the engine's figure.
"""
src = open("scripts/verify_subsector_flow11.py").read()

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

src = src.replace('f"{SCR}/sub11/flow11.json"', 'f"{SCR}/sub12/flow12.json"', 1)
open("scripts/verify_subsector_flow12.py", "w").write(src)
print("wrote scripts/verify_subsector_flow12.py")
