# derive build_sub3.py from build_sub2.py, asserting every anchor
src = open("sub/build_sub2.py", encoding="utf-8").read()
def rep(old, new, cnt=1):
    global src
    assert src.count(old) >= 1, old[:80]
    src = src.replace(old, new, cnt)
def seg(start, end_marker, new):
    """replace from `start` up to and including the first `end_marker` after it"""
    global src
    i = src.index(start); j = src.index(end_marker, i) + len(end_marker)
    src = src[:i] + new + src[j:]

rep('"""Sub-Sector 資金流向 Watchlist — 111 sub-sectors x 5 sessions of money-flow scores.',
    '"""Sub-Sector 資金流向 Watchlist R3.00 — 111 sub-sectors x 5 sessions of money-flow scores.')
rep('F = json.load(open(f"{SCRATCH}/sub/flow2.json"))\nB = json.load(open(f"{SCRATCH}/sub/flow.json"))   # R1.01, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub3/flow3.json"))\nB = json.load(open(f"{SCRATCH}/sub/flow2.json"))   # R2.00, for the change summary only\n'
    'OW = json.load(open(f"{SCRATCH}/sub3/flow3_oldwin.json"))   # R3 engine on the R2 window: isolates engine vs. new-session effects\n'
    'OWROW = {r["zh"]: r for r in OW["rows"] if r.get("days")}')
rep('OUTNAME = f"SubSector_flow_watchlist_R2.00_claudeopus5high_{STAMP}.html"',
    'VER = "R3.00"\nOUTNAME = f"SubSector_flow_watchlist_{VER}_claudefable51high_{STAMP}.html"')
rep('<title>Sub-Sector 資金流向 Watchlist R1</title>', '<title>Sub-Sector 資金流向 Watchlist R3</title>')
rep('<h1>Sub-Sector 資金流向 Watchlist R1.01（', '<h1>Sub-Sector 資金流向 Watchlist {VER}（')
rep('open(f"{SCRATCH}/sub/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub3/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

# ---- sample-quality cell & basket cell ----
seg('def basket_cell(r):', 'return f\'<div class="bk">{tks}{mtag}</div>\'\n', '''def basket_cell(r):
    nb = set(r.get("nobase") or [])
    def cls(t):
        c = "tk"
        if t in (r.get("supp") or []): c += " sup"
        if t in nb: c += " nb"
        return c
    tks = "".join(f'<a href="{tv(t)}" target="_blank" rel="noopener" class="{cls(t)}"'
                  f'{" title=\\"快照 08-28 起先有數據，無 20 日量能基準：只計方向（B=0）\\"" if t in nb else ""}>{esc(t)}</a>'
                  for t in r["basket"])
    miss = r.get("missing") or []
    mtag = f'<span class="miss" title="所有可達鏡像都無視窗內數據，未計入">缺 {esc("、".join(miss))}</span>' if miss else ""
    return f'<div class="bk">{tks}{mtag}</div>'
''')
seg('def qual(r):', 'for t in tags) + "</div>")\n', '''def qual(r):
    n = r["n_basket"]
    cls = "qlo" if n <= 2 else ("qmid" if n <= 3 else "qok")
    conf = "低" if n <= 2 else ("中" if n <= 3 else "高")
    tags = [f"可信度{conf}"]
    if r.get("proxy"): tags.append("代理樣本")
    if r.get("supp"): tags.append(f"補{len(r['supp'])}")
    if r.get("src") == "snap": tags.append("僅收盤")
    elif r.get("src") == "mix": tags.append(f"OHLC {r['ohlc_cov5']*100:.0f}%")
    if r.get("nobase"): tags.append(f"無量基準{len(r['nobase'])}")
    if r.get("est_days"): tags.append(f"內插{len(r['est_days'])}日")
    return (f'<div class="qc"><b class="{cls}">{n}</b>'
            + "".join(f'<span class="qt{" cf" + t[3:] if t.startswith("可信度") else ""}">{esc(t)}</span>'
                      for t in tags) + "</div>")
''')
rep('''nv = '<span class="nvw" title="當日成交量尚未公布，量能項設為中性">量?</span>' if x.get("novol") else ""''',
    '''nv = (f'<span class="nvw" title="{x["novol"]}/{r["n_basket"]} 隻當日成交量未公布或只有內插值（或無量能基準），量能項 B 設為中性">量?</span>'
          if x.get("novol") else "")''')
rep('.bk .tk.sup{border-style:dashed;color:var(--ink2)}',
    '.bk .tk.sup{border-style:dashed;color:var(--ink2)}\n.bk .tk.nb{border-bottom:2px dotted var(--warn)}')

# ---- 本版更新 block ----
seg('upd = f"""', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]),
              key=lambda x: -(x[2] - x[1]))
