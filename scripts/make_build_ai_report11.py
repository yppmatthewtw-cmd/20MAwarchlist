S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/ai10/build_ai10.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('F = json.load(open(f"{SCRATCH}/ai10/flow10.json"))\nB = json.load(open(f"{SCRATCH}/ai9/flow9.json"))   # R9.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/ai11/flow11.json"))\nB = json.load(open(f"{SCRATCH}/ai10/flow10.json"))   # R10.00, for the change summary only')
rep('VER = "R10.00"', 'VER = "R11.00"')
rep('open(f"{SCRATCH}/ai10/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/ai11/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

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
<div class="upd"><h3>本版更新（{VER} vs R10.00）—— 數據推進至 9/15 收盤 + 對 R10.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/15 由 <b>Yahoo 收市後日線</b>提供（{SRCC.get("yahoo", 0)} 隻）；日線鏡像<b>連續第二日喺收市前提交</b>（美東 14:13），該日 bar 已剔除。</li>
<li><b>修正①（最重要）：上一版嘅「收市前快照」偵測用錯判準 —— 會誤刪真實嘅半日巿。</b>
上一版用<b>絕對水平</b>：成交量週轉率低於 0.80 就當未收巿。但鏡像 2025-10 至今低於 0.80 嘅 12 個交易日，
<b>11 個係真實收市日</b> —— <b>2025-12-24 平安夜 0.348</b>、<b>2025-11-28 感恩節翌日 0.418</b>（兩個都係半日巿）、
12-26 0.507、12-30 0.664、2026-07-10 0.694、12-31 0.709、12-29 0.718、04-06 0.719、08-14 0.744、12-23 0.762、04-10 0.799。
<b>兩個半日巿嘅週轉率仲低過今次真正嘅盤中快照（0.472）</b>，即任何絕對門檻都分唔開。<br>
<b>正確判準係跨來源分歧</b>：半日巿對所有來源都短，兩邊讀數一致；盤中快照係一個來源睇錯鐘。
實測清淡日 04-06 0.719／0.756（比值 0.952）、04-10 0.799／0.805（0.993）、07-10 0.694／0.705（0.984）、
08-14 0.744／0.793（0.938）；而 9/15 鏡像 {rvnz.get(DAYS[-1], 0):.3f} 對 Yahoo {rvyh.get(DAYS[-1], 0):.3f}，
比值只有 <b>{(rvnz.get(DAYS[-1], 0)/rvyh.get(DAYS[-1], 1)):.3f}</b>。
本版：一個來源要另一來源同日讀數高過佢（比值低於 {CROSS}）先剔除；清淡日若只得一個來源則整日拒絕。
本版剔除鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}；拒絕 {esc("、".join(UNADJ)) or "無"}。</li>
<li><b>驗證上一版：用 Yahoo 做 9/14 嘅收盤價完全正確。</b> 鏡像而家已結算 9/14，同上一版用嗰批 Yahoo 比較（402 隻）：
<b>收盤價中位／p95 偏差 0.0000%、最大 0.0027%，冇一隻差過 0.5%</b>；成交量中位差 0.38%、p95 5.45%（正如當時標示未結算）。
用結算值重跑同一視窗：|Δ名次| 中位 0、最大 4，<b>TOP12 同 BOTTOM12 全部留低 12/12</b>。</li>
<li><b>成交量定案狀態</b>：9/15 嘅 Yahoo bar 完整一日（週轉率 {rvyh.get(DAYS[-1], 0):.3f}）但未 vendor 結算
（整百比例 <b>{SP.get(DAYS[-1], 0)*100:.1f}%</b>），故標記 <b>{esc("、".join(PROV)) if PROV else "無"}</b>。</li>
<li><b>全巿中位面板</b>：沿用廣宇宙 <code>tickers_broad.txt</code>（1,692 隻），面板 <b>{max(M["mkt_n"].values()):,}</b> 隻。</li>
<li><b>儀表板象限日期</b>（沿用並重算距離）：A9.2 面板自報 <code>asof {ASOF}</code>，唔係 8/27；距本表視窗 <b>{GAP} 個交易日</b>。</li>
<li><b>沿用嘅規則</b>：B 量能用成交股數、逐來源計交易日曆、結算列印偵測喺合併後嘅 bar 上量、40% 硬上限。
鏡像須喺 {M.get("merge_since", "—")} 後仍有數據先合併（本次 {len(stale)} 隻用 Yahoo：{esc("、".join(stale)) or "無"}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
{M["n_tick"]} 隻全部有真實 OHLCV。{len(grew)} 個籃子改變{("：" + esc("、".join(f"{cur[c]['code']} {a}→{b}" for c, a, b in grew))) if grew else ""}。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑）；{len(moved)} 個小群組名次有變。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

i = src.index('④ <b>數據終點'); j = src.index('<br>', src.index('廣宇宙由 tickers_broad.txt')) + 4
src = src[:i] + '''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：建置時 {BUILD_TS}。
視窗 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。
<b>收市前快照防護（R11 改良）</b>：每個來源、每個交易日計「成交量週轉率」，低於 {LIGHT} 為清淡；
但清淡唔等於未收巿（半日巿對所有來源都短），所以判準係<b>跨來源分歧</b> —— 一個來源低過同日最高來源嘅 {CROSS} 倍先當盤中快照並剔走該日，
清淡日若只得一個來源則整日拒絕。本版剔除鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}
（{DAYS[-1]} 週轉率 {rvnz.get(DAYS[-1], 0):.3f} 對 Yahoo {rvyh.get(DAYS[-1], 0):.3f}）、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}。
<b>成交量定案狀態</b>：{("五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))}（{DAYS[-1]} 整百比例 {SP.get(DAYS[-1], 0)*100:.1f}%）。
<b>全巿中位</b>取自平衡面板（五日同一批 {max(M["mkt_n"].values()):,} 隻，廣宇宙由 tickers_broad.txt 1,692 隻拉取）。<br>''' + src[j:]
open(f"{S}/ai11/build_ai11.py", "w", encoding="utf-8").write(src); print("ai11/build_ai11.py written")
