#!/usr/bin/env python3
"""Build the R4 5-page HTML report: split VCP/certainty columns, 7 sortable
certainty columns, split & condensed reason columns with hype highlights,
sort buttons in the top bar, draggable column widths."""
import json, datetime, html, os, sys

SCRATCH = os.environ.get("WORK_DIR", "./data")
O = json.load(open(f"{SCRATCH}/screen_results3.json"))
NEWS = json.load(open(f"{SCRATCH}/news.json"))
SHORT = json.load(open(f"{SCRATCH}/news_short.json")) if os.path.exists(f"{SCRATCH}/news_short.json") else {}
MKT = json.load(open(f"{SCRATCH}/market.json")) if os.path.exists(f"{SCRATCH}/market.json") else None
M = O["meta"]

now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
OUTNAME = f"20MA_uptrend_watchlistGit_R4.00_claudefable5xhigh_{STAMP}.html"

PAGE_DEFS = [
    ("1", "PAGE 1 · 總覽", "爆發潛力排名"),
    ("2", "PAGE 2 · 1星期", "10MA · 5個交易日"),
    ("3", "PAGE 3 · 2星期", "20MA · 10個交易日"),
    ("4", "PAGE 4 · 1個月", "20MA · 21個交易日"),
    ("5", "PAGE 5 · 2個月", "20MA · 42個交易日"),
]

def esc(s): return html.escape(str(s), quote=True)

def spark_svg(sp, L):
    cs = sp["closes"]; ma = sp["ma"]; bots = dict(sp["bots"])
    W, H, P = 150, 40, 3
    lo = min(cs); hi = max(cs)
    vals = [v for v in ma if v is not None]
    if vals: lo = min(lo, min(vals)); hi = max(hi, max(vals))
    rng = (hi - lo) or 1.0
    def xy(i, v):
        x = P + i * (W - 2 * P) / (len(cs) - 1)
        y = H - P - (v - lo) * (H - 2 * P) / rng
        return f"{x:.1f},{y:.1f}"
    pl_c = " ".join(xy(i, v) for i, v in enumerate(cs))
    seg, segs = [], []
    for i, v in enumerate(ma):
        if v is None:
            if seg: segs.append(seg); seg = []
        else:
            seg.append(xy(i, v))
    if seg: segs.append(seg)
    ma_polys = "".join(f'<polyline points="{" ".join(s)}" fill="none" stroke="var(--seq)" stroke-width="1.3" opacity=".9"/>' for s in segs if len(s) > 1)
    dots = ""
    for i, v in bots.items():
        x, y = xy(i, v).split(",")
        dots += f'<circle cx="{x}" cy="{y}" r="2.4" fill="var(--good)"/>'
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-label="60日走勢">'
            f'<polyline points="{pl_c}" fill="none" stroke="var(--ink2)" stroke-width="1"/>'
            f'{ma_polys}{dots}</svg>')

def meter_cell(v, cls=""):
    return (f'<div class="mc {cls}"><b class="nums">{v:.1f}</b>'
            f'<span class="meter"><i style="width:{max(0, min(100, v)):.0f}%"></i></span></div>')

def cert_cols_cells(r):
    c = r["cert_c"]; s = c["s"]
    brk = '<td class="cv ok">✓突破</td>' if c["broke"] else f'<td class="cv no">{max(0, min(99, c["retrace_pct"])):.0f}%</td>'
    retr = c["retrace_pct"]
    retr_s = "100%+" if retr >= 100 else f"{max(0.0, retr):.0f}%"
    held = f'<td class="cv{" wr" if c["undercut"] else ""}">{c["d_held"]}日{"⚠" if c["undercut"] else ""}</td>'
    maf = sum(c["ma_flags"])
    return (brk
            + f'<td class="cv">{retr_s}</td>'
            + held
            + f'<td class="cv{" ok" if c["dv_ratio"] < 0.85 else ""}">{c["dv_ratio"]:.2f}</td>'
            + f'<td class="cv{" ok" if c["contr"] < 0.6 else ""}">{c["contr"]:.2f}</td>'
            + f'<td class="cv{" ok" if c["rs21_pct"] > 0 else ""}">{c["rs21_pct"]:+.1f}%</td>'
            + f'<td class="cv{" ok" if maf == 3 else ""}">{maf}/3</td>')

