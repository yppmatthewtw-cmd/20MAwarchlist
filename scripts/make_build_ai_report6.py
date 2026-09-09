S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/ai5/build_ai5.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
def seg(a,end,b):
    global src
    i=src.index(a); j=src.index(end,i)+len(end); src=src[:i]+b+src[j:]
rep('F = json.load(open(f"{SCRATCH}/ai5/flow5.json"))\nB = json.load(open(f"{SCRATCH}/ai4/flow4.json"))   # R4.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/ai6/flow6.json"))\nB = json.load(open(f"{SCRATCH}/ai5/flow5.json"))   # R5.00, for the change summary only')
rep('VER = "R5.00"','VER = "R6.00"')
rep('claudefable51high','claudeopus5high')
rep('open(f"{SCRATCH}/ai5/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/ai6/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
# --- the headline correction: the dashboard's AI panel is dated 2026-07-09, not 8/27 ---
rep('def md(d): return f"{int(d[5:7])}/{int(d[8:10])}"',
    'def md(d): return f"{int(d[5:7])}/{int(d[8:10])}"\nASOF = M.get("asof_dash") or "—"\nGAP = M.get("asof_gap_sessions") or 0')
rep('''① <b>分類來源</b>：直接採用附件 <b>Dashboard R15.6</b>（2026-08-27 收盤版）嘅 <b>41 個 AI 小群組</b>分類、''',
    '''① <b>分類來源</b>：直接採用附件 <b>Dashboard R15.6</b>（檔案 built 2026-08-28，但 A9.2 AI 小群組面板自報
<code>asof {ASOF}</code>）嘅 <b>41 個 AI 小群組</b>分類、''')
rep('''⑨ <b>儀表板象限</b>（領先／改善／轉弱／落後）同 RS、RS動能係<b>儀表板 8/27 收盤</b>嘅數值，
本表資金流向係 <b>{DAYS[0]} → {DAYS[-1]}</b>（相差 {len(DAYS) + 1} 個交易日），兩者時點唔同，正好用嚟睇背離 —— 見第 4 頁。''',
    '''⑨ <b>儀表板象限</b>（領先／改善／轉弱／落後）同 RS、RS動能係<b>儀表板 {ASOF} 收盤</b>嘅數值 ——
<span class="cav">注意：唔係 8/27。R1–R5 一直寫「8/27 收盤」係讀錯咗 —— 8/27 係儀表板<b>其他</b>面板（大巿廣度）嘅日期，
A9.2 AI 小群組面板自己嘅 <code>asof</code> 欄位寫住 {ASOF}，週度序列亦止於該日。</span>
本表資金流向係 <b>{DAYS[0]} → {DAYS[-1]}</b>，同儀表板數值<b>相隔 {GAP} 個交易日（約兩個月）</b>，
所以第 4 頁應該讀成「兩個月前嘅 RS 位置 vs 最近五日嘅資金流向」，唔係近乎同步嘅對照 —— 見第 4 頁。''')
rep('''<span>儀表板 RS 象限（8/27）vs 本次實測資金流向（{md(DAYS[0])}–{md(DAYS[-1])}）</span>''',
    '''<span>儀表板 RS 象限（{ASOF}）vs 本次實測資金流向（{md(DAYS[0])}–{md(DAYS[-1])}）· 相隔 {GAP} 個交易日</span>''')
rep('''① <b>AI 小群組分類</b>：附件 <b>Dashboard_R15.6_0828_hk16.15.html</b>（2026-08-27 收盤 · built 2026-08-28 16:15 HKT）''',
    '''① <b>AI 小群組分類</b>：附件 <b>Dashboard_R15.6_0828_hk16.15.html</b>（檔案 built 2026-08-28 16:15 HKT；A9.2 面板數據自報 asof <b>{ASOF}</b>）''')
rep('''連同 RS 象限、RSI 及 1週／1月／3月報酬。RS 象限與報酬為<b>儀表板 8/27 數值</b>，非本表重算。<br>''',
    '''連同 RS 象限、RSI 及 1週／1月／3月報酬。RS 象限與報酬為<b>儀表板 {ASOF} 數值</b>（距本表視窗 {GAP} 個交易日），非本表重算。<br>''')
rep('''<div class="sub">分類取自 <b>Dashboard R15.6</b>（8/27 收盤）· 資金流向資料至 <b>{DAYS[-1]}</b>''',
    '''<div class="sub">分類取自 <b>Dashboard R15.6</b>（A9.2 面板 asof {ASOF}）· 資金流向資料至 <b>{DAYS[-1]}</b>''')
# --- update block ---
seg('grew = sorted(','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {})
same_window = DAYS == BDAYS
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R5.00）—— 對 R5.00 嘅 critical review 修正</h3><ul>
<li><b>⚠ 最重要嘅修正：儀表板象限嘅日期一直寫錯</b>。R1.00 至 R5.00 都寫住「儀表板 8/27 收盤」，並話同資金流向視窗只相隔幾個交易日。
今次逐個欄位翻查附件 HTML 先發現：8/27 係儀表板<b>大巿廣度</b>面板嘅日期；<b>A9.2 AI 小群組</b>面板自己嘅 JSON 寫住
<code>"asof":"{ASOF}","coverage":"224/236"</code>，其週度日期軸亦止於 {ASOF}。即係話 RS 象限、RS 動能、RSI 同 1週／1月／3月報酬
全部係 <b>{ASOF}</b> 嘅數值，距離本表視窗 <b>{GAP} 個交易日（約兩個月）</b>，唔係幾日。
第 4 頁「象限背離」因此要重新理解：係「兩個月前嘅相對強弱位置」對「最近五日嘅資金流向」，
背離可能只反映期間發生咗嘅事，唔可以當成同步訊號。全部相關文字（說明 ①⑨、第 4 頁標題、頁尾 ①、頂部副標題）已改正。</li>
<li><b>9月8日（週二）收盤：全部可達來源都未發佈</b>。建置時（{BUILD_TS} ＝ 美東 9/8 20:5x）日線鏡像對 09-08 只推送咗成交量、
Nasdaq 快照最新一筆係 09-08 盤中價（其反推收盤係 09-04，因 9/7 勞動節休市）、Yahoo 535 隻之中只有 3 隻有 09-08 日線。
故數據終點維持 <b>{DAYS[-1]}</b>，{"計分視窗與 R5.00 相同" if same_window else f"視窗改為 {DAYS[0]} → {DAYS[-1]}"}。</li>
<li><b>修正②：日線鏡像「過期仍照合併」</b>。R5 嘅基準核對只用兩邊最近 15 個共同交易日，若鏡像早幾個月停更，核對必然通過，
停更後先發生嘅拆股會被靜靜拼接。本版要求鏡像喺 {M.get("merge_since", "—")} 之後仍有數據先可合併，核對亦只計視窗內交易日；
本次 <b>{len(stale)}</b> 隻改為全段用 Yahoo（{esc("、".join(stale))}）。對今期數字影響為零，係堵住將來會靜靜出錯嘅路徑。</li>
<li><b>修正③：交易日距離用視窗長度推算</b>。R5 用「視窗長度 + 1」當交易日距離，逢假期偏細；本版改為喺實際交易日曆上數，
上面 {GAP} 個交易日就係咁計出嚟。</li>
<li><b>修正④：頁面寫死嘅來源數字</b>改由 meta 動態帶入：Yahoo 宇宙 {M.get("yahoo_n_symbols", 0):,} 隻、
全巿中位基準每日約 {max(M["mkt_n"].values()):,} 隻、合併來源 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻。
交叉核對：日線鏡像 vs Yahoo 視窗內 {XN.get("n", 0):,} 個收盤中位 {XN.get("median_pct", 0):.4f}%，基準不符者 {esc("、".join(basis)) or "無"} 已改用 Yahoo。</li>
<li><b>名次變動</b>：{len(moved)} 個小群組名次有變{"（純粹來自來源合併規則收緊）" if same_window else ""}。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
i=src.index('④ <b>數據終點'); j=src.index('<br>',i)+4
src=src[:i]+'''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：建置時 {BUILD_TS}，
9/8 收盤未有任何可達來源發佈（日線鏡像只有成交量、Nasdaq 快照係盤中、Yahoo 535 隻得 3 隻），故未納入。
視窗 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%；
鏡像須喺 {M.get("merge_since", "—")} 後仍有數據先合併，否則整段用 Yahoo（本次 {len(stale)} 隻）。<br>'''+src[j:]
open(f"{S}/ai6/build_ai6.py","w",encoding="utf-8").write(src); print("build_ai6.py written")
