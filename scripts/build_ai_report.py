#!/usr/bin/env python3
"""AI Sector Watchlist — 41 AI 小群組 x 5 sessions of money-flow scores.

Same framework as the Sub-Sector watchlist R1.01: identical scoring engine, identical
palette / theme control / table interactions (CSS and JS are read from that build so the
two reports stay one system). What differs is the domain: baskets come from the Dashboard
R15.6 AI 小群組 classification, restricted to US listings and US ADRs, and the divergence
page compares the dashboard's RS quadrant against the measured money flow.

Pages: 總覽 / 每日矩陣 / 大分類匯總 / 象限背離.
"""
import json, datetime, html, os, statistics, collections

SCRATCH = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
F = json.load(open(f"{SCRATCH}/ai/flow.json"))
M = F["meta"]; ROWS = F["rows"]; DAYS = M["days"]
CSS = open(f"{SCRATCH}/ai/_css.txt").read()
JS = open(f"{SCRATCH}/ai/_js.txt").read()
now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
OUTNAME = f"AI_Sector_watchlist_R1.00_claudeopus5high_{STAMP}.html"
WD = "一二三四五六日"

def esc(s): return html.escape(str(s), quote=True)
def dlab(d):
    dt = datetime.date.fromisoformat(d)
    return f"{dt.month}/{dt.day}<span class=\"wd\">週{WD[dt.weekday()]}</span>"

GRADE_ZH = {3: "強力流入", 2: "流入", 1: "偏流入", 0: "中性", -1: "偏流出", -2: "流出", -3: "強力流出"}
def gcls(g): return f"g{'p' if g > 0 else 'n' if g < 0 else '0'}{abs(g)}"

def fmt_m(v):
    a = abs(v) / 1e6
    if a >= 1000: return f"{'+' if v > 0 else '-'}${a/1000:.1f}B"
    return f"{'+' if v > 0 else '-'}${a:,.0f}M"

def tv(t):
    return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={esc(t.lower())}'

def meter(v, cls=""):
    return (f'<div class="mc {cls}"><b class="nums">{v:.0f}</b>'
            f'<span class="meter"><i style="width:{max(0, min(100, v)):.0f}%"></i></span></div>')

live = [r for r in ROWS if r.get("days")]
dead = [r for r in ROWS if not r.get("days")]
CATS = sorted({r["cat"] for r in ROWS})
CAT_IDX = {c: i for i, c in enumerate(CATS)}
QUAD_CLS = {"領先": "qlead", "改善": "qimp", "轉弱": "qweak", "落後": "qlag"}

def basket_cell(r):
    tks = "".join(f'<a href="{tv(t)}" target="_blank" rel="noopener" class="tk">{esc(t)}</a>'
                  for t in r["basket"])
    miss = [t for t in r["us"] if t not in r["basket"]]
    mtag = (f'<span class="miss" title="美股上市但鏡像數據不足，未計入">數據不足 {esc("、".join(miss))}</span>'
            if miss else "")
    non = r.get("nonus") or []
    ntag = (f'<span class="miss nu" title="非美股上市、亦無 US ADR，按指示排除：{esc("、".join(non))}">'
            f'排除非美股 {len(non)}</span>' if non else "")
    return f'<div class="bk">{tks}{mtag}{ntag}</div>'

def cover_cell(r):
    n, us, tot = r["n_basket"], len(r["us"]), len(r["members"])
    cls = "qlo" if n <= 1 else ("qmid" if n <= 2 else "qok")
    pct = n / tot * 100 if tot else 0
    return (f'<div class="qc"><b class="{cls}">{n}</b>'
            f'<span class="qt">美股 {us}／全球 {tot}</span>'
            f'<span class="qt">覆蓋 {pct:.0f}%</span></div>')

def trend_cell(r):
    s = r["slope"]
    lab = "加速流入" if s >= 0.35 else "轉流入" if s >= 0.12 else "加速流出" if s <= -0.35 else "轉流出" if s <= -0.12 else "持平"
    cls = "up" if s >= 0.12 else "dn" if s <= -0.12 else "fl"
    return (f'<div class="tr {cls}"><b>{s:+.2f}</b><span>{lab}</span>'
            f'<i>{r["pos"]}↑/{r["neg"]}↓</i></div>')

