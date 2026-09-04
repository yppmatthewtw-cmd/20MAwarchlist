#!/usr/bin/env python3
"""series8.pkl: R7 series (series7b.pkl) with every missing-snapshot session repaired,
the 08-27 pre-settlement volumes corrected, and unadjusted stock splits back-adjusted.

Missing sessions (the Nasdaq-snapshot mirror had no commit) are repaired per name:
  1. real daily bar from natezone/market-tracker (S&P 1500), scaled by the series/natezone
     close ratio on the nearest genuine snapshot day (natezone closes are dividend-adjusted)
  2. 2026-08-31 only: official close implied by the 09-01 snapshot (price - price_change)
  3. otherwise linear interpolation between the nearest real snapshot closes
Volume on an estimated bar = mean of the neighbouring real bars. The 08-27 snapshot was taken
at 16:05 ET before consolidated volume settled (median 0.62x of the daily-bar mirror); names
without a real bar get that day's volume scaled by the cross-sectional median ratio.
Splits: a one-day close ratio within 1.5% of a standard split ratio is back-adjusted when the
implied share count (marketCap/price across the two snapshots) or the adjusted natezone bar
confirms it. meta8 records every estimated bar and every split so the report can flag them."""
import csv, io, os, pickle, subprocess, statistics, datetime, re
SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
REPO = os.environ.get("TICKERS_REPO", "/home/user/zyhe16/top-us-stock-tickers")
NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker")
SNAP_SHA = "7dc8799"   # 2026-09-01 22:44 UTC post-close snapshot
src = open(f"{SCR}/extract_series7b.py").read()
exec(src[src.index("HOLIDAYS = {"):src.index("log = subprocess.run")])   # calendar helpers
d = pickle.load(open(f"{SCR}/series7b.pkl", "rb")); cal = d["cal"]; S = d["series"]
N = len(cal); cidx = {c: i for i, c in enumerate(cal)}
log = subprocess.run(["git", "-C", REPO, "log", "origin/main", "--format=%H|%aI|%s"], capture_output=True, text=True, check=True).stdout
snap = {}
for line in log.strip().split("\n"):
    sha, iso, subj = line.split("|", 2)
    if "auto-update ticker lists" not in subj.lower(): continue
    ts = datetime.datetime.fromisoformat(iso).astimezone(datetime.timezone.utc)
    dd = commit_to_date(ts).isoformat()
    if dd not in snap or ts > snap[dd][0]: snap[dd] = (ts, sha)
missing = [c for c in cal if c not in snap]
print("missing-snapshot sessions:", missing, "| in last 60 bars:", [c for c in missing if cidx[c] >= N - 60])

# ---- natezone daily bars (full history per overlapping name) ----
nzdir = f"{NZ}/data/UNIFIED/history"
nz = {}
for fn in os.listdir(nzdir):
    sym = fn[:-4]
    if sym not in S: continue
    rows = {}
    with open(f"{nzdir}/{fn}", newline="") as f:
        for row in csv.DictReader(f):
            dd = (row.get("Date") or "")[:10]
            try: c, v = float(row["Close"] or 0), float(row["Volume"] or 0)
            except ValueError: continue
            if c > 0: rows[dd] = (c, v)
    if rows: nz[sym] = rows

blob = subprocess.run(["git", "-C", REPO, "show", f"{SNAP_SHA}:data/v2/tickers.csv"], capture_output=True, text=True, check=True).stdout
implied = {}
for row in csv.DictReader(io.StringIO(blob.lstrip("﻿"))):
    try: implied[row["symbol"].strip()] = (float(row["price"]), float(row["price_change"]))
    except (ValueError, KeyError): pass

# 08-27 cross-sectional volume ratio (snapshot / real) over the overlap
i27 = cidx["2026-08-27"]
r27 = []
for sym, rows in nz.items():
    if "2026-08-27" in rows:
        fi, cs, vs, ff = S[sym]; j = i27 - fi
        if 0 <= j < len(vs) and vs[j] > 0 and rows["2026-08-27"][1] > 0: r27.append(vs[j] / rows["2026-08-27"][1])
med27 = statistics.median(r27); print(f"08-27 snapshot/real volume median ratio {med27:.3f} over {len(r27)} names")

def nearest_real(sym, i, fi, li):
    """nearest earlier (then later) calendar index with a genuine snapshot bar and a natezone bar"""
    for k in list(range(i - 1, fi - 1, -1)) + list(range(i + 1, li + 1)):
        if cal[k] not in missing and cal[k] in nz.get(sym, {}): return k
    return None

