#!/usr/bin/env python3
"""Build the R5 report: 12 market-cap-tiered timeframe pages + a full summary table,
with a dedicated market-hype catalyst column and per-page catalyst banner."""
import json, datetime, html, os, sys

SCRATCH = os.environ.get("WORK_DIR", "./data")
O = json.load(open(f"{SCRATCH}/screen_results6.json"))
NEWS = json.load(open(f"{SCRATCH}/news6.json")) if os.path.exists(f"{SCRATCH}/news6.json") else {}
MKT = json.load(open(f"{SCRATCH}/market.json")) if os.path.exists(f"{SCRATCH}/market.json") else None
M = O["meta"]

now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
OUTNAME = f"20MA_uptrend_watchlistGit_R6.01_claudeopus5max_{STAMP}.html"

TF = [("2", "1星期", "10MA · 5個交易日"), ("3", "2星期", "20MA · 10個交易日"),
      ("4", "1個月", "20MA · 21個交易日"), ("5", "2個月", "20MA · 42個交易日")]
TIERS = [("a", "大型股", "S&P 500", "大型股指數"), ("b", "中型股", "S&P 400", "中型股指數"),
         ("c", "小型股", "S&P 600", "小型股指數")]
TIER_ZH = {k: zh for k, zh, _, _ in TIERS}
TIER_RANGE = {k: rg for k, _, _, rg in TIERS}

def esc(s): return html.escape(str(s), quote=True)

def fmt_cap(v):
    if not v: return "—"
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9: return f"${v/1e9:.1f}B"
    if v >= 1e6: return f"${v/1e6:.0f}M"
    return f"${v:,.0f}"

def spark_svg(sp):
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
    ma_polys = "".join(f'<polyline points="{" ".join(s)}" fill="none" stroke="var(--seq)" stroke-width="1.3" opacity=".9"/>'
                       for s in segs if len(s) > 1)
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

CERT_HEADS = [("bbreak", "突破", "中間高位"), ("bretr", "回補", "跌幅收復"), ("btime", "守底", "未破日數"),
              ("bdv", "量縮", "跌/升量比"), ("bcontr", "遞減", "末/首跌幅"),
              ("brs", "RS", "21日相對"), ("bma", "均線", "結構")]
CERT_KEYS = [("bbreak", "break"), ("bretr", "retr"), ("btime", "time"),
             ("bdv", "dv"), ("bcontr", "contr"), ("brs", "rs"), ("bma", "ma")]

def cert_ths():
    return "".join(f'<th class="srt" data-key="{k}">{t}<span class="thn">{n} ↓</span></th>'
                   for k, t, n in CERT_HEADS)

def cert_cells(r):
    c = r["cert_c"]
    brk = ('<td class="cv ok">✓突破</td>' if c["broke"]
           else f'<td class="cv no">{max(0, min(99, c["retrace_pct"])):.0f}%</td>')
    retr = c["retrace_pct"]
    retr_s = "100%+" if retr >= 100 else f"{max(0.0, retr):.0f}%"
    held = f'<td class="cv{" wr" if c["undercut"] else ""}">{c["d_held"]}日{"⚠" if c["undercut"] else ""}</td>'
    maf = sum(c["ma_flags"])
    return (brk + f'<td class="cv">{retr_s}</td>' + held
            + f'<td class="cv{" ok" if c["dv_ratio"] < 0.85 else ""}">{c["dv_ratio"]:.2f}</td>'
            + f'<td class="cv{" ok" if c["contr"] < 0.6 else ""}">{c["contr"]:.2f}</td>'
            + f'<td class="cv{" ok" if c["rs21_pct"] > 0 else ""}">{c["rs21_pct"]:+.1f}%</td>'
            + f'<td class="cv{" ok" if maf == 3 else ""}">{maf}/3</td>')

def row_attrs(r, rank, p1=False):
    s = r["cert_c"]["s"]
    a = (f' data-rank="{rank}" data-vcp="{r["vcp"]}" data-cert="{r["cert"]}"'
         f' data-mcap="{r.get("mcap", 0):.0f}" data-hype="{1 if (NEWS.get(r["sym"], {}).get("hype")) else 0}"')
    if p1: a += f' data-score="{r["score"]}"'
    for dk, sk in CERT_KEYS:
        a += f' data-{dk}="{s[sk]}"'
    return a

def tv_url(r):
    sym = r["sym"].replace("/", ".").lower()
    if r["exch"] != "—":
        return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={r["exch"].lower()}%3A{esc(sym)}'
    return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={esc(sym)}'

