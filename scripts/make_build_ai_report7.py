S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/ai6/build_ai6.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
def seg(a,end,b):
    global src
    i=src.index(a); j=src.index(end,i)+len(end); src=src[:i]+b+src[j:]
rep('F = json.load(open(f"{SCRATCH}/ai6/flow6.json"))\nB = json.load(open(f"{SCRATCH}/ai5/flow5.json"))   # R5.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/ai7/flow7.json"))\nB = json.load(open(f"{SCRATCH}/ai6/flow6.json"))   # R6.00, for the change summary only')
rep('VER = "R6.00"','VER = "R7.00"')
rep('open(f"{SCRATCH}/ai6/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/ai7/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
seg('grew = sorted(','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R6.00）—— 數據推進至 9/8 收盤 + 對 R6.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/7 勞動節休市，所以 9/4 之後直接跳 9/8；今次 9/8 日線鏡像同 Yahoo 都有完整 OHLCV。
<b>9月9日收盤未納入</b>：建置時（{BUILD_TS} ＝ 美東 9/9 20:2x）鏡像對 09-09 只有成交量、Yahoo 532 隻得 2 隻，兩者都要隔晚結算。</li>
<li><b>修正①：全巿中位基準每日成分股唔一致</b>。R6 用「當日有報價就計」嘅池，但廣宇宙 Yahoo 檔案只去到 09-04，
令 <b>09-08 當日基準池由 2,851 隻縮到 1,632 隻</b>且偏向大型股 —— 最新一日嘅超額報酬同前四日唔同一把尺。
實測不平衡池與平衡池嘅中位數相差最多 <b>0.20 個百分點</b>。本版改用<b>平衡面板</b>：五個計分日同各自前一日都有報價嘅
<b>{max(M["mkt_n"].values()):,}</b> 隻，五日同一批。</li>
<li><b>修正②：最新一日成交量係暫定值</b>。翻查日線鏡像自己嘅提交歷史：09-04 首發（09-05 00:11 UTC）對比五日後，
抽樣 256 隻有 <b>255 隻被修訂</b>，34% 改動 &gt;1%、11% &gt;5%、p95 +11.4%。即 R5／R6 最後一日嘅量能項 B 用咗未定案成交量。
本版新增偵測並標記；<b>{"本版五日全部係定案成交量" if not PROV else "本版暫定日：" + esc("、".join(PROV))}</b>（9/8 兩邊已結算）。</li>
<li><b>儀表板象限日期</b>（R6 已更正，本版沿用並重算距離）：A9.2 面板自報 <code>asof {ASOF}</code>，唔係 8/27；
距本表視窗 <b>{GAP} 個交易日</b>，第 4 頁應讀成「兩個月前嘅 RS 位置 vs 最近五日資金流向」。</li>
<li><b>沿用 R6.00 嘅來源規則</b>：鏡像須喺 {M.get("merge_since", "—")} 後仍有數據先合併（本次 {len(stale)} 隻用 Yahoo：{esc("、".join(stale))}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，
{M["n_tick"]} 隻全部有真實 OHLCV。{len(grew)} 個籃子改變{("：" + esc("、".join(f"{cur[c]['code']} {a}→{b}" for c, a, b in grew))) if grew else ""}。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑），視窗內最大單日跌幅；
{len(moved)} 個小群組名次有變。升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
i=src.index('④ <b>數據終點'); j=src.index('<br>',i)+4
src=src[:i]+'''④ <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}收盤）</b>：建置時 {BUILD_TS}，
9/9 收盤兩個來源都未結算（鏡像只有成交量、Yahoo 532 隻得 2 隻），9/7 勞動節休市。
視窗 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。
<b>成交量定案狀態</b>：{("五日全部已結算" if not PROV else "暫定日 " + esc("、".join(PROV)))} —— 最新一日成交量首發後仍會修訂（實測 256 隻有 255 隻被改，11% &gt;5%），
故只喺兩個來源都有嗰日先當定案。<b>全巿中位</b>取自平衡面板（五日同一批 {max(M["mkt_n"].values()):,} 隻）。<br>'''+src[j:]
open(f"{S}/ai7/build_ai7.py","w",encoding="utf-8").write(src); print("build_ai7.py written")
