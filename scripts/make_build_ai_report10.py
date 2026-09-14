S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/ai9/build_ai9.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('F = json.load(open(f"{SCRATCH}/ai9/flow9.json"))\nB = json.load(open(f"{SCRATCH}/ai8/flow8.json"))   # R8.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/ai10/flow10.json"))\nB = json.load(open(f"{SCRATCH}/ai9/flow9.json"))   # R9.00, for the change summary only')
rep('VER = "R9.00"', 'VER = "R10.00"')
rep('open(f"{SCRATCH}/ai9/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/ai10/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
SP = M.get("settled_print_share", {}); RV = M.get("relvol_by_source", {})
RVMIN = M.get("relvol_min", 0.8); MID = M.get("mid_session_dropped", {}) or {}
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
rvnz = RV.get("mirror", {}); rvyh = RV.get("yahoo", {})
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R9.00）—— 數據推進至 9/14 收盤 + 對 R9.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/14 由 <b>Yahoo 收市後日線</b>提供（{SRCC.get("yahoo", 0)} 隻）；日線鏡像嗰日嘅 bar 係收市前嘅盤中快照，已被本版剔除。</li>
<li><b>修正①（最重要）：引擎一直假設「有日期嘅 bar 就係嗰日嘅收盤」——今次爆咗。</b>
日線鏡像喺 <b>2026-09-14 美東 15:21（收市前 40 分鐘）</b>提交咗 1,503 隻嘅「09-14」bar，
但 R9 只會檢查成交量結唔結算，唔會發現收盤價係錯嘅。對比 Yahoo 同日收市後嘅 bar（403 隻）：
鏡像收盤價中位差 <b>0.29%</b>、p95 1.38%、最大 2.83%，<b>29.5% 差超過 0.5%</b> —— A 方向項喺 ±2% 就飽和，呢個唔係捨入差異。<br>
<b>偵測方法（唔需第二來源）：成交量週轉率</b> —— 當日成交量 ÷ 該股前 20 日中位成交量，取橫向中位數；
真實收市日近 1.0，盤中快照遠低。實測鏡像 9/14 只有 <b>0.596</b>（真實收市日 0.99–1.10），
Yahoo 收市後嘅 9/14 係 <b>{rvyh.get(DAYS[-1], 0):.3f}</b>。低於 <b>{RVMIN}</b> 即喺該來源整個剔走該日：
本版剔走鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}。</li>
<li><b>驗證上一版：用 Yahoo 做 9/11 係完全正確。</b> 鏡像而家已結算 9/11，同上一版用嗰批 Yahoo 數據比較（1,502 隻）：
<b>收盤價同成交量全部完全一致</b>，中位／p95／最大偏差都係 0.0000%。</li>
<li><b>成交量定案狀態</b>：9/14 嘅 Yahoo bar 雖係完整一日但未 vendor 結算（整百比例 <b>{SP.get(DAYS[-1], 0)*100:.1f}%</b>，已結算日約 99.7%），
故標記 <b>{esc("、".join(PROV)) if PROV else "無"}</b>。歷史實測呢類日子對 5 日排名嘅影響：|Δ名次| 中位 0、最大 3。</li>
<li><b>全巿中位面板</b>：沿用廣宇宙 <code>tickers_broad.txt</code>（1,692 隻），面板 <b>{max(M["mkt_n"].values()):,}</b> 隻，五日同一批。</li>
<li><b>儀表板象限日期</b>（沿用並重算距離）：A9.2 面板自報 <code>asof {ASOF}</code>，唔係 8/27；
距本表視窗 <b>{GAP} 個交易日</b>，第 4 頁應讀成「兩個多月前嘅 RS 位置 vs 最近五日資金流向」。</li>
<li><b>沿用嘅規則</b>：B 量能用成交股數、逐來源計交易日曆、結算列印偵測喺合併後嘅 bar 上量、40% 硬上限。
鏡像須喺 {M.get("merge_since", "—")} 後仍有數據先合併（本次 {len(stale)} 隻用 Yahoo：{esc("、".join(stale)) or "無"}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
{M["n_tick"]} 隻全部有真實 OHLCV。{len(grew)} 個籃子改變{("：" + esc("、".join(f"{cur[c]['code']} {a}→{b}" for c, a, b in grew))) if grew else ""}。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑）；{len(moved)} 個小群組名次有變。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

i = src.index('④ <b>數據終點'); j = src.index('<br>', src.index('廣宇宙日線由 tickers_broad.txt')) + 4
src = src[:i] + '''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：建置時 {BUILD_TS}。
視窗 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。
<b>收市前快照防護（R10 新增）</b>：每個來源嘅每個交易日先過「成交量週轉率」檢查（當日成交量 ÷ 該股前 20 日中位成交量，取橫向中位數），
低於 {RVMIN} 即當作未收巿並喺該來源整個剔走 —— 本版剔走鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}
（9/14 週轉率 {rvnz.get(DAYS[-1], 0):.3f}，鏡像喺美東 15:21 收市前就提交咗）、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}。
<b>成交量定案狀態</b>：{("五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))}（{DAYS[-1]} 整百比例 {SP.get(DAYS[-1], 0)*100:.1f}%）。
<b>全巿中位</b>取自平衡面板（五日同一批 {max(M["mkt_n"].values()):,} 隻，廣宇宙由 tickers_broad.txt 1,692 隻拉取）。<br>''' + src[j:]
open(f"{S}/ai10/build_ai10.py", "w", encoding="utf-8").write(src); print("ai10/build_ai10.py written")