def quad_cell(r):
    q = r.get("quad") or "—"
    rs, rm = r.get("rs"), r.get("rsmom")
    sub = f'{rs:.1f} / {rm:.1f}' if rs is not None and rm is not None else "—"
    return f'<td class="qd {QUAD_CLS.get(q, "")}">{esc(q)}<span class="hl">RS {esc(sub)}</span></td>'

def dash_cell(r):
    bits = []
    for lab, key, suf in (("RSI", "rsi", ""), ("1週", "ret1w", "%"), ("1月", "ret1m", "%"), ("3月", "ret3m", "%")):
        v = r.get(key)
        if v is None: continue
        cls = "" if key == "rsi" else (" pos" if v > 0 else " neg")
        bits.append(f'<span class="dm"><i>{lab}</i><b class="{cls}">{v:+.1f}{suf}</b></span>'
                    if key != "rsi" else f'<span class="dm"><i>{lab}</i><b>{v:.1f}</b></span>')
    fr = r.get("flowRatio")
    if fr is not None:
        bits.append(f'<span class="dm"><i>資金比</i><b>{fr:.1f}</b></span>')
    return f'<div class="dash">{"".join(bits)}</div>'

def row_attrs(r):
    a = (f' data-z5="{r["z5"]:.4f}" data-score5="{r["score5"]:.2f}" data-mfd="{r["mfd5"]:.0f}"'
         f' data-rs="{r.get("rs") or 0}" data-slope="{r["slope"]:.4f}" data-ret5="{r["ret5"]*100:.3f}"'
         f' data-n="{r["n_basket"]}" data-rank="{r["rank"]}" data-r1m="{r.get("ret1m") or 0}"')
    for i, d in enumerate(DAYS, 1):
        a += f' data-d{i}="{r["days"][d]["score"]:.2f}"'
    return a

def table_main():
    head = ('<tr><th>#</th><th>AI 小群組 Sub-Group</th><th>大分類</th>'
            '<th class="srt" data-key="score5">5日資金流向<span class="thn">綜合分 0-100 ↓</span></th>'
            + "".join(f'<th class="srt d" data-key="d{i}">{dlab(d)}<span class="thn">日分 ↓</span></th>'
                      for i, d in enumerate(DAYS, 1))
            + '<th class="srt" data-key="mfd">淨額估算<span class="thn">5日合計 ↓</span></th>'
              '<th class="srt" data-key="ret5">籃子報酬<span class="thn">5日 % ↓</span></th>'
              '<th class="srt" data-key="slope">趨勢<span class="thn">日分斜率 ↓</span></th>'
              '<th class="srt" data-key="rs">儀表板象限<span class="thn">RS / RS動能 ↓</span></th>'
              '<th class="srt" data-key="r1m">儀表板指標<span class="thn">1月% ↓</span></th>'
              '<th class="srt" data-key="n">樣本<span class="thn">美股數 ↓</span></th>'
              '<th>成分股（美股／ADR）</th></tr>')
    body = []
    for r in live:
        body.append(
            f'<tr{row_attrs(r)} data-sym="s{r["n"]}"><td class="rk">{r["rank"]}</td>'
            f'<td><div class="ss"><b><span class="code">{esc(r["code"])}</span>{esc(r["zh"])}</b>'
            f'<em>{esc(r["tier"])}型 · 全球成分 {len(r["members"])} 隻</em></div></td>'
            f'<td class="sec"><span class="sdot s{CAT_IDX[r["cat"]]%11}"></span>{esc(r["cat"])}</td>'
            f'<td>{meter(r["score5"], "m5")}</td>'
            + "".join(f'<td class="dcell {gcls(r["days"][d]["grade"])}" title="z {r["days"][d]["z"]:+.2f} · '
                      f'籃子報酬 {r["days"][d]["ret"]*100:+.2f}% · 量能 {r["days"][d]["rvol"]:.2f}x">'
                      f'{r["days"][d]["score"]:.0f}<span class="gz">{GRADE_ZH[r["days"][d]["grade"]]}</span></td>'
                      for d in DAYS)
            + f'<td class="nums mf {"pos" if r["mfd5"] > 0 else "neg"}">{fmt_m(r["mfd5"])}</td>'
              f'<td class="nums {"pos" if r["ret5"] > 0 else "neg"}">{r["ret5"]*100:+.2f}%</td>'
              f'<td>{trend_cell(r)}</td>'
            + quad_cell(r)
            + f'<td>{dash_cell(r)}</td><td>{cover_cell(r)}</td><td>{basket_cell(r)}</td></tr>')
    return head, "".join(body)

