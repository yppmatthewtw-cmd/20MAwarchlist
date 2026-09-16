S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub10/build_sub10.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)
def seg(a, end, b):
    global src
    i = src.index(a); j = src.index(end, i) + len(end); src = src[:i] + b + src[j:]

rep('"""Sub-Sector 資金流向 Watchlist R10.00', '"""Sub-Sector 資金流向 Watchlist R11.00')
rep('.mf{font-weight:600}',
    '.mf{font-weight:600}\n'
    '.pvm{color:var(--mut);font-weight:400;font-size:.78em;cursor:help;margin-left:1px}')
rep('F = json.load(open(f"{SCRATCH}/sub10/flow10.json"))\nB = json.load(open(f"{SCRATCH}/sub9/flow9_published.json"))   # R9.00 as shipped, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub11/flow11.json"))\nB = json.load(open(f"{SCRATCH}/sub10/flow10_published.json"))   # R10.00 as shipped, for the change summary only')
rep('VER = "R10.00"', 'VER = "R11.00"')
rep('<title>Sub-Sector 資金流向 Watchlist R10</title>', '<title>Sub-Sector 資金流向 Watchlist R11</title>')
rep('open(f"{SCRATCH}/sub10/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub11/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')

# ---- F1: mark the net-flow dollars that rest on an unsettled session ----
rep('''def fmt_m(v):''',
'''MFD_SETTLED = F["meta"].get("mfd_settled") or {}
PROV_DAYS = [d for d, ok in MFD_SETTLED.items() if not ok]
# F1: the score is robust to an unsettled session (p95 1.82 of 100 points, rank max 4) but the
# net-flow dollars are linear in volume and move by a p95 of 16.3%. Mark every dollar figure that
# includes such a session so the reader knows which number to lean on.
MFD_TIP = ("　※ 含未結算成交量嘅交易日（" + "、".join(PROV_DAYS) + "）：淨額估算屬臨時值，"
           "實測中位偏差 1.2%、第 95 百分位 16.3%、最大 75.4%（分數與名次唔受影響：p95 1.8 分、名次最多差 4）") if PROV_DAYS else ""

def prov_mark(has_prov=True):
    return f'<sup class="pvm" title="{esc(MFD_TIP.strip())}">≈</sup>' if (PROV_DAYS and has_prov) else ""

def fmt_m(v):''')

rep('''                   f'籃子報酬 {x["ret"]*100:+.2f}% · 量能 {x["rvol"]:.2f}x · 淨額 {fmt_m(x["mfd"])}">'
                   f'{x["score"]:.0f}</span>')''',
'''                   f'籃子報酬 {x["ret"]*100:+.2f}% · 量能 {x["rvol"]:.2f}x · '
                   f'淨額 {fmt_m(x["mfd"])}{"（成交量未結算，屬臨時值）" if not MFD_SETTLED.get(d, True) else ""}">'
                   f'{x["score"]:.0f}</span>')''')


# the three places a net-flow figure is printed, each disambiguated by what follows it
A1 = '{fmt_m(r["mfd5"])}</td>\'\n              f\'<td class="nums {"pos" if r["intensity"]'
rep(A1, A1.replace('{fmt_m(r["mfd5"])}</td>', '{fmt_m(r["mfd5"])}{prov_mark()}</td>'))
A2 = '{fmt_m(r["mfd5"])}</td></tr>'
rep(A2, '{fmt_m(r["mfd5"])}{prov_mark()}</td></tr>')
A3 = '{fmt_m(a["mfd"])}</td>\'\n              f\'<td class="nums mut">'
rep(A3, A3.replace('{fmt_m(a["mfd"])}</td>', '{fmt_m(a["mfd"])}{prov_mark()}</td>'))

rep('''<th class="srt" data-key="mfd">淨額估算<span class="thn">5日合計 ↓</span></th>''',
    '''<th class="srt" data-key="mfd">淨額估算<span class="thn">{"5日合計 ↓　≈臨時" if PROV_DAYS else "5日合計 ↓"}</span></th>''')

