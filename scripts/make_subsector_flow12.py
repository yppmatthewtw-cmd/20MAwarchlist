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

  G3  The LNG basket printed a 5-day return of +9111%. Its member NFE did a reverse split:
      Yahoo's `close` column carries the raw historical price and was not restated, while
      `adj_close` was, so the close series jumps 0.33 -> 12.77 between two sessions and the
      engine read it as a +3771% day. tanh saturates, so the score was capped rather than
      absurd, but two of that group's daily scores were credited as maximum up days and the
      printed return was meaningless. Comparing the close ratio against the adj_close ratio
      catches exactly this: a dividend moves the two apart by a fraction of a percent, an
      unadjusted split by orders of magnitude.

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

# ---- G3: carry adj_close alongside the close, from both the range pull and the tails
rep('''YH = {}
for path in YF_FILES:''',
'''YH = {}
ADJ = {}          # G3: symbol -> date -> adj_close, used only to spot unadjusted splits
for path in YF_FILES:''')
rep('''            if c > 0: YH.setdefault(r["symbol"].replace("/", ".").replace("-", "."), {})[r["date"]] = (o, h, l, c, v)''',
'''            if c > 0:
                _s = r["symbol"].replace("/", ".").replace("-", ".")
                YH.setdefault(_s, {})[r["date"]] = (o, h, l, c, v)
                try:
                    _a = float(r.get("adj_close") or 0)
                    if _a > 0: ADJ.setdefault(_s, {})[r["date"]] = _a
                except (ValueError, TypeError): pass''')
rep('''            YH.setdefault(sym, {})[d] = (o, h, l, c, v)
            TAIL_ROUTE[sym][d] = r.get("route", "")''',
'''            YH.setdefault(sym, {})[d] = (o, h, l, c, v)
            try:
                _a = float(r.get("adj_close") or 0)
                if _a > 0: ADJ.setdefault(sym, {})[d] = _a
            except (ValueError, TypeError): pass
            TAIL_ROUTE[sym][d] = r.get("route", "")''')

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

# ---- G3: drop bars where `close` carries an unadjusted corporate action -------------
rep('''# ---- Yahoo tail: the session that closed a few hours ago, which the range pull does not carry ----''',
'''# G3: `close` is the raw historical price and `adj_close` is restated for splits and
# dividends, so the two ratios track each other to within a dividend on an ordinary day
# and diverge by the split factor on an unadjusted one.
SPLIT_DROPPED = {}
def _drop_unadjusted(tol=1.25, hard=4.0):
    """Remove price history left on a pre-corporate-action basis.

    Two tests, because one alone is not enough:
      * close-vs-adj_close ratio -- `close` is the raw historical price and `adj_close` is
        restated, so the two track each other to within a dividend on an ordinary day and
        diverge by the split factor on an unadjusted one.
      * an absolute session ratio outside 1/hard .. hard -- needed because Yahoo sometimes
        restates NEITHER column (NFE's adj_close equals its close on every row, so the first
        test is blind to its reverse split: 0.33 -> 12.77 between two sessions).

    Everything up to and including the action date is dropped, not just the transition bar:
    the bars before it are on the old basis, so keeping them only moves the bad ratio to the
    following session.
    """
    for sym, bars in YH.items():
        adj = ADJ.get(sym) or {}
        ds = sorted(bars)
        hit = None
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
if SPLIT_DROPPED:
    print("bars dropped -- close carries an unadjusted corporate action: "
          + str({d: sorted(v) for d, v in sorted(SPLIT_DROPPED.items())}))

# ---- Yahoo tail: the session that closed a few hours ago, which the range pull does not carry ----''')

# ---- report both in meta ------------------------------------------------------------
rep('''                "relvol_by_source": RELVOL, "relvol_light": LIGHT, "relvol_cross_tol": CROSS_TOL,''',
'''                # G1: named here so a mirror that publishes a session without prices is a
                # stated fact rather than something inferred from a low coverage count.
                "mirror_priceless": {d: len(s) for d, s in sorted(MIRROR_PRICELESS.items()) if d >= DAYS[0]},
                "tail_files": [os.path.basename(p) for p in TAIL_FILES],
                # G3: bars removed because `close` had not been restated for a split
                "split_dropped": {d: sorted(v) for d, v in sorted(SPLIT_DROPPED.items()) if d >= DAYS[0]},
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
