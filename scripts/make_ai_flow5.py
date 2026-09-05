S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub4/flow4.py",encoding="utf-8").read()
def rep(old,new):
    global src
    assert old in src, old[:70]; src=src.replace(old,new,1)
rep('"""Sub-sector money-flow scoring — R4.00 engine (111 sub-sectors of the R2 heat-map workbook).',
    '"""AI money-flow scoring — R5.00 engine (41 AI 小群組 of the Dashboard R15.6 classification).\n\n'
    'Identical scoring math to the Sub-Sector watchlist R4.00 engine (Yahoo second source); only\n'
    'the baskets differ.  Per the brief, baskets hold US-listed shares and US ADRs only — members\n'
    'carrying a foreign-exchange suffix are excluded and reported, not substituted.')
rep('subs = json.load(open(f"{SCR}/sub/subsectors.json"))', 'AI = json.load(open(f"{SCR}/ai/aigroups.json"))\nsubs = AI["groups"]')
i=src.index("# ---- curated supplements"); j=src.index("# ---------------- load real daily OHLCV")
src=src[:i]+"SUPP = {}      # no hand substitutes: the brief restricts baskets to US listings / ADRs\nPROXY = {}\n\n"+src[j:]
rep('listed_all = {t for s in subs for t in s["tickers"]}', 'listed_all = {t for s in subs for t in s["us"]}')
rep('    listed = PROXY.get(s["n"]) or [t for t in s["tickers"] if TICKER_RE.match(t)]',
    '    listed = [t for t in s["us"] if TICKER_RE.match(t)]')
rep('        rows.append(dict(s, basket=[], n_basket=0, proxy=proxy, days=None, note="無可用樣本"))',
    '        rows.append(dict(s, basket=[], n_basket=0, proxy=proxy, days=None,\n'
    '                         note=("成分股全部非美股上市／無 US ADR" if not s["us"] else "美股成分股數據不足")))')
rep('    rows.append(dict(s, basket=tk, n_basket=len(tk), proxy=proxy, supp=supp,',
    '''    # per-ticker 5-day flow, same recency weights as the group score, for the ticker column
    W5 = [1.0, 1.15, 1.35, 1.6, 1.9]
    ticks = []
    for t in tk:
        td = TICK[t]["days"]
        tf5 = sum(w * td[d]["f"] for w, d in zip(W5, DAYS)) / sum(W5)
        ticks.append({"sym": t, "tf5": round(tf5, 4),
                      "mfd5": sum(td[d]["mfd"] for d in DAYS),
                      "dv5": sum(td[d]["dv"] for d in DAYS),
                      "ret5": round(math.prod(1 + td[d]["ret"] for d in DAYS) - 1, 5),
                      "src": TICK[t]["src"], "nobase": TICK[t]["nobase"],
                      "novol": sum(1 for d in DAYS if td[d]["novol"])})
    ticks.sort(key=lambda x: -x["tf5"])          # most inflow first, most outflow last
    rows.append(dict(s, basket=tk, ticks=ticks, n_basket=len(tk), proxy=proxy, supp=supp,''')
rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub4/flow4.json"), "w"), ensure_ascii=False)',
    'out["meta"]["asof_dash"] = AI["asof_dash"]\nout["meta"]["nonus_excluded"] = sorted({m for s in subs for m in s["nonus"]})\n'
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/ai5/flow5.json"), "w"), ensure_ascii=False)')
rep('''    print(f"  {r['rank']:3d} {r['zh'][:14]:<16} z5{r['z5']:+.2f} 5日分{r['score5']:5.1f} "
          f"日格{[r['days'][d]['grade'] for d in DAYS]} 淨額${r['mfd5']/1e6:+,.0f}M 樣本{r['n_basket']}")
print("BOTTOM 12 outflow:")''','''    print(f"  {r['rank']:3d} {r['code']:<5}{r['zh'][:20]:<22} z5{r['z5']:+.2f} 5日分{r['score5']:5.1f} "
          f"日格{[r['days'][d]['grade'] for d in DAYS]} 淨額${r['mfd5']/1e6:+,.0f}M 樣本{r['n_basket']}")
print("BOTTOM 12 outflow:")''')
rep('print("no-basket rows:", [(r[\'n\'], r[\'zh\']) for r in rows if not r["days"]])',
    'print("unscorable:", [(r[\'code\'], r[\'note\']) for r in rows if not r["days"]])')
open(f"{S}/ai5/flow5.py","w",encoding="utf-8").write(src); print("ai5/flow5.py written")
