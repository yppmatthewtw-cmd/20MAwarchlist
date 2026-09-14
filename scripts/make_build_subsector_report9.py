S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub8/build_sub8.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('"""Sub-Sector 資金流向 Watchlist R8.00', '"""Sub-Sector 資金流向 Watchlist R9.00')
rep('F = json.load(open(f"{SCRATCH}/sub8/flow8.json"))\nB = json.load(open(f"{SCRATCH}/sub7/flow7_published.json"))   # R7.00 as shipped, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub9/flow9.json"))\nB = json.load(open(f"{SCRATCH}/sub8/flow8.json"))   # R8.00, for the change summary only')
rep('VER = "R8.00"', 'VER = "R9.00"')
rep('<title>Sub-Sector 資金流向 Watchlist R8</title>', '<title>Sub-Sector 資金流向 Watchlist R9</title>')
rep('open(f"{SCRATCH}/sub8/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub9/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
SP = M.get("settled_print_share", {}); MU = M.get("mirror_unsettled") or []
RV = M.get("relvol_by_source", {}); RVMIN = M.get("relvol_min", 0.8)
MID = M.get("mid_session_dropped", {}) or {}
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
rvnz = RV.get("mirror", {}); rvyh = RV.get("yahoo", {})
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R8.00）—— 數據推進至 9/14 收盤 + 對 R8.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/14 由 <b>Yahoo 收市後日線</b>提供（{SRCC.get("yahoo", 0)} 隻）；日線鏡像嗰日嘅 bar 係<b>收市前嘅盤中快照</b>，已被本版剔除（見修正①）。</li>
<li><b>修正①（本版最重要）：引擎一直假設「有日期嘅 bar 就係嗰日嘅收盤」——今次呢個假設爆咗。</b>
日線鏡像喺 <b>2026-09-14 19:21 UTC（美東 15:21，收市前 40 分鐘）</b>提交咗 1,503 隻嘅「09-14」bar。
嗰批係<b>盤中快照</b>，但 R8 冇任何機制會發現收盤價係錯嘅 —— 佢只會檢查成交量結唔結算。
對比 Yahoo 同一日收市後嘅 bar（403 隻共同覆蓋）：鏡像收盤價中位差 <b>0.29%</b>、p95 1.38%、最大 2.83%，
<b>29.5% 嘅股票差超過 0.5%</b>。A 方向項喺 ±2% 就飽和，0.29% 嘅中位誤差唔係捨入差異，係另一個價。<br>
<b>偵測方法（唔需要第二個來源）：成交量週轉率。</b> 將每隻股票當日成交量除以佢自己前 20 日中位成交量，再取橫向中位數 ——
真實收市日會落喺 1.0 附近，盤中快照會遠低，因為得半日成交。實測鏡像：
真實收市日 {esc("、".join(f"{d[5:]} {v:.3f}" for d, v in sorted(rvnz.items())[:-1][-4:]))}，
而 {DAYS[-1][5:]} 只有 <b>{rvnz.get(DAYS[-1], 0):.3f}</b>（87.6% 股票低於 0.9 倍，真實收市日只有 23–37%）；
Yahoo 收市後嘅 9/14 係 <b>{rvyh.get(DAYS[-1], 0):.3f}</b> —— 完整一日，只係未 vendor 結算。
低於 <b>{RVMIN}</b> 嘅交易日會<b>喺該來源整個剔走</b>：本版剔走鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}。
冇任何來源收咗巿嘅交易日，唔會進入日曆。</li>
<li><b>驗證上一版：R8.00 用 Yahoo 做 9/11 係完全正確。</b> 鏡像而家已結算 9/11，同 R8.00 用嗰批 Yahoo 數據比較
（1,502 隻共同覆蓋）：<b>收盤價同成交量全部 1,502 隻完全一致</b> —— 中位、p95、最大偏差都係 0.0000%，
冇一隻唔同。即「最新一日改用 Yahoo」冇引入任何差異。</li>
<li><b>成交量定案狀態</b>：9/14 嘅 Yahoo bar 雖然係完整一日，但未 vendor 結算（整百比例 <b>{SP.get(DAYS[-1], 0)*100:.1f}%</b>，
已結算日約 99.7%），所以本版標記 <b>{esc("、".join(PROV)) if PROV else "無"}</b> 為成交量未結算。
歷史實測（R8.00 對 9/10 做過）：呢類未結算日嘅收盤價準確，成交量之後會改，對 5 日排名嘅影響 |Δ名次| 中位 0、最大 3。</li>
<li><b>全巿中位面板</b>：沿用 R8.00 嘅廣宇宙做法 —— <code>data/yahoo/tickers_broad.txt</code>（1,692 隻）拉取，
面板 <b>{max(M["mkt_n"].values()):,}</b> 隻，五日同一批。（若淨用報告名單，9/14 面板會塌到 532 隻大型股。）</li>
<li><b>沿用 R8.00 嘅規則</b>：B 量能用成交股數、逐來源計交易日曆、結算列印偵測喺合併後嘅 bar 上量、40% 硬上限。
鏡像須喺 {M.get("merge_since", "—")} 之後仍有數據先合併（本次 {len(stale)} 隻改用 Yahoo：{esc("、".join(stale)) or "無"}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。來源分佈：合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
全部 {M["n_tick"]} 隻有真實 OHLCV。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑）；{len(moved)} 個子板塊名次有變。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

i = src.index('② <b>數據終點'); j = src.index('<br>', src.index('依據係 9/10 結算後')) + 4
src = src[:i] + '''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}。
視窗內 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。<br>
<b>收市前快照防護（R9 新增）</b>：每個來源嘅每個交易日都要先過「成交量週轉率」檢查 ——
當日成交量 ÷ 該股前 20 日中位成交量，取橫向中位數；低於 {RVMIN} 即當作<b>未收巿</b>並將該日喺該來源整個剔走。
本版剔走：鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}（9/14 週轉率 {rvnz.get(DAYS[-1], 0):.3f}，因為鏡像喺美東 15:21 收市前就提交咗）、
Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}（9/14 週轉率 {rvyh.get(DAYS[-1], 0):.3f}）。<br>
<b>成交量定案狀態</b>：{("本版五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))} ——
以合併後實際計分嘅 bar 判別「成交量是否 100 股整數倍」（已結算日約 99.7%；{DAYS[-1]} 為 {SP.get(DAYS[-1], 0)*100:.1f}%）。
未結算日嘅收盤價準確，成交量之後仍會修訂；實測對 5 日排名嘅影響 |Δ名次| 中位 0、最大 3。<br>''' + src[j:]
open(f"{S}/sub9/build_sub9.py", "w", encoding="utf-8").write(src); print("sub9/build_sub9.py written")
