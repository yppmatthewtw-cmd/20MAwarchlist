S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub7/build_sub7.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('"""Sub-Sector 資金流向 Watchlist R7.00', '"""Sub-Sector 資金流向 Watchlist R8.00')
rep('F = json.load(open(f"{SCRATCH}/sub7/flow7.json"))\nB = json.load(open(f"{SCRATCH}/sub6/flow6.json"))   # R6.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub8/flow8.json"))\nB = json.load(open(f"{SCRATCH}/sub7/flow7_published.json"))   # R7.00 as shipped, for the change summary only')
rep('VER = "R7.00"', 'VER = "R8.00"')
rep('<title>Sub-Sector 資金流向 Watchlist R7</title>', '<title>Sub-Sector 資金流向 Watchlist R8</title>')
rep('open(f"{SCRATCH}/sub7/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub8/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
SP = M.get("settled_print_share", {}); MU = M.get("mirror_unsettled") or []
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
TSV = (M.get("tail_softvol", {}) or {}).get(DAYS[-1], 0)
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R7.00）—— 數據推進至 9/11 收盤 + 對 R7.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
今次 <b>9/11 由 Yahoo 已結算日線提供</b>（{SRCC.get("yahoo", 0)} 隻），日線鏡像收市後已清走該日、正重新灌入結算值，
建置時只剩 {SRCC.get("mirror", 0)} 隻，所以最新一日以 Yahoo 為準。</li>
<li><b>驗證上一版嘅判斷：R7.00 用未結算成交量計 9/10 係啱嘅。</b> 9/10 而家喺鏡像已經結算（整百比例由 1.8% 升到 99.7%），
用結算值重跑同一個視窗再同<b>已發佈嘅 R7.00 逐個子板塊對比</b>：|Δ5日 z| 中位 <b>0.0015</b>、p95 0.0116、最大 0.0235；
|Δ名次| 中位 <b>0</b>、p95 1、<b>最大 3</b>，111 個之中 76 個名次完全冇變；<b>TOP12 留低 11/12、BOTTOM12 留低 12/12</b>。
即「照計但標示」冇歪曲排名。順帶一提，兩個來源結算後係同一個數：9/10 Yahoo 日線成交量同鏡像 <b>403 隻完全一致</b>（中位偏差 0.000%，冇一隻唔同）。</li>
<li><b>修正①：結算列印偵測量錯咗對象</b>。R7 喺<b>鏡像</b>上量「成交量係咪 100 股整數倍」，但引擎實際計分嘅係<b>合併後</b>嘅數據。
9/11 鏡像已清走（1,503 隻剩 4 隻）而 Yahoo 已結算 —— 淨量鏡像就會把一個<b>已結算</b>嘅交易日誤報為暫定。
本版改為喺<b>合併後嘅逐隻 bar</b> 上量（今次 9/11：<b>{SP.get(DAYS[-1], 0)*100:.1f}%</b> 整百 ＝ 已結算），
並取消 R6 遺留嘅「鏡像未發佈就當暫定」條款。本版暫定日：<b>{esc("、".join(PROV)) if PROV else "無"}</b>。</li>
<li><b>修正②：鏡像未結算嘅交易日唔應該贏合併</b>。合併規則一向係「鏡像為主、Yahoo 補其未有」，
但嗰 {len(SRCC.get("mirror", 0) and [1] or [1])*SRCC.get("mirror", 0)} 隻鏡像 9/11 bar 係<b>即場數據</b>（0% 整百），Yahoo 同一日係<b>結算值</b>（99.4% 整百）——
即係明明有更好嘅數字卻揀咗差嗰個。本版：<b>鏡像已發佈但未結算嘅交易日（{esc("、".join(MU)) if MU else "無"}），由已結算嘅第二來源勝出</b>。</li>
<li><b>修正③：全巿中位面板唔可以只得報告名單</b>（本版最重要嘅修正）。平衡面板要求五個計分日同各自前一日都有報價；
9/11 只有 532 隻報告名單有數，面板即由 1,563 隻<b>塌到 535 隻大型股</b>，中位報酬完全變樣（9/10：−1.02% vs 本版 {mkt.get("2026-09-10", 0)*100:+.2f}%）。
本版新增 <code>data/yahoo/tickers_broad.txt</code>（鏡像 1,560 隻 ∪ 報告名單 546 隻 ＝ <b>1,692 隻</b>）同 workflow 輸入，
專為基準面板拉取廣宇宙日線，面板回復 <b>{max(M["mkt_n"].values()):,}</b> 隻。</li>
<li><b>Yahoo 尾段來源今次退為後備</b>：9/11 嘅 Yahoo 日線歷史已經結算，所以量能項 B 可以正常計，尾段檔 <b>0 行</b>被採用（{TSV} 隻用尾段價格）。
同時用<b>已結算</b>嘅 9/10 重新驗證上一版嘅尾段小時線（402 隻）：收盤中位偏差 0.015%（p95 0.077%）、
<b>高／低中位偏差 0.0000%</b>（p95 0.014%／0.012%）、C 收位中位 |Δ| 0.013（p95 0.062，8% 超過 0.05），
但成交量中位低 <b>1.308</b> 倍（p05 1.112／p95 1.773）—— 印證 R7「尾段只供價格、B 設中性」嘅處理係啱嘅。</li>
<li><b>沿用 R7.00 嘅規則</b>：B 量能用成交股數、逐來源計交易日曆、平衡面板、40% 硬上限。
鏡像須喺 {M.get("merge_since", "—")} 之後仍有數據先合併（本次 {len(stale)} 隻改用 Yahoo：{esc("、".join(stale)) or "無"}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。來源分佈：合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
全部 {M["n_tick"]} 隻有真實 OHLCV。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑），
{"為視窗內唯一上升交易日，四連跌後反彈" if mkt[DAYS[-1]] > 0 else "續跌"}；{len(moved)} 個子板塊名次有變。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

# 數據來源與限制 ②
i = src.index('② <b>數據終點'); j = src.index('<br>', src.index('B 已設為中性')) + 4
src = src[:i] + '''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}。
視窗內 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。
最新一日 {DAYS[-1]} 由 <b>Yahoo 已結算日線</b>提供（鏡像收市後清走該日、正重新灌入，建置時只剩 {SRCC.get("mirror", 0)} 隻）。<br>
<b>成交量定案狀態</b>：{("本版五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))} ——
以<b>合併後實際計分嘅 bar</b> 判別「成交量是否 100 股整數倍」（已結算日約 99.7%；{DAYS[-1]} 為 {SP.get(DAYS[-1], 0)*100:.1f}%）。
鏡像已發佈但未結算嘅交易日（{esc("、".join(MU)) if MU else "無"}）由已結算嘅第二來源勝出；
依據係 9/10 結算後 Yahoo 日線成交量與鏡像 403 隻完全一致。<br>''' + src[j:]

# ④b 平衡面板：說明廣宇宙來源
rep('''五日同一批，令逐日分數用同一把尺。（若改用「當日有報價就計」嘅不平衡池，最新一日會因為廣宇宙數據未到而換成另一批偏大型股嘅樣本。）<br>''',
    '''五日同一批，令逐日分數用同一把尺。基準面板嘅廣宇宙日線由 <code>data/yahoo/tickers_broad.txt</code>（鏡像 ∪ 報告名單 ＝ 1,692 隻）
經 GitHub Actions runner 拉取；若淨用報告名單，最新一日嘅面板會塌到 535 隻大型股，中位報酬會差成 0.3 個百分點以上。<br>''')
open(f"{S}/sub8/build_sub8.py", "w", encoding="utf-8").write(src); print("sub8/build_sub8.py written")
