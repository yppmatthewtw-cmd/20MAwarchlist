#!/usr/bin/env python3
"""sub7/flow7.py -> sub8/flow8.py : make the settled-print test source-aware.

R7 introduced the test but ran it on the daily-bar mirror only, and let the mirror win every
overlap unconditionally.  Both assumptions broke on 2026-09-11:

  C1  the mirror had cleared its 09-11 bars (4 names left of 1,503) while Yahoo had settled the
      session for 532.  Measuring the mirror alone therefore says nothing about the data the
      engine is actually scoring.  The share is now measured over the MERGED bars each ticker
      is scored from, which is what the flag is meant to describe.

  C2  for the 4 names the mirror did carry, its 09-11 volume was the unsettled live feed
      (0% vendor-rounded) while Yahoo's was the settled print (99.4% rounded).  The mirror
      winning the overlap meant deliberately taking the worse of two available figures.
      On a session the mirror has not settled, a settled second-source bar now wins.

That Yahoo's settled bar is the same print the mirror eventually publishes is not assumed:
on 2026-09-10, once the mirror settled it, Yahoo's daily volume matched the mirror EXACTLY
for all 403 names both carry (median deviation 0.000%, zero names differing).
"""
SRC = "sub7/flow7.py"; DST = "sub8/flow8.py"
s = open(SRC).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, f"anchor x{s.count(a)} (want {n}): {a[:90]!r}"
    s = s.replace(a, b)

# ---- C2: a session the mirror has not settled is not the mirror's to win ----
rep('''def merge_bars(nz, yh, since=None):''',
'''def settled_share(bars, day):
    """Share of a day's volumes that are an exact multiple of 100 shares — the vendor's settled
    print.  A live feed reports exact share counts, so this separates the two without needing
    to know which endpoint produced the bar."""
    v = [b[4] for b in (bars or {}).values() if b and b[4]]
    return None

NZ_UNSETTLED = set()      # sessions the mirror has published but not settled (filled in below)

def merge_bars(nz, yh, since=None):''')

rep('''    if med is not None and med <= BASIS_TOL:
        out = dict(yh); out.update(nz); return out, "real", med''',
'''    if med is not None and med <= BASIS_TOL:
        out = dict(yh); out.update(nz)
        # C2: on a session the mirror has published but not settled, a settled Yahoo bar is the
        # better of the two — the mirror's own figure is still the live feed and will be revised.
        for d in NZ_UNSETTLED:
            if d in yh: out[d] = yh[d]
        return out, "real", med''')

# the mirror's unsettled sessions have to be known before the merge runs
rep('''listed_all = {t for s in subs for t in s["tickers"]}''',
'''# ---- which sessions has the mirror published but not settled? (its own coverage only) ----
_mv = collections.defaultdict(lambda: [0, 0])
for _f in os.listdir(NZ):
    if not _f.endswith(".csv"): continue
    for _d, _b in (load_nz(_f[:-4]) or {}).items():
        if _d < "2026-08-01" or not _b[4]: continue
        _mv[_d][0] += 1
        if abs(_b[4] - round(_b[4] / 100.0) * 100.0) < 1e-6: _mv[_d][1] += 1
_typ = statistics.median(sorted(t for t, _ in _mv.values())) if _mv else 0
# Two ways the mirror's copy of a session is not the one to prefer: it is published in full but
# still the live feed (unrounded volumes), or it is mid-repopulation after the close, carrying a
# handful of names (4 of 1,503 for 2026-09-11 at 23:33 ET) that are still the live feed too.
NZ_UNSETTLED |= {d for d, (tot, rnd) in _mv.items()
                 if (tot >= 25 and rnd / tot < 0.5) or (_typ and tot < 0.5 * _typ)}
print(f"mirror sessions published but not settled: {sorted(NZ_UNSETTLED) or 'none'} "
      f"(typical mirror coverage {_typ:.0f})")

listed_all = {t for s in subs for t in s["tickers"]}''')

# ---- C1: measure the settled-print share on the bars actually scored ----
rep('''ROUND_SHARE = {}
for d in seq[-(WIN + 3):]:
    tot = rnd = 0
    for t in wanted:
        b = (load_nz(t) or {}).get(d)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    if tot: ROUND_SHARE[d] = rnd / tot''',
'''# C1: the flag describes the data the engine scores, so measure the MERGED bars, not the
# mirror's. On 2026-09-11 the mirror had cleared the session (4 names) while Yahoo had settled
# it (532) — measuring the mirror alone would have called a settled session provisional.
ROUND_SHARE = {}
for d in seq[-(WIN + 3):]:
    tot = rnd = 0
    for t in wanted:
        b = (NZD.get(t) or {}).get(d)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    if tot >= 25: ROUND_SHARE[d] = rnd / tot''')

rep('''print(f"settled-print share (volume an exact multiple of 100): "''',
'''print(f"settled-print share of the MERGED bars (volume an exact multiple of 100): "''')

rep('''                "settled_print_share": {d: round(ROUND_SHARE.get(d, 0.0), 4) for d in DAYS},''',
'''                "settled_print_share": {d: round(ROUND_SHARE.get(d, 0.0), 4) for d in DAYS},
                "mirror_unsettled": sorted(NZ_UNSETTLED),
                "settled_basis": "merged_bars",''')

rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub7/flow7.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub8/flow8.json"), "w"), ensure_ascii=False)')

rep('''"""Sub-sector money-flow scoring — R7.00 engine (111 sub-sectors of the R2 heat-map workbook).''',
'''"""Sub-sector money-flow scoring — R8.00 engine (111 sub-sectors of the R2 heat-map workbook).

R8 makes R7's settled-print test source-aware. R7 measured the signature on the daily-bar
mirror and let the mirror win every overlap; on 2026-09-11 the mirror had cleared the session
(4 names left of 1,503) while Yahoo had settled it for 532, so measuring the mirror alone would
have called a settled session provisional, and the 4 mirror names would have been scored on the
live feed when a settled figure was sitting in the other source. The share is now measured over
the merged bars each ticker is actually scored from, and on a session the mirror has published
but not settled, a settled second-source bar wins the overlap. That the two sources agree once
both settle is measured, not assumed: for 2026-09-10 Yahoo's daily volume matched the settled
mirror EXACTLY on all 403 names both carry.''')
# ---- the broad Yahoo pull, so the market panel spans the market and not the report list ----
rep("""            + ";".join(sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz")))).split(";") if p]""",
    """            + ";".join(sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz"))
                          + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/broad_*.csv.gz")))).split(";") if p]""")

# ---- PROV_VOL: the settled-print test on the merged bars is now the whole test ----
# The old mirror-coverage clause asked "has the mirror published this session", which says
# nothing once a second source has settled it: on 2026-09-11 the mirror carried 1 of the 384
# scored names it usually does, while Yahoo had the settled print for 491.
rep("""PROV_VOL = sorted({d for d in seq[-(WIN + 2):] if NZ_COV[d] < 0.5 * NZ_TYP}
                  | {d for d, sh in ROUND_SHARE.items() if d in seq[-(WIN + 2):] and sh < 0.5})""",
    """PROV_VOL = sorted(d for d, sh in ROUND_SHARE.items() if d in seq[-(WIN + 2):] and sh < 0.5)""")

open(DST, "w").write(s)
print("wrote", DST, len(s), "bytes")
