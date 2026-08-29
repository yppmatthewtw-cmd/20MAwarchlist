#!/usr/bin/env python3
"""20MA uptrend watchlist R2 screener.

Pages (timeframe W = trading-day window over which the MA must be rising; L = MA length):
  P2: L=10, W=5   (1 week)      P3: L=20, W=10  (2 weeks)
  P4: L=20, W=21  (1 month)     P5: L=20, W=42  (2 months)

Per page a ticker qualifies iff:
  1. MA_L[t] > MA_L[t-W]; MA_L strictly rising over the last 3 obs;
     >=70% of MA_L one-day diffs positive within the window W.
  2. Higher-lows structure (R1 definition, close-based):
     bottom i: close[i] == min(close[i-3..i+3]) and close[i-3] > close[i] < close[i+3];
     dedupe bottoms <=3 obs apart (keep lower); all bottoms within last 45 obs
     strictly ascending, >=2 of them, most recent within last 25 obs.
  3. Basic eligibility: >=90 obs, close >= $2, median 20-day dollar volume >= $1M.

Ranking inside each page: VCP index desc (volatility contraction; higher = tighter).
Page 1 explosive-potential score = 0.7*VCP + 0.3*(pages_qualified/4*100).
"""
import csv, io, json, math, os, pickle, statistics, subprocess

SCRATCH = os.environ.get("WORK_DIR", "./data")
ZREPO = os.environ.get("TICKERS_REPO", "/home/user/zyhe16/top-us-stock-tickers")
MC = os.environ.get("CHRONICLE_REPO", "/home/user/klaywang24/market-chronicle")
IRA = os.environ.get("OPENSTOCK_REPO", "/home/user/irachex/open-stock-data")

d = pickle.load(open(f"{SCRATCH}/series2.pkl", "rb"))
CAL, SER = d["cal"], d["series"]
LAST_DATE = CAL[-1]

# ---------------- metadata ----------------
def norm(sym):  # BRK/A -> BRK.A ; drop ^ suffixes
    return sym.replace("/", ".").strip().upper()

meta = {}
blob = subprocess.run(["git", "-C", ZREPO, "show", "HEAD:data/v2/tickers.csv"],
                      capture_output=True, text=True).stdout
for row in csv.DictReader(io.StringIO(blob.lstrip("﻿"))):
    s = row["symbol"].strip()
    meta[s] = {
        "name": row["name"].split(" Common Stock")[0].split(" Ordinary Shares")[0].strip().rstrip(","),
        "sector": row["sector"].strip() or "—",
        "industry": row["industry"].strip() or "—",
        "country": row["country"].strip(),
        "sp500": row["is_sp500"].strip() == "True",
        "mcap": float(row["market_cap"] or 0),
    }

gics = {}
mcj = json.load(open(f"{MC}/data/sp500_constituents.json"))
for r in mcj["rows"]:
    gics[norm(r["ticker"])] = {"gsec": r["sector"], "gsub": r["sub"]}