def tick_cell(r, L):
    sp = '<span class="badge">S&amp;P500</span>' if r["sp500"] else ""
    warn = ' <span class="warn">⚠低於MA</span>' if r["below_ma"] else ""
    return (f'<div class="tk"><a href="{tv_url(r)}" target="_blank" rel="noopener">{esc(r["sym"])}</a>'
            f'<span class="ex">{esc(r["exch"])}</span>{sp}<em>{esc(r["name"][:32])}</em>'
            f'<span class="pxl nums">{r["close"]:g} <span class="mut">/ MA{L} {r["ma"]:g}</span>{warn}</span></div>')

def cap_cell(r):
    return (f'<div class="capc"><b class="nums">{fmt_cap(r.get("mcap", 0))}</b>'
            f'<span class="tierb t{r["tier"]}">{TIER_ZH[r["tier"]]}</span></div>')

def spark_cell(r):
    return (f'{spark_svg(r["spark"])}'
            f'<div class="subsc nums slope">MA{r["L"]} {r["slope"]:+.2f}% <span class="mut">/{r["W"]}日</span></div>')

def bottoms_chain(hl):
    shown = hl[-4:]
    parts = [f'<span class="bot">{d[5:]}<i>@{p:g}</i></span>' for d, p in shown]
    sep = '<span class="arr">→</span>'
    pre = '<span class="arr">…→</span>' if len(hl) > 4 else ""
    return f'<div class="botwrap">{pre}{sep.join(parts)}</div>'

def hype_cell(sym):
    e = NEWS.get(sym) or {}
    if e.get("hype") and e.get("hype_zh"):
        return f'<td class="hypec"><span class="hype">🔥 {esc(e["hype_zh"])}</span></td>'
    return '<td class="hypec"><span class="nohype">—</span></td>'

CONF_CLS = {"高": "chi", "中": "cmid", "低": "clo"}

def news_cells(sym):
    e = NEWS.get(sym) or {}
    dn = e.get("decline_short", "—")
    up = e.get("recovery_short", "—")
    conf = e.get("confidence", "低")
    upcls = " hypebg" if e.get("hype") else ""
    lowcls = " lowconf" if conf == "低" else ""
    return (f'<td class="whyc{lowcls}"><div class="why">{esc(dn)}</div></td>'
            f'<td class="whyc{upcls}{lowcls}"><div class="why">{esc(up)}'
            f'<span class="conf {CONF_CLS.get(conf, "clo")}">信心{esc(conf)}</span></div></td>')

def sector_cell(r):
    sub = r["gsub"] if (r["sp500"] and r.get("gsub")) else r["industry"]
    gtag = f'<i class="gics">GICS·{esc(r["gsec"])}</i>' if (r["sp500"] and r.get("gsec")) else ""
    return (f'<div class="sect"><b>{esc(r["sector_zh"])}</b> <span>{esc(r["sector"])}</span>{gtag}'
            f'<em>{esc(sub)}</em></div>')

def sector_chips(rows):
    cnt = {}
    for r in rows:
        cnt[(r["sector_zh"], r["sector"])] = cnt.get((r["sector_zh"], r["sector"]), 0) + 1
    return '<div class="chips">' + "".join(
        f'<span class="chip"><b>{esc(z)}</b> {esc(e)} <i>{n}</i></span>'
        for (z, e), n in sorted(cnt.items(), key=lambda x: -x[1])) + '</div>'

def hype_banner(rows):
    hy = [(r["sym"], NEWS[r["sym"]]["hype_zh"]) for r in rows
          if NEWS.get(r["sym"], {}).get("hype") and NEWS[r["sym"]].get("hype_zh")]
    if not hy:
        return '<div class="hbanner none">本頁未見市場熱炒 news-driven 催化劑（回升多屬業績穩健或跟隨大市）</div>'
    items = "".join(f'<a class="hitem" href="#" data-sym="{esc(s)}"><b>{esc(s)}</b>{esc(t)}</a>' for s, t in hy)
    return (f'<div class="hbanner"><span class="hlab">🔥 本頁熱炒催化 <b>{len(hy)}</b> 隻</span>{items}</div>')

COLW_TIER = [34, 178, 78, 76, 76, 62, 56, 56, 56, 56, 62, 54, 152, 148, 128, 196, 210, 138]
COLW_P1 = [34, 178, 78, 84, 76, 76, 130, 62, 56, 56, 56, 56, 62, 54, 152, 128, 196, 210, 138]

def colgroup(ws):
    return "<colgroup>" + "".join(f'<col style="width:{w}px">' for w in ws) + "</colgroup>", sum(ws)

