# -*- coding: utf-8 -*-
"""Derive subsector_flow12.py from subsector_flow11.py.

R12 is a data-integrity revision, not a scoring change. The 2026-09-17 session showed
a mirror failure the existing screens cannot see:

  G1  The mirror published 09-17 as volume-only rows -- Open/High/Low/Close empty on
      all 1,503 names. load_nz_raw already skipped such rows, but silently, so the
      operator saw only "mirror coverage 1" with no reason attached. A turnover screen
      cannot catch this either: the volume WAS published in full (mirror turnover
      1.0585, an ordinary session), and it is the prices that are missing. That is a
      different failure from the mid-session snapshots of 09-14..09-16, so it needs its
      own counter rather than a wider version of the old one.

  G2  With the mirror carrying no prices, the tail pull was the only source for that
      close, and the tail pull covers the 546-name report list. The balanced market
      panel needs a name quoted on every scored session, so it collapsed from 1,658
      names to 535. The loader now takes every data/yahoo/tail*.csv.gz, so a broad
      tail pull can stand in for the mirror when the mirror fails.
"""
import re

src = open("scripts/subsector_flow11.py").read()

def rep(a, b):
    global src
    assert src.count(a) == 1, "anchor not unique: " + a[:70]
    src = src.replace(a, b)

# ---- G1: count and report the price-less mirror rows -------------------------------
rep('''def load_nz_raw(sym):''',
'''# G1: keyed by session -> set of symbols, because load_nz_raw runs more than once per
# symbol over a full pass and a plain counter would multiply the figure by that count.
MIRROR_PRICELESS = collections.defaultdict(set)

def load_nz_raw(sym):''')
rep('''            except (ValueError, KeyError, TypeError):
                continue                      # partial rows (volume published before the bar)''',
'''            except (ValueError, KeyError, TypeError):
                # G1: a row with a volume but no Open/High/Low/Close. Unusable, and
                # invisible to the turnover screen because the volume is complete.
                # keyed by mirror FILE, not by ticker: two tickers can map to one file
                # (nzname folds BRK.B and BRK-B together) and that would count it twice.
                if d and (row.get("Volume") or "").strip(): MIRROR_PRICELESS[d].add(nzname(sym))
                continue                      # partial rows (volume published before the bar)''')

# ---- G2: accept every tail pull in the data directory ------------------------------
rep('''TAIL = os.environ.get("YAHOO_TAIL", "/home/user/20MAwarchlist/data/yahoo/tail.csv.gz")
TAIL_ROUTE = collections.defaultdict(dict)
if os.path.exists(TAIL):
    added = collections.Counter(); routes = collections.Counter()''',
'''TAIL_GLOB = os.environ.get("YAHOO_TAIL", "/home/user/20MAwarchlist/data/yahoo/tail*.csv.gz")
TAIL_FILES = (sorted(glob.glob(TAIL_GLOB)) if any(c in TAIL_GLOB for c in "*?[")
              else ([TAIL_GLOB] if os.path.exists(TAIL_GLOB) else []))
TAIL_ROUTE = collections.defaultdict(dict)
# G2: more than one tail pull can be in hand -- the 546-name report list, and a broad
# pull taken when the mirror fails, which the balanced market panel needs.
for TAIL in TAIL_FILES:
    added = collections.Counter(); routes = collections.Counter()''')
rep('''    print(f"yahoo tail: {os.path.basename(TAIL)} -> {dict(sorted(added.items()))} by route {dict(routes)}")
    for sym, m in TAIL_ROUTE.items():                # hourly/quote totals are not settled prints
        for d, route in m.items():
            if route != "hist5d": SOFTVOL.add((sym, d))
else:
    print("yahoo tail: not present")''',
'''    print(f"yahoo tail: {os.path.basename(TAIL)} -> {dict(sorted(added.items()))} by route {dict(routes)}")
if TAIL_FILES:
    for sym, m in TAIL_ROUTE.items():                # hourly/quote totals are not settled prints
        for d, route in m.items():
            if route != "hist5d": SOFTVOL.add((sym, d))
else:
    print("yahoo tail: not present")''')

# ---- report both in meta ------------------------------------------------------------
rep('''                "relvol_by_source": RELVOL, "relvol_light": LIGHT, "relvol_cross_tol": CROSS_TOL,''',
'''                # G1: named here so a mirror that publishes a session without prices is a
                # stated fact rather than something inferred from a low coverage count.
                "mirror_priceless": {d: len(s) for d, s in sorted(MIRROR_PRICELESS.items()) if d >= DAYS[0]},
                "tail_files": [os.path.basename(p) for p in TAIL_FILES],
                "relvol_by_source": RELVOL, "relvol_light": LIGHT, "relvol_cross_tol": CROSS_TOL,''')

rep('''print(f"daily-bar files too stale to merge (Yahoo used alone): {len(STALE)} {sorted(STALE)}")''',
'''print(f"daily-bar files too stale to merge (Yahoo used alone): {len(STALE)} {sorted(STALE)}")
_priceless = {d: len(s) for d, s in sorted(MIRROR_PRICELESS.items())[-6:]}
print(f"mirror rows with a volume but no OHLC, by session: {_priceless}")''')

src = src.replace('"""Sub-sector money-flow scoring — R11.00 engine',
                  '"""Sub-sector money-flow scoring — R12.00 engine', 1)
src = src.replace('f"{SCR}/sub11/flow11.json"', 'f"{SCR}/sub12/flow12.json"', 1)
open("scripts/subsector_flow12.py", "w").write(src)
print("wrote scripts/subsector_flow12.py")