CERT_KEYS = [("bbreak", "break"), ("bretr", "retr"), ("btime", "time"),
             ("bdv", "dv"), ("bcontr", "contr"), ("brs", "rs"), ("bma", "ma")]

def row_data_attrs(r, rank, p1=False):
    s = r["cert_c"]["s"]
    a = f' data-rank="{rank}" data-vcp="{r["vcp"]}" data-cert="{r["cert"]}"'
    if p1: a += f' data-score="{r["score"]}"'
    for dk, sk in CERT_KEYS:
        a += f' data-{dk}="{s[sk]}"'
    return a

def news_cells(sym):
    e = NEWS.get(sym) or {}
    sh = SHORT.get(sym) or {}
    dn = sh.get("decline_short") or e.get("decline_zh", "—")
    up = sh.get("recovery_short") or e.get("recovery_zh", "—")
    conf = e.get("confidence", "低")
    hype = sh.get("hype") and sh.get("hype_zh")
    hypeb = f'<span class="hype">🔥 {esc(sh["hype_zh"])}</span>' if hype else ""
    upcls = " hypebg" if hype else ""
    return (f'<td class="whyc"><div class="why">{esc(dn)}</div></td>'
            f'<td class="whyc{upcls}"><div class="why">{hypeb}{esc(up)}'
            f'<span class="conf c{conf}">信心{esc(conf)}</span></div></td>')

def sector_cell(r):
    zh = r["sector_zh"]; en = r["sector"]
    sub = r["gsub"] if (r["sp500"] and r.get("gsub")) else r["industry"]
    gtag = f'<i class="gics">GICS·{esc(r["gsec"])}</i>' if (r["sp500"] and r.get("gsec")) else ""
    return f'<div class="sect"><b>{esc(zh)}</b> <span>{esc(en)}</span>{gtag}<em>{esc(sub)}</em></div>'

def tv_url(r):
    sym = r["sym"].replace("/", ".").lower()
    if r["exch"] != "—":
        return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={r["exch"].lower()}%3A{esc(sym)}'
    return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={esc(sym)}'

def tick_cell(r, L=None):
    sp = '<span class="badge">S&amp;P500</span>' if r["sp500"] else ""
    warn = ' <span class="warn">⚠低於MA</span>' if r["below_ma"] else ""
    ml = f'MA{L}' if L else "MA"
    return (f'<div class="tk"><a href="{tv_url(r)}" target="_blank" rel="noopener">{esc(r["sym"])}</a>'
            f'<span class="ex">{esc(r["exch"])}</span>{sp}<em>{esc(r["name"][:34])}</em>'
            f'<span class="pxl nums">{r["close"]:g} <span class="mut">/ {ml} {r["ma"]:g}</span>{warn}</span></div>')

def spark_cell(r):
    return (f'{spark_svg(r["spark"], r["L"])}'
            f'<div class="subsc nums slope">MA{r["L"]} {r["slope"]:+.2f}% <span class="mut">/{r["W"]}日</span></div>')

def bottoms_chain(hl):
    parts = []
    shown = hl[-4:]
    for d, p in shown:
        parts.append(f'<span class="bot">{d[5:]}<i>@{p:g}</i></span>')
    chain = '<span class="arr">→</span>'.join(parts)
    pre = '<span class="arr">…→</span>' if len(hl) > 4 else ""
    return f'<div class="botwrap">{pre}{chain}</div>'

def sector_chips(rows):
    cnt = {}
    for r in rows:
        k = (r["sector_zh"], r["sector"])
        cnt[k] = cnt.get(k, 0) + 1
    chips = "".join(f'<span class="chip"><b>{esc(z)}</b> {esc(e)} <i>{n}</i></span>'
                    for (z, e), n in sorted(cnt.items(), key=lambda x: -x[1]))
    return f'<div class="chips">{chips}</div>'