def table_matrix():
    head = ('<tr><th>#</th><th>AI 小群組</th><th>大分類</th>'
            + "".join(f'<th class="srt d" data-key="d{i}">{dlab(d)}<span class="thn">日分 ↓</span></th>'
                      for i, d in enumerate(DAYS, 1))
            + '<th class="srt" data-key="score5">5日綜合<span class="thn">0-100 ↓</span></th>'
              '<th>逐日走勢</th>'
              '<th class="srt" data-key="mfd">淨額估算<span class="thn">5日 ↓</span></th></tr>')
    body = []
    for r in live:
        spark = ""
        for d in DAYS:
            x = r["days"][d]
            h = max(4, min(38, abs(x["z"]) * 16))
            spark += (f'<span class="bar {"bp" if x["z"] >= 0 else "bn"}" style="height:{h:.0f}px" '
                      f'title="{esc(d)} z {x["z"]:+.2f}"></span>')
        body.append(
            f'<tr{row_attrs(r)} data-sym="m{r["n"]}"><td class="rk">{r["rank"]}</td>'
            f'<td><div class="ss"><b><span class="code">{esc(r["code"])}</span>{esc(r["zh"])}</b></div></td>'
            f'<td class="sec">{esc(r["cat"])}</td>'
            + "".join(f'<td class="dcell big {gcls(r["days"][d]["grade"])}">{r["days"][d]["score"]:.0f}'
                      f'<span class="gz">{r["days"][d]["z"]:+.1f}</span></td>' for d in DAYS)
            + f'<td>{meter(r["score5"], "m5")}</td>'
              f'<td class="spk"><div class="spark">{spark}</div></td>'
              f'<td class="nums mf {"pos" if r["mfd5"] > 0 else "neg"}">{fmt_m(r["mfd5"])}</td></tr>')
    return head, "".join(body)

def cat_agg():
    by = collections.defaultdict(list)
    for r in live: by[r["cat"]].append(r)
    out = []
    for cat, rs in by.items():
        dv = sum(r["dv5"] for r in rs) or 1
        z5 = sum(r["z5"] * r["dv5"] for r in rs) / dv
        dayz = {d: sum(r["days"][d]["z"] * r["days"][d]["dv"] for r in rs) /
                   (sum(r["days"][d]["dv"] for r in rs) or 1) for d in DAYS}
        out.append({"cat": cat, "n": len(rs), "z5": z5, "mfd": sum(r["mfd5"] for r in rs),
                    "dayz": dayz, "dv5": dv, "dead": sum(1 for x in dead if x["cat"] == cat),
                    "top": sorted(rs, key=lambda r: -r["z5"])[:3],
                    "bot": sorted(rs, key=lambda r: r["z5"])[:3],
                    "npos": sum(1 for r in rs if r["z5"] >= 0.25),
                    "nneg": sum(1 for r in rs if r["z5"] <= -0.25)})
    out.sort(key=lambda x: -x["z5"])
    return out

def zc(z):
    g = 3 if z >= 1.0 else 2 if z >= 0.5 else 1 if z >= 0.2 else 0 if z > -0.2 else -1 if z > -0.5 else -2 if z > -1.0 else -3
    return f'<td class="dcell {gcls(g)}">{z:+.2f}</td>'