# a visible legend line under the table controls
rep('''<span>格內數字＝當日 0–100 分（橫向百分位）· 滑鼠停留睇 z 值／籃子報酬／量能倍數</span>''',
    '''<span>格內數字＝當日 0–100 分（橫向百分位）· 滑鼠停留睇 z 值／籃子報酬／量能倍數{"　·　淨額估算旁嘅 ≈ ＝ 含未結算成交量嘅交易日，屬臨時值（分數與名次唔受影響）" if PROV_DAYS else ""}</span>''')

seg('grew = sorted(', '</ul></div>"""', '''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
SP = M.get("settled_print_share", {}); RV = M.get("relvol_by_source", {})
CROSS = M.get("relvol_cross_tol", 0.75); MID = M.get("mid_session_dropped", {}) or {}
PE = M.get("mfd_provisional_effect", {}) or {}
SRCC = (M.get("src_coverage", {}) or {}).get(DAYS[-1], {})
rvnz = RV.get("mirror", {}); rvyh = RV.get("yahoo", {})
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R10.00）—— 數據推進至 9/16 收盤（FOMC 日）+ 對 R10.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/16 由 <b>Yahoo 收市後日線</b>提供（{SRCC.get("yahoo", 0)} 隻）；日線鏡像<b>連續第三日喺收市前提交</b>（今次美東 14:15，
週轉率 {rvnz.get(DAYS[-1], 0):.3f} 對 Yahoo {rvyh.get(DAYS[-1], 0):.3f}，比值 {(rvnz.get(DAYS[-1], 0)/rvyh.get(DAYS[-1], 1)):.3f}），R10 嘅跨來源裁決照樣剔走。</li>
<li><b>修正①（本版最重要）：分清楚「未結算成交量」究竟影響邊個數字。</b>
連續三版（9/10、9/14、9/15）都試過喺成交量未結算嘅情況下計最新一日，之後鏡像結算咗再回頭核對，結論一致：
<b>收盤價完全準確</b>（三次共同覆蓋 402–1,502 隻，中位同 p95 偏差都係 0.0000%，冇一隻差過 0.5%），
但<b>成交量偏差逐日唔同</b>（9/14 中位 0.38%／p95 5.45%；<b>9/15 中位 0.30%／p95 14.95%／最大 61%，1,502 隻之中 224 隻差過 5%</b>）。<br>
之前一直冇量度嘅係：<b>呢個誤差會傳到邊個已公佈嘅數字</b>。用結算值重跑 R10.00 同一視窗：
<b>逐日分數</b>中位差 <b>0.00</b> 分、p95 <b>{PE.get("score_p95_pts", 0):.2f}</b> 分（100 分制）、最大 {PE.get("score_max_pts", 0):.2f} 分；
<b>名次</b>中位差 0、<b>最大 {PE.get("rank_max", 0)}</b>，TOP12 同 BOTTOM12 全部留低 12/12；
但 <b>淨額估算（美元）</b>中位差 {PE.get("mfd_median_pct", 0):.2f}%、<b>p95 {PE.get("mfd_p95_pct", 0):.1f}%</b>、最大 {PE.get("mfd_max_pct", 0):.1f}%，
<b>111 個之中 {PE.get("mfd_gt10pct_rows", 0)} 個差過 10%、3 個差過 25%</b>（最差係機械與重工 −$33M 對結算值 −$133M）。<br>
原因好直接：分數經過 log 壓縮嘅 B 再做橫向百分位，誤差被兩重削平；<b>淨額估算係成交量嘅線性函數</b>，15% 成交量誤差就係 15% 金額誤差，
而絕對金額細嘅籃子百分比會爆。<b>之前報表印呢啲美元數字係冇任何註明嘅</b> —— 本版喺所有含未結算交易日嘅淨額估算旁加 <b>≈</b> 標記，
滑鼠停留列明實測偏差，並喺表頭同圖例講明「分數同名次唔受影響，淨額屬臨時值」。</li>
<li><b>驗證上一版：R10.00 用 Yahoo 做 9/15 嘅收盤價完全正確。</b> 鏡像現已結算 9/15（整百比例 1.8% → 99.7%），
同 R10.00 用嗰批 Yahoo 比較（<b>1,502 隻</b>共同覆蓋）：<b>收盤價中位／p95 偏差 0.0000%、最大 0.0580%，冇一隻差過 0.5%，645 隻完全一致</b>；
成交量則如標示般未結算。</li>
<li><b>成交量定案狀態</b>：9/16 嘅 Yahoo bar 係完整一日（週轉率 {rvyh.get(DAYS[-1], 0):.3f}）但未 vendor 結算
（整百比例 <b>{SP.get(DAYS[-1], 0)*100:.1f}%</b>），故標記 <b>{esc("、".join(PROV)) if PROV else "無"}</b>，
該日嘅淨額估算已加 ≈ 標記。</li>
<li><b>沿用 R10.00 嘅規則</b>：清淡交易日由<b>跨來源分歧</b>裁決（比值低於 {CROSS} 先剔除，保住平安夜／感恩節翌日嗰類半日巿）；
B 量能用成交股數；逐來源計交易日曆；結算列印偵測喺合併後嘅 bar 上量；40% 硬上限；
全巿中位用廣宇宙平衡面板 <b>{max(M["mkt_n"].values()):,}</b> 隻。
本版剔除鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}、Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}。
來源分佈：合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，全部 {M["n_tick"]} 隻有真實 OHLCV；
鏡像停更 {len(stale)} 隻改用 Yahoo（{esc("、".join(stale)) or "無"}）；基準不符 {esc("、".join(basis)) or "無"}。</li>
<li><b>市況</b>：{DAYS[-1]}（FOMC 決議日）全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑）；{len(moved)} 個子板塊名次有變。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')

i = src.index('② <b>數據終點'); j = src.index('<br>', src.index('|Δ名次| 中位 0、最大 4')) + 4
src = src[:i] + '''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}。
視窗內 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。<br>
<b>收市前快照防護</b>：每個來源、每個交易日計「成交量週轉率」（當日成交量 ÷ 該股前 20 日中位成交量，取橫向中位）；
清淡唔等於未收巿（半日巿對所有來源都短），所以由<b>跨來源分歧</b>裁決 —— 一個來源低過同日最高來源嘅 {CROSS} 倍先當盤中快照並剔走該日。
本版剔除鏡像 {esc("、".join(MID.get("mirror") or [])) or "無"}（{DAYS[-1]} 週轉率 {rvnz.get(DAYS[-1], 0):.3f} 對 Yahoo {rvyh.get(DAYS[-1], 0):.3f}）、
Yahoo {esc("、".join(MID.get("yahoo") or [])) or "無"}。<br>
<b>成交量定案狀態與影響範圍</b>：{("本版五日全部已結算" if not PROV else "未結算：" + esc("、".join(PROV)))}
（以合併後實際計分嘅 bar 判別「成交量是否 100 股整數倍」；已結算日約 99.7%，{DAYS[-1]} 為 {SP.get(DAYS[-1], 0)*100:.1f}%）。
未結算日嘅<b>收盤價準確</b>（連續三次實測，中位與 p95 偏差 0.0000%），但成交量會修訂，而且<b>只影響金額、唔影響排名</b>：
實測逐日分數 p95 差 {PE.get("score_p95_pts", 0):.2f} 分（100 分制）、名次最多差 {PE.get("rank_max", 0)}；
<b>淨額估算 p95 差 {PE.get("mfd_p95_pct", 0):.1f}%、最大 {PE.get("mfd_max_pct", 0):.1f}%</b>，故該等金額旁標 <b>≈</b>。<br>''' + src[j:]
open(f"{S}/sub11/build_sub11.py", "w", encoding="utf-8").write(src); print("sub11/build_sub11.py written")