CERT_HEADS = [
    ("bbreak", "突破", "中間高位"), ("bretr", "回補", "跌幅收復"), ("btime", "守底", "未破日數"),
    ("bdv", "量縮", "跌/升量比"), ("bcontr", "遞減", "末/首跌幅"), ("brs", "RS", "21日相對"), ("bma", "均線", "結構"),
]

def cert_ths():
    return "".join(f'<th class="srt" data-key="{k}">{t}<span class="thn">{n} ↓</span></th>'
                   for k, t, n in CERT_HEADS)

COLW_P = [36, 190, 86, 86, 74, 66, 66, 66, 66, 74, 58, 168, 185, 205, 235, 150]
COLW_1 = [36, 190, 96, 86, 86, 118, 74, 66, 66, 66, 66, 74, 58, 168, 205, 235, 150]

def colgroup(ws):
    return "<colgroup>" + "".join(f'<col style="width:{w}px">' for w in ws) + "</colgroup>", sum(ws)

def table_page(p):
    pg = O["pages"][p]
    L = pg["L"]
    head = (f'<tr><th>#</th><th>Ticker · 現價/MA{L}</th>'
            f'<th class="srt" data-key="vcp">VCP指數<span class="thn">收縮度 ↓</span></th>'
            f'<th class="srt" data-key="cert">確定性<span class="thn">7項合成 ↓</span></th>'
            f'{cert_ths()}'
            f'<th>60日走勢 · 斜率</th>'
            f'<th>底部序列<span class="thn">45日內遞升</span></th>'
            f'<th>下跌原因</th><th>回升原因<span class="thn">🔥=市場熱炒</span></th><th>類別</th></tr>')
    rows = []
    for i, r in enumerate(pg["rows"], 1):
        rows.append(
            f'<tr{row_data_attrs(r, i)}><td class="rk">{i}</td><td>{tick_cell(r, L)}</td>'
            f'<td>{meter_cell(r["vcp"])}</td>'
            f'<td>{meter_cell(r["cert"], "certm")}</td>'
            f'{cert_cols_cells(r)}'
            f'<td>{spark_cell(r)}</td>'
            f'<td class="bots">{bottoms_chain(r["hl"])}</td>'
            f'{news_cells(r["sym"])}'
            f'<td>{sector_cell(r)}</td></tr>')
    cg, tw = colgroup(COLW_P)
    return head, "".join(rows), pg, cg, tw

def table_page1():
    labels = {"2": "1週", "3": "2週", "4": "1月", "5": "2月"}
    head = ('<tr><th>#</th><th>Ticker · 現價/MA</th>'
            '<th class="srt" data-key="score">爆發潛力<span class="thn">0.4V+0.4確+0.2覆 ↓</span></th>'
            '<th class="srt" data-key="vcp">VCP指數<span class="thn">收縮度 ↓</span></th>'
            '<th class="srt" data-key="cert">確定性<span class="thn">7項合成 ↓</span></th>'
            '<th>達標時間框<span class="thn">頁內排名</span></th>'
            f'{cert_ths()}'
            '<th>60日走勢 · 斜率</th>'
            '<th>下跌原因</th><th>回升原因<span class="thn">🔥=市場熱炒</span></th><th>類別</th></tr>')
    rows = []
    for i, r in enumerate(O["page1"], 1):
        frames = []
        for p in ("2", "3", "4", "5"):
            if p in r["ranks"]:
                frames.append(f'<span class="fr on">{labels[p]}<i>#{r["ranks"][p]}</i></span>')
            else:
                frames.append(f'<span class="fr">{labels[p]}</span>')
        rows.append(
            f'<tr{row_data_attrs(r, i, p1=True)}><td class="rk">{i}</td><td>{tick_cell(r, r["L"])}</td>'
            f'<td>{meter_cell(r["score"], "scorem")}</td>'
            f'<td>{meter_cell(r["vcp"])}</td>'
            f'<td>{meter_cell(r["cert"], "certm")}</td>'
            f'<td class="frs">{"".join(frames)}</td>'
            f'{cert_cols_cells(r)}'
            f'<td>{spark_cell(r)}</td>'
            f'{news_cells(r["sym"])}'
            f'<td>{sector_cell(r)}</td></tr>')
    cg, tw = colgroup(COLW_1)
    return head, "".join(rows), cg, tw

