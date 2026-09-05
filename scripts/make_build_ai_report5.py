S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/ai4/build_ai4.py",encoding="utf-8").read()
def rep(old,new):
    global src
    assert old in src, old[:80]; src=src.replace(old,new,1)
def seg(start,end,new):
    global src
    i=src.index(start); j=src.index(end,i)+len(end); src=src[:i]+new+src[j:]
rep('F = json.load(open(f"{SCRATCH}/ai4/flow4.json"))\nB = json.load(open(f"{SCRATCH}/ai/flow3.json"))   # R3.00, for the change summary only\n'
    'OW = json.load(open(f"{SCRATCH}/ai4/flow4_oldwin.json"))   # R4 engine on the R3 window (cap + 08-31 fixes only)\n'
    'OWROW = {r["code"]: r for r in OW["rows"] if r.get("days")}',
    'F = json.load(open(f"{SCRATCH}/ai5/flow5.json"))\nB = json.load(open(f"{SCRATCH}/ai4/flow4.json"))   # R4.00, for the change summary only')
rep('VER = "R4.00"','VER = "R5.00"')
rep('open(f"{SCRATCH}/ai4/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)','open(f"{SCRATCH}/ai5/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
seg('grew = sorted(','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
grew_s = "、".join(f"{cur[c]['code']} {cur[c]['zh'].split(' ')[0]} {a}→{b}" for c, a, b in grew)
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
xc_days = "、".join(f"{md(d)} n={v['n']} 中位 {v['median_pct']:.4f}%（>0.5%：{v['gt_0_5']}）" for d, v in XC.items() if d[:2] == "20")
basis = XC.get("basis_disagree", [])
d5 = cur.get("D5"); d5_old = BROW.get("D5")
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R4.00）—— 數據推進至 9/4 收盤 + 加入 Yahoo Finance 第二數據源交叉核對</h3><ul>
<li><b>數據推進一個交易日</b>：計分視窗由 {BDAYS[0]} → {BDAYS[-1]} 改為 <b>{DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD))}，移出 {esc("、".join(GONED))}）。
<b>9月4日（週五）收盤</b>兩個鏡像至今（{BUILD_TS}）仍未發佈，本版改由 <b>Yahoo Finance 日線</b>提供：研究容器無法連接 Yahoo，故由 GitHub Actions runner 執行
<code>scripts/fetch_yahoo.py</code>（yfinance，未調整價）拉取兩份報告合共 546 隻代表股 06-01 → 09-04 嘅日線並提交至 <code>data/yahoo/</code>，
再連同 10MA Watchlist 倉庫同一方法拉取嘅 2,758 隻合資格股，合共 {M.get("yahoo_n_symbols", 0):,} 隻。</li>
<li><b>交叉核對</b>：快照序列（R4 用嘅收盤）逐日對照 Yahoo：{esc(xc_days)} —— 09-02、09-03 反推嘅官方收盤與 Yahoo 100% 喺 0.5% 之內。
日線鏡像 vs Yahoo（視窗內 {XN.get("n", 0):,} 個收盤）中位 {XN.get("median_pct", 0):.4f}%，偏差 >0.5% 嘅只集中喺 {esc("、".join(basis))}（APH 拆股未調整、QCOM 股息調整差異），該兩隻改用 Yahoo 全段歷史。</li>
<li><b>修正：APH 2 拆 1（09-02 生效）R4.00 未有調整</b>。快照序列 APH 09-01 收 $163.18、09-02 收 $80.04，係拆股而非跌 51%：R4.00 <b>D5 連接器／線纜</b>
09-02 籃子報酬因此顯示 −26.9%、APH 個股 5 日報酬 −49%，但該組仍排第 1。本版採 Yahoo 已回溯調整嘅歷史（D5 由 R4 第 {d5_old["rank"] if d5_old else "—"} 位變為第 {d5["rank"] if d5 else "—"} 位）。
呢個係 R4 引擎缺少拆股偵測嘅漏洞；Yahoo 基準核對今後每版都會做。</li>
<li><b>數據品質全面提升</b>：R4 有 13 隻 ADR 冇量能基準（TSM／ASML／ARM／BABA／BIDU／NBIS 等只計方向）、38 隻只有收盤價、三日成交量未知 ——
本版 <b>{M["n_tick"]} 隻全部有真實 OHLCV</b>（日線鏡像+Yahoo 合併 {M.get("src_counts", {}).get("real", 0)} 隻、Yahoo 獨有 {M.get("src_counts", {}).get("yahoo", 0)} 隻），
SBGSY、TCEHY（OTC ADR）亦由 Yahoo 補齊，未計入名單清零；量能項 B 同收位項 C 五日全部可算，「量?」「無量基準」標記全部消失。
{len(grew)} 個籃子改變：{esc(grew_s) or "無"}。</li>
<li><b>全巿中位基準</b>：由日線鏡像 ~1,500 隻改為日線鏡像 ∪ Yahoo 合併宇宙（每日約 {max(M["mkt_n"].values()):,} 隻），五日一致。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>；{len(moved)} 個小群組名次有變（新交易日＋數據源升級＋APH 修正合計）。升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
seg('⑦ <b>成交量缺口</b>：','唔以估算量冒充。<br>','''⑦ <b>成交量</b>：本版視窗內 {M["n_tick"]} 隻美股／ADR 五日成交量與日內高低價齊備（日線鏡像未發佈嘅日子及 09-04 整日由 Yahoo 補齊），無「量?」格；
Yahoo 與日線鏡像基準核對（最近 15 個共同交易日收盤中位偏差 ≤0.5% 先合併，否則整段改用 Yahoo 已回溯調整嘅歷史）。<br>''')
rep('（相差 {len(DAYS)} 個交易日）','（相差 {len(DAYS) + 1} 個交易日）')   # dashboard 08-27 -> window 08-31..09-04: 08-28 sits in between
rep('與 Sub-Sector Watchlist R3.00 完全相同','與 Sub-Sector Watchlist R4.00 完全相同')
i=src.index('08-28 起先有數據嘅 ADR（TSM、ASML、ARM、BABA、BIDU 等'); j=src.index('<br>',i)+4
src=src[:i]+'''08-28 起先有數據嘅 ADR（TSM、ASML、ARM、BABA、BIDU 等）及 OTC ADR（SBGSY、TCEHY）本版全部由 Yahoo 日線提供完整歷史，無未計入成分股。<br>'''+src[j:]
i=src.index('④ <b>數據終點'); j=src.index('<br>',i)+4
src=src[:i]+'''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：日線鏡像（09-05 00:11 UTC 提交）對 09-04 只有成交量、Nasdaq 快照最新一筆係 09-04 盤中，
故 09-04 整日 OHLCV 來自 <b>Yahoo Finance</b>（GitHub Actions runner 以 yfinance 拉取未調整日線：{esc("、".join(M.get("yahoo_files", [])))}）。
Yahoo 與日線鏡像視窗內共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%；與快照序列逐日中位偏差 0.0000%。每隻股票以日線鏡像為主、Yahoo 補其未有嘅交易日；基準不符者（{esc("、".join(basis))}）整段改用 Yahoo。<br>'''+src[j:]
rep('計分方法與 Sub-Sector Watchlist R3.00 完全一致','計分方法與 Sub-Sector Watchlist R4.00 完全一致')
rep('② <b>價量數據</b>：natezone/market-tracker 真實日線 OHLCV 為主（有日內高低價，可算 Chaikin 收位），\n其餘以 Nasdaq 快照重建序列補足（只有收盤與成交量）。',
    '② <b>價量數據</b>：natezone/market-tracker 日線 OHLCV 與 Yahoo Finance 日線合併（全部有日內高低價，可算 Chaikin 收位）；Nasdaq 快照重建序列只作交叉對照。')
open(f"{S}/ai5/build_ai5.py","w",encoding="utf-8").write(src); print("build_ai5.py written")