def table_tier(pid):
    pg = O["pages"][pid]
    L = pg["L"]
    head = (f'<tr><th>#</th><th>Ticker · 現價/MA{L}</th>'
            f'<th class="srt" data-key="mcap">市值<span class="thn">層級 ↓</span></th>'
            f'<th class="srt" data-key="vcp">VCP指數<span class="thn">收縮度 ↓</span></th>'
            f'<th class="srt" data-key="cert">確定性<span class="thn">7項合成 ↓</span></th>'
            f'{cert_ths()}'
            f'<th>60日走勢 · 斜率</th>'
            f'<th>底部序列<span class="thn">45日內遞升</span></th>'
            f'<th class="srt hy" data-key="hype">🔥 熱炒催化劑<span class="thn">news-driven ↓</span></th>'
            f'<th>下跌原因</th><th>回升原因</th><th>類別</th></tr>')
    rows = []
    for i, r in enumerate(pg["rows"], 1):
        rows.append(
            f'<tr{row_attrs(r, i)} data-sym="{esc(r["sym"])}"><td class="rk">{i}</td><td>{tick_cell(r, L)}</td>'
            f'<td>{cap_cell(r)}</td><td>{meter_cell(r["vcp"])}</td><td>{meter_cell(r["cert"], "certm")}</td>'
            f'{cert_cells(r)}<td>{spark_cell(r)}</td><td class="bots">{bottoms_chain(r["hl"])}</td>'
            f'{hype_cell(r["sym"])}{news_cells(r["sym"])}<td>{sector_cell(r)}</td></tr>')
    cg, tw = colgroup(COLW_TIER)
    return head, "".join(rows), pg, cg, tw

def table_p1():
    head = ('<tr><th>#</th><th>Ticker · 現價/MA</th>'
            '<th class="srt" data-key="mcap">市值<span class="thn">層級 ↓</span></th>'
            '<th class="srt" data-key="score">爆發潛力<span class="thn">0.4V+0.4確+0.2覆 ↓</span></th>'
            '<th class="srt" data-key="vcp">VCP指數<span class="thn">收縮度 ↓</span></th>'
            '<th class="srt" data-key="cert">確定性<span class="thn">7項合成 ↓</span></th>'
            '<th>上榜分頁<span class="thn">頁內排名</span></th>'
            f'{cert_ths()}'
            '<th>60日走勢 · 斜率</th>'
            '<th class="srt hy" data-key="hype">🔥 熱炒催化劑<span class="thn">news-driven ↓</span></th>'
            '<th>下跌原因</th><th>回升原因</th><th>類別</th></tr>')
    rows = []
    for i, r in enumerate(O["page1"], 1):
        frs = "".join(f'<span class="fr on">{p[0]}{TIER_ZH[p[1]][0]}<i>#{n}</i></span>'
                      for p, n in sorted(r["ranks"].items()))
        rows.append(
            f'<tr{row_attrs(r, i, p1=True)} data-sym="{esc(r["sym"])}"><td class="rk">{i}</td>'
            f'<td>{tick_cell(r, r["L"])}</td><td>{cap_cell(r)}</td>'
            f'<td>{meter_cell(r["score"], "scorem")}</td><td>{meter_cell(r["vcp"])}</td>'
            f'<td>{meter_cell(r["cert"], "certm")}</td><td class="frs">{frs}</td>'
            f'{cert_cells(r)}<td>{spark_cell(r)}</td>'
            f'{hype_cell(r["sym"])}{news_cells(r["sym"])}<td>{sector_cell(r)}</td></tr>')
    cg, tw = colgroup(COLW_P1)
    return head, "".join(rows), cg, tw

c = M["counts"]
UNIVERSE_LINE = (f'S&P 1500 綜合指數成分（大型 S&P 500 ＋ 中型 S&P 400 ＋ 小型 S&P 600）—— '
                 f'有 {M["last_date"]} 收盤報價 {c["current"]:,} 隻 · 歷史 ≥90 交易日 {c["hist"]:,} 隻 · '
                 f'價格 ≥$2 {c["price"]:,} 隻 · 流動性達標（20日中位成交額 ≥$1M）{c["liq"]:,} 隻合資格')