c = M["counts"]
UNIVERSE_LINE = (f'Universe：全美上市普通股掃描 — 快照涵蓋 {c["total"]:,} 隻 · 存續至 08-28 有報價 {c["current"]:,} 隻 · '
                 f'歷史 ≥90 交易日 {c["hist"]:,} 隻 · 價格 ≥$2 {c["price"]:,} 隻 · 流動性達標（20日中位成交額 ≥$1M）{c["liq"]:,} 隻合資格')

css = """
:root{color-scheme:light;--pg:#f9f9f7;--sf:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mut:#898781;
 --grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--seq:#2a78d6;--link:#1c5cab;--good:#006300;
 --warn:#8a5a00;--bad:#9c2121;--hl:#eef3fa;--meter:#dfe7f2;--okbg:#eaf3ea;--nobg:#f3ecec;
 --hype:#8a4b00;--hypebg:#fdf3e3;--hypebd:#e8b04a}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;
 --pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;--grid:#2c2c2a;--axis:#383835;
 --ring:rgba(255,255,255,.10);--seq:#3987e5;--link:#6da7ec;--good:#0ca30c;--warn:#d99a2b;--bad:#e06c6c;
 --hl:#16202d;--meter:#25303e;--okbg:#15230f;--nobg:#2a1c1c;
 --hype:#f0b45a;--hypebg:#2a2010;--hypebd:#8a6a2a}}
:root[data-theme="dark"]{color-scheme:dark;--pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;
 --mut:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--seq:#3987e5;
 --link:#6da7ec;--good:#0ca30c;--warn:#d99a2b;--bad:#e06c6c;--hl:#16202d;--meter:#25303e;
 --okbg:#15230f;--nobg:#2a1c1c;--hype:#f0b45a;--hypebg:#2a2010;--hypebd:#8a6a2a}
*{box-sizing:border-box}
body{margin:0;background:var(--pg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Noto Sans TC",sans-serif}
.wrap{max-width:1500px;margin:0 auto;padding:26px 20px 60px}
h1{font-size:21px;margin:0 0 4px}
.sub{color:var(--ink2);font-size:12.5px;margin-bottom:14px}
.card{background:var(--sf);border:1px solid var(--ring);border-radius:10px;padding:14px 16px;margin-bottom:14px}
h2{font-size:13px;margin:0 0 8px;color:var(--ink2);font-weight:600}
.rules{font-size:12.5px;color:var(--ink2);line-height:1.65}
.rules b{color:var(--ink)}
.mkt{font-size:12.5px;color:var(--ink2);line-height:1.7}
.mkt b{color:var(--ink)}
.mkt .mf{margin-top:6px}
.mkt .mf span{display:inline-block;background:var(--hl);border:1px solid var(--ring);border-radius:12px;
 padding:2px 9px;margin:2px 4px 2px 0;font-size:11.5px}
.nav{position:sticky;top:0;z-index:5;display:flex;gap:6px;flex-wrap:wrap;align-items:center;background:var(--pg);
 padding:10px 0;border-bottom:1px solid var(--grid);margin-bottom:14px}
.nav button{font:600 13px/1 system-ui,"Noto Sans TC",sans-serif;color:var(--ink2);background:var(--sf);
 border:1px solid var(--ring);border-radius:20px;padding:9px 14px;cursor:pointer}
.nav button .s{display:block;font-weight:400;font-size:10.5px;color:var(--mut);margin-top:3px}
.nav button.on{color:var(--pg);background:var(--ink);border-color:var(--ink)}
.nav button.on .s{color:var(--pg);opacity:.75}
.nav .div{width:1px;height:26px;background:var(--grid);margin:0 4px}
.nav .sortb{font-weight:600;font-size:12px;padding:8px 12px}
.nav .sortb.on{color:var(--pg);background:var(--seq);border-color:var(--seq)}
.pghead{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;margin:2px 0 10px;font-size:12.5px;color:var(--ink2)}
.pghead b{font-size:15px;color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.chip{font-size:11.5px;color:var(--ink2);background:var(--sf);border:1px solid var(--ring);
 border-radius:14px;padding:4px 10px}
.chip b{color:var(--ink)}
.chip i{font-style:normal;font-weight:700;color:var(--seq)}
.tblwrap{overflow-x:auto;background:var(--sf);border:1px solid var(--ring);border-radius:10px}
table{border-collapse:collapse;table-layout:fixed;font-size:12.5px}
th{position:sticky;top:0;text-align:left;font-size:11px;color:var(--mut);font-weight:600;
 padding:9px 8px;border-bottom:1px solid var(--grid);background:var(--sf);white-space:nowrap;z-index:1;
 overflow:hidden;text-overflow:ellipsis}
th.srt{cursor:pointer}
th.srt:hover{color:var(--seq)}
th.srt.act{color:var(--seq)}
.thn{display:block;font-weight:400;font-size:10px}
.rz{position:absolute;top:0;right:0;width:7px;height:100%;cursor:col-resize;user-select:none}
.rz:hover{background:var(--seq);opacity:.4}
td{padding:8px 8px;border-bottom:1px solid var(--grid);vertical-align:middle;overflow:hidden}
tr:last-child td{border-bottom:0}
tr:hover td{background:var(--hl)}
td.hypebg,tr:hover td.hypebg{background:var(--hypebg)}
.rk{color:var(--mut);font-weight:600}
.nums{font-variant-numeric:tabular-nums;white-space:nowrap}
.mut{color:var(--mut)}
.slope{color:var(--good);font-weight:600}
.tk a{color:var(--link);font-weight:700;text-decoration:none;font-size:13.5px}
.tk a:hover{text-decoration:underline}
.tk .ex{font-size:10px;color:var(--mut);margin-left:6px}
.tk em{display:block;font-style:normal;font-size:10.5px;color:var(--mut);max-width:180px;
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tk .pxl{display:block;font-size:11px;margin-top:2px}
.badge{font-size:9px;font-weight:700;color:var(--seq);border:1px solid var(--seq);
 border-radius:8px;padding:1px 5px;margin-left:6px;vertical-align:1px;white-space:nowrap}
.mc b{display:block;font-size:13px}
.mc .meter{display:block;height:5px;border-radius:3px;background:var(--meter);margin-top:3px}
.mc .meter i{display:block;height:100%;border-radius:3px;background:var(--seq)}
.mc.certm .meter i{background:var(--warn)}
.mc.scorem .meter i{background:var(--good)}
.cv{font-variant-numeric:tabular-nums;font-size:12px;white-space:nowrap}
.cv.ok{color:var(--good);font-weight:600}
.cv.no{color:var(--bad)}
.cv.wr{color:var(--warn);font-weight:600}
.bots{}
.botwrap{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 4px}
.bot{white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px}
.bot i{font-style:normal;color:var(--mut);font-size:10px}
.arr{color:var(--axis);margin:0 3px}
.warn{color:var(--warn);font-size:10.5px;white-space:nowrap}
.whyc{vertical-align:middle}
.why{font-size:11.5px;line-height:1.5;color:var(--ink2);overflow-wrap:break-word}
.hype{display:inline-block;font-size:10.5px;font-weight:700;color:var(--hype);background:var(--hypebg);
 border:1px solid var(--hypebd);border-radius:9px;padding:1px 7px;margin:0 4px 2px 0}
.conf{display:inline-block;font-size:9.5px;border-radius:8px;padding:0 5px;margin-left:4px;border:1px solid var(--ring);color:var(--mut)}
.conf.c高{color:var(--good);border-color:var(--good)}
.conf.c中{color:var(--warn);border-color:var(--warn)}
.sect b{font-size:12px}
.sect span{font-size:10.5px;color:var(--mut);margin-left:4px}
.sect em{display:block;font-style:normal;font-size:10.5px;color:var(--ink2)}
.gics{display:inline-block;font-style:normal;font-size:9px;color:var(--seq);border:1px solid var(--ring);border-radius:7px;padding:0 4px;margin-left:5px;vertical-align:1px}
.frs{white-space:normal}
.fr{display:inline-block;font-size:10px;color:var(--mut);border:1px dashed var(--axis);
 border-radius:9px;padding:1px 5px;margin:1px 3px 1px 0}
.fr.on{color:var(--ink);border:1px solid var(--seq);background:var(--hl)}
.fr.on i{font-style:normal;color:var(--seq);font-weight:700;margin-left:2px}
.subsc{font-size:10.5px;color:var(--mut);margin-top:3px;white-space:nowrap}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--ink2);margin:8px 2px 0}
.legend .sw{display:inline-block;width:14px;height:3px;vertical-align:3px;margin-right:5px;border-radius:2px}
.foot{font-size:11.5px;color:var(--ink2);line-height:1.7}
.foot b{color:var(--ink)}
section[hidden]{display:none}
@media (prefers-reduced-motion:no-preference){.nav button{transition:background .15s,color .15s}}
"""

