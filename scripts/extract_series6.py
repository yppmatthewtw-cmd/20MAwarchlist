#!/usr/bin/env python3
"""R6 series: real daily OHLCV from the natezone/market-tracker mirror,
through the 2026-08-31 close, with the 08-28 bar restored from the prior commit."""
import csv, os, glob, pickle, subprocess, sys

SCRATCH = os.environ.get("WORK_DIR", "./data")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker")
PREV = os.environ.get("NZ_PREV", "/tmp/nz_prev")          # `git archive <prior commit>` extract
HIST = f"{NZ}/data/UNIFIED/history"
PHIST = f"{PREV}/data/UNIFIED/history"
KEEP = 260            # trading days retained per ticker (metrics need <= 62)
LAST = "2026-08-31"

def read_csv(path):
    """-> {date: (close, volume)}, skipping malformed/zero rows."""
    out = {}
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                d = (row.get("Date") or "")[:10]
                if len(d) != 10:
                    continue
                try:
                    c = float(row["Close"]); v = float(row["Volume"] or 0)
                except (ValueError, KeyError, TypeError):
                    continue
                if c > 0:
                    out[d] = (c, v)
    except OSError:
        pass
    return out

files = sorted(glob.glob(f"{HIST}/*.csv"))
print(f"ticker files: {len(files)}")

raw, restored = {}, 0
for p in files:
    sym = os.path.basename(p)[:-4]
    cur = read_csv(p)
    if not cur:
        continue
    if "2026-08-28" not in cur:                      # dropped by today's run
        prev = read_csv(f"{PHIST}/{sym}.csv")
        if "2026-08-28" in prev:
            cur["2026-08-28"] = prev["2026-08-28"]
            restored += 1
    raw[sym] = cur
print(f"parsed {len(raw)} tickers; restored 2026-08-28 for {restored}")

current = {s: d for s, d in raw.items() if LAST in d}
print(f"with a {LAST} bar: {len(current)}")

# trading calendar = dates present for >=20% of current tickers (drops per-ticker gaps)
tally = {}
for d in current.values():
    for dt in d:
        tally[dt] = tally.get(dt, 0) + 1
need = max(2, int(len(current) * 0.20))
cal = sorted(dt for dt, n in tally.items() if n >= need and dt <= LAST)[-KEEP:]
print(f"calendar: {len(cal)} sessions {cal[0]} -> {cal[-1]}")
assert cal[-1] == LAST, cal[-1]

series, gapped = {}, 0
for sym, d in current.items():
    idx = [i for i, dt in enumerate(cal) if dt in d]
    if not idx:
        continue
    fi, li = idx[0], idx[-1]
    if li != len(cal) - 1:
        continue
    cs, vs, ff, gap, ok = [], [], 0, 0, True
    lastc = lastv = None
    for i in range(fi, li + 1):
        dt = cal[i]
        if dt in d:
            lastc, lastv = d[dt]; gap = 0
        else:
            gap += 1; ff += 1
            if gap > 3:
                ok = False; break
        cs.append(lastc); vs.append(lastv)
    if ok:
        series[sym] = (fi, cs, vs, ff)
    else:
        gapped += 1
print(f"aligned: {len(series)} (dropped {gapped} with a >3-session gap)")

pickle.dump({"cal": cal, "series": series}, open(f"{SCRATCH}/series6.pkl", "wb"))
print("saved", f"{SCRATCH}/series6.pkl")

# ---- cross-validate against the R5 series (independent Nasdaq-snapshot lineage) ----
try:
    old = pickle.load(open(f"{SCRATCH}/series2.pkl", "rb"))
except OSError:
    sys.exit(0)
ocal, oser = old["cal"], old["series"]
opos = {d: i for i, d in enumerate(ocal)}
checks, agree, devs = 0, 0, []
for sym in list(series)[:4000]:
    if sym not in oser:
        continue
    fi, cs, vs, ff = series[sym]
    ofi, ocs, ovs, off = oser[sym]
    for dt in ("2026-08-27", "2026-08-28"):
        if dt not in opos:
            continue
        oi = opos[dt] - ofi
        ni = cal.index(dt) - fi if dt in cal else -1
        if 0 <= oi < len(ocs) and 0 <= ni < len(cs):
            a, b = ocs[oi], cs[ni]
            checks += 1
            dev = abs(a - b) / b * 100
            devs.append(dev)
            if dev < 0.5:
                agree += 1
devs.sort()
if checks:
    print(f"\ncross-check vs R5 lineage: {agree}/{checks} within 0.5% "
          f"({agree/checks*100:.1f}%); median dev {devs[len(devs)//2]:.3f}%")