grew_s = "、".join(f"{c} {a}→{b}" for c, a, b in grew[:8])
d_eng = [abs(BROW[c]["rank"] - OWROW[c]["rank"]) for c in OWROW if c in BROW]
d_win = [abs(OWROW[c]["rank"] - cur[c]["rank"]) for c in cur if c in OWROW]
med_eng = statistics.median(d_eng); med_win = statistics.median(d_win)
nb_names = sorted({t for r in live for t in (r.get("nobase") or [])})
nvd = M.get("novol_by_date", {})
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R2.00）—— 數據推進 + 對 R2.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進一個交易日</b>：計分視窗由 {BDAYS[0]} → {BDAYS[-1]} 改為 <b>{DAYS[0]} → {DAYS[-1]}</b>
（新增 {esc("、".join(NEWD))}，移出 {esc("、".join(GONED))}）。{DAYS[-1]} 收盤：日線鏡像 1,502 隻有完整 OHLCV；
其餘取 09-04 盤中快照嘅 <code>price − price_change</code>（官方前收），與日線鏡像 1,497 隻交叉核對中位偏差 0.0000%。
<b>9月4日（週五）收盤未納入</b>：截至建置時（{BUILD_TS}）所有可達鏡像都未發佈 09-04 收盤價 —— 日線鏡像只推送咗成交量、
Nasdaq 快照最新一筆係 09-04 10:24 ET 盤中價 —— 唔以盤中價冒充收盤。</li>
<li><b>修正①：40% 單一股票上限實際上無生效</b>。R2 先截上限再重新歸一化，一隻佔籃子成交額 80% 嘅股票最終仍佔 66.7%；
本版改為迭代 water-filling，實際權重嚴格 ≤40%（≥3 隻樣本嘅籃子），2 隻樣本嘅籃子上限不可達、改為等權。
同一視窗下呢項修正令名次中位變動 {med_eng:.0f} 位，最大 {max(d_eng)} 位。</li>
<li><b>修正②：唔再剔除「缺 20 日量能基準」嘅代表股</b>。R2 因此丟走 {len(nb_names)} 隻其實五日都有收盤價嘅成分股
（快照 08-28 起先有數據嘅外國發行人／ADR：{esc("、".join(nb_names[:14]))} 等）；本版以方向項計分、量能項 B 設 0 並標「無量基準」（成分股虛線底）。
08-27 前收由 08-28 收市後快照（17:03 ET）嘅 price − price_change 補回，該快照 price 與序列 08-28 收盤 6,866 隻核對偏差 0.0000%。
樣本由 {B["meta"]["n_tick"]} 隻增至 <b>{M["n_tick"]}</b> 隻，{len(grew)} 個籃子改變：{esc(grew_s)}。</li>
<li><b>修正③：08-31 內插成交量唔再當真</b>。08-31 快照序列嘅收盤係官方精確值，成交量卻係前後兩日平均；
R2 用嚟計量能項並一律標「估算」。本版將該日成交量視為<b>未知</b>（B=0、標「量?」），只有 13 隻真正內插收盤嘅先標「內插」；
各日量能未知股票數：{esc("、".join(f"{dlab(d).split('<')[0]} {nvd.get(d, 0)}" for d in DAYS if nvd.get(d)))}（全宇宙口徑）。</li>
<li><b>修正④～⑥</b>：代號含「.」（BF.B）現可對上日線檔案（BF-B）；工作簿兩句說明文字（「XBI 成分股為主」「—（多為中小型）」）
唔再被當成 ticker；混合來源籃子新增 <b>OHLC 覆蓋率</b>（有日內高低價嘅成交額比例），令「淨額估算」有幾多係真 Chaikin 一目了然。</li>
<li><b>修正⑦：頁面文字</b>。R2.00 嘅 title／H1 仍寫 R1.01、頁尾「數據終點」段仍係 R1.01 舊文並將盤中快照誤稱「盤前」—— 全部重寫。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>，連同 {dlab(DAYS[-2]).split('<')[0]} 嘅 {mkt[DAYS[-2]]*100:+.2f}% 為連續第二日回升；
{len(moved)} 個子板塊名次有變（新交易日本身令名次中位變動 {med_win:.0f} 位）。升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