rules_html = f"""
<div class="card rules">
<h2>篩選規則（R4 · 分欄 + 可排序 + 可調欄闊）</h2>
① <b>{esc(UNIVERSE_LINE)}</b>。<br>
② <b>MA 上升</b>：PAGE 2：<b>10 天 MA</b> 較 <b>5 個交易日</b>前高；PAGE 3/4/5：<b>20 天 MA</b> 分別較 <b>10 / 21 / 42 個交易日</b>前高；且 MA 最後 3 日逐日上升、期內 ≥70% 日子上升。 ③ <b>「底」</b>：某日收盤係 ±3 日內最低，且 3 日前收盤高過佢、3 日後收盤高過佢；相鄰 ≤3 日去重。 ④ <b>一底高於一底</b>：45 個交易日內 ≥2 個底逐個遞升，最近一個底喺 25 日內。<br>
⑤ <b>VCP 指數（0–100）</b>：10日/前30日波幅（35%）＋近10日區間佔價（25%）＋近10日/前30日成交量（20%）＋近15日/前30–45日區間（20%），全體百分位合成。 ⑥ <b>確定性（0–100，7 欄）</b>：突破中間高位（25%）· 回補幅度（10%）· 守底時間（15日滿分，曾跌穿×0.25，15%）· 下試量縮（跌日/升日量比，15%）· 回撤遞減（末段/首段跌幅，10%）· 相對強度（21日−全體中位，10%）· 均線位置（價>20MA＋20MA>50MA＋50MA向上，15%）。<br>
⑦ <b>預設排名</b>：PAGE 2–5 按綜合分數（0.5×VCP＋0.5×確定性）取 top 50 排列；PAGE 1 按爆發潛力分數（0.4×VCP＋0.4×確定性＋0.2×覆蓋度）。<b>TOP BAR 可切換「按VCP」「按確定性」排列（降序）；7 個確定性欄嘅表頭都可以㩒一下按該項得分降序排</b>（量縮/遞減兩項數值越低得分越高）。<b>欄闊可以拖拉表頭右邊調整</b>。<br>
⑧ <b>下跌原因 / 回升原因（兩欄）</b>：AI 代理經 <a href="https://bigdata.com" target="_blank" rel="noopener">Bigdata.com</a> 新聞索引＋公開網頁逐隻研究後濃縮；<b>🔥 標示 = 市場熱炒嘅 news-driven 催化</b>（收購/私有化、爆炸性數據、大幅盈喜等）；信心度：高＝明確個股消息，中＝板塊/部分證據，低＝只反映大市背景。
</div>"""

