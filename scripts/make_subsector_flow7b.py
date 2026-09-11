#!/usr/bin/env python3
"""sub7/flow7_a.py -> sub7/flow7.py : the two data-integrity fixes the R7 review found.

B1  The trading calendar demanded 80% coverage across ALL scored names, natezone-only and
    Yahoo-only alike.  Yahoo's consolidated daily bar for a session only settles overnight
    (the 2026-09-10 pull carried 4 of 535 symbols for 2026-09-10), so the newest session --
    fully published by the daily-bar mirror -- fell below the threshold and was silently
    dropped: the engine scored through 09-09 when 09-10 was available.  Coverage is now
    judged per source, and a session counts when EITHER source covers its own universe.

B2  The provisional-volume detector keyed on mirror coverage, so it reported "none" for a
    session the mirror HAS published but has not settled.  The mirror's settled bars carry a
    vendor-rounded volume (an exact multiple of 100 on 99.7% of names, every session
    2026-08-25..2026-09-09); its live-feed bars do not (1.2% on 2026-09-10).  That signature
    is now the test.  Measured on the one session where both forms survive in the mirror's
    history (2026-09-09, post-close commit vs settled, 214 names): the CLOSE is identical for
    every name, Open/High/Low move for 8-42% of them (p95 <= 0.43%), and the VOLUME is revised
    for 99.5% -- 32% by more than 1%, 9% by more than 5%, p95 +9.2%, max +37%.
    So A 方向 on such a session is exact, C 收位 is very slightly soft, and B 量能 carries a
    p95 uncertainty of about +-0.06.  That is smaller than the dollar-volume leak R7 removes,
    so the session is still scored; it is flagged instead of dropped or neutralised.
"""
import re, sys
SRC = "sub7/flow7_a.py"; DST = "sub7/flow7_b.py"
s = open(SRC).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, f"anchor x{s.count(a)} (want {n}): {a[:90]!r}"
    s = s.replace(a, b)

# ---- B1: per-source calendar ----
rep('''# ---------------- calendar: the last WIN sessions both sources agree on ----------------
nz_dates = collections.Counter()
for d in NZD.values():
    for k in d: nz_dates[k] += 1
full = sorted(k for k, n in nz_dates.items() if n >= 0.8 * len(NZD))''',
'''# ---------------- calendar: sessions that at least one source covers properly ----------------
# B1: judging coverage over the pooled universe lets one lagging source veto a real session.
# Yahoo's consolidated daily bar settles overnight, so on the evening of a session the mirror
# has it and Yahoo does not; pooled coverage then sits near the mirror's share of the universe
# (74% on 2026-09-10) and an 80% pooled threshold drops the newest close. Each source is now
# measured against its OWN universe and a session counts when either source is complete.
nz_dates = collections.Counter(); yh_dates = collections.Counter()
nz_univ = yh_univ = 0
for t in wanted:
    nzb = load_nz(t); yhb = yh_get(t)
    if nzb:
        nz_univ += 1
        for k in nzb: nz_dates[k] += 1
    if yhb:
        yh_univ += 1
        for k in yhb: yh_dates[k] += 1
alld = set(nz_dates) | set(yh_dates)
full = sorted(k for k in alld
              if (nz_univ and nz_dates[k] >= 0.8 * nz_univ) or (yh_univ and yh_dates[k] >= 0.8 * yh_univ))
SRC_COV = {k: {"mirror": nz_dates[k], "yahoo": yh_dates[k]} for k in sorted(alld)}
print(f"calendar universes: mirror {nz_univ} names, yahoo {yh_univ} names")''')

# ---- B2: settled-print detector ----
rep('''NZ_TYP = statistics.median([NZ_COV[d] for d in seq[-30:] if NZ_COV[d]]) if seq else 0
PROV_VOL = [d for d in seq[-(WIN + 2):] if NZ_COV[d] < 0.5 * NZ_TYP]
print(f"mirror coverage of the last sessions: "
      f"{ {d: NZ_COV[d] for d in seq[-6:]} } (typical {NZ_TYP:.0f})")
print(f"sessions whose volume is still provisional (mirror has not published them): {PROV_VOL or 'none'}")''',
'''NZ_TYP = statistics.median([NZ_COV[d] for d in seq[-30:] if NZ_COV[d]]) if seq else 0
# B2: coverage alone misses a session the mirror HAS published but has not settled. The mirror's
# settled bars carry a vendor-rounded volume (an exact multiple of 100 share for ~99.7% of names
# on every settled session); its live-feed bars are exact-to-the-share. Use that signature.
ROUND_SHARE = {}
for d in seq[-(WIN + 3):]:
    tot = rnd = 0
    for t in wanted:
        b = (load_nz(t) or {}).get(d)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    if tot: ROUND_SHARE[d] = rnd / tot
PROV_VOL = sorted({d for d in seq[-(WIN + 2):] if NZ_COV[d] < 0.5 * NZ_TYP}
                  | {d for d, sh in ROUND_SHARE.items() if d in seq[-(WIN + 2):] and sh < 0.5})
print(f"mirror coverage of the last sessions: "
      f"{ {d: NZ_COV[d] for d in seq[-6:]} } (typical {NZ_TYP:.0f})")
print(f"settled-print share (volume an exact multiple of 100): "
      f"{ {d: round(v, 3) for d, v in sorted(ROUND_SHARE.items())} }")
print(f"sessions whose volume is not settled yet: {PROV_VOL or 'none'}")''')

rep('''                "provisional_vol_days": PROV_VOL,
                "mirror_coverage": {d: NZ_COV[d] for d in DAYS}, "mirror_typical": NZ_TYP,''',
'''                "provisional_vol_days": PROV_VOL,
                "settled_print_share": {d: round(ROUND_SHARE.get(d, 0.0), 4) for d in DAYS},
                "prov_vol_effect": {"close": "exact", "ohl_p95": 0.0043, "vol_revised": 0.995,
                                    "vol_gt1pct": 0.322, "vol_gt5pct": 0.093, "vol_p95": 0.0919,
                                    "b_p95_uncertainty": 0.06, "measured_on": "2026-09-09", "n": 214},
                "src_coverage": {d: SRC_COV.get(d, {}) for d in DAYS},
                "mirror_coverage": {d: NZ_COV[d] for d in DAYS}, "mirror_typical": NZ_TYP,''')

# docstring: record the two fixes at the top
rep('''R6 adds a provisional-volume detector''',
'''R7 also repairs two data-integrity defects the R6.00 review found:
  B1  the trading calendar required 80% coverage over the POOLED universe, so Yahoo -- whose
      consolidated daily bar settles overnight -- vetoed the newest session even though the
      daily-bar mirror had published it in full (the 2026-09-10 Yahoo pull carried 4 of 535
      symbols for that date). Coverage is now judged per source.
  B2  the provisional-volume detector keyed on mirror coverage and therefore reported "none"
      for a session the mirror has published but not settled. Settled mirror bars carry a
      vendor-rounded volume (multiple of 100 on 99.7% of names on every session from
      2026-08-25 to 2026-09-09; 1.2% on 2026-09-10); that signature is now the test. On the
      one session where both forms survive in the mirror's history (2026-09-09, 214 names):
      the close is identical for every name, O/H/L move for 8-42% of them (p95 <= 0.43%), and
      volume is revised for 99.5% -- 32% by >1%, 9% by >5%, p95 +9.2%. So the session is
      scored (A is exact, C very slightly soft, B carries about +-0.06 of p95 noise) and
      flagged, not dropped.

R6 adds a provisional-volume detector''')

open(DST, "w").write(s)
print("wrote", DST, len(s), "bytes")
