S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub3/build_sub3.py",encoding="utf-8").read()
def rep(old,new):
    global src
    assert old in src, old[:80]; src=src.replace(old,new,1)
def seg(start,end,new):
    global src
    i=src.index(start); j=src.index(end,i)+len(end); src=src[:i]+new+src[j:]
rep('"""Sub-Sector 資金流向 Watchlist R3.00 — 111 sub-sectors x 5 sessions of money-flow scores.','"""Sub-Sector 資金流向 Watchlist R4.00 — 111 sub-sectors x 5 sessions of money-flow scores (Yahoo second source).')
rep('F = json.load(open(f"{SCRATCH}/sub3/flow3.json"))\nB = json.load(open(f"{SCRATCH}/sub/flow2.json"))   # R2.00, for the change summary only\n'
    'OW = json.load(open(f"{SCRATCH}/sub3/flow3_oldwin.json"))   # R3 engine on the R2 window: isolates engine vs. new-session effects\n'
    'OWROW = {r["zh"]: r for r in OW["rows"] if r.get("days")}',
    'F = json.load(open(f"{SCRATCH}/sub4/flow4.json"))\nB = json.load(open(f"{SCRATCH}/sub3/flow3.json"))   # R3.00, for the change summary only')
rep('VER = "R3.00"','VER = "R4.00"')
rep('open(f"{SCRATCH}/sub3/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)','open(f"{SCRATCH}/sub4/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
# sample tags: Yahoo-only members instead of no-baseline
rep('''    if r.get("nobase"): tags.append(f"無量基準{len(r['nobase'])}")''',
    '''    if r.get("nobase"): tags.append(f"無量基準{len(r['nobase'])}")
    if (r.get("src_detail") or {}).get("yahoo"): tags.append(f"Yahoo {r['src_detail']['yahoo']}")''')
# update block
seg('grew = sorted(','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
xc_days = "、".join(f"{dlab(d).split('<')[0]} n={v['n']} 中位 {v['median_pct']:.4f}%（>0.5%：{v['gt_0_5']}）" for d, v in XC.items() if d[:2] == "20")
basis = XC.get("basis_disagree", [])
elec = next((r for r in live if "電子硬件" in r["zh"]), None)
import gzip as _gz, glob as _gl
_aph = {}
for _p in sorted(_gl.glob("/home/user/20MAwarchlist/data/yahoo/eod_*.csv.gz")):
    with _gz.open(_p, "rt") as _f:
        for _r in csv.DictReader(_f):
            if _r["symbol"] == "APH": _aph[_r["date"]] = float(_r["close"])
aph_ret = (_aph["2026-09-02"] / _aph["2026-09-01"] - 1) * 100 if "2026-09-02" in _aph and "2026-09-01" in _aph else None
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R3.00）—— 數據推進至 9/4 收盤 + 加入 Yahoo Finance 第二數據源交叉核對</h3><ul>
<li><b>數據推進一個交易日</b>：計分視窗由 {BDAYS[0]} → {BDAYS[-1]} 改為 <b>{DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD))}，移出 {esc("、".join(GONED))}）。
<b>9月4日（週五）收盤</b>兩個鏡像至今（{BUILD_TS}）仍未發佈，本版改由 <b>Yahoo Finance 日線</b>提供：研究容器無法連接 Yahoo，
故由 GitHub Actions runner 執行 <code>scripts/fetch_yahoo.py</code>（yfinance，未調整價）拉取本表 546 隻代表股 06-01 → 09-04 嘅日線並提交至 <code>data/yahoo/</code>（535 隻有數據），
再連同 10MA Watchlist 倉庫同一方法拉取嘅 2,758 隻合資格股（含 09-04），合共 {M.get("yahoo_n_symbols", 0):,} 隻。</li>
<li><b>交叉核對</b>：快照序列（R3 用嘅收盤）逐日對照 Yahoo：{esc(xc_days)} —— 09-02、09-03 由 price − price_change 反推嘅官方收盤與 Yahoo 100% 喺 0.5% 之內。
日線鏡像 vs Yahoo（視窗內 {XN.get("n", 0):,} 個收盤）中位 {XN.get("median_pct", 0):.4f}%，>0.5% 嘅 {XN.get("gt_0_5", 0)} 個全部集中喺 {len(basis)} 隻：
<b>APH</b>（見下）同 {esc("、".join(t for t in basis if t != "APH"))} —— 後者係日線鏡像有做股息調整（偏差 0.5–1.2%）、Yahoo 未調整價先係實際成交價，本版對呢 {len(basis)} 隻改用 Yahoo 全段歷史。</li>
<li><b>修正：APH 2 拆 1（09-02 生效）R3.00 未有調整</b>。交叉核對揭發快照序列 APH 09-01 收 $163.18、09-02 收 $80.04，係拆股而非跌 51%，
R3.00「電子硬件與EMS/連接器」09-02 嘅籃子報酬因此被拉低（當日 −6.5%）。本版採 Yahoo 已回溯調整嘅歷史（APH 09-01 收 ${_aph.get("2026-09-01", 0):.2f} → 09-02 收 ${_aph.get("2026-09-02", 0):.2f}，實際報酬 {aph_ret:+.2f}%），
電子硬件與EMS/連接器由 R3 第 {BROW[elec["zh"]]["rank"] if elec and elec["zh"] in BROW else "—"} 位變為第 {elec["rank"] if elec else "—"} 位。
呢個係 R3 引擎缺少拆股偵測嘅漏洞；Yahoo 基準核對（15 個共同交易日收盤中位偏差 ≤0.5% 先合併）今後每版都會做。</li>
<li><b>數據品質全面提升</b>：R3 有 33 隻 08-28 起先有數據嘅外國發行人／ADR 冇量能基準（只計方向）、108 隻只有收盤價冇日內高低價、08-31／09-02／09-03 三日成交量未知 ——
本版 <b>491 隻全部有真實 OHLCV</b>（日線鏡像+Yahoo 合併 {M.get("src_counts", {}).get("real", 0)} 隻、Yahoo 獨有 {M.get("src_counts", {}).get("yahoo", 0)} 隻），
量能項 B 同收位項 C 五日全部可算，「量?」「無量基準」「僅收盤」標記本版全部消失；樣本欄改標「Yahoo n」表示該籃有 n 隻只靠 Yahoo。</li>
<li><b>全巿中位基準</b>：由日線鏡像 ~1,500 隻改為日線鏡像 ∪ Yahoo 合併宇宙（每日約 {max(M["mkt_n"].values()):,} 隻），五日一致。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>；{len(moved)} 個子板塊名次有變（新交易日＋數據源升級＋APH 修正三者合計）。升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
# rules ① / ④
rep('''08-28 起先有數據嘅外國發行人／ADR（TSM、ASML、ARM、NVO 等）照計方向、量能項設中性（虛線底）。三者都喺「樣本」欄標示。<br>''',
    '''08-28 起先有數據嘅外國發行人／ADR（TSM、ASML、ARM、NVO 等）本版改由 Yahoo 日線提供完整歷史，量能基準與日內高低價齊備。<br>''')
