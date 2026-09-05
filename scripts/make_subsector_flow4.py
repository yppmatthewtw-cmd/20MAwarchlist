# derive sub4/flow4.py (Yahoo second source) from sub3/flow3.py, asserting every anchor
S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub3/flow3.py",encoding="utf-8").read()
def rep(old,new):
    global src
    assert old in src, old[:80]; src=src.replace(old,new,1)
rep('"""Sub-sector money-flow scoring — R3.00 engine (111 sub-sectors of the R2 heat-map workbook).',
 '"""Sub-sector money-flow scoring — R4.00 engine (111 sub-sectors of the R2 heat-map workbook).\n\n'
 'R4 adds Yahoo Finance daily bars as a second, independent price source (pulled by a GitHub\n'
 'Actions runner, see .github/workflows/fetch_yahoo_eod.yml — the research container cannot\n'
 'reach Yahoo).  Per ticker the natezone daily bars and the Yahoo bars are merged after a\n'
 'share-basis check (median close deviation over the common sessions <= 0.5%); natezone wins\n'
 'on overlap, Yahoo supplies what natezone has not published (the 2026-09-04 session, and\n'
 'the whole history of names outside the natezone universe).  The snapshot-rebuilt series is\n'
 'used only where neither has the window.  Every close the snapshot series carries is\n'
 'cross-checked against Yahoo and the per-day agreement is written to meta["yahoo_xcheck"].')
rep('import csv, json, math, os, pickle, statistics, collections, re',
    'import csv, json, math, os, pickle, statistics, collections, re, glob, gzip')
rep('NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"',
    'NZ = os.environ.get("NZ_REPO", "/home/user/natezone/market-tracker") + "/data/UNIFIED/history"\n'
    'YF_FILES = [p for p in os.environ.get("YAHOO_FILES",\n'
    '            "/home/user/yppmatthewtw-cmd/10ma-watchlist/data/yahoo/eod_2025-12-26_2026-09-05.csv.gz;"\n'
    '            + ";".join(sorted(glob.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz")))).split(";") if p]\n'
    'BASIS_TOL = 0.005            # natezone and Yahoo closes must agree within 0.5% to be merged')
# Yahoo loader right after load_nz definition
rep('''listed_all = {t for s in subs for t in s["tickers"]}''',
'''# ---------------- Yahoo daily bars (second source) ----------------
YH = {}
for path in YF_FILES:                     # later files override earlier ones (this repo's own pull last)
    if not os.path.exists(path): continue
    n0 = len(YH)
    with gzip.open(path, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try:
                o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError):
                continue
            if c > 0: YH.setdefault(r["symbol"].replace("/", ".").replace("-", "."), {})[r["date"]] = (o, h, l, c, v)
    print(f"yahoo bars: {os.path.basename(path)} -> {len(YH) - n0} new symbols ({len(YH)} total)")
def yh_get(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))

def merge_bars(nz, yh):
    """natezone bars, extended by Yahoo where natezone has no bar, once the two agree on
    share basis; returns (bars, source_tag, deviation_median or None)."""
    if not nz and not yh: return None, None, None
    if not yh: return nz, "real", None
    if not nz: return dict(yh), "yahoo", None
    common = sorted(set(nz) & set(yh))[-15:]
    dev = [abs(nz[d][3] - yh[d][3]) / yh[d][3] for d in common if yh[d][3] > 0]
    med = statistics.median(dev) if dev else None
    if med is not None and med <= BASIS_TOL:
        out = dict(yh); out.update(nz); return out, "real", med
    return dict(yh), "yahoo", med           # bases disagree (unadjusted split etc.): trust Yahoo's restated history

listed_all = {t for s in subs for t in s["tickers"]}''')
# NZD -> merged bars per wanted ticker
rep('''NZD = {}
for t in wanted:
    d = load_nz(t)
    if d: NZD[t] = d''',
'''NZD = {}; SRC = {}; BASIS = {}
for t in wanted:
    bars, tag, med = merge_bars(load_nz(t), yh_get(t))
    if bars: NZD[t] = bars; SRC[t] = tag; BASIS[t] = med''')
# calendar: union coverage (NZD now includes yahoo) — unchanged code works; market baseline: union universe
rep('''allnz = {}
for f in os.listdir(NZ):
    if not f.endswith(".csv"): continue
    sym = f[:-4]
    if sym in NZD: allnz[sym] = NZD[sym]
    else:
        d = load_nz(sym)
        if d: allnz[sym] = d''',
'''allnz = {}
for f in os.listdir(NZ):
    if not f.endswith(".csv"): continue
    sym = f[:-4].replace("-", ".")
    bars, tag, med = merge_bars(load_nz(f[:-4]), yh_get(sym))
    if bars: allnz[sym] = bars
for sym in YH:                                # Yahoo-only names (the 10MA eligible universe + this repo's list)
    if sym not in allnz: allnz[sym] = YH[sym]
for t in NZD: allnz[t] = NZD[t]''')
# tick_flow: source tag
rep('''    data = NZD.get(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    if not real:
        data = series_snap(sym)''',
'''    data = NZD.get(sym)
    real = bool(data) and all(d in data for d in DAYS) and sum(1 for d in BASE if d in data) >= 10
    srctag = SRC.get(sym, "real") if real else "snap"
    if not real:
        data = series_snap(sym)''')