css = """
/* Committed dark theme: the palette is defined once on :root and never
   flips, so the page reads the same whatever theme the viewer is in. */
:root{color-scheme:dark;
 --pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;
 --grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
 --seq:#3987e5;--link:#6da7ec;--good:#0ca30c;--warn:#d99a2b;--bad:#e06c6c;
 --hl:#16202d;--meter:#25303e;--okbg:#15230f;--nobg:#2a1c1c;
 --hype:#f2b95f;--hypebg:#2d2211;--hypebd:#8f6d2c;
 --tierA:#6da7ec;--tierB:#a98ce8;--tierC:#3fc49b}
*{box-sizing:border-box}
body{margin:0;background:var(--pg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Noto Sans TC",sans-serif}
.wrap{max-width:1560px;margin:0 auto;padding:26px 20px 60px}
h1{font-size:21px;margin:0 0 4px}
.sub{color:var(--ink2);font-size:12.5px;margin-bottom:14px}
.card{background:var(--sf);border:1px solid var(--ring);border-radius:10px;padding:14px 16px;margin-bottom:14px}
h2{font-size:13px;margin:0 0 8px;color:var(--ink2);font-weight:600}
.rules{font-size:12.5px;color:var(--ink2);line-height:1.65}
.rules b{color:var(--ink)}
.rules .cav{color:var(--warn)}
.mkt{font-size:12.5px;color:var(--ink2);line-height:1.7}
.mkt b{color:var(--ink)}
.mkt .mf{margin-top:6px}
.mkt .mf span{display:inline-block;background:var(--hl);border:1px solid var(--ring);border-radius:12px;
 padding:2px 9px;margin:2px 4px 2px 0;font-size:11.5px}
.nav{position:sticky;top:0;z-index:6;background:var(--pg);padding:10px 0 8px;
 border-bottom:1px solid var(--grid);margin-bottom:12px}
.nrow{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.nrow+.nrow{margin-top:7px}
.nav button{font:600 13px/1 system-ui,"Noto Sans TC",sans-serif;color:var(--ink2);background:var(--sf);
 border:1px solid var(--ring);border-radius:20px;padding:9px 14px;cursor:pointer}
.nav button .s{display:block;font-weight:400;font-size:10.5px;color:var(--mut);margin-top:3px}
.nav button.on{color:var(--pg);background:var(--ink);border-color:var(--ink)}
.nav button.on .s{color:var(--pg);opacity:.75}
.nav .tierb{font-size:12.5px;padding:8px 13px}
.nav .tierb.on{background:var(--seq);border-color:var(--seq);color:#fff}
.nav .tierb.on .s{color:#fff;opacity:.8}
.nav .lab{font-size:11px;color:var(--mut);margin-right:2px}
.nav .div{width:1px;height:24px;background:var(--grid);margin:0 5px}
.nav .sortb{font-weight:600;font-size:12px;padding:8px 12px}
.nav .sortb.on{color:#fff;background:var(--seq);border-color:var(--seq)}
#tierrow[hidden]{display:none}
.pghead{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;margin:2px 0 10px;font-size:12.5px;color:var(--ink2)}
.pghead b{font-size:15px;color:var(--ink)}
.pghead .tg{font-size:11px;border:1px solid var(--ring);border-radius:10px;padding:2px 8px}
.hbanner{display:flex;flex-wrap:wrap;gap:5px;align-items:center;background:var(--hypebg);
 border:1px solid var(--hypebd);border-radius:10px;padding:8px 12px;margin-bottom:12px}
.hbanner.none{background:var(--sf);border-color:var(--ring);color:var(--mut);font-size:11.5px}
.hlab{font-size:12px;font-weight:700;color:var(--hype);margin-right:4px}
.hitem{font-size:11px;color:var(--hype);background:var(--sf);border:1px solid var(--hypebd);
 border-radius:9px;padding:2px 8px;text-decoration:none}
.hitem b{color:var(--ink);margin-right:5px}
.hitem:hover{background:var(--hypebd);color:var(--pg)}
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
th.hy{color:var(--hype)}
.thn{display:block;font-weight:400;font-size:10px}
.rz{position:absolute;top:0;right:0;width:7px;height:100%;cursor:col-resize;user-select:none}
.rz:hover{background:var(--seq);opacity:.4}
td{padding:8px 8px;border-bottom:1px solid var(--grid);vertical-align:middle;overflow:hidden}
tr:last-child td{border-bottom:0}
tr:hover td{background:var(--hl)}
td.hypebg,tr:hover td.hypebg{background:var(--hypebg)}
tr.flash td{background:var(--hypebg)!important}
.rk{color:var(--mut);font-weight:600}
.nums{font-variant-numeric:tabular-nums;white-space:nowrap}
.mut{color:var(--mut)}
.slope{color:var(--good);font-weight:600}
.tk a{color:var(--link);font-weight:700;text-decoration:none;font-size:13.5px}
.tk a:hover{text-decoration:underline}
.tk .ex{font-size:10px;color:var(--mut);margin-left:6px}
.tk em{display:block;font-style:normal;font-size:10.5px;color:var(--mut);
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tk .pxl{display:block;font-size:11px;margin-top:2px}
.badge{font-size:9px;font-weight:700;color:var(--seq);border:1px solid var(--seq);
 border-radius:8px;padding:1px 5px;margin-left:6px;vertical-align:1px;white-space:nowrap}
.capc b{display:block;font-size:12.5px}
.tierb{display:inline-block;font-size:9.5px;border-radius:8px;padding:0 5px;margin-top:2px;border:1px solid}
.tierb.ta{color:var(--tierA);border-color:var(--tierA)}
.tierb.tb{color:var(--tierB);border-color:var(--tierB)}
.tierb.tc{color:var(--tierC);border-color:var(--tierC)}
.mc b{display:block;font-size:13px}
.mc .meter{display:block;height:5px;border-radius:3px;background:var(--meter);margin-top:3px}
.mc .meter i{display:block;height:100%;border-radius:3px;background:var(--seq)}
.mc.certm .meter i{background:var(--warn)}
.mc.scorem .meter i{background:var(--good)}
.cv{font-variant-numeric:tabular-nums;font-size:12px;white-space:nowrap}
.cv.ok{color:var(--good);font-weight:600}
.cv.no{color:var(--bad)}
.cv.wr{color:var(--warn);font-weight:600}
.botwrap{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 4px}
.bot{white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px}
.bot i{font-style:normal;color:var(--mut);font-size:10px}
.arr{color:var(--axis);margin:0 3px}
.warn{color:var(--warn);font-size:10.5px;white-space:nowrap}
.hypec{text-align:left}
.hype{display:inline-block;font-size:11px;font-weight:700;color:var(--hype);background:var(--hypebg);
 border:1px solid var(--hypebd);border-radius:9px;padding:3px 8px;line-height:1.35}
.nohype{color:var(--axis);font-size:11px}
.why{font-size:11.5px;line-height:1.5;color:var(--ink2);overflow-wrap:break-word}
.conf{display:inline-block;font-size:9.5px;border-radius:8px;padding:0 5px;margin-left:4px;
 border:1px solid var(--ring);color:var(--mut)}
.conf.chi{color:var(--good);border-color:var(--good)}
.conf.cmid{color:var(--warn);border-color:var(--warn)}
.conf.clo{color:var(--mut);border-style:dashed}
.whyc.lowconf .why{color:var(--mut);font-style:italic}
.sect b{font-size:12px}
.sect span{font-size:10.5px;color:var(--mut);margin-left:4px}
.sect em{display:block;font-style:normal;font-size:10.5px;color:var(--ink2)}
.gics{display:inline-block;font-style:normal;font-size:9px;color:var(--seq);border:1px solid var(--ring);
 border-radius:7px;padding:0 4px;margin-left:5px;vertical-align:1px}
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
@media (prefers-reduced-motion:no-preference){.nav button{transition:background .15s,color .15s}
 tr.flash td{transition:background .4s}}
"""