seg('成交量<b>未公布</b>（','唔以估算量冒充。<br>','''本版視窗內 491 隻代表股五日成交量與日內高低價齊備（日線鏡像未發佈嘅 08-31／09-02／09-03 成交量及 09-04 整日由 Yahoo 補齊），無「量?」格。<br>''')
# footer ②/③
i=src.index('② <b>數據終點</b>'); j=src.index('<br>',i)+4
src=src[:i]+'''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：日線鏡像（09-05 00:11 UTC 提交）對 09-04 只有成交量、
Nasdaq 快照最新一筆係 09-04 盤中，故 09-04 整日 OHLCV 來自 <b>Yahoo Finance</b>（GitHub Actions runner 以 yfinance 拉取未調整日線，檔案 {esc("、".join(M.get("yahoo_files", [])))}）。
Yahoo 與日線鏡像喺視窗內共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%；與快照序列逐日中位偏差 0.0000%。<br>'''+src[j:]
i=src.index('③ <b>08-31 快照缺口</b>'); j=src.index('<br>',i)+4
src=src[:i]+'''③ <b>來源合併規則</b>：每隻股票以日線鏡像為主，Yahoo 補其未有嘅交易日；兩者最近 15 個共同交易日收盤中位偏差 ≤0.5% 先合併，
否則（拆股未調整、股息調整差異：{esc("、".join(basis))}）整段改用 Yahoo 已回溯調整嘅歷史。快照序列本版只作對照，唔再入計分。<br>'''+src[j:]
rep('① <b>價量數據</b>：以 <b>natezone/market-tracker</b> 嘅真實日線 OHLCV 為主（','① <b>價量數據</b>：<b>natezone/market-tracker</b> 日線 OHLCV 與 <b>Yahoo Finance</b> 日線合併（')
open(f"{S}/sub4/build_sub4.py","w",encoding="utf-8").write(src); print("build_sub4.py written")
