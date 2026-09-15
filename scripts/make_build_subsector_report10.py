S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub9/build_sub9.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('"""Sub-Sector 資金流向 Watchlist R9.00', '"""Sub-Sector 資金流向 Watchlist R10.00')
rep('F = json.load(open(f"{SCRATCH}/sub9/flow9.json"))\nB = json.load(open(f"{SCRATCH}/sub8/flow8.json"))   # R8.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub10/flow10.json"))\nB = json.load(open(f"{SCRATCH}/sub9/flow9_published.json"))   # R9.00 as shipped, for the change summary only')
rep('VER = "R9.00"', 'VER = "R10.00"')
rep('<title>Sub-Sector 資金流向 Watchlist R9</title>', '<title>Sub-Sector 資金流向 Watchlist R10</title>')
rep('open(f"{SCRATCH}/sub9/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub10/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
SP = M.get("settled_print_share", {}); RV = M.get("relvol_by_source", {})
LIGHT = M.get("relvol_light", 0.8); CROSS = M.get("relvol_cross_tol", 0.75)
MID = M.get("mid_session_dropped", {}) or {}; UNADJ = M.get("unadjudicated_sessions") or []
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
rvnz = RV.get("mirror", {}); rvyh = RV.get("yahoo", {})
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R9.00）—— 數據推進至 9/15 收盤 + 對 R9.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/15 由 <b>Yahoo 收市後日線</b>提供（{SRCC.get("yahoo", 0)} 隻）；日線鏡像<b>連續第二日喺收市前提交</b>
（今次美東 14:13），該日 bar 已被剔除。</li>
<li><b>修正①（本版最重要）：R9 嘅「收市前快照」偵測用錯咗判準 —— 佢會誤刪真實嘅半日巿。</b>
R9 用<b>絕對水平</b>判斷：成交量週轉率（當日成交量 ÷ 該股前 20 日中位成交量，取橫向中位）低於 0.80 就當未收巿。
但翻查鏡像 2025-10 至今嘅歷史，低於 0.80 嘅交易日有 12 個，其中 <b>11 個係真實收市日</b>：
<b>2025-12-24 平安夜半日巿 0.348</b>、<b>2025-11-28 感恩節翌日半日巿 0.418</b>、12-26 0.507、12-30 0.664、
2026-07-10 0.694、12-31 0.709、12-29 0.718、2026-04-06 0.719、2026-08-14 0.744、12-23 0.762、2026-04-10 0.799。
<b>兩個半日巿嘅週轉率仲低過今次真正嘅盤中快照（0.472）</b> —— 即係話任何絕對門檻都分唔開兩者。
R9 呢條規則會靜靜刪走呢 11 個真實交易日，其中兩個仲要係每年固定出現。<br>
<b>真正嘅判準係「兩個來源有冇分歧」</b>：半日巿對所有來源都係短，兩邊會讀到同樣低嘅數；
盤中快照係<b>一個來源睇錯鐘</b>，另一個來源有足全日。實測四個兩邊都有 20 日基準嘅清淡交易日：
2026-04-06 鏡像 0.719／Yahoo 0.756（比值 0.952）、04-10 0.799／0.805（0.993）、07-10 0.694／0.705（0.984）、
08-14 0.744／0.793（0.938）；正常交易日 09-14 1.131／1.111（1.018）。
而今次 <b>9/15 鏡像 {rvnz.get(DAYS[-1], 0):.3f} 對 Yahoo {rvyh.get(DAYS[-1], 0):.3f}，比值只有
{(rvnz.get(DAYS[-1], 0)/rvyh.get(DAYS[-1], 1)):.3f}</b> —— 分歧明顯。<br>
本版規則：一個來源要<b>另一個來源同日讀數明顯高過佢（比值低於 {CROSS}）</b>先會被剔除；
若某個清淡交易日<b>只得一個來源</b>，冇嘢可以對證，就<b>整日拒絕</b>而唔係當佢啱。
本版剔除：鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}；
無法裁決而拒絕：{esc("、".join(UNADJ)) or "無"}。</li>
<li><b>驗證上一版：R9.00 用 Yahoo 做 9/14 嘅收盤價完全正確，成交量如標示般未結算。</b>
鏡像而家已結算 9/14（整百比例 1.6% → 99.4%）。同 R9.00 用嗰批 Yahoo 數據比較（402 隻共同覆蓋）：
<b>收盤價中位偏差 0.0000%、p95 0.0000%、最大 0.0027%，冇一隻差過 0.5%</b>；
成交量則中位差 0.38%、p95 5.45%、最大 22.3%（26 隻差過 5%）—— 正如 R9.00 當時標記「成交量未結算」。
用結算值重跑同一視窗再對比已發佈嘅 R9.00：|Δ5日 z| 中位 0.0010、最大 0.0210；
<b>|Δ名次| 中位 0、最大 4，111 個之中 88 個完全冇變，TOP12 同 BOTTOM12 全部留低 12/12</b>。</li>
<li><b>成交量定案狀態</b>：9/15 嘅 Yahoo bar 係完整一日（週轉率 {rvyh.get(DAYS[-1], 0):.3f}）但未 vendor 結算
（整百比例 <b>{SP.get(DAYS[-1], 0)*100:.1f}%</b>，已結算日約 99.7%），故標記 <b>{esc("、".join(PROV)) if PROV else "無"}</b>。</li>
<li><b>全巿中位面板</b>：沿用廣宇宙 <code>tickers_broad.txt</code>（1,692 隻），面板 <b>{max(M["mkt_n"].values()):,}</b> 隻，五日同一批。</li>
<li><b>沿用 R9.00 嘅規則</b>：B 量能用成交股數、逐來源計交易日曆、結算列印偵測喺合併後嘅 bar 上量、40% 硬上限。
鏡像須喺 {M.get("merge_since", "—")} 之後仍有數據先合併（本次 {len(stale)} 隻改用 Yahoo：{esc("、".join(stale)) or "無"}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。來源分佈：合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
全部 {M["n_tick"]} 隻有真實 OHLCV。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑）；{len(moved)} 個子板塊名次有變。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