_listed = [r["sym"] for r in O["page1"]]
_conf = {"高": 0, "中": 0, "低": 0}
_hy = 0
for _s in _listed:
    _e = NEWS.get(_s)
    if not _e:
        _conf["低"] += 1
        continue
    _conf[_e.get("confidence", "低")] = _conf.get(_e.get("confidence", "低"), 0) + 1
    if _e.get("hype"):
        _hy += 1
COVERAGE = (f'研究覆蓋 {len(_listed)} 隻：<b>信心高 {_conf["高"]}</b>（搵到明確個股消息）· '
            f'<b>中 {_conf["中"]}</b>（板塊或部分證據）· <b>低 {_conf["低"]}</b>（未搵到個股消息，只反映大市背景）· '
            f'其中 <b>🔥 {_hy} 隻</b>屬市場熱炒 news-driven 催化')

rules_html = f"""
<div class="card rules">
<h2>篩選規則（R6 · 數據更新至 8/31 收盤 · S&amp;P 1500 三層分榜）</h2>
① <b>Universe：{esc(UNIVERSE_LINE)}</b>。<br>
② <b>市值分層（改用指數成分）</b>：<b>大型股 = S&amp;P 500</b> · <b>中型股 = S&amp;P 400</b> · <b>小型股 = S&amp;P 600</b> —— 呢個係業界標準嘅大／中／小型股定義，喺 S&amp;P 1500 宇宙下三層分佈均衡（本次上榜股市值中位數分別約 $45B／$9.5B／$3.5B）。每個時間框各自分三層，<b>每層獨立取 top 50</b>。市值一欄以最新收盤重估後嘅實際市值顯示，可獨立排序。<br>
③ <b>MA 上升</b>：PAGE 2a-c：<b>10 天 MA</b> 較 <b>5 個交易日</b>前高；PAGE 3/4/5：<b>20 天 MA</b> 分別較 <b>10 / 21 / 42 個交易日</b>前高；且 MA 最後 3 日逐日上升、期內 ≥70% 日子上升。<br>
④ <b>「底」</b>：某日收盤係 ±3 日內最低，且 3 日前收盤高過佢、3 日後收盤高過佢；相鄰 ≤3 日去重。 ⑤ <b>一底高於一底</b>：45 個交易日內 ≥2 個底逐個遞升，最近一個底喺 25 日內。<br>
⑥ <b>VCP 指數（0–100）</b>：10日/前30日波幅（35%）＋近10日區間佔價（25%）＋近10日/前30日成交量（20%）＋近15日/前30–45日區間（20%），全體百分位合成。<br>
⑦ <b>確定性（0–100，7 欄）</b>：突破中間高位（25%）· 回補幅度（10%）· 守底時間（15日滿分，曾跌穿×0.25，15%）· 下試量縮（15%）· 回撤遞減（10%）· 相對強度（10%）· 均線位置（15%）。<br>
⑧ <b>排名</b>：各分層頁按綜合分數（0.5×VCP＋0.5×確定性）取 top 50；總表按爆發潛力分數（0.4×VCP＋0.4×確定性＋0.2×時間框覆蓋度）。<b>TOP BAR 及表頭可切換排序（市值／VCP／確定性／7 項證據／熱炒）</b>；<b>欄闊可拖拉表頭右邊調整</b>。<br>
⑨ <b>🔥 熱炒催化劑欄</b>：AI 代理經 <a href="https://bigdata.com" target="_blank" rel="noopener">Bigdata.com</a> 新聞索引＋公開網頁逐隻研究後，凡回升由<b>市場熱炒嘅 news-driven 事件</b>帶動（收購／私有化、爆炸性臨床數據、大幅盈喜引發急升、AI 熱潮、單日暴漲），以獨立一欄＋每頁頂部橫幅精簡標示；其餘顯示「—」。<br>
⑩ <b>{COVERAGE}</b>。<span class="cav">⚠ 本次研究途中新聞搜尋額度耗盡，部分（信心低）股票未能完成個股新聞查證 —— 該等欄位以斜體灰字標示，只代表「未查證」，唔代表「無消息」。</span>
</div>"""

