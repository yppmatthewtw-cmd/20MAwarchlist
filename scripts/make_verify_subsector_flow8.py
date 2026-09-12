S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub7/verify7.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:90]); src = src.replace(a, b, 1)

rep('F = json.load(open(f"{SCR}/sub7/flow7.json"))', 'F = json.load(open(f"{SCR}/sub8/flow8.json"))')

# the old coverage heuristic survives only as a printed diagnostic; relabel it so the output
# cannot be read as a provisional-volume verdict (the settled-print test below is the verdict)
rep('print(f"provisional-volume sessions: {prov or \'none\'} (mirror coverage {[nzc[d] for d in DAYS]}, typical {typ:.0f})")',
    'print(f"mirror-coverage diagnostic (not the verdict): {prov or \'none\'} '
    '(coverage {[nzc[d] for d in DAYS]}, typical {typ:.0f})")')

# the broad pull, loaded here independently
rep('''YFILES = ["/home/user/yppmatthewtw-cmd/10ma-watchlist/data/yahoo/eod_2025-12-26_2026-09-05.csv.gz"] + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz"))''',
    '''YFILES = (["/home/user/yppmatthewtw-cmd/10ma-watchlist/data/yahoo/eod_2025-12-26_2026-09-05.csv.gz"]
          + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz"))
          + sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/broad_*.csv.gz")))''')

# C2: recompute, from the raw mirror files, which sessions the mirror has not settled
rep('''SINCE = M.get("merge_since")
def merged(sym):''',
'''SINCE = M.get("merge_since")
# C2 re-derived: a mirror session is "not settled" when its volumes are not vendor-rounded, or
# when the mirror is mid-repopulation and carries a fraction of its usual names.
_mv = collections.defaultdict(lambda: [0, 0])
for _f in os.listdir(NZ):
    if not _f.endswith(".csv"): continue
    for _d, _b in (nzraw(_f[:-4].replace("-", ".")) or {}).items():
        if _d < "2026-08-01" or not _b[4]: continue
        _mv[_d][0] += 1
        if abs(_b[4] - round(_b[4] / 100.0) * 100.0) < 1e-6: _mv[_d][1] += 1
_typ = statistics.median(sorted(t for t, _ in _mv.values())) if _mv else 0
NZ_UNSETTLED = {d for d, (tot, rnd) in _mv.items()
                if (tot >= 25 and rnd / tot < 0.5) or (_typ and tot < 0.5 * _typ)}
if sorted(NZ_UNSETTLED) != sorted(M.get("mirror_unsettled") or []):
    bad(f"mirror-unsettled {sorted(NZ_UNSETTLED)} != {M.get('mirror_unsettled')}")
print(f"mirror sessions published but not settled: {sorted(NZ_UNSETTLED) or 'none'} (typical {_typ:.0f})")

def merged(sym):''')

rep('''    if dev and statistics.median(dev) <= 0.005:
        m = dict(b); m.update(a); return m, "real"''',
'''    if dev and statistics.median(dev) <= 0.005:
        m = dict(b); m.update(a)
        for d in NZ_UNSETTLED:                  # C2: a settled second-source bar wins there
            if d in b: m[d] = b[d]
        return m, "real"''')

# C1: settled-print share over the MERGED bars, and PROV_VOL from that alone
rep('''def rounded_share(day):
    tot = rnd = 0
    for t in NB:
        b = (nzraw(t) or {}).get(day)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    return rnd / tot if tot else None
mine = sorted(d for d in DAYS if (rounded_share(d) or 1.0) < 0.5)''',
'''def rounded_share(day):
    """C1: measured on the bars actually scored, not on the mirror's copy."""
    tot = rnd = 0
    for t in NB:
        b = (NB[t] or {}).get(day)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    return rnd / tot if tot >= 25 else None
mine = sorted(d for d in DAYS if (rounded_share(d) or 1.0) < 0.5)''')

# the balanced panel must not have collapsed to the report universe
rep('''print("PROBLEMS:", len(P))''',
'''if len(PANEL) < 1000:
    bad(f"market panel collapsed to {len(PANEL)} names — the broad Yahoo pull is missing a session")
print("PROBLEMS:", len(P))''')
open(f"{S}/sub8/verify8.py", "w", encoding="utf-8").write(src); print("sub8/verify8.py written")
