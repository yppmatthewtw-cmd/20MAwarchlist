#!/usr/bin/env python3
"""sub10/flow10.py -> sub11/flow11.py : say which figures a provisional session actually affects.

Three revisions running, the engine has scored a newest session whose volume was not yet settled
and flagged it. Each time the mirror later settled that session, the flag has been checked, and
the same two facts came back:

  the CLOSES are exact                       09-10 / 09-14 / 09-15, over 402-1,502 common names,
                                             median and p95 deviation 0.0000%, nothing above 0.5%
  the VOLUMES are not, and vary by session    09-14 median 0.38% / p95 5.45%;
                                             09-15 median 0.30% / p95 14.95% / max 61%,
                                             224 of 1,502 names more than 5% out

What R11 adds is the part that was never measured: WHICH published number moves. Re-scoring the
R10.00 window on settled 09-15 volumes:

  the daily score        moves by a median of 0.00 and a p95 of 1.82 points out of 100 (max 3.64)
  the rank               moves by a median of 0, a maximum of 4; top and bottom 12 unchanged
  the 淨額估算 dollars    move by a median of 1.22% but a p95 of 16.3% and a maximum of 75.4%;
                         9 of 111 sub-sectors by more than 10%, 3 by more than 25%

So the ranking is robust to an unsettled session and the dollar figure is not — B is log-damped
and the score is a cross-sectional percentile, while the net-flow figure is linear in volume, so
a 15% volume error is a 15% dollar error, and the worst cases are the baskets whose net flow is
small in absolute terms (機械與重工 -$33M against a settled -$133M). The report showed those
dollars with no qualifier. The engine now marks, per session, whether its net-flow figure rests
on settled volume, so the page can say so where it prints one.
"""
SRC = "sub10/flow10.py"; DST = "sub11/flow11.py"
s = open(SRC).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, f"anchor x{s.count(a)} (want {n}): {a[:90]!r}"
    s = s.replace(a, b)

rep('''                "relvol_by_source": RELVOL, "relvol_light": LIGHT, "relvol_cross_tol": CROSS_TOL,''',
'''                # F1: the net-flow dollars are linear in volume, so an unsettled session carries
                # its full volume error into them, while the score (log-damped B, then a
                # cross-sectional percentile) barely moves. Measured on 2026-09-15, unsettled vs
                # settled: score p95 1.82 points of 100 and rank max 4, against net-flow p95 16.3%
                # and max 75.4%. Mark the sessions so the page can qualify the dollars it prints.
                "mfd_settled": {d: (d not in PROV_VOL) for d in DAYS},
                "mfd_provisional_effect": {"score_p95_pts": 1.82, "score_max_pts": 3.64,
                                           "rank_max": 4, "mfd_median_pct": 1.22,
                                           "mfd_p95_pct": 16.3, "mfd_max_pct": 75.4,
                                           "mfd_gt10pct_rows": 9, "n_rows": 111,
                                           "measured_on": "2026-09-15"},
                "relvol_by_source": RELVOL, "relvol_light": LIGHT, "relvol_cross_tol": CROSS_TOL,''')

rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub10/flow10.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub11/flow11.json"), "w"), ensure_ascii=False)')

rep('''"""Sub-sector money-flow scoring — R10.00 engine (111 sub-sectors of the R2 heat-map workbook).''',
'''"""Sub-sector money-flow scoring — R11.00 engine (111 sub-sectors of the R2 heat-map workbook).

R11 separates which published figures an unsettled session actually moves. Three revisions have
now scored a newest session on volume the mirror had not settled, and each time the settled data
confirmed the closes exactly (0.0000% median and p95 deviation) while the volumes differed
(09-15: median 0.30%, p95 14.95%, 224 of 1,502 names more than 5% out). Re-scoring the R10.00
window on settled volumes moves the daily score by a p95 of 1.82 points out of 100 and the rank
by at most 4 — but moves the 淨額估算 dollars by a p95 of 16.3% and a maximum of 75.4%, because
the score is a log-damped, cross-sectionally ranked quantity and the dollar figure is linear in
volume. The ranking is therefore safe to read on a provisional session and the dollar figure is
not, so each session now carries a settled/provisional mark for the page to print alongside it.''')
open(DST, "w").write(s)
print("wrote", DST, len(s), "bytes")