mkt_html = ""
if MKT:
    factors = "".join(f'<span><b>{esc(f["period"])}</b> {esc(f["factor_zh"])}</span>' for f in MKT.get("factors", []))
    mkt_html = (f'<div class="card mkt"><h2>2026年6–8月 市場背景（底部成因的共同分母）</h2>'
                f'{esc(MKT["summary_zh"])}<div class="mf">{factors}</div></div>')

# ---- sections ----
secs = []
head, body, cg, tw = table_p1()
tier_n = {}
for r in O["page1"]:
    tier_n[r["tier"]] = tier_n.get(r["tier"], 0) + 1
pghead = (f'<div class="pghead"><b>總表 · 全部分層數據</b>'
          f'<span>12 個分層榜合共 <b>{len(O["page1"])}</b> 隻不重複股票</span>'
          f'<span class="tg">大型 {tier_n.get("a", 0)}</span><span class="tg">中型 {tier_n.get("b", 0)}</span>'
          f'<span class="tg">小型 {tier_n.get("c", 0)}</span>'
          f'<span>排序 = 爆發潛力分數</span></div>')
secs.append(f'''<section id="p1">
{pghead}{mkt_html}{hype_banner(O["page1"])}{sector_chips(O["page1"])}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw" style="background:var(--ink2)"></i>收盤</span>
<span><i class="sw" style="background:var(--seq)"></i>MA</span>
<span><i class="sw" style="background:var(--good);height:8px;width:8px;border-radius:50%"></i>底部（最後60個交易日）</span>
<span>上榜分頁：2大 = PAGE 2a（1星期·大型股），如此類推</span>
<span>走勢圖／斜率取<b>最短一個達標時間框</b>（該股上榜分頁中最前者）；各時間框詳情見對應分層頁</span></div>
</section>''')

