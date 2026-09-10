S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub5/build_sub5.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
def seg(a,end,b):
    global src
    i=src.index(a); j=src.index(end,i)+len(end); src=src[:i]+b+src[j:]
rep('"""Sub-Sector 資金流向 Watchlist R5.00','"""Sub-Sector 資金流向 Watchlist R6.00')
rep('F = json.load(open(f"{SCRATCH}/sub5/flow5.json"))\nB = json.load(open(f"{SCRATCH}/sub4/flow4.json"))   # R4.00, for the change summary only',
    'F = json.load(open(f"{SCRATCH}/sub6/flow6.json"))\nB = json.load(open(f"{SCRATCH}/sub5/flow5.json"))   # R5.00, for the change summary only')
rep('VER = "R5.00"','VER = "R6.00"')
rep('<title>Sub-Sector 資金流向 Watchlist R5</title>','<title>Sub-Sector 資金流向 Watchlist R6</title>')
rep('open(f"{SCRATCH}/sub5/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)',
    'open(f"{SCRATCH}/sub6/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)')
seg('grew = sorted(','</ul></div>"""','''grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
XC = M.get("yahoo_xcheck", {}); XN = XC.get("natezone_vs_yahoo") or {}
basis = XC.get("basis_disagree", []); stale = M.get("stale_mirror", [])
SRCN = M.get("src_counts", {}); PROV = M.get("provisional_vol_days") or []
NEWD2 = [d for d in DAYS if d not in BDAYS]; GONED2 = [d for d in BDAYS if d not in DAYS]
upd = f"""
<div class="upd"><h3>本版更新（{VER} vs R5.00）—— 數據推進至 9/8 收盤 + 對 R5.00 嘅 critical review 修正</h3><ul>
<li><b>數據推進：計分視窗 {DAYS[0]} → {DAYS[-1]}</b>（新增 {esc("、".join(NEWD2))}，移出 {esc("、".join(GONED2))}）。
9/7 為勞動節休市，所以 9/4 之後直接跳到 9/8。<b>今次 9/8 兩個來源都齊</b>：日線鏡像（09-10 00:09 UTC 提交）同 Yahoo 都有完整 09-08 OHLCV。
<b>9月9日（週三）收盤未納入</b>：建置時（{BUILD_TS} ＝ 美東 9/9 20:2x）日線鏡像對 09-09 只推送咗成交量、
Yahoo 532 隻只有 2 隻有 09-09 日線 —— 兩者都要隔晚先結算。</li>
<li><b>修正①：全巿中位基準每日嘅成分股唔一樣</b>（本版最重要嘅修正）。R5 嘅基準池係「當日有報價嘅所有股票」，
但 10MA 倉庫嗰份 2,758 隻嘅 Yahoo 檔案只去到 09-04，所以 <b>09-08 當日基準池由 2,851 隻跌到 1,632 隻</b>，
而且剩低嘅偏向大型股 —— 即係最新一日嘅「超額報酬」係同另一批股票比較，同前四日唔同一把尺。
實測：喺廣宇宙有覆蓋嘅日子，不平衡池同平衡池嘅中位數相差最多 <b>0.20 個百分點</b>（9/2：+0.82% vs +0.62%），
足以令一隻超額報酬為零嘅股票 A 項偏移約 0.10。本版改為<b>平衡面板</b> —— 只計五個計分日<b>同各自前一日</b>都有報價嘅
<b>{max(M["mkt_n"].values()):,}</b> 隻，五日同一批。</li>
<li><b>修正②：最新一日嘅成交量係暫定值</b>。翻查日線鏡像自己嘅歷史提交發現：09-04 首次發佈（09-05 00:11 UTC）同五日後嘅同一日成交量，
抽樣 256 隻之中 <b>255 隻被修訂過</b> —— 34% 改動超過 1%、11% 超過 5%、第 95 百分位 +11.4%。
即係話 R4.00／R5.00 嘅最後一日（09-04）量能項 B 係用未定案成交量計嘅。本版新增偵測：
若某日只有 Yahoo 有、鏡像未發佈，就標記為「成交量暫定」。<b>{"本版五日全部係定案成交量" if not PROV else "本版暫定日：" + esc("、".join(PROV))}</b> ——
9/8 兩邊都已結算，所以今期五日全部係定案成交量。</li>
<li><b>沿用 R5.00 嘅來源規則</b>：鏡像須喺 {M.get("merge_since", "—")} 之後仍有數據先合併（本次 {len(stale)} 隻改用 Yahoo：{esc("、".join(stale))}）；
基準不符者 {esc("、".join(basis)) or "無"} 整段用 Yahoo。交叉核對：鏡像 vs Yahoo 視窗內 {XN.get("n", 0):,} 個收盤中位 {XN.get("median_pct", 0):.4f}%。
來源分佈：合併 {SRCN.get("real", 0)} 隻、Yahoo 獨有 {SRCN.get("yahoo", 0)} 隻，全部 {M["n_tick"]} 隻有真實 OHLCV。</li>
<li><b>市況</b>：{DAYS[-1]} 全巿中位 <b>{mkt[DAYS[-1]]*100:+.2f}%</b>（平衡面板口徑），
為視窗內最大單日跌幅；{len(moved)} 個子板塊名次有變（新交易日＋基準改為平衡面板）。
升幅最大 {esc("、".join(up3)) or "無"}；跌幅最大 {esc("、".join(dn3)) or "無"}。</li>
</ul></div>"""''')
i=src.index('② <b>數據終點'); j=src.index('<br>',i)+4
src=src[:i]+'''② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：建置時 {BUILD_TS}，
9/9 收盤兩個來源都未結算（鏡像只有成交量、Yahoo 532 隻得 2 隻），故未納入；9/7 勞動節休市。
視窗內 OHLCV 為日線鏡像與 Yahoo Finance 合併（{esc("、".join(M.get("yahoo_files", [])))}），共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%。
<b>成交量定案狀態</b>：{("本版五日全部已結算（兩個來源都有）" if not PROV else "暫定日 " + esc("、".join(PROV)))} ——
最新一日嘅成交量喺首次發佈後仍會修訂（實測抽樣 256 隻有 255 隻被改，11% 改動 &gt;5%），故本表只喺兩邊都有嗰日先當定案。<br>'''+src[j:]
rep('''④ <b>穩健分／資金強度／廣度</b>''',
    '''④b <b>全巿中位基準</b>：A 項嘅「當日全巿場中位報酬」取自<b>平衡面板</b> —— 五個計分日同各自前一日都有報價嘅 {max(M["mkt_n"].values()):,} 隻股票，
五日同一批，令逐日分數用同一把尺。（若改用「當日有報價就計」嘅不平衡池，最新一日會因為廣宇宙數據未到而換成另一批偏大型股嘅樣本。）<br>
④ <b>穩健分／資金強度／廣度</b>''')
open(f"{S}/sub6/build_sub6.py","w",encoding="utf-8").write(src); print("build_sub6.py written")
