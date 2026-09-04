#!/usr/bin/env python3
"""series9.pkl = series8.pkl (through 2026-09-01) + the 2026-09-02 session.

The only zyhe16 commit after the 09-02 close (47251a8, 2026-09-03 14:37 UTC) was taken
10:37 ET — i.e. INTRADAY on 09-03, not post-close. So its `price` is a live 09-03 quote and
its `volume` is a partial 09-03 day; what it does carry reliably is `price - price_change`
= the official 09-02 close. Volume for 09-02 therefore comes only from the daily-bar mirror,
and names outside that mirror carry an unknown 09-02 volume (recorded, not invented).
"""
import csv, io, os, pickle, statistics, subprocess
SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
REPO = os.environ.get("TICKERS_REPO", "/home/user/zyhe16/top-us-stock-tickers")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"
SNAP = "47251a8"; NEW = "2026-09-02"; PREV = "2026-09-01"

d = pickle.load(open(f"{SCR}/series8.pkl", "rb")); CAL = d["cal"]; SER = d["series"]; META = d.get("meta8", {})
assert CAL[-1] == PREV, CAL[-1]
blob = subprocess.run(["git", "-C", REPO, "show", f"{SNAP}:data/v2/tickers.csv"],
                      capture_output=True, text=True, check=True).stdout
snap = {}
for row in csv.DictReader(io.StringIO(blob.lstrip("﻿"))):
    try: snap[row["symbol"].strip()] = (float(row["price"]), float(row["price_change"]))
    except (ValueError, KeyError): pass
nz = {}
for f in os.listdir(NZ):
    sym = f[:-4]
    for row in csv.DictReader(open(f"{NZ}/{f}")):
        if row["Date"][:10] == NEW and (row.get("Close") or "").strip():
            nz[sym] = (float(row["Close"]), float(row["Volume"] or 0)); break
print(f"snapshot rows {len(snap)} | daily-bar 09-02 closes {len(nz)}")

# cross-check: implied official close from the snapshot vs the real daily bar
dev = [abs((p - chg) - nz[s][0]) / nz[s][0] * 100 for s, (p, chg) in snap.items() if s in nz and nz[s][0] > 0]
print(f"09-02 implied close vs daily mirror: n={len(dev)}, median {statistics.median(dev):.4f}%, "
      f">0.5% {sum(x > .5 for x in dev)}, >2% {sum(x > 2 for x in dev)}")

CAL2 = CAL + [NEW]
out = {}; added = 0; novol = []
for s, (fi, cs, vs, ff) in SER.items():
    cs, vs = list(cs), list(vs)
    if fi + len(cs) == len(CAL):
        c = v = None
        if s in nz and nz[s][0] > 0:
            c, v = nz[s]
        elif s in snap:
            op = snap[s][0] - snap[s][1]
            if op > 0: c, v = op, None
        if c:
            cs.append(c); vs.append(v if v is not None else 0.0); added += 1
            if v is None: novol.append(s)
    out[s] = (fi, cs, vs, ff)
pickle.dump({"cal": CAL2, "series": out, "meta8": META,
             "meta9": {"added_date": NEW, "n_added": added, "snapshot": SNAP,
                       "real_bars": sorted(nz), "no_volume": sorted(novol),
                       "close_dev_median": round(statistics.median(dev), 4) if dev else None}},
            open(f"{SCR}/series9.pkl", "wb"))
print(f"series9.pkl: {NEW} added for {added} names — {added - len(novol)} with real volume, "
      f"{len(novol)} close-only (volume unknown); calendar {len(CAL2)} days")