exch = {}
for ex in ("NASDAQ", "NYSE", "AMEX"):
    with open(f"{IRA}/symbols/{ex}.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            exch[norm(row["code"])] = ex

ZH_SECTOR = {  # Nasdaq screener sector taxonomy -> zh-Hant
    "Technology": "科技", "Consumer Discretionary": "非必需消費", "Health Care": "醫療保健",
    "Finance": "金融", "Industrials": "工業", "Consumer Staples": "必需消費",
    "Energy": "能源", "Real Estate": "房地產", "Utilities": "公用事業",
    "Basic Materials": "原材料", "Telecommunications": "電訊", "Miscellaneous": "其他", "—": "—",
}

# ---------------- indicator helpers ----------------
def sma_series(cs, L):
    out = [None] * len(cs)
    run = 0.0
    for i, c in enumerate(cs):
        run += c
        if i >= L: run -= cs[i - L]
        if i >= L - 1: out[i] = run / L
    return out

def find_bottoms(cs):
    """R1 bottom definition on closes. Returns list of (idx, close)."""
    n = len(cs); raw = []
    for i in range(3, n - 3):
        w = cs[i - 3:i + 4]
        if cs[i] == min(w) and cs[i - 3] > cs[i] and cs[i + 3] > cs[i]:
            raw.append((i, cs[i]))
    dedup = []
    for i, c in raw:
        if dedup and i - dedup[-1][0] <= 3:
            if c < dedup[-1][1]: dedup[-1] = (i, c)
        else:
            dedup.append((i, c))
    return dedup

def higher_lows(bots, n, look=45, recent=25):
    inw = [(i, c) for i, c in bots if i >= n - look]
    if len(inw) < 2: return None
    for a, b in zip(inw, inw[1:]):
        if b[1] <= a[1]: return None
    if inw[-1][0] < n - recent: return None
    return inw

def ma_uptrend(ma, W):
    n = len(ma)
    if n < W + 1 or ma[-1] is None or ma[-1 - W] is None: return None
    if not ma[-1] > ma[-1 - W]: return None
    if not (ma[-1] > ma[-2] > ma[-3]): return None
    diffs = [1 if ma[-k] > ma[-k - 1] else 0 for k in range(1, W + 1)]
    if sum(diffs) / W < 0.70: return None
    return (ma[-1] / ma[-1 - W] - 1) * 100  # slope % over window

# ---------------- eligibility + VCP raw components ----------------
PAGES = {2: (10, 5, "1星期"), 3: (20, 10, "2星期"), 4: (20, 21, "1個月"), 5: (20, 42, "2個月")}
elig = {}
stats_counts = {"total": len(SER), "hist": 0, "price": 0, "liq": 0}
stats_counts["current"] = 0
for sym, (fi, cs, vs, ff) in SER.items():
    if fi + len(cs) != len(CAL):  # series must extend to the last trading day
        continue
    stats_counts["current"] += 1
    if len(cs) < 90: continue
    stats_counts["hist"] += 1
    if cs[-1] < 2.0: continue
    stats_counts["price"] += 1
    dv = [c * v for c, v in zip(cs[-20:], vs[-20:])]
    if statistics.median(dv) < 1_000_000: continue
    stats_counts["liq"] += 1

    rets = [cs[i] / cs[i - 1] - 1 for i in range(1, len(cs))]
    s_rec = statistics.pstdev(rets[-10:])
    s_pri = statistics.pstdev(rets[-40:-10])
    if s_pri <= 1e-9: continue  # degenerate flat series; never fires on current data
    cr = s_rec / s_pri
    t10 = (max(cs[-10:]) - min(cs[-10:])) / cs[-1]
    v_rec = sum(vs[-10:]) / 10
    v_pri = sum(vs[-40:-10]) / 30
    vr = v_rec / v_pri if v_pri > 0 else 1.0
    blocks = [cs[-45:-30], cs[-30:-15], cs[-15:]]
    rng = [(max(b) - min(b)) / (sum(b) / len(b)) for b in blocks]
    pc = rng[2] / rng[0] if rng[0] > 1e-9 else 1.0
    elig[sym] = {"cr": cr, "t10": t10, "vr": vr, "pc": pc}

def pct_ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    for rank, i in enumerate(order):
        r[i] = rank / (len(vals) - 1) if len(vals) > 1 else 0.5
    return r

syms = list(elig)
for comp in ("cr", "t10", "vr", "pc"):
    pr = pct_ranks([elig[s][comp] for s in syms])
    for s, p in zip(syms, pr): elig[s]["pr_" + comp] = p
for s in syms:
    e = elig[s]
    e["vcp_raw"] = 100 * (0.35 * (1 - e["pr_cr"]) + 0.25 * (1 - e["pr_t10"])
                          + 0.20 * (1 - e["pr_vr"]) + 0.20 * (1 - e["pr_pc"]))
    e["vcp"] = round(e["vcp_raw"], 1)

# ---------------- per-page qualification ----------------
qual = {p: {} for p in PAGES}
for sym in syms:
    fi, cs, vs, ff = SER[sym]
    ma10 = sma_series(cs, 10); ma20 = sma_series(cs, 20)
    bots = find_bottoms(cs)
    hl = higher_lows(bots, len(cs))
    if hl is None: continue
    for p, (L, W, _) in PAGES.items():
        ma = ma10 if L == 10 else ma20
        slope = ma_uptrend(ma, W)
        if slope is None: continue
        qual[p][sym] = {"slope": slope, "ma": ma[-1], "hl": hl, "bots": bots, "L": L, "W": W}

hits = {s: sum(1 for p in PAGES if s in qual[p]) for s in syms}

def row(sym, q):
    fi, cs, vs, ff = SER[sym]
    m = meta.get(sym) or meta.get(norm(sym)) or {}
    g = gics.get(norm(sym), {})
    n = len(cs)
    off = n - 60
    spark_b = [(i - off, round(c, 4)) for i, c in q["bots"] if i >= off]
    return {
        "sym": sym, "name": m.get("name", sym), "exch": exch.get(norm(sym), "—"),
        "sector": m.get("sector", "—"), "sector_zh": ZH_SECTOR.get(m.get("sector", "—"), m.get("sector", "—")),
        "industry": m.get("industry", "—"),
        "gsec": g.get("gsec"), "gsub": g.get("gsub"), "sp500": m.get("sp500", False),
        "mcap": m.get("mcap", 0),
        "close": round(cs[-1], 2), "ma": round(q["ma"], 2), "below_ma": cs[-1] < q["ma"],
        "slope": round(q["slope"], 2), "L": q["L"], "W": q["W"],
        "vcp": elig[sym]["vcp"], "_vcpr": elig[sym]["vcp_raw"],
        "vcp_c": {k: round(elig[sym][k], 4) for k in ("cr", "t10", "vr", "pc")},
        "hits": hits[sym],
        "hl": [[CAL[SER[sym][0] + i] if False else CAL[i + SER[sym][0]], round(c, 4)] for i, c in q["hl"]],
        "spark": {"closes": [round(c, 4) for c in cs[-60:]],
                  "ma": [round(x, 4) if x else None for x in (sma_series(cs, q["L"]))[-60:]],
                  "dates": CAL[SER[sym][0] + n - 60: SER[sym][0] + n],
                  "bots": spark_b},
    }

out = {"meta": {"last_date": LAST_DATE, "cal_first": CAL[0], "cal_last": CAL[-1],
                "n_days": len(CAL), "counts": stats_counts, "eligible": len(syms)},
       "pages": {}}
for p, (L, W, label) in PAGES.items():
    rows = [row(s, q) for s, q in qual[p].items()]
    rows.sort(key=lambda r: -r["_vcpr"])
    out["pages"][str(p)] = {"L": L, "W": W, "label": label,
                            "qualified": len(rows), "rows": rows[:50]}
    print(f"P{p} ({label}, MA{L}, W={W}): qualified {len(rows)}, listing top 50 by VCP")

# page 1: union of listed tickers
listed = {}
for p in PAGES:
    for i, r in enumerate(out["pages"][str(p)]["rows"], 1):
        listed.setdefault(r["sym"], dict(r, ranks={}))["ranks"][str(p)] = i
p1 = []
for s, r in listed.items():
    score_raw = 0.7 * r["_vcpr"] + 0.3 * (hits[s] / 4 * 100)
    r["score"] = round(score_raw, 1)
    r["_scorer"] = score_raw
    p1.append(r)
p1.sort(key=lambda r: -r["_scorer"])
for r in p1:
    del r["_scorer"]
for pdata in out["pages"].values():
    for r in pdata["rows"]:
        r.pop("_vcpr", None)
for r in p1:
    r.pop("_vcpr", None)
out["page1"] = p1
print(f"P1 summary: {len(p1)} distinct tickers")
json.dump(out, open(f"{SCRATCH}/screen_results.json", "w"), ensure_ascii=False)
print("counts:", stats_counts, "eligible:", len(syms))