def table_cat():
    agg = cat_agg()
    head = ('<tr><th>#</th><th>大分類 Category</th><th>可計算<span class="thn">／未能計算</span></th>'
            '<th>5日資金流向<span class="thn">成交額加權 z</span></th>'
            + "".join(f'<th class="d">{dlab(d)}</th>' for d in DAYS)
            + '<th>淨額估算<span class="thn">5日合計</span></th><th>5日成交額</th>'
              '<th>流入/流出群組</th><th>最強小群組</th><th>最弱小群組</th></tr>')
    body = []
    for i, a in enumerate(agg, 1):
        body.append(
            f'<tr><td class="rk">{i}</td><td><div class="ss"><b>{esc(a["cat"])}</b></div></td>'
            f'<td class="nums">{a["n"]}<span class="mut"> / {a["dead"]}</span></td>{zc(a["z5"])}'
            + "".join(zc(a["dayz"][d]) for d in DAYS)
            + f'<td class="nums mf {"pos" if a["mfd"] > 0 else "neg"}">{fmt_m(a["mfd"])}</td>'
              f'<td class="nums mut">${a["dv5"]/1e9:,.0f}B</td>'
              f'<td class="nums"><span class="pos">{a["npos"]}↑</span> / <span class="neg">{a["nneg"]}↓</span></td>'
              f'<td class="lst">' + "".join(f'<span class="pill pos">{esc(x["code"])} {x["z5"]:+.2f}</span>' for x in a["top"]) + '</td>'
              f'<td class="lst">' + "".join(f'<span class="pill neg">{esc(x["code"])} {x["z5"]:+.2f}</span>' for x in a["bot"]) + '</td></tr>')
    return head, "".join(body)

def quadrants():
    q = {"lead_out": [], "lag_in": [], "lead_in": [], "lag_out": []}
    for r in live:
        qd = r.get("quad")
        strong = qd in ("領先", "改善")
        weak = qd in ("落後", "轉弱")
        if strong and r["z5"] <= -0.25: q["lead_out"].append(r)
        elif weak and r["z5"] >= 0.25: q["lag_in"].append(r)
        elif strong and r["z5"] >= 0.25: q["lead_in"].append(r)
        elif weak and r["z5"] <= -0.25: q["lag_out"].append(r)
    for k in q: q[k].sort(key=lambda r: -abs(r["z5"]))
    return q

def qbox(title, sub, rows, cls):
    if not rows:
        return f'<div class="qbox {cls}"><h3>{esc(title)}<span>{esc(sub)}</span></h3><p class="none">本次無</p></div>'
    items = "".join(
        f'<div class="qrow"><b><span class="code">{esc(r["code"])}</span>{esc(r["zh"][:16])}</b>'
        f'<span class="qz">{r["z5"]:+.2f}</span>'
        f'<span class="qh">{esc(r.get("quad") or "—")}</span>'
        f'<span class="qm {"pos" if r["mfd5"] > 0 else "neg"}">{fmt_m(r["mfd5"])}</span>'
        f'<i>{esc(r["cat"])}</i></div>' for r in rows[:14])
    return (f'<div class="qbox {cls}"><h3>{esc(title)} <b class="cnt">{len(rows)}</b><span>{esc(sub)}</span></h3>'
            f'{items}</div>')

def dead_card():
    if not dead: return ""
    items = "".join(
        f'<span class="dli"><b>{esc(r["code"])}</b> {esc(r["zh"][:28])} · 全球成分 {len(r["members"])} 隻'
        f'（美股 {len(r["us"])}）· {esc(r["note"])}'
        f'<span class="nu">{esc("、".join((r.get("nonus") or [])[:8]))}{"…" if len(r.get("nonus") or []) > 8 else ""}</span></span>'
        for r in sorted(dead, key=lambda x: x["code"]))
    return (f'<div class="dcard"><span class="dlab">⚠ 未能計算資金流向 <b>{len(dead)}</b> 個小群組</span>'
            f'<span class="dnote">按指示只納入美股上市股票及 US ADR；以下小群組嘅成分股全部喺中國A股／台股／日韓／歐洲掛牌，'
            f'本環境無該等市場嘅價量數據，故列出但唔參與排名</span>{items}</div>')

top5 = live[:5]; bot5 = live[-5:][::-1]
acc = sorted(live, key=lambda r: -r["slope"])[:5]
dec = sorted(live, key=lambda r: r["slope"])[:5]
last = DAYS[-1]
today_top = sorted(live, key=lambda r: -r["days"][last]["z"])[:5]
today_bot = sorted(live, key=lambda r: r["days"][last]["z"])[:5]
mkt = M["mkt_med"]
n_us = sum(len(r["us"]) for r in ROWS); n_glob = sum(len(r["members"]) for r in ROWS)