# ---- rules text ----
rep('''唔另行按行業擴充 —— 令 111 個子板塊嘅樣本口徑一致、可橫向比較。工作簿無列 ticker 嘅 2 個子板塊
（臨床期中小型生技、腫瘤與細胞治療）以<b>代理樣本</b>補上；工作簿列咗但鏡像無數據嘅股票（外國 ADR 或已除牌，
如 TSM、ASML、NVO、EA、K、X）以<b>同業補充樣本</b>頂替（虛線框），兩者都喺「樣本」欄標示。<br>''',
    '''唔另行按行業擴充 —— 令 111 個子板塊嘅樣本口徑一致、可橫向比較。工作簿無列 ticker 嘅 2 個子板塊
（臨床期中小型生技、腫瘤與細胞治療）以<b>代理樣本</b>補上；工作簿列咗但所有可達鏡像視窗內都無數據嘅 {len(M["dropped"])} 隻
（{esc("、".join(M["dropped"]))}：已除牌、已被收購或跌出鏡像宇宙）唔計入，部分子板塊以<b>同業補充樣本</b>頂替（虛線框）；
08-28 起先有數據嘅外國發行人／ADR（TSM、ASML、ARM、NVO 等）照計方向、量能項設中性（虛線底）。三者都喺「樣本」欄標示。<br>''')
rep('③ <b>子板塊分</b>：籃子內以<b>成交額加權</b>（資金加權，單一股票上限 40%，避免一隻大巿值蓋過全籃）。<br>',
    '③ <b>子板塊分</b>：籃子內以<b>成交額加權</b>（資金加權），單一股票<b>硬上限 40%</b>（迭代 water-filling，超限部分按成交額比例分返俾其餘成分股；'
    '2 隻樣本嘅籃子上限不可達、改等權），避免一隻大巿值蓋過全籃。<br>')
rep('''{DAYS[-1]} 只有日線鏡像覆蓋嘅股票有真實成交量，其餘股票該日量能項設為中性、格內標「量?」，唔以估算量冒充。<br>''',
    '''成交量<b>未公布</b>（{esc("、".join(dlab(d).split("<")[0] for d in DAYS if nvd.get(d)))}：非日線鏡像覆蓋嘅股票）、
<b>只有內插值</b>（08-31）或<b>無 20 日基準</b>（08-28 起先有數據）嘅股票，該日量能項一律設為中性 0、格內標「量?」，唔以估算量冒充。<br>''')

# ---- footer ② ③ ----
i = src.index('② <b>數據終點</b>'); j = src.index('<br>', i) + 4
src = src[:i] + ('''② <b>數據終點</b>：本表以 <b>{DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>為最後一日 ——
建置時（{BUILD_TS}）日線鏡像最新提交（09-05 00:11 UTC）對 09-04 只推送咗成交量、未有 OHLC；Nasdaq 快照最新一筆（09-04 14:24 UTC）
係 10:24 ET 盤中價，其 price − price_change 只可還原 09-03 官方收盤。<span class="cav">9/4 收盤要等 9/5 快照（約 14:2x UTC）或日線鏡像下一次推送先齊；
本表唔以盤中價或成交量單邊數據冒充收盤。</span><br>''') + src[j:]
i = src.index('③ <b>估算 bar</b>'); j = src.index('<br>', i) + 4
src = src[:i] + ('''③ <b>08-31 快照缺口</b>：該日無全宇宙快照，非日線鏡像覆蓋嘅股票收盤以 09-01 快照 price − price_change（官方前收）補回、屬精確值；
成交量則無來源，本版視為未知（量能項中性、標「量?」）；只有 13 隻無法還原官方收盤嘅以前後內插，喺「樣本」欄標「內插」。<br>''') + src[j:]
rep('量能基準為 {M["base"][0]} → {M["base"][1]}（{esc("21")} 個交易日中位成交額）', '量能基準為 {M["base"][0]} → {M["base"][1]}（{M["n_base"]} 個交易日中位成交額）')
rep('本表只新增資金流向計分。<br>', '本表只新增資金流向計分。<br>\n⑦ <b>Critical review 紀錄</b>：本版對 R2.00 嘅七項修正見頂部「本版更新」，未有以紅字標示變動（依指示）。<br>'.replace('⑦','⑥b'))
open("sub3/build_sub3.py", "w", encoding="utf-8").write(src)
print("build_sub3.py written", len(src))