rep('''    out = {"sym": sym, "src": "real" if real else "snap", "med_dv": med_dv,
           "nobase": nobase, "days": {}}''',
'''    out = {"sym": sym, "src": srctag, "med_dv": med_dv, "basis_dev": BASIS.get(sym),
           "nobase": nobase, "days": {}}''')
rep('''print(f"tickers scored: {len(TICK)} (real OHLCV {sum(1 for v in TICK.values() if v['src']=='real')}, "
      f"snapshot {sum(1 for v in TICK.values() if v['src']=='snap')}, of which {nb} without a volume "
      f"baseline -> B held at 0); dropped {len(dropped)}: {dropped}")''',
'''srcn = collections.Counter(v["src"] for v in TICK.values())
print(f"tickers scored: {len(TICK)} (natezone+yahoo {srcn['real']}, yahoo-only {srcn['yahoo']}, "
      f"snapshot {srcn['snap']}, of which {nb} without a volume baseline -> B held at 0); dropped {len(dropped)}: {dropped}")

# ---------------- cross-check: snapshot-series closes vs Yahoo, per session in the window ----------------
XC = {}
for day in [LAST[LAST.index(DAYS[0]) - 1]] + DAYS:
    dev = []
    for sym in wanted:
        y = yh_get(sym); sd = series_snap(sym)
        if y and sd and day in y and day in sd and y[day][3] > 0:
            dev.append(abs(sd[day][3] - y[day][3]) / y[day][3] * 100)
    if dev:
        XC[day] = {"n": len(dev), "median_pct": round(statistics.median(dev), 4),
                   "gt_0_5": sum(1 for x in dev if x > 0.5), "gt_2": sum(1 for x in dev if x > 2)}
nzdev = []
for sym in wanted:
    nz = load_nz(sym); y = yh_get(sym)
    if nz and y:
        for d in DAYS:
            if d in nz and d in y and y[d][3] > 0: nzdev.append(abs(nz[d][3] - y[d][3]) / y[d][3] * 100)
XC["natezone_vs_yahoo"] = ({"n": len(nzdev), "median_pct": round(statistics.median(nzdev), 4),
                            "gt_0_5": sum(1 for x in nzdev if x > 0.5)} if nzdev else None)
XC["basis_disagree"] = sorted(t for t, m in BASIS.items() if m is not None and m > BASIS_TOL)
print("snapshot vs yahoo close deviation:", {d: v for d, v in XC.items() if d[:2] == "20"})
print("natezone vs yahoo:", XC["natezone_vs_yahoo"], "| basis disagreements:", XC["basis_disagree"])''')
# rows src tags: real / yahoo / snap / mix
rep('''                     src=("real" if all(TICK[t]["src"] == "real" for t in tk) else
                          ("snap" if all(TICK[t]["src"] == "snap" for t in tk) else "mix")),''',
'''                     src=("real" if all(TICK[t]["src"] in ("real", "yahoo") for t in tk) else
                          ("snap" if all(TICK[t]["src"] == "snap" for t in tk) else "mix")),
                     src_detail=dict(collections.Counter(TICK[t]["src"] for t in tk)),''')
rep('''                "terminal_note": M10.get("note_0904", ""),''',
'''                "yahoo_xcheck": XC, "yahoo_files": [os.path.basename(p) for p in YF_FILES if os.path.exists(p)],
                "yahoo_n_symbols": len(YH), "src_counts": dict(srcn),''')
rep("seq = [d for d in CAL if d in set(full)]",
    "seq = list(full)                            # trading calendar from the bar sources (natezone ∪ Yahoo), not the snapshot series")
rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub3/flow3.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub4/flow4.json"), "w"), ensure_ascii=False)')
rep('"source_note": "natezone/market-tracker 真實日線 OHLCV 為主，其餘以快照序列（僅收盤，成交量有則用）補足"',
    '"source_note": "natezone/market-tracker 日線 OHLCV 與 Yahoo Finance 日線（GitHub Actions runner 拉取）合併，快照序列只作對照及最後補足"')
open(f"{S}/sub4/flow4.py","w",encoding="utf-8").write(src); print("sub4/flow4.py written")