for p, tf_zh, tf_sub in TF:
    for k, tzh, ten, rng in TIERS:
        pid = f"{p}{k}"
        head, body, pg, cg, tw = table_tier(pid)
        pghead = (f'<div class="pghead"><b>PAGE {pid} · {tf_zh} · {tzh}</b>'
                  f'<span class="tg">{ten} {rng}</span>'
                  f'<span>{tf_sub}</span>'
                  f'<span>該層合資格 <b>{pg["qualified"]}</b> 隻 → 按綜合分數取 top {len(pg["rows"])}</span></div>')
        secs.append(f'''<section id="p{pid}" hidden>
{pghead}{hype_banner(pg["rows"])}{sector_chips(pg["rows"])}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw" style="background:var(--ink2)"></i>收盤</span>
<span><i class="sw" style="background:var(--seq)"></i>MA{pg["L"]}</span>
<span><i class="sw" style="background:var(--good);height:8px;width:8px;border-radius:50%"></i>底部</span>
<span>突破欄：✓＝中間高位已升穿，百分比＝現價喺「底→中間高位」嘅位置 · 表頭 ↓＝可㩒排序 · 拖表頭右邊＝調欄闊</span></div>
</section>''')

tf_btns = ('<button data-g="1" class="on">總表<span class="s">全部分層數據</span></button>'
           + "".join(f'<button data-g="{p}">{tf_zh}<span class="s">{tf_sub}</span></button>'
                     for p, tf_zh, tf_sub in TF))
tier_btns = "".join(f'<button class="tierb{" on" if k == "a" else ""}" data-t="{k}">{tzh}<span class="s">{rng}</span></button>'
                    for k, tzh, ten, rng in TIERS)

foot = f"""
<div class="card foot">
<h2>備註 · 數據 lineage</h2>
① <b>覆蓋範圍（R6 有變）</b>：本版改用 S&amp;P 1500 綜合指數成分（1,504 隻有 08-31 收盤），涵蓋美股約九成市值，但<b>唔再包括指數以外嘅細價股／微型股</b>——R5 嘅 217 隻上榜股中有 103 隻唔屬 S&amp;P 1500，故未出現喺本版。價格未除息調整。<br>② <b>數據來源（R6 有變）</b>：改用 GitHub 每日鏡像 natezone/market-tracker 嘅真實日線 OHLCV（yfinance 來源，收市後 20:09 UTC 推送），逐隻股票讀取完整日線歷史，本表取最近 {M["n_days"]} 個交易日（{M["cal_first"]} → {M["cal_last"]}）；該次跑漏咗 08-28，已由上一個 commit 完整還原（1,500 隻）。<b>與 R5 嘅獨立來源（Nasdaq 每日快照）交叉核對：2,932 個重疊收盤價中 2,926 個（99.8%）偏差 &lt;0.5%，中位偏差 0.000%</b>。<br>③ 類別：Nasdaq 分類＋GICS（S&amp;P 500）；交易所：irachex/open-stock-data。VCP、確定性 7 項及排名邏輯沿用 R3–R5 定義（未改動），已經 R3 階段 6 組、R5 分層 1 組獨立代理人對抗性驗證：12 頁排名、三層守恆、分層歸屬、與前版指標一致性、總表聯集及名次映射全部 PASS；驗證揪出「無市值數據被當成小型股」一項缺陷，已於本版修正（改為剔出分層頁並喺上方列明）。<br>
④ 原因及熱炒催化劑由 AI 代理經 <a href="https://bigdata.com" target="_blank" rel="noopener">Bigdata.com</a> 新聞索引及公開網頁研究後濃縮——係新聞摘要，可能有錯漏，請以原始公告為準。<br>
⑤ <b>數據終點 {M["last_date"]}，建置時間 {BUILD_TS}</b>（週末，08-28 五係最後交易日）· 快照只有收盤/成交量 · 本表只係篩選工具，唔係投資建議。<br>
⑥ Ticker 點擊開 TradingView chart（https://www.tradingview.com/chart/Q1c5VWwD/?symbol=交易所%3Aticker）。
</div>"""