i = src.index('② <b>數據終點'); j = src.index('<br>', src.index('|Δ名次| 中位 0、最大 3')) + 4
src = src[:i] + '''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}。
視窗內 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。<br>
<b>收市前快照防護（R10 改良）</b>：每個來源、每個交易日先計「成交量週轉率」（當日成交量 ÷ 該股前 20 日中位成交量，取橫向中位）。
低於 {LIGHT} 為<b>清淡</b>，但清淡本身唔代表未收巿 —— 半日巿（平安夜、感恩節翌日）對所有來源都係短。
所以判準係<b>跨來源分歧</b>：一個來源低過同日最高來源嘅 {CROSS} 倍先當作盤中快照並喺該來源剔走該日；
若清淡日只得一個來源、無從對證，則整日拒絕。本版剔除鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}
（{DAYS[-1]} 週轉率 {rvnz.get(DAYS[-1], 0):.3f} 對 Yahoo {rvyh.get(DAYS[-1], 0):.3f}）、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}；
拒絕 {esc("、".join(UNADJ)) or "無"}。<br>
<b>成交量定案狀態</b>：{("本版五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))} ——
以合併後實際計分嘅 bar 判別「成交量是否 100 股整數倍」（已結算日約 99.7%；{DAYS[-1]} 為 {SP.get(DAYS[-1], 0)*100:.1f}%）。
未結算日嘅收盤價準確（實測 402 隻中位偏差 0.0000%），成交量之後仍會修訂（中位 0.38%、p95 5.45%）；
對 5 日排名嘅影響實測 |Δ名次| 中位 0、最大 4。<br>''' + src[j:]
open(f"{S}/sub10/build_sub10.py", "w", encoding="utf-8").write(src); print("sub10/build_sub10.py written")
