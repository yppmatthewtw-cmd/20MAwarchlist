S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub4/flow4.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
rep('"""Sub-sector money-flow scoring — R4.00 engine (111 sub-sectors of the R2 heat-map workbook).',
 '"""Sub-sector money-flow scoring — R5.00 engine (111 sub-sectors of the R2 heat-map workbook).\n\n'
 'R5 fixes what the R4.00 review turned up:\n'
 '  * merge_bars accepted a daily-bar file whose coverage stops months before the scored window\n'
 '    (8 names: ALAB, ARM, ASML, CRWV, NBIS, RKLB, SHOP, ZS end 2026-06/07). The share-basis check\n'
 '    then compared only stale sessions, so a split occurring after the mirror went quiet would be\n'
 '    spliced in undetected. The mirror is now used only when it actually covers the window; the\n'
 '    basis check must also pass on sessions inside it.\n'
 '  * the trading-day distance between two dates was inferred from the window length, which is\n'
 '    wrong across a market holiday. gap_sessions() counts real sessions on the bar calendar.')
rep('''def merge_bars(nz, yh):
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
    return dict(yh), "yahoo", med           # bases disagree (unadjusted split etc.): trust Yahoo\'s restated history''',
'''def merge_bars(nz, yh, since=None):
    """natezone bars, extended by Yahoo where natezone has no bar, once the two agree on share
    basis over sessions that actually overlap the period being scored.

    A mirror file that stopped months ago contributes nothing to the window but would still pass
    a basis check run on its own stale sessions — and would hide any split that happened after it
    went quiet. So when `since` is given and the mirror has no bar at or after it, Yahoo is used
    alone. Returns (bars, source_tag, deviation_median or None)."""
    if not nz and not yh: return None, None, None
    if not yh: return nz, "real", None
    if not nz: return dict(yh), "yahoo", None
    if since is not None and not any(d >= since for d in nz):
        return dict(yh), "yahoo", None      # mirror is stale: nothing to merge, nothing to check
    common = sorted(set(nz) & set(yh))
    if since is not None:
        recent = [d for d in common if d >= since]
        common = recent if recent else common
    common = common[-15:]
    dev = [abs(nz[d][3] - yh[d][3]) / yh[d][3] for d in common if yh[d][3] > 0]
    med = statistics.median(dev) if dev else None
    if med is not None and med <= BASIS_TOL:
        out = dict(yh); out.update(nz); return out, "real", med
    return dict(yh), "yahoo", med           # bases disagree (unadjusted split etc.): trust Yahoo\'s restated history''')
# two-pass: provisional calendar from Yahoo alone, then merge with the window known
rep('''NZD = {}; SRC = {}; BASIS = {}
for t in wanted:
    bars, tag, med = merge_bars(load_nz(t), yh_get(t))
    if bars: NZD[t] = bars; SRC[t] = tag; BASIS[t] = med''',
'''# the merge needs to know which sessions matter, and the calendar needs the merged bars:
# settle it with a provisional calendar from the Yahoo bars, which cover the whole universe.
_cov = collections.Counter()
for t in wanted:
    for d in (yh_get(t) or {}): _cov[d] += 1
_seq = sorted(d for d, n in _cov.items() if n >= 0.8 * len(wanted))
TERM0 = os.environ.get("TERMINAL_DATE")
if TERM0: _seq = [d for d in _seq if d <= TERM0]
SINCE = _seq[-(WIN + LOOK + 1)] if len(_seq) > WIN + LOOK else (_seq[0] if _seq else None)
print("merge window starts at", SINCE)

NZD = {}; SRC = {}; BASIS = {}; STALE = []
for t in wanted:
    nz = load_nz(t)
    if nz and SINCE and not any(d >= SINCE for d in nz): STALE.append(t)
    bars, tag, med = merge_bars(nz, yh_get(t), SINCE)
    if bars: NZD[t] = bars; SRC[t] = tag; BASIS[t] = med
print(f"daily-bar files too stale to merge (Yahoo used alone): {len(STALE)} {sorted(STALE)}")''')
rep('''    bars, tag, med = merge_bars(load_nz(f[:-4]), yh_get(sym))
    if bars: allnz[sym] = bars''',
'''    bars, tag, med = merge_bars(load_nz(f[:-4]), yh_get(sym), SINCE)
    if bars: allnz[sym] = bars''')
# session-distance helper on the real calendar
rep('''print("scored sessions:", DAYS)''',
'''CALSEQ = seq          # every session the bar sources agree on, oldest first
def gap_sessions(a, b):
    """Trading sessions between two dates on the bar calendar (0 if either is unknown)."""
    fwd = [d for d in CALSEQ if a <= d <= b]
    return max(0, len(fwd) - 1) if fwd else 0
print("scored sessions:", DAYS)''')
rep('''                "yahoo_xcheck": XC,''',
'''                "stale_mirror": sorted(STALE), "merge_since": SINCE,
                "calendar_tail": CALSEQ[-30:],
                "yahoo_xcheck": XC,''')
rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub4/flow4.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub5/flow5.json"), "w"), ensure_ascii=False)')
open(f"{S}/sub5/flow5.py","w",encoding="utf-8").write(src); print("sub5/flow5.py written")