html_doc = f"""<title>20MA Uptrend Watchlist R6</title>
<style>{css}</style>
<div class="wrap">
<h1>20MA Uptrend Watchlist R6（S&amp;P 1500 分層 × VCP × 底部確定性）</h1>
<div class="sub">數據至 <b>{M["last_date"]}</b>（美東週一）收盤 · S&amp;P 1500 掃描 {c["liq"]:,} 隻合資格 · 12 個分層榜（4 時間框 × S&amp;P 500／400／600）＋總表 · 🔥 熱炒 news-driven 催化劑獨立成欄</div>
{rules_html}
<nav class="nav">
<div class="nrow">{tf_btns}<span class="div"></span>
<button class="sortb on" data-sort="">預設排名</button>
<button class="sortb" data-sort="vcp">按 VCP 排列</button>
<button class="sortb" data-sort="cert">按 確定性 排列</button>
<button class="sortb" data-sort="mcap">按 市值 排列</button>
<button class="sortb" data-sort="hype">按 熱炒 排列</button></div>
<div class="nrow" id="tierrow" hidden><span class="lab">市值層級</span>{tier_btns}</div>
</nav>
{"".join(secs)}
{foot}
</div>
<script>
(function() {{
  var gbtns = document.querySelectorAll('.nav button[data-g]');
  var tbtns = document.querySelectorAll('.nav button[data-t]');
  var sbtns = document.querySelectorAll('.nav button.sortb');
  var tierrow = document.getElementById('tierrow');
  var g = '1', t = 'a';
  function cur() {{ return g === '1' ? '1' : g + t; }}
  function show() {{
    var id = 'p' + cur();
    document.querySelectorAll('section[id^="p"]').forEach(function(s) {{ s.hidden = (s.id !== id); }});
    gbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.g === g); }});
    tbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.t === t); }});
    tierrow.hidden = (g === '1');
    syncSort();
    try {{ localStorage.setItem('r6nav', g + '|' + t); }} catch (e) {{}}
  }}
  var sortState = {{}};
  function sortSec(pid, key) {{
    sortState[pid] = key;
    var tb = document.querySelector('#p' + pid + ' tbody');
    if (!tb) return;
    var rows = Array.prototype.slice.call(tb.rows);
    if (key) {{
      rows.sort(function(a, b) {{
        var d = (+b.dataset[key]) - (+a.dataset[key]);
        return d !== 0 ? d : (+a.dataset.rank) - (+b.dataset.rank);
      }});
    }} else {{
      rows.sort(function(a, b) {{ return (+a.dataset.rank) - (+b.dataset.rank); }});
    }}
    rows.forEach(function(r, i) {{ r.cells[0].textContent = i + 1; tb.appendChild(r); }});
    syncSort();
  }}
  function syncSort() {{
    var key = sortState[cur()] || '';
    sbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.sort === key); }});
    document.querySelectorAll('#p' + cur() + ' th.srt').forEach(function(h) {{
      h.classList.toggle('act', h.dataset.key === key && key !== '');
    }});
  }}
  gbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ g = b.dataset.g; show(); }}); }});
  tbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ t = b.dataset.t; show(); }}); }});
  sbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ sortSec(cur(), b.dataset.sort); }}); }});
  document.querySelectorAll('th.srt').forEach(function(h) {{
    h.addEventListener('click', function() {{ sortSec(h.closest('section').id.slice(1), h.dataset.key); }});
  }});
  document.querySelectorAll('.hitem').forEach(function(a) {{
    a.addEventListener('click', function(e) {{
      e.preventDefault();
      var sec = a.closest('section');
      var tr = sec.querySelector('tr[data-sym="' + a.dataset.sym + '"]');
      if (!tr) return;
      sec.querySelectorAll('tr.flash').forEach(function(x) {{ x.classList.remove('flash'); }});
      tr.classList.add('flash');
      tr.scrollIntoView({{block: 'center', behavior: 'smooth'}});
      setTimeout(function() {{ tr.classList.remove('flash'); }}, 2600);
    }});
  }});
  document.querySelectorAll('.tblwrap table').forEach(function(tb) {{
    var cols = tb.querySelectorAll('col');
    tb.querySelectorAll('th').forEach(function(th, i) {{
      var h = document.createElement('span');
      h.className = 'rz';
      th.appendChild(h);
      h.addEventListener('click', function(e) {{ e.stopPropagation(); }});
      h.addEventListener('mousedown', function(e) {{
        e.preventDefault(); e.stopPropagation();
        var startX = e.pageX, col = cols[i];
        var w0 = parseInt(col.style.width, 10) || col.offsetWidth;
        function mv(ev) {{
          col.style.width = Math.max(40, w0 + ev.pageX - startX) + 'px';
          var sum = 0;
          cols.forEach(function(c2) {{ sum += parseInt(c2.style.width, 10) || 60; }});
          tb.style.width = sum + 'px';
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
  try {{
    var sv = localStorage.getItem('r6nav');
    if (sv) {{
      var parts = sv.split('|');
      if (document.getElementById('p' + (parts[0] === '1' ? '1' : parts[0] + parts[1]))) {{
        g = parts[0]; t = parts[1];
      }}
    }}
  }} catch (e) {{}}
  show();
}})();
</script>
"""

out_path = f"{SCRATCH}/{OUTNAME}"
open(out_path, "w", encoding="utf-8").write(html_doc)
print("wrote", out_path, f"{len(html_doc)/1024:.0f} KB")
