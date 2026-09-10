S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub5/flow5.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
rep('"""Sub-sector money-flow scoring — R5.00 engine (111 sub-sectors of the R2 heat-map workbook).',
 '"""Sub-sector money-flow scoring — R6.00 engine (111 sub-sectors of the R2 heat-map workbook).\n\n'
 'R6 adds a provisional-volume detector, from what the R5.00 review measured: a session\'s volume\n'
 'is NOT final on the day it first appears. Comparing the 2026-09-04 volumes the daily-bar mirror\n'
 'first published (its 09-05 00:11 UTC commit) with the same session five days later, 255 of 256\n'
 'sampled names had been revised — 34% by more than 1%, 11% by more than 5%, 95th percentile\n'
 '+11.4%. A session carried only by Yahoo (which settles overnight) is therefore still moving,\n'
 'and the volume term B computed on it is provisional. Such sessions are now identified from\n'
 'per-day mirror coverage and recorded, so the report can say which day is not yet settled.')
# per-day mirror coverage -> provisional-volume sessions
rep('''CALSEQ = seq          # every session the bar sources agree on, oldest first''',
'''# how many of the scored universe the mirror itself carries, per session: a day the mirror has
# not published yet reaches us through Yahoo alone and its volume is still provisional.
NZ_COV = collections.Counter()
for t in wanted:
    for d in (load_nz(t) or {}): NZ_COV[d] += 1
NZ_TYP = statistics.median([NZ_COV[d] for d in seq[-30:] if NZ_COV[d]]) if seq else 0
PROV_VOL = [d for d in seq[-(WIN + 2):] if NZ_COV[d] < 0.5 * NZ_TYP]
print(f"mirror coverage of the last sessions: "
      f"{ {d: NZ_COV[d] for d in seq[-6:]} } (typical {NZ_TYP:.0f})")
print(f"sessions whose volume is still provisional (mirror has not published them): {PROV_VOL or 'none'}")

CALSEQ = seq          # every session the bar sources agree on, oldest first''')
rep('''                "stale_mirror": sorted(STALE), "merge_since": SINCE,''',
'''                "stale_mirror": sorted(STALE), "merge_since": SINCE,
                "provisional_vol_days": PROV_VOL,
                "mirror_coverage": {d: NZ_COV[d] for d in DAYS}, "mirror_typical": NZ_TYP,''')
rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub5/flow5.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub6/flow6.json"), "w"), ensure_ascii=False)')

# ---- balanced market panel (R6 review fix) --------------------------------------------
rep("""MKT = {}
for day in DAYS:
    prev = LAST[LAST.index(day) - 1]
    rets = [d[day][3] / d[prev][3] - 1 for d in allnz.values() if day in d and prev in d and d[prev][3] > 0]
    MKT[day] = statistics.median(rets)
    MKT.setdefault("_n", {})[day] = len(rets)""",
"""# The market baseline must be the SAME universe every day, or a day the broad Yahoo file has
# not reached yet is measured against a different (large-cap-heavy) crowd than its neighbours.
# R5 left it unbalanced: on 2026-09-08 the pool fell from 2,851 names to 1,632, and on the days
# where the broad file was present the median differed from the balanced panel by up to 0.20pp
# — enough to move A by ~0.10 for a name sitting at zero excess return. So the panel is now
# restricted to names quoted on every scored session and on each session's predecessor.
NEED = set(DAYS) | {LAST[LAST.index(d) - 1] for d in DAYS}
PANEL = {s: d for s, d in allnz.items() if NEED <= set(d)}
print(f"market panel: {len(PANEL)} names quoted on all {len(NEED)} sessions "
      f"(unbalanced pool was {len(allnz)})")
MKT = {}
for day in DAYS:
    prev = LAST[LAST.index(day) - 1]
    rets = [d[day][3] / d[prev][3] - 1 for d in PANEL.values() if d[prev][3] > 0]
    MKT[day] = statistics.median(rets)
    MKT.setdefault("_n", {})[day] = len(rets)""")
rep('"mirror_coverage": {d: NZ_COV[d] for d in DAYS}, "mirror_typical": NZ_TYP,',
    '"mirror_coverage": {d: NZ_COV[d] for d in DAYS}, "mirror_typical": NZ_TYP,\n'
    '                "panel_balanced": True, "panel_pool": len(allnz),')

open(f"{S}/sub6/flow6.py","w",encoding="utf-8").write(src); print("sub6/flow6.py written")
