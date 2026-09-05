#!/usr/bin/env python3
"""series10.pkl = series9.pkl (through 2026-09-02) + the 2026-09-03 session,
plus a back-fill of the 09-02 volumes that were unpublished when series9 was built.

Data timing, as observed on 2026-09-05 03:12 UTC:
  * natezone/market-tracker publishes a complete OHLCV bar for session D roughly one
    calendar day later.  Its newest commit (1e18ccc, 2026-09-05 00:11 UTC) therefore
    carries a FULL 09-03 bar and only a volume-only stub for 09-04.
  * zyhe16/top-us-stock-tickers' newest snapshot (7bbf53a, 2026-09-04 14:24 UTC =
    10:24 ET) was taken INTRADAY on 09-04, so its `price` is a live 09-04 quote and its
    `volume` a partial 09-04 day.  What it does carry reliably is
    `price - price_change` = the official 09-03 close, for the whole universe.
  => 2026-09-03 is the newest US session with a published close anywhere reachable.
     09-04's close does not exist in any mirror yet (only its volume does).

Volume for 09-03 outside the daily-bar mirror is therefore unknown and is recorded as
unknown (never invented); the same treatment 09-02 got in series9, which this script now
repairs for the ~1.5k names the mirror has since published.
"""
import csv, io, os, pickle, statistics, subprocess

SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
REPO = os.environ.get("TICKERS_REPO", "/home/user/zyhe16/top-us-stock-tickers")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"
SNAP = "7bbf53a"; NEW = "2026-09-03"; PREV = "2026-09-02"

d = pickle.load(open(f"{SCR}/series9.pkl", "rb"))
CAL = d["cal"]; SER = d["series"]; META8 = d.get("meta8", {}); META9 = d.get("meta9", {})
assert CAL[-1] == PREV, CAL[-1]
OLD_NOVOL = set(META9.get("no_volume", []))

blob = subprocess.run(["git", "-C", REPO, "show", f"{SNAP}:data/v2/tickers.csv"],
                      capture_output=True, text=True, check=True).stdout
snap = {}
for row in csv.DictReader(io.StringIO(blob.lstrip("﻿"))):
    try: snap[row["symbol"].strip()] = (float(row["price"]), float(row["price_change"]))
    except (ValueError, KeyError): pass

nz_new, nz_prev = {}, {}
for f in os.listdir(NZ):
    if not f.endswith(".csv"): continue
    sym = f[:-4]
    for row in csv.DictReader(open(f"{NZ}/{f}")):
        dt = (row.get("Date") or "")[:10]
        if dt not in (NEW, PREV): continue
        if not (row.get("Close") or "").strip(): continue
        try: c, v = float(row["Close"]), float(row["Volume"] or 0)
        except ValueError: continue
        if c > 0: (nz_new if dt == NEW else nz_prev)[sym] = (c, v)
print(f"snapshot rows {len(snap)} | daily-bar {NEW} closes {len(nz_new)} | {PREV} closes {len(nz_prev)}")

dev = [abs((p - chg) - nz_new[s][0]) / nz_new[s][0] * 100
       for s, (p, chg) in snap.items() if s in nz_new and nz_new[s][0] > 0]
print(f"{NEW} implied close vs daily mirror: n={len(dev)}, median {statistics.median(dev):.4f}%, "
      f">0.5% {sum(x > .5 for x in dev)}, >2% {sum(x > 2 for x in dev)}")

CAL2 = CAL + [NEW]
out = {}; added = 0; novol = []; fixed = 0; still = []
for s, (fi, cs, vs, ff) in SER.items():
    cs, vs = list(cs), list(vs)
    # --- back-fill the 09-02 volume the mirror has published since series9 ---
    if s in OLD_NOVOL and fi + len(cs) == len(CAL) and s in nz_prev and nz_prev[s][1] > 0:
        vs[-1] = nz_prev[s][1]; fixed += 1
    elif s in OLD_NOVOL and fi + len(cs) == len(CAL):
        still.append(s)
    # --- append the 09-03 session ---
    if fi + len(cs) == len(CAL):
        c = v = None
        if s in nz_new and nz_new[s][0] > 0:
            c, v = nz_new[s]
        elif s in snap:
            imp = snap[s][0] - snap[s][1]
            if imp > 0: c, v = imp, None
        if c:
            cs.append(c); vs.append(v if v is not None else 0.0); added += 1
            if v is None: novol.append(s)
    out[s] = (fi, cs, vs, ff)