COLW_MAIN = [40, 210, 118, 96] + [74] * len(DAYS) + [84, 74, 88, 94, 190, 96, 210]
COLW_MTX = [40, 230, 118] + [88] * len(DAYS) + [96, 92, 92]
COLW_CAT = [40, 150, 76, 92] + [72] * len(DAYS) + [92, 88, 92, 220, 220]

def colgroup(ws):
    return "<colgroup>" + "".join(f'<col style="width:{w}px">' for w in ws) + "</colgroup>", sum(ws)

EXTRA_CSS = """
.ss .code{display:inline-block;font-size:10px;font-weight:700;color:var(--seq);border:1px solid var(--ring);
 border-radius:6px;padding:0 5px;margin-right:6px;vertical-align:1px;background:var(--hl)}
.qd{text-align:left;font-size:12px;font-weight:700}
.qd .hl{display:block;font-weight:400;font-size:9.5px;color:var(--mut)}
.qd.qlead{color:var(--pt)}.qd.qimp{color:var(--seq)}.qd.qweak{color:var(--warn)}.qd.qlag{color:var(--nt)}
.dash{display:flex;flex-wrap:wrap;gap:3px 6px}
.dm{font-size:10.5px;white-space:nowrap}
.dm i{font-style:normal;color:var(--mut);margin-right:3px}
.dm b{font-variant-numeric:tabular-nums}
.miss.nu{color:var(--nt);border-color:var(--negbd)}
.qrow b .code{font-size:9.5px;margin-right:4px}
.dcard{display:flex;flex-wrap:wrap;gap:5px 6px;align-items:center;border-radius:10px;padding:10px 12px;
 margin-bottom:12px;background:var(--n1);border:1px solid var(--negbd)}
.dlab{font-size:12px;font-weight:700;color:var(--nt);margin-right:4px}
.dlab b{color:var(--ink)}
.dnote{width:100%;font-size:11px;color:var(--ink2)}
.dli{display:block;width:100%;font-size:11px;color:var(--ink2);background:var(--sf);border:1px solid var(--ring);
 border-radius:8px;padding:3px 8px;line-height:1.5}
.dli b{color:var(--ink);margin-right:5px}
.dli .nu{display:block;font-size:9.5px;color:var(--mut)}
.qbox.leadout{border-color:var(--negbd)}.qbox.lagin{border-color:var(--posbd)}
"""

