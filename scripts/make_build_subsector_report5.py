S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub4/build_sub4.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
def seg(a,end,b):
    global src
    i=src.index(a); j=src.index(end,i)+len(end); src=src[:i]+b+src[j:]
rep('"""Sub-Sector 資金流向 Watchlist R4.00','"""Sub-Sector 資金流向 Watchlist R5.00')
rep('F = json.load(open(f"{SCRATCH}/sub4/flow4.json"))\nB = json.load(open(f"{SCRATCH}/sub3/flow3.json"))   # R3.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub5/flow5.json"))\nB = json.load(open(f"{SCRATCH}/sub4/flow4.json"))   # R4.00, for the change summary only')
rep('VER = "R4.00"','VER = "R5.00"')
rep('claudefable51high','claudeopus5high')
rep('<title>Sub-Sector 資金流向 Watchlist R3</title>','<title>Sub-Sector 資金流向 Watchlist R5</title>')
rep('open(f"{SCRATCH}/sub4/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub5/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
seg('grew = sorted(','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
xc_days = "、".join(f"{dlab(d).split('<')[0]} n={v['n']} 中位 {v['median_pct']:.4f}%" for d, v in XC.items() if d[:2] == "20")
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {})
same_window = DAYS == BDAYS
moved_note = ("計分視窗與 R4.00 相同" if same_window else
              f'計分視窗由 {BDAYS[0]} → {BDAYS[-1]} 改為 {DAYS[0]} → {DAYS[-1]}')
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R4.00）—— 對 R4.00 嘅 critical review 修正</h3><ul>
<li><b>9月8日（週二）收盤：全部可達來源都未發佈</b>。建置時（{BUILD_TS} ＝ 美東 9/8 20:5x）三個來源嘅狀況係 ——
日線鏡像最新提交（09-09 00:04 UTC）對 09-08 只推送咗成交量；Nasdaq 快照最新一筆係 09-08 10:36 ET <b>盤中</b>價，
其 <code>price − price_change</code> 只可還原 09-04 官方收盤（9/7 勞動節休市）；<b>Yahoo Finance 535 隻之中只有 3 隻</b>
（HUBB、SBGSY、TCEHY）有 09-08 日線，其餘要等隔夜結算。故本版數據終點維持 <b>{DAYS[-1]}</b>，{moved_note} ——
<span class="cav">唔以盤中價或單邊成交量冒充收盤。</span>Yahoo 通常隔晚結算（上次 09-04 嘅日線係翌日 05:27 ET 抓到），9/8 收盤要再拉一次先有。</li>
<li><b>修正①：日線鏡像「過期仍照合併」</b>。R4 嘅來源合併只用兩邊最近 15 個<b>共同</b>交易日做基準核對；若鏡像檔案早幾個月就停止更新，
呢 15 日全部係舊數據，核對必然通過，而停更之後先發生嘅拆股就會被靜靜地拼接入去。本版規定：鏡像必須喺計分＋量能基準視窗
（{M.get("merge_since", "—")} 起）內有數據先可以合併，基準核對亦只計視窗內嘅交易日；唔達標就整段改用 Yahoo。
本次受影響 <b>{len(stale)}</b> 隻（{esc("、".join(stale))}），佢哋嘅鏡像檔案分別停喺 2026-06 / 07 月。
<b>對今期數字影響為零</b>（呢幾隻嘅鏡像本來就冇覆蓋視窗，實際一直用緊 Yahoo），修正係為咗堵住將來會靜靜出錯嘅路徑。</li>
<li><b>修正②：交易日距離用視窗長度推算</b>。R4 將「兩個日期相隔幾多個交易日」寫成「視窗長度 + 1」，逢假期就會偏細。
本版改為喺實際交易日曆上數（<code>gap_sessions()</code>）—— 今期視窗跨越 <b>9/7 勞動節</b>，舊寫法會少數一日。</li>
<li><b>修正③：頁面寫死嘅來源數字</b>。R4 頁尾寫死「546 隻」「535 隻」「2,758 隻」「日線鏡像 1,502 隻」「09-05 00:11 UTC」等，
換一期數據就會過時。本版全部改由 meta 動態帶入：本次 Yahoo 宇宙 <b>{M.get("yahoo_n_symbols", 0):,}</b> 隻、
全巿中位基準每日約 <b>{max(M["mkt_n"].values()):,}</b> 隻、合併來源 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻。</li>
<li><b>交叉核對（本期重跑）</b>：快照序列 vs Yahoo 逐日中位偏差 —— {esc(xc_days)}；日線鏡像 vs Yahoo 視窗內 {XN.get("n", 0):,} 個收盤中位
{XN.get("median_pct", 0):.4f}%，>0.5% 嘅 {XN.get("gt_0_5", 0)} 個集中喺 {len(basis)} 隻（{esc("、".join(basis))}），已整段改用 Yahoo。</li>
<li><b>名次變動</b>：{len(moved)} 個子板塊名次有變{"（純粹來自來源合併規則收緊）" if same_window else ""}。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
# footer ②/③ dynamic
i=src.index('② <b>數據終點'); j=src.index('<br>',i)+4
src=src[:i]+'''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}，
9/8 收盤未有任何可達來源發佈（日線鏡像只有成交量、Nasdaq 快照係盤中、Yahoo 535 隻得 3 隻有日線），故未納入。
視窗內嘅 OHLCV 來自日線鏡像與 <b>Yahoo Finance</b> 合併（GitHub Actions runner 以 yfinance 拉取未調整日線：{esc("、".join(M.get("yahoo_files", [])))}），
兩者共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。<br>'''+src[j:]
i=src.index('③ <b>來源合併規則</b>'); j=src.index('<br>',i)+4
src=src[:i]+'''③ <b>來源合併規則</b>：每隻股票以日線鏡像為主、Yahoo 補其未有嘅交易日，但<b>鏡像必須喺 {M.get("merge_since", "—")} 之後仍有數據</b>先可以合併，
且基準核對只計視窗內嘅共同交易日（最近 15 個，收盤中位偏差 ≤0.5%）；停更太耐（本次 {len(stale)} 隻：{esc("、".join(stale))}）
或基準不符（{esc("、".join(basis))}）者，整段改用 Yahoo 已回溯調整嘅歷史。快照序列只作對照，唔入計分。<br>'''+src[j:]
rep('''其餘以 Nasdaq 快照重建序列補足（只有收盤價與成交量，收位項 C 不適用，已於「樣本」欄標示）。''',
    '''其餘由 Yahoo Finance 日線補足；本版 {M["n_tick"]} 隻代表股全部有真實 OHLCV。''')
open(f"{S}/sub5/build_sub5.py","w",encoding="utf-8").write(src); print("build_sub5.py written")