mkt_html = ""
if MKT:
    factors = "".join(f'<span><b>{esc(f["period"])}</b> {esc(f["factor_zh"])}</span>' for f in MKT.get("factors", []))
    mkt_html = (f'<div class="card mkt"><h2>2026年6–8月 市場背景（底部成因的共同分母）</h2>'
                f'{esc(MKT["summary_zh"])}<div class="mf">{factors}</div></div>')

secs = []
nav_btns = []
for pid, tab, subt in PAGE_DEFS:
    on_cls = ' class="on"' if pid == "1" else ""
    nav_btns.append(f'<button data-p="{pid}"{on_cls}>{tab}<span class="s">{subt}</span></button>')
    if pid == "1":
        head, body, cg, tw = table_page1()
        pghead = (f'<div class="pghead"><b>總覽 · 爆發潛力排名</b>'
                  f'<span>4 個時間框 top 50 合共 <b>{len(O["page1"])}</b> 隻不重複股票</span>'
                  f'<span>預設排序 = 爆發潛力分數（0.4×VCP＋0.4×確定性＋0.2×覆蓋度）</span></div>')
        chips = sector_chips(O["page1"])
        extra = mkt_html
    else:
        head, body, pg, cg, tw = table_page(pid)
        pghead = (f'<div class="pghead"><b>{tab.split("·")[1].strip()} · {subt}</b>'
                  f'<span>合資格 <b>{pg["qualified"]}</b> 隻 → 按綜合分數（0.5×VCP＋0.5×確定性）取 top 50</span></div>')
        chips = sector_chips(pg["rows"])
        extra = ""
    secs.append(f'''<section id="p{pid}"{"" if pid == "1" else " hidden"}>
{pghead}{extra}{chips}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw" style="background:var(--ink2)"></i>收盤</span>
<span><i class="sw" style="background:var(--seq)"></i>MA（頁面各自 10/20 天）</span>
<span><i class="sw" style="background:var(--good);height:8px;width:8px;border-radius:50%"></i>底部（最後60個交易日）</span>
<span>突破欄：✓＝中間高位已升穿，百分比＝現價喺「底→中間高位」嘅位置 · 表頭 ↓＝可㩒排序 · 拖表頭右邊＝調欄闊</span></div>
</section>''')