# ---- back-fill the one prior close the 08-28 feed intake never carried -------------------
# The feed added ~1.4k foreign issuers and ADRs (TSM, ASML, ARM, TEAM, SHOP, NVO, DEO, INFY,
# TECK, CCJ, AEM, KGC, UUUU, WCN ...) on 2026-08-28, so their series starts that day and the
# first scored session has no previous close to measure a return against.  The 08-28 21:03 UTC
# commit (6733016) was taken 17:03 ET, AFTER the close: its `price` reproduces the 08-28 close
# already in the series (n=6866, median deviation 0.0000%, none above 0.5%) and its
# `price - price_change` is therefore the official 08-27 close.  Volume stays unknown.
POST = "6733016"; PRIOR = "2026-08-27"
blob2 = subprocess.run(["git", "-C", REPO, "show", f"{POST}:data/v2/tickers.csv"],
                       capture_output=True, text=True, check=True).stdout
post = {}
for row in csv.DictReader(io.StringIO(blob2.lstrip("\ufeff"))):
    try: post[row["symbol"].strip()] = (float(row["price"]), float(row["price_change"]))
    except (ValueError, KeyError): pass
i28, i27 = CAL2.index("2026-08-28"), CAL2.index(PRIOR)
chk = [abs(post[s][0] - out[s][1][i28 - out[s][0]]) / out[s][1][i28 - out[s][0]] * 100
       for s in out if s in post and out[s][0] <= i28 < out[s][0] + len(out[s][1]) and out[s][1][i28 - out[s][0]] > 0]
print(f"6733016 price vs series 08-28 close: n={len(chk)}, median {statistics.median(chk):.4f}%, "
      f">0.5% {sum(x > .5 for x in chk)}")
back = []
for s, (fi, cs, vs, ff) in list(out.items()):
    if fi != i28 or s not in post: continue
    p0 = post[s][0] - post[s][1]
    if p0 <= 0 or not (0.5 < post[s][0] / p0 < 2.0): continue
    out[s] = (i27, [p0] + list(cs), [0.0] + list(vs), ff)      # volume unknown -> 0.0 -> treated as None
    back.append(s)
print(f"prior-close back-fill for {len(back)} names first seen on 2026-08-28")

meta10 = {"added_date": NEW, "n_added": added, "snapshot": SNAP,
          "real_bars": sorted(nz_new), "no_volume": sorted(novol),
          "close_dev_median": round(statistics.median(dev), 4) if dev else None,
          "vol_backfilled_prev": fixed, "prev_date": PREV,
          "novol_by_date": {PREV: sorted(still), NEW: sorted(novol), PRIOR: sorted(back)},
          "prior_close_backfill": sorted(back), "prior_close_date": PRIOR,
          "prior_close_snapshot": POST, "note_0904": "2026-09-04 close unpublished in every reachable mirror as of "
                       "2026-09-05 03:12 UTC (natezone carries volume only; zyhe16's newest "
                       "snapshot is intraday 09-04)."}
# keep meta9 readable by older consumers, with its no_volume list narrowed to what is still unknown
META9 = dict(META9); META9["no_volume"] = sorted(still); META9["vol_backfilled"] = fixed
pickle.dump({"cal": CAL2, "series": out, "meta8": META8, "meta9": META9, "meta10": meta10},
            open(f"{SCR}/series10.pkl", "wb"))
print(f"series10.pkl: {NEW} added for {added} names — {added - len(novol)} with real volume, "
      f"{len(novol)} close-only | {PREV} volumes back-filled for {fixed} (still unknown {len(still)}) | "
      f"calendar {len(CAL2)} days")