stats = {dd: {"real": 0, "official": 0, "interp": 0, "edge": 0, "real_unscaled": 0} for dd in missing}
est = {}      # sym -> {date: method}
new = {}
factors = []
for sym, (fi, cs, vs, ff) in S.items():
    cs, vs = list(cs), list(vs); li = fi + len(cs) - 1
    e = {}
    for dd in missing:
        i = cidx[dd]
        if i < fi or i > li: continue
        j = i - fi
        if sym in nz and dd in nz[sym]:
            k = nearest_real(sym, i, fi, li)
            fac = None
            if k is not None:
                nzc = nz[sym][cal[k]][0]
                if nzc > 0: fac = S[sym][1][k - fi] / nzc
            if fac is not None and 0.9 < fac < 1.1:
                cs[j] = round(nz[sym][dd][0] * fac, 4); vs[j] = nz[sym][dd][1]
                e[dd] = "real"; stats[dd]["real"] += 1; factors.append(fac); continue
            elif fac is None:
                cs[j], vs[j] = nz[sym][dd]; e[dd] = "real"; stats[dd]["real_unscaled"] += 1; continue
            # factor outside 0.9-1.1 (split/odd): fall through to official/interp
        if dd == "2026-08-31" and sym in implied:
            p, chg = implied[sym]; op = round(p - chg, 4)
            if op > 0 and abs(p / op - 1) < 0.5 and j + 1 < len(cs):
                cs[j] = op; vs[j] = (vs[j - 1] + vs[j + 1]) / 2.0 if j >= 1 else vs[j + 1]
                e[dd] = "official"; stats[dd]["official"] += 1; continue
        a = i - 1
        while a >= fi and cal[a] in missing: a -= 1
        b = i + 1
        while b <= li and cal[b] in missing: b += 1
        if a >= fi and b <= li:
            ca, cb = S[sym][1][a - fi], S[sym][1][b - fi]; va, vb = S[sym][2][a - fi], S[sym][2][b - fi]
            w = (i - a) / (b - a)
            cs[j] = round(ca + (cb - ca) * w, 4); vs[j] = va + (vb - va) * w
            e[dd] = "interp"; stats[dd]["interp"] += 1
        else:
            e[dd] = "edge"; stats[dd]["edge"] += 1
    j = i27 - fi
    if 0 <= j < len(vs):
        if sym in nz and "2026-08-27" in nz[sym]: vs[j] = nz[sym]["2026-08-27"][1]
        elif vs[j] > 0: vs[j] = vs[j] / med27; e["2026-08-27"] = "vol_scaled"
    if e: est[sym] = e
    new[sym] = (fi, cs, vs, ff)
print("natezone scale factor: median %.4f, p5 %.4f, p95 %.4f" % (statistics.median(factors), sorted(factors)[len(factors)//20], sorted(factors)[-len(factors)//20]))

# ---- split back-adjustment ----
RATIOS = {2, 3, 4, 5, 6, 8, 10, 1.5, 2/3, 1/2, 1/3, 1/4, 1/5, 1/6, 1/8, 1/10, 1/12, 1/15, 1/20, 1/25, 1/30, 1/40, 1/50}
mc_cache = {}
def mcap_price(sha, sym):
    if sha not in mc_cache:
        blob = subprocess.run(["git", "-C", REPO, "show", f"{sha}:tickers/all.csv"], capture_output=True, text=True).stdout
        m = {}
        for row in csv.DictReader(io.StringIO(blob.lstrip("﻿"))):
            try: m[row["symbol"].strip()] = (float(row.get("marketCap") or row.get("market_cap") or 0), float(row["price"]))
            except (ValueError, KeyError): pass
        mc_cache[sha] = m
    return mc_cache[sha].get(sym)
splits = []
for sym, (fi, cs, vs, ff) in new.items():
    li = fi + len(cs) - 1
    for i in range(fi + 1, li + 1):
        j = i - fi
        if cal[i] in missing or cal[i - 1] in missing or cs[j - 1] <= 0: continue
        r = cs[j] / cs[j - 1]
        hit = next((x for x in RATIOS if abs(r / x - 1) < 0.015), None)
        if hit is None: continue
        confirmed = None
        # (1) the adjusted daily-bar mirror is authoritative where it covers the name:
        #     no jump there = split; the same jump there = a real price move
        if sym in nz and cal[i] in nz[sym] and cal[i - 1] in nz[sym]:
            nr = nz[sym][cal[i]][0] / nz[sym][cal[i - 1]][0]
            confirmed = "natezone" if (abs(nr / r - 1) > 0.25 and abs(nr - 1) < 0.25) else False
        # (2) otherwise the implied share count across the two snapshots (or a week later)
        if confirmed is None:
            a = mcap_price(snap[cal[i - 1]][1], sym); b = mcap_price(snap[cal[i]][1], sym)
            later = [c for c in cal[i + 1:i + 8] if c in snap]
            b2 = mcap_price(snap[later[-1]][1], sym) if later else None
            for bb in (b, b2):
                if a and bb and a[0] > 0 and bb[0] > 0 and a[1] > 0 and bb[1] > 0:
                    sh = (bb[0] / bb[1]) / (a[0] / a[1])
                    if abs(sh * hit - 1) < 0.05: confirmed = "shares"; break
            if confirmed is None: confirmed = False
        if confirmed:
            for k in range(j):
                cs[k] = round(cs[k] * hit, 4); vs[k] = vs[k] / hit
            splits.append({"sym": sym, "date": cal[i], "ratio": round(hit, 4), "confirmed_by": confirmed})
    new[sym] = (fi, cs, vs, ff)
print("splits back-adjusted:", len(splits), [(x["sym"], x["date"], x["ratio"], x["confirmed_by"]) for x in splits][:40])

meta = {"missing_sessions": missing, "fill_stats": stats, "vol_ratio_0827": med27, "estimated": est, "splits": splits,
        "official_source": f"zyhe16 {SNAP_SHA} price-price_change", "real_source": "natezone/market-tracker 00fc782 (dividend-ratio scaled)"}
pickle.dump({"cal": cal, "series": new, "meta8": meta}, open(f"{SCR}/series8.pkl", "wb"))
for dd in missing: print(dd, stats[dd])
print("names with any estimated bar:", sum(1 for s, e in est.items() if any(m in ("official", "interp") for m in e.values())))