foot = f"""
<div class="card foot">
<h2>備註 · 數據 lineage</h2>
① 覆蓋範圍：美國上市普通股 {c["total"]:,} 隻（含 S&amp;P 500 全部 503 隻）；外國註冊而非 S&amp;P 500 嘅美國上市股未有完整歷史，未納入。價格未除息調整。<br>
② 數據重建：GitHub 每日 Nasdaq 快照鏡像（zyhe16/top-us-stock-tickers）逐 commit 重建收盤序列，{M["n_days"]} 個交易日（{M["cal_first"]} → {M["cal_last"]}）；4 日無快照以前值填補；08-27 以官方 net-change 校正；與 R1 抽樣核對底部價 10/10 一致、20MA 平均偏差 0.18%。<br>
③ 類別：Nasdaq 分類＋GICS（S&amp;P 500）；交易所：irachex/open-stock-data。確定性 7 項及排名經獨立代理人對抗性驗證。<br>
④ 原因兩欄由 AI 代理經 <a href="https://bigdata.com" target="_blank" rel="noopener">Bigdata.com</a> 新聞索引及公開網頁研究後濃縮——係新聞摘要，可能有錯漏，請以原始公告為準。<br>
⑤ <b>數據終點 {M["last_date"]}，建置時間 {BUILD_TS}</b>（週末，08-28 五係最後交易日）· 快照只有收盤/成交量 · 本表只係篩選工具，唔係投資建議。<br>
⑥ Ticker 點擊開 TradingView chart（https://www.tradingview.com/chart/Q1c5VWwD/?symbol=交易所%3Aticker）。
</div>"""

