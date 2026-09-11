S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub6/build_sub6.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('"""Sub-Sector 資金流向 Watchlist R6.00', '"""Sub-Sector 資金流向 Watchlist R7.00')
rep('F = json.load(open(f"{SCRATCH}/sub6/flow6.json"))\nB = json.load(open(f"{SCRATCH}/sub5/flow5.json"))   # R5.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub7/flow7.json"))\nB = json.load(open(f"{SCRATCH}/sub6/flow6.json"))   # R6.00, for the change summary only')
rep('VER = "R6.00"', 'VER = "R7.00"')
rep('<title>Sub-Sector 資金流向 Watchlist R6</title>', '<title>Sub-Sector 資金流向 Watchlist R7</title>')
rep('open(f"{SCRATCH}/sub6/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub7/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

# ---- 本版更新 ----
seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
BYD = XC.get("nz_vs_yh_by_day", {}).get(DAYS[-1], {}); TXC = M.get("tail_xcheck", {})
SP = M.get("settled_print_share", {}); TR = (M.get("tail_routes", {}) or {}).get(DAYS[-1], {})
TSV = (M.get("tail_softvol", {}) or {}).get(DAYS[-1], 0); PVE = M.get("prov_vol_effect", {})
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R6.00）—— 數據推進至 9/10 收盤 + 對 R6.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/7 為勞動節休市。<b>今次首次做到最新一日有兩個獨立來源</b>：日線鏡像（09-10 23:59 UTC 提交）同 Yahoo 尾段抓取
（{TR.get("hourly", 0)} 隻經小時線合成、{TR.get("hist5d", 0)} 隻經日線），兩者 09-10 收盤中位偏差
<b>{BYD.get("median_pct", 0):.4f}%</b>（{BYD.get("n", 0):,} 隻共同覆蓋，超過 0.5% 者 {BYD.get("gt_0_5", 0)} 隻）。</li>
<li><b>修正①：量能項 B 用緊成交「金額」，價格漂移會偽裝成參與度</b>（本版最重要嘅修正）。
R6 之前 B ＝ log₂(當日<b>成交額</b> ÷ 前 20 日中位<b>成交額</b>) ÷ 2 —— 分子分母都含價格，
所以一隻自基準期以來已經重估嘅股票，即使換手股數一模一樣，都會被讀成「放量」。
實測 R6 視窗 2,455 個「股票×交易日」：用成交額同用成交股數計出嚟嘅 B，中位差 −0.009、平均 −0.007，
第 5／95 百分位 ±0.09，但 <b>6.7%（164 個）相差超過 0.10</b>，最嚴重 CRCL 9/3（0.664 vs 0.394）、CRM 9/3（0.41 vs 0.163）——
乘數 (1+0.5B) 因而偏差最多 13%。本版 <b>B 改為比較成交股數與前 20 日中位成交股數</b>；
成交額繼續做佢本來嘅工作：籃子加權同淨額估算。</li>
<li><b>修正②：交易日曆會被落後嘅來源否決，最新一日靜靜被丟棄</b>。R6 要求一個交易日喺<b>合併後</b>嘅宇宙有 80% 覆蓋先算數，
但 Yahoo 嘅日線要隔晚先結算（09-10 嗰次抓取，535 隻入面得 4 隻有 09-10），令合併覆蓋率跌到 74%，
於是<b>鏡像已經完整發佈嘅 9/10 被剔走，引擎默默停喺 9/9</b>。本版改為<b>逐來源計覆蓋率</b>，任何一個來源覆蓋自己宇宙 80% 就當交易日
（今次 9/10：鏡像 {SRCC.get("mirror", 0)}／{M.get("mirror_typical", 0):.0f} 隻，Yahoo {SRCC.get("yahoo", 0)} 隻）。</li>
<li><b>修正③：「成交量暫定」偵測器測錯嘢</b>。R6 嘅偵測條件係「鏡像未發佈」，所以對住一個<b>鏡像已發佈但未結算</b>嘅交易日會報「無暫定日」。
鏡像嘅已結算列印有一個特徵：成交量係 100 股嘅整數倍（08-25 至 09-09 每日都係 99.7%）；未結算嘅即場數據冇
（<b>9/10 只有 {SP.get(DAYS[-1], 0)*100:.1f}%</b>）。本版改用呢個特徵做偵測，今次正確標記
<b>{esc("、".join(PROV)) if PROV else "無"}</b> 為成交量未結算。
實測影響（用鏡像歷史上同時存在兩種版本嘅 09-09、{PVE.get("n", 0)} 隻）：<b>收盤價完全一樣</b>，
開／高／低第 95 百分位差 {PVE.get("ohl_p95", 0)*100:.2f}%，但<b>成交量 {PVE.get("vol_revised", 0)*100:.1f}% 被修訂</b>
（>1%：{PVE.get("vol_gt1pct", 0)*100:.0f}%，>5%：{PVE.get("vol_gt5pct", 0)*100:.0f}%，第 95 百分位 +{PVE.get("vol_p95", 0)*100:.1f}%）——
即 A 方向準確、C 收位略軟、B 量能帶約 ±{PVE.get("b_p95_uncertainty", 0):.2f} 噪音，故<b>照計但標示</b>，唔丟棄亦唔歸零。</li>
<li><b>新增：Yahoo 尾段來源（scripts/fetch_yahoo_tail.py）</b>。Yahoo 嘅日線歷史落後收市超過五個鐘，
如果最新一日只靠鏡像，就會丟失鏡像唔覆蓋嘅 <b>129 隻</b>（ARM、ASML、TSM、IONQ、OKLO、RKLB、CRWV 等）同<b>清空 6 個子板塊</b>。
新腳本改用「相對期間／小時線／報價」三條路徑向 Yahoo 攞返嗰一日。
用途分清楚：<b>價格可信</b>（對比鏡像 {TXC.get("n", 0)} 隻，收盤中位偏差 {TXC.get("close_median_pct", 0):.3f}%、第 95 百分位 {TXC.get("close_p95_pct", 0):.3f}%），
<b>成交量唔可信</b>（小時線漏咗收市競價同延遲列印，中位低 {TXC.get("vol_ratio_median", 1):.3f} 倍、第 5／95 百分位 {TXC.get("vol_ratio_p05", 1):.3f}／{TXC.get("vol_ratio_p95", 1):.3f}，
直接用會令 B 系統性低 0.18）。所以尾段來源<b>只供價格</b>，佢嘅 B 一律設為中性 0（今次 {TSV} 隻），籃子權重改用 20 日中位成交額。</li>
<li><b>沿用 R6.00 嘅來源規則同平衡面板</b>：鏡像須喺 {M.get("merge_since", "—")} 之後仍有數據先合併（本次 {len(stale)} 隻改用 Yahoo：{esc("、".join(stale))}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。全巿中位基準用平衡面板 <b>{max(M["mkt_n"].values()):,}</b> 隻，五日同一批。
來源分佈：合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，全部 {M["n_tick"]} 隻有真實 OHLCV。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑），為連續第三個下跌交易日；
{len(moved)} 個子板塊名次有變（新交易日＋B 改用成交股數）。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

# ---- 方法論：B 的定義 ----
rep('　<code>B 量能 = log₂(當日成交額 / 前 20 日中位成交額) ÷ 2</code>，截於 ±1 —— 放量或縮量；<br>',
    '　<code>B 量能 = log₂(當日<b>成交股數</b> / 前 20 日中位<b>成交股數</b>) ÷ 2</code>，截於 ±1 —— 放量或縮量；<br>'
    '　（R7 起用股數而非成交額：分子分母同用價格會令價格漂移混入參與度，實測 6.7% 嘅「股票×交易日」因而偏差超過 0.10。'
    '成交額仍然負責籃子加權同淨額估算。）<br>')

# ---- 數據來源與限制 ② ----
i = src.index('② <b>數據終點'); j = src.index('<br>', src.index('故本表只喺兩邊都有嗰日先當定案')) + 4
src = src[:i] + '''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}；9/7 勞動節休市。
視窗內 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))} 加尾段檔 tail.csv.gz），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%；
最新一日 {DAYS[-1]} 亦有兩個來源核對，中位偏差 {BYD.get("median_pct", 0):.4f}%（{BYD.get("n", 0):,} 隻）。<br>
<b>成交量定案狀態</b>：{("本版五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))} ——
以「成交量是否 100 股整數倍」判別（已結算日 99.7%，{DAYS[-1]} 只有 {SP.get(DAYS[-1], 0)*100:.1f}%）。
未結算日嘅<b>收盤價準確</b>（實測 {PVE.get("n", 0)} 隻全部一致），但成交量之後仍會改（{PVE.get("vol_revised", 0)*100:.1f}% 被修訂、
{PVE.get("vol_gt5pct", 0)*100:.0f}% 改動 &gt;5%），故 B 量能帶約 ±{PVE.get("b_p95_uncertainty", 0):.2f} 噪音；
另有 {TSV} 隻嘅最新一日只有 Yahoo 尾段價格，B 已設為中性。<br>''' + src[j:]

open(f"{S}/sub7/build_sub7.py", "w", encoding="utf-8").write(src); print("sub7/build_sub7.py written")
