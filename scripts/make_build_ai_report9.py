S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/ai8/build_ai8.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('F = json.load(open(f"{SCRATCH}/ai8/flow8.json"))\nB = json.load(open(f"{SCRATCH}/ai7/flow7.json"))   # R7.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/ai9/flow9.json"))\nB = json.load(open(f"{SCRATCH}/ai8/flow8.json"))   # R8.00, for the change summary only')
rep('VER = "R8.00"', 'VER = "R9.00"')
rep('open(f"{SCRATCH}/ai8/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/ai9/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
SP = M.get("settled_print_share", {}); MU = M.get("mirror_unsettled") or []
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R8.00）—— 數據推進至 9/11 收盤 + 對 R8.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
今次 <b>9/11 由 Yahoo 已結算日線提供</b>（{SRCC.get("yahoo", 0)} 隻）；日線鏡像收市後已清走該日、正重新灌入結算值，
建置時只剩 {SRCC.get("mirror", 0)} 隻，故最新一日以 Yahoo 為準。</li>
<li><b>驗證上一版嘅判斷：用未結算成交量計 9/10 係啱嘅。</b> 9/10 而家喺鏡像已結算（整百比例 1.8% → 99.7%），
用結算值重跑同一視窗再同已發佈版本逐個板塊對比：|Δ5日 z| 中位 <b>0.0015</b>、最大 0.0235；
|Δ名次| 中位 <b>0</b>、<b>最大 3</b>，<b>TOP12 留 11/12、BOTTOM12 留 12/12</b>。
兩個來源結算後亦係同一個數：9/10 Yahoo 日線成交量同鏡像 <b>403 隻完全一致</b>（中位偏差 0.000%）。</li>
<li><b>修正①：結算列印偵測量錯咗對象</b> —— 之前喺<b>鏡像</b>上量「成交量係咪 100 股整數倍」，但引擎計分用嘅係<b>合併後</b>數據。
9/11 鏡像已清走而 Yahoo 已結算，淨量鏡像就會把一個已結算嘅交易日誤報為暫定。本版改喺<b>合併後嘅 bar</b> 上量
（9/11：<b>{SP.get(DAYS[-1], 0)*100:.1f}%</b> ＝ 已結算），並取消「鏡像未發佈就當暫定」嘅遺留條款。本版暫定日：<b>{esc("、".join(PROV)) if PROV else "無"}</b>。</li>
<li><b>修正②：鏡像未結算嘅交易日唔應該贏合併</b> —— 嗰幾隻鏡像 9/11 bar 係即場數據（0% 整百），Yahoo 同日係結算值（99.4%）。
本版：鏡像已發佈但未結算嘅交易日（{esc("、".join(MU)) if MU else "無"}）由已結算嘅第二來源勝出。</li>
<li><b>修正③：全巿中位面板唔可以只得報告名單</b>（最重要）。平衡面板要求五個計分日同各自前一日都有報價；
9/11 只有 532 隻報告名單有數，面板會由 1,563 隻<b>塌到 535 隻大型股</b>，中位報酬完全變樣。
新增 <code>data/yahoo/tickers_broad.txt</code>（鏡像 1,560 ∪ 報告名單 546 ＝ <b>1,692 隻</b>）專為基準面板拉取廣宇宙日線，
面板回復 <b>{max(M["mkt_n"].values()):,}</b> 隻。</li>
<li><b>Yahoo 尾段來源今次退為後備</b>：9/11 嘅 Yahoo 日線已結算，量能項 B 可正常計。
同時用已結算嘅 9/10 重新驗證上一版嘅尾段小時線（402 隻）：收盤中位偏差 0.015%、<b>高／低中位 0.0000%</b>、
C 收位中位 |Δ| 0.013（p95 0.062），但成交量中位低 <b>1.308</b> 倍 —— 印證「尾段只供價格」嘅處理。</li>
<li><b>儀表板象限日期</b>（沿用並重算距離）：A9.2 面板自報 <code>asof {ASOF}</code>，唔係 8/27；
距本表視窗 <b>{GAP} 個交易日</b>，第 4 頁應讀成「兩個月前嘅 RS 位置 vs 最近五日資金流向」。</li>
<li><b>沿用嘅規則</b>：B 量能用成交股數、逐來源計交易日曆、平衡面板、40% 硬上限。
鏡像須喺 {M.get("merge_since", "—")} 後仍有數據先合併（本次 {len(stale)} 隻用 Yahoo：{esc("、".join(stale)) or "無"}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
{M["n_tick"]} 隻全部有真實 OHLCV。{len(grew)} 個籃子改變{("：" + esc("、".join(f"{cur[c]['code']} {a}→{b}" for c, a, b in grew))) if grew else ""}。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑）{"，為視窗內唯一上升交易日" if mkt[DAYS[-1]] > 0 else ""}；
{len(moved)} 個小群組名次有變。升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

i = src.index('④ <b>數據終點'); j = src.index('<br>', src.index('全巿中位</b>取自平衡面板')) + 4
src = src[:i] + '''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：建置時 {BUILD_TS}。
視窗 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%；
最新一日 {DAYS[-1]} 由 <b>Yahoo 已結算日線</b>提供（鏡像收市後清走該日、正重新灌入，建置時只剩 {SRCC.get("mirror", 0)} 隻）。
<b>成交量定案狀態</b>：{("五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))} ——
以<b>合併後實際計分嘅 bar</b> 判別「成交量是否 100 股整數倍」（已結算日約 99.7%，{DAYS[-1]} 為 {SP.get(DAYS[-1], 0)*100:.1f}%）；
鏡像已發佈但未結算嘅交易日（{esc("、".join(MU)) if MU else "無"}）由已結算嘅第二來源勝出。
<b>全巿中位</b>取自平衡面板（五日同一批 {max(M["mkt_n"].values()):,} 隻，廣宇宙日線由 tickers_broad.txt 1,692 隻拉取）。<br>''' + src[j:]

open(f"{S}/ai9/build_ai9.py", "w", encoding="utf-8").write(src); print("ai9/build_ai9.py written")