html_doc = f"""<title>20MA Uptrend Watchlist R4</title>
<style>{css}</style>
<div class="wrap">
<h1>20MA Uptrend Watchlist R4（一底高於一底 × VCP × 底部確定性 · 可排序分欄版）</h1>
<div class="sub">數據至 <b>{M["last_date"]}</b> 收盤 · 全美掃描 {c["liq"]:,} 隻合資格 · VCP／確定性／7 項證據全部分欄，TOP BAR 同表頭可切換排序，欄闊可拖拉調整 · 🔥＝市場熱炒 news-driven 回升</div>
{rules_html}
<nav class="nav">{"".join(nav_btns)}<span class="div"></span>
<button class="sortb on" data-sort="">預設排名</button>
<button class="sortb" data-sort="vcp">按 VCP 排列</button>
<button class="sortb" data-sort="cert">按 確定性 排列</button></nav>
{"".join(secs)}
{foot}
</div>
<script>
(function() {{
  var pbtns = document.querySelectorAll('.nav button[data-p]');
  var sbtns = document.querySelectorAll('.nav button.sortb');
  var cur = '1';
  function show(p) {{
    cur = p;
    document.querySelectorAll('section[id^="p"]').forEach(function(s) {{ s.hidden = (s.id !== 'p' + p); }});
    pbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.p === p); }});
    syncSortUi();
    try {{ localStorage.setItem('r4page', p); }} catch (e) {{}}
  }}
  var sortState = {{}};
  function sortSec(p, key) {{
    sortState[p] = key;
    var tb = document.querySelector('#p' + p + ' tbody');
    var rows = Array.prototype.slice.call(tb.rows);
    if (key) {{
      rows.sort(function(a, b) {{ return (+b.dataset[key]) - (+a.dataset[key]); }});
    }} else {{
      rows.sort(function(a, b) {{ return (+a.dataset.rank) - (+b.dataset.rank); }});
    }}
    rows.forEach(function(r, i) {{ r.cells[0].textContent = i + 1; tb.appendChild(r); }});
    syncSortUi();
  }}
  function syncSortUi() {{
    var key = sortState[cur] || '';
    sbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.sort === key); }});
    document.querySelectorAll('#p' + cur + ' th.srt').forEach(function(h) {{
      h.classList.toggle('act', h.dataset.key === key && key !== '');
    }});
  }}
  pbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ show(b.dataset.p); }}); }});
  sbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ sortSec(cur, b.dataset.sort); }}); }});
  document.querySelectorAll('th.srt').forEach(function(h) {{
    h.addEventListener('click', function() {{
      var sec = h.closest('section');
      sortSec(sec.id.slice(1), h.dataset.key);
    }});
  }});
  // draggable column widths
  document.querySelectorAll('.tblwrap table').forEach(function(t) {{
    var cols = t.querySelectorAll('col');
    t.querySelectorAll('th').forEach(function(th, i) {{
      var h = document.createElement('span');
      h.className = 'rz';
      th.appendChild(h);
      h.addEventListener('click', function(e) {{ e.stopPropagation(); }});
      h.addEventListener('mousedown', function(e) {{
        e.preventDefault(); e.stopPropagation();
        var startX = e.pageX, col = cols[i];
        var w0 = parseInt(col.style.width, 10) || col.offsetWidth;
        function mv(ev) {{
          var w = Math.max(40, w0 + ev.pageX - startX);
          col.style.width = w + 'px';
          var sum = 0;
          cols.forEach(function(c2) {{ sum += parseInt(c2.style.width, 10) || 60; }});
          t.style.width = sum + 'px';
        }}
        function up() {{
          document.removeEventListener('mousemove', mv);
          document.removeEventListener('mouseup', up);
        }}
        document.addEventListener('mousemove', mv);
        document.addEventListener('mouseup', up);
      }});
    }});
  }});
  var saved = null;
  try {{ saved = localStorage.getItem('r4page'); }} catch (e) {{}}
  if (saved && document.getElementById('p' + saved)) show(saved);
}})();
</script>
"""

out_path = f"{SCRATCH}/{OUTNAME}"
open(out_path, "w", encoding="utf-8").write(html_doc)
print("wrote", out_path, f"{len(html_doc)/1024:.0f} KB")