rules = f"""
<div class="card rules">
<h2>打分方法（AI 小群組 · 資金流向 · 每日）</h2>
① <b>分類來源</b>：直接採用附件 <b>Dashboard R15.6</b>（2026-08-27 收盤版）嘅 <b>41 個 AI 小群組</b>分類、
大分類（A.運算核心／AA.AI Neo Cloud／B.製造／C.記憶體儲存／D.互連／E.系統整合／F.基礎設施／G.雲端應用）、
成分股名單、RS 象限與 RSI／1週／1月／3月報酬。本表唔改分類，只新增資金流向計分。<br>
② <b>只納入美股上市股票及 US ADR</b>（按指示）：全球成分股共 {n_glob} 隻，其中美股／ADR {n_us} 隻。
儀表板本身已用 ADR 代號表示有 ADR 嘅外國公司（如台積電＝TSM、ASML＝Nasdaq ADR），
其餘帶交易所後綴（.SS／.SZ／.TW／.T／.KS／.DE 等）嘅中國A股、台股、日韓及歐洲掛牌股票<b>一律排除</b>，
唔以其他股票代替。因此有 <b>{len(dead)} 個小群組</b>（成分股全部非美股）無法計算，另列於下方紅框。<br>
③ <b>逐日資金流向分</b>（每隻股票、每個交易日，與 Sub-Sector Watchlist R1.01 完全相同）：<br>
　<code>A 方向 = tanh((個股報酬 − 當日全巿場中位報酬) / 2%)</code>；
<code>B 量能 = log₂(當日成交額 / 前20日中位成交額) ÷ 2</code>，截於 ±1；
<code>C 收位 = ((收−低)−(高−收))/(高−低)</code>（Chaikin 資金流乘數）；<br>
　<code>f = (0.70×A + 0.30×C) × (1 + 0.50×B)</code> —— 放量上升＝真流入，放量下跌＝真流出，縮量打折。
無日內高低價嘅股票只用 A 項。<br>
④ <b>小群組分</b>：籃子內以<b>成交額加權</b>（單一股票上限 40%）。<b>0–100 分</b>＝每日將
{len(live)} 個可計算小群組<b>橫向標準化</b>後取百分位，係「今日資金相對流向邊個 AI 環節」，唔係「升定跌」。
等級：z≥1.5 強力流入 · ≥0.75 流入 · ≥0.25 偏流入 · ±0.25 中性 · ≤−0.25 偏流出 · ≤−0.75 流出 · ≤−1.5 強力流出。<br>
⑤ <b>5 日綜合分</b>：五日 z 值按 <code>{esc(" / ".join(f"{w:g}" for w in M["weights"]))}</code> 加權（近日較重）後取百分位；
<b>趨勢</b>＝五日 z 斜率；<b>↑/↓</b>＝五日內流入／流出日數。<br>
⑥ <b>淨額估算</b>＝Σ(Chaikin 乘數 × 成交額)。<span class="cav">⚠ 呢個係價量推算嘅<b>代理指標</b>，
唔係真實基金流數據，亦只計算籃子內嘅美股成分股，唔等於該 AI 環節嘅全球實際資金額。</span><br>
⑦ <b>儀表板象限</b>（領先／改善／轉弱／落後）同 RS、RS動能係<b>儀表板 8/27 收盤</b>嘅數值，
本表資金流向係 <b>8/26 → 9/1</b>，兩者時點唔同，正好用嚟睇背離 —— 見第 4 頁。
</div>"""

mkt_chips = "".join(f'<span>{dlab(d)} 全巿中位 <b class="{"pos" if mkt[d] > 0 else "neg"}">{mkt[d]*100:+.2f}%</b></span>' for d in DAYS)
summary = f"""
<div class="card">
<h2>五日資金流向摘要（{DAYS[0]} → {DAYS[-1]}）</h2>
<div class="sumgrid">
<div class="sumbox"><h3>5 日最強流入</h3>{"".join(f'<div class="li"><b>{esc(r["code"])} {esc(r["zh"][:14])}</b><span class="pos">{r["z5"]:+.2f}</span><span class="mut">{fmt_m(r["mfd5"])}</span></div>' for r in top5)}</div>
<div class="sumbox"><h3>5 日最強流出</h3>{"".join(f'<div class="li"><b>{esc(r["code"])} {esc(r["zh"][:14])}</b><span class="neg">{r["z5"]:+.2f}</span><span class="mut">{fmt_m(r["mfd5"])}</span></div>' for r in bot5)}</div>
<div class="sumbox"><h3>最後一日（{DAYS[-1]}）流入</h3>{"".join(f'<div class="li"><b>{esc(r["code"])} {esc(r["zh"][:14])}</b><span class="pos">{r["days"][last]["z"]:+.2f}</span><span class="mut">分 {r["days"][last]["score"]:.0f}</span></div>' for r in today_top)}</div>
<div class="sumbox"><h3>最後一日（{DAYS[-1]}）流出</h3>{"".join(f'<div class="li"><b>{esc(r["code"])} {esc(r["zh"][:14])}</b><span class="neg">{r["days"][last]["z"]:+.2f}</span><span class="mut">分 {r["days"][last]["score"]:.0f}</span></div>' for r in today_bot)}</div>
<div class="sumbox"><h3>資金加速流入（斜率）</h3>{"".join(f'<div class="li"><b>{esc(r["code"])} {esc(r["zh"][:14])}</b><span class="pos">{r["slope"]:+.2f}</span><span class="mut">5日分 {r["score5"]:.0f}</span></div>' for r in acc)}</div>
<div class="sumbox"><h3>資金加速流出（斜率）</h3>{"".join(f'<div class="li"><b>{esc(r["code"])} {esc(r["zh"][:14])}</b><span class="neg">{r["slope"]:+.2f}</span><span class="mut">5日分 {r["score5"]:.0f}</span></div>' for r in dec)}</div>
</div>
<div class="mkrow">{mkt_chips}</div>
</div>"""

