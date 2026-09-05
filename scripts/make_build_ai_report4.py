S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/ai/build_ai3.py",encoding="utf-8").read()
def rep(old,new):
    global src
    assert old in src, old[:80]; src=src.replace(old,new,1)
def seg(start,end,new):
    global src
    i=src.index(start); j=src.index(end,i)+len(end); src=src[:i]+new+src[j:]
rep('F = json.load(open(f"{SCRATCH}/ai/flow3.json"))\nB = json.load(open(f"{SCRATCH}/ai/flow2.json"))   # R2.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/ai4/flow4.json"))\nB = json.load(open(f"{SCRATCH}/ai/flow3.json"))   # R3.00, for the change summary only\n'
    'OW = json.load(open(f"{SCRATCH}/ai4/flow4_oldwin.json"))   # R4 engine on the R3 window (cap + 08-31 fixes only)\n'
    'OWROW = {r["code"]: r for r in OW["rows"] if r.get("days")}')
rep('OUTNAME = f"AI_Sector_watchlist_R3.00_claudeopus5high_{STAMP}.html"','def md(d): return f"{int(d[5:7])}/{int(d[8:10])}"\nVER = "R4.00"\nOUTNAME = f"AI_Sector_watchlist_{VER}_claudefable51high_{STAMP}.html"')
rep('<h1>AI Sector 資金流向 Watchlist R1.00（','<h1>AI Sector 資金流向 Watchlist {VER}（')
rep('open(f"{SCRATCH}/ai/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)','open(f"{SCRATCH}/ai4/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
# ticks cell: generic novol text + no-baseline marker
rep('''        nv = "（9/2 成交量未公布）" if t.get("novol") else ""
        out.append(
            f'<a class="tkf {tf_cls(t["tf5"])}" href="{tv(t["sym"])}" target="_blank" rel="noopener" \'''',
    '''        nv = (f"（{t['novol']} 日量能未知，B=0）" if t.get("novol") else "")
        nb = "（08-28 起先有數據，無 20 日量能基準：只計方向）" if t.get("nobase") else ""
        out.append(
            f'<a class="tkf {tf_cls(t["tf5"])}{" nb" if t.get("nobase") else ""}" href="{tv(t["sym"])}" target="_blank" rel="noopener" \'''')
rep('''            f'5日報酬 {t["ret5"]*100:+.2f}%{nv}">{esc(t["sym"])}<i>{t["tf5"]:+.2f}</i></a>')''',
    '''            f'5日報酬 {t["ret5"]*100:+.2f}%{nv}{nb}">{esc(t["sym"])}<i>{t["tf5"]:+.2f}</i></a>')''')
rep('''    mtag = (f'<span class="miss" title="美股上市但鏡像歷史不足 5+20 個交易日，未計入">數據不足 {esc("、".join(miss))}</span>\'''',
    '''    mtag = (f'<span class="miss" title="所有可達鏡像視窗內都無數據（OTC ADR 不在快照宇宙），未計入">數據不足 {esc("、".join(miss))}</span>\'''')
rep('''    nv = '<span class="nvw" title="當日成交量尚未公布，量能項設為中性">量?</span>' if x.get("novol") else ""''',
    '''    nv = (f'<span class="nvw" title="{x["novol"]}/{r["n_basket"]} 隻當日成交量未公布或只有內插值（或無量能基準），量能項 B 設為中性">量?</span>'
          if x.get("novol") else "")''')
rep('EXTRA_CSS = """','EXTRA_CSS = """\n.tkf.nb{border-bottom:2px dotted var(--warn)}')
rep('<span>儀表板 RS 象限（8/27）vs 本次實測資金流向（8/26–9/1）</span>',
    '<span>儀表板 RS 象限（8/27）vs 本次實測資金流向（{md(DAYS[0])}–{md(DAYS[-1])}）</span>')
# update block
seg('upd = f"""','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
grew_s = "、".join(f"{cur[c]['code']} {cur[c]['zh'].split(' ')[0]} {a}→{b}" for c, a, b in grew)
newg = [cur[c] for c in cur if c not in BROW]
d_eng = [abs(BROW[c]["rank"] - OWROW[c]["rank"]) for c in OWROW if c in BROW]
nb_names = sorted({t["sym"] for r in live for t in (r.get("ticks") or []) if t.get("nobase")})
nvd = M.get("novol_by_date", {})
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R3.00）—— 數據推進 + 對 R3.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進一個交易日</b>：計分視窗由 {BDAYS[0]} → {BDAYS[-1]} 改為 <b>{DAYS[0]} → {DAYS[-1]}</b>
（新增 {esc("、".join(NEWD))}，移出 {esc("、".join(GONED))}）。{DAYS[-1]} 收盤：日線鏡像 1,502 隻有完整 OHLCV，其餘取 09-04 盤中快照嘅
<code>price − price_change</code>（官方前收，與日線鏡像 1,497 隻交叉核對中位偏差 0.0000%）。<b>9月4日（週五）收盤未納入</b>：截至建置時（{BUILD_TS}）
所有可達鏡像都未發佈 09-04 收盤價 —— 日線鏡像只推送咗成交量、Nasdaq 快照最新一筆係 09-04 10:24 ET 盤中價 —— 唔以盤中價冒充收盤。</li>
<li><b>修正①：唔再剔除「缺 20 日量能基準」嘅成分股</b>。R3 因此丟走 {len(nb_names)} 隻其實五日都有收盤價嘅美股／ADR（快照 08-28 起先有數據：
{esc("、".join(nb_names))}）—— 對 AI 產業鏈影響尤大，TSM／ASML／ARM／NBIS／CCJ／BABA／BIDU 全部缺席。本版以方向項計分、量能項 B 設 0，
個股虛線底標示；08-27 前收由 08-28 收市後快照（17:03 ET）補回。計分美股由 {B["meta"]["n_tick"]} 隻增至 <b>{M["n_tick"]}</b> 隻，
{len(grew)} 個小群組籃子改變：{esc(grew_s)}；<b>{esc("、".join(f"{r['code']} {r['zh'].split(' ')[0]}" for r in newg)) or "無"}</b> 由「數據不足」變為可計算（現可計算 {len(live)} 組）。
未計入淨得 {esc("、".join(M["dropped"]))}（OTC ADR，唔在快照宇宙）。</li>
<li><b>修正②：40% 單一股票上限實際上無生效</b>。R3 先截上限再重新歸一化，一隻佔籃子成交額 80% 嘅股票最終仍佔 66.7%；本版改為迭代 water-filling，
實際權重嚴格 ≤40%（≥3 隻樣本嘅籃子；2 隻樣本上限不可達、改等權）。同一視窗下「上限＋08-31 量能」兩項修正令名次中位變動 {statistics.median(d_eng):.0f} 位、最大 {max(d_eng)} 位。</li>
<li><b>修正③：08-31 內插成交量唔再當真</b>。08-31 快照序列嘅收盤係官方精確值，成交量卻係前後兩日平均；本版將該日成交量視為<b>未知</b>（B=0、標「量?」）。
各日量能未知股票數（全宇宙口徑）：{esc("、".join(f"{md(d)} {nvd.get(d, 0)}" for d in DAYS if nvd.get(d)))}。</li>
<li><b>修正④：頁面文字</b>。R3.00 嘅 H1 仍寫 R1.00、第 4 頁標題仍寫「8/26–9/1」、頁尾「數據終點」段係 R2 舊文並話 TSM／ASML／BABA「數據不足」—— 全部重寫；
成分股欄嘅「9/2 成交量未公布」提示改為逐股顯示量能未知日數。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>，連同 {md(DAYS[-2])} 嘅 {mkt[DAYS[-2]]*100:+.2f}% 為連續第二日回升；
{len(moved)} 個小群組名次有變。升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
# rules
rep('③ <b>逐日資金流向分</b>（每隻股票、每個交易日，與 Sub-Sector Watchlist R1.01 完全相同）：<br>','③ <b>逐日資金流向分</b>（每隻股票、每個交易日，與 Sub-Sector Watchlist R3.00 完全相同）：<br>')
rep('④ <b>小群組分</b>：籃子內以<b>成交額加權</b>（單一股票上限 40%）。','④ <b>小群組分</b>：籃子內以<b>成交額加權</b>，單一股票<b>硬上限 40%</b>（迭代 water-filling；2 隻樣本嘅籃子上限不可達、改等權）。')
rep('''⑦ <b>成交量缺口</b>：{esc(DAYS[-1])} 只有日線鏡像覆蓋嘅股票有真實成交量，其餘股票該日量能項設為中性（格內標「量?」），
唔以估算量冒充；受影響嘅小群組見「趨勢」欄下方標示。<br>''',
    '''⑦ <b>成交量缺口</b>：成交量<b>未公布</b>（8/31、9/2、9/3：非日線鏡像覆蓋嘅股票）、<b>只有內插值</b>（08-31）或<b>無 20 日基準</b>
（08-28 起先有數據嘅外國發行人／ADR，如 TSM、ASML、ARM、BABA）嘅股票，該日量能項一律設為中性 0（格內標「量?」，個股虛線底），唔以估算量冒充。<br>''')
rep('本表資金流向係 <b>{DAYS[0]} → {DAYS[-1]}</b>（相差 4 個交易日）','本表資金流向係 <b>{DAYS[0]} → {DAYS[-1]}</b>（相差 {len(DAYS)} 個交易日）')
# footer ③ ④ ⑥
i=src.index('成分股全屬非美股嘅 {len(dead)} 個小群組列於總覽頂部紅框、唔參與排名。'); j=src.index('<br>',i)+4
src=src[:i]+'''成分股全屬非美股嘅 {len(dead)} 個小群組列於總覽頂部紅框、唔參與排名。08-28 起先有數據嘅 ADR（TSM、ASML、ARM、BABA、BIDU 等 {len(nb_names)} 隻）
照計方向、量能項設中性；只有 {esc("、".join(M["dropped"]))}（OTC ADR，唔在快照宇宙）因所有可達鏡像都無數據而未計入，於各行「數據不足」標示。<br>'''+src[j:]
i=src.index('④ <b>數據終點'); j=src.index('<br>',i)+4
src=src[:i]+'''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：建置時（{BUILD_TS}）日線鏡像最新提交（09-05 00:11 UTC）
對 09-04 只推送咗成交量、未有 OHLC；Nasdaq 快照最新一筆（09-04 14:24 UTC）係 10:24 ET 盤中價，其 price − price_change 只可還原 09-03 官方收盤
（與日線鏡像 1,497 隻交叉核對中位偏差 0.0000%）。<span class="cav">9/4 收盤要等 9/5 快照（約 14:2x UTC）或日線鏡像下一次推送先齊；本表唔以盤中價冒充收盤。</span>
視窗內 08-31 仍屬快照缺日：非日線鏡像覆蓋嘅股票收盤以 09-01 快照 price − price_change（官方前收）補回、屬精確值，成交量則視為未知（量能項中性）。<br>'''+src[j:]
rep('計分方法與 Sub-Sector Watchlist R1.01 完全一致 · 本表只係研究工具','計分方法與 Sub-Sector Watchlist R3.00 完全一致 · 未有以紅字標示變動（依指示）· 本表只係研究工具')
assert "WD = " in src or "WD=" in src, "need WD"
open(f"{S}/ai4/build_ai4.py","w",encoding="utf-8").write(src); print("build_ai4.py written")