secs = []
head, body = table_main(); cg, tw = colgroup(COLW_MAIN)
secs.append(f'''<section id="p1">
<div class="pghead"><b>總覽 · {len(live)} 個可計算 AI 小群組 × 5 個交易日</b>
<span class="tg">{DAYS[0]} → {DAYS[-1]}</span><span>排序 = 5 日資金流向綜合分</span>
<span class="tg">分類取自 Dashboard R15.6（41 組）</span></div>
{summary}{dead_card()}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw gp3"></i>強力流入 z≥1.5</span><span><i class="sw gp2"></i>流入 ≥0.75</span>
<span><i class="sw gp1"></i>偏流入 ≥0.25</span><span><i class="sw g00"></i>中性</span>
<span><i class="sw gn1"></i>偏流出</span><span><i class="sw gn2"></i>流出</span><span><i class="sw gn3"></i>強力流出</span>
<span>格內數字＝當日 0–100 分（橫向百分位）· 滑鼠停留睇 z 值／籃子報酬／量能倍數</span></div>
</section>''')

head, body = table_matrix(); cg, tw = colgroup(COLW_MTX)
secs.append(f'''<section id="p2" hidden>
<div class="pghead"><b>每日矩陣 · AI 資金流向熱力圖</b><span>{len(live)} × 5 逐日分數與 z 值</span>
<span class="tg">柱狀圖＝逐日 z 值（上綠下紅）</span></div>
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
</section>''')

head, body = table_cat(); cg, tw = colgroup(COLW_CAT)
secs.append(f'''<section id="p3" hidden>
<div class="pghead"><b>AI 產業鏈 8 大分類匯總</b><span>小群組以成交額加權合成</span>
<span class="tg">排序 = 5 日加權 z</span></div>
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
</section>''')

q = quadrants()
secs.append(f'''<section id="p4" hidden>
<div class="pghead"><b>象限背離</b><span>儀表板 RS 象限（8/27）vs 本次實測資金流向（8/26–9/1）</span></div>
<div class="qgrid">
{qbox("RS 領先/改善 但資金流出", "儀表板強、5 日 z ≤ −0.25：漲勢缺資金追捧，留意派發", q["lead_out"], "leadout")}
{qbox("RS 落後/轉弱 但資金流入", "儀表板弱、5 日 z ≥ +0.25：資金先行，早期輪動候選", q["lag_in"], "lagin")}
{qbox("RS 領先/改善 且資金流入", "儀表板強且 z ≥ +0.25：趨勢與資金一致", q["lead_in"], "")}
{qbox("RS 落後/轉弱 且資金流出", "儀表板弱且 z ≤ −0.25：持續失血", q["lag_out"], "")}
</div>
</section>''')

foot = f"""
<div class="card foot">
<h2>數據來源與限制</h2>
① <b>AI 小群組分類</b>：附件 <b>Dashboard_R15.6_0828_hk16.15.html</b>（2026-08-27 收盤 · built 2026-08-28 16:15 HKT）
嘅 A9.2 AI 小群組表：41 個小群組、8 個大分類、全球成分股 {n_glob} 隻（儀表板自報覆蓋 {esc(M.get("coverage_dash", "—"))}），
連同 RS 象限、RSI 及 1週／1月／3月報酬。RS 象限與報酬為<b>儀表板 8/27 數值</b>，非本表重算。<br>
② <b>價量數據</b>：natezone/market-tracker 真實日線 OHLCV 為主（有日內高低價，可算 Chaikin 收位），
其餘以 Nasdaq 快照重建序列補足（只有收盤與成交量）。計分視窗 <b>{DAYS[0]} → {DAYS[-1]}</b> 共 5 個交易日，
量能基準 {M["base"][0]} → {M["base"][1]}。實際計分 {M["n_tick"]} 隻美股。<br>
③ <b>只計美股／ADR</b>：按指示排除所有非美股掛牌成分股（中國A股 .SS/.SH/.SZ、台股 .TW、日股 .T、韓股 .KS、
歐股 .DE/.AS/.VI），亦無以其他股票代替；被排除嘅代號喺各行「排除非美股」標示，
成分股全屬非美股嘅 {len(dead)} 個小群組列於總覽頂部紅框、唔參與排名。少數美股成分股（如 TSM、ASML、BABA 等）
因鏡像歷史不足 5+20 個交易日亦未能計入，於各行「數據不足」標示。<br>
④ <b>數據終點</b>：9/2 收盤後日線鏡像只推送成交量、未有收盤價，Nasdaq 快照最新一筆為盤前（載 9/1 收盤），
故本表以 <b>2026-09-01 收盤</b>為最後一日，與 Sub-Sector Watchlist R1.01 同一視窗。
08-26 及 08-31 快照缺當日資料，非日線鏡像覆蓋嘅股票以官方收盤或內插補回、成交量取前後平均。<br>
⑤ <b>本表唔係真實基金流</b>：環境內無法取得 ETF 申購贖回、13F 或委託簿數據，「資金流向」全部由價格、成交量
與收盤位置推算，屬市場微觀結構代理指標。<br>
⑥ <b>建置時間 {BUILD_TS}</b> · 點擊成分股開 TradingView chart · 版面可切淺色／深色（預設「自動」）·
計分方法與 Sub-Sector Watchlist R1.01 完全一致 · 本表只係研究工具，唔係投資建議。
</div>"""

html_doc = f"""<title>AI Sector 資金流向 Watchlist</title>
<style>{CSS}{EXTRA_CSS}</style>
<div class="wrap">
<h1>AI Sector 資金流向 Watchlist R1.00（41 個 AI 小群組 × 5 個交易日逐日打分）</h1>
<div class="sub">分類取自 <b>Dashboard R15.6</b>（8/27 收盤）· 資金流向資料至 <b>{DAYS[-1]}</b>
（美東星期{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤 · 只計美股上市及 US ADR
（{n_us}/{n_glob} 隻，實際計分 {M["n_tick"]} 隻）· {len(live)} 組可計算、{len(dead)} 組成分全非美股 ·
<b>淺色／深色版面可切換</b></div>
{rules}
<nav class="nav">
<div class="nrow">
<button data-g="1" class="on">總覽<span class="s">{len(live)} 個小群組主表</span></button>
<button data-g="2">每日矩陣<span class="s">{len(live)} × 5 熱力圖</span></button>
<button data-g="3">分類匯總<span class="s">AI 產業鏈 8 大分類</span></button>
<button data-g="4">象限背離<span class="s">RS vs 資金</span></button>
<span class="div"></span>
<span class="lab">排序</span>
<button class="sortb on" data-sort="">5日綜合</button>
<button class="sortb" data-sort="d{len(DAYS)}">最後一日</button>
<button class="sortb" data-sort="mfd">淨額估算</button>
<button class="sortb" data-sort="slope">趨勢</button>
<button class="sortb" data-sort="ret5">籃子報酬</button>
<button class="sortb" data-sort="rs">儀表板RS</button>
<span class="div"></span>
<span class="lab">版面</span>
<div class="seg" id="thm" role="group" aria-label="淺色／深色版面">
<button data-t="auto" title="跟隨系統或檢視器設定">自動</button>
<button data-t="light" title="淺色版面">☀ 淺色</button>
<button data-t="dark" title="深色版面">🌙 深色</button></div></div>
</nav>
{"".join(secs)}
{foot}
</div>
<script>
{JS}
</script>
"""

standalone = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1">'
              + html_doc.split("</title>", 1)[0] + "</title></head><body>"
              + html_doc.split("</title>", 1)[1] + "</body></html>")
out_path = f"{SCRATCH}/{OUTNAME}"
open(out_path, "w", encoding="utf-8").write(standalone)
open(f"{SCRATCH}/ai/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)
print("wrote", out_path, f"{len(standalone)/1024:.0f} KB | scored {len(live)} | unscorable {len(dead)} | days {DAYS}")
