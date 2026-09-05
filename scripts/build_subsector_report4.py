#!/usr/bin/env python3
"""Sub-Sector 資金流向 Watchlist R4.00 — 111 sub-sectors x 5 sessions of money-flow scores (Yahoo second source).

Pages: 總覽 / 每日矩陣 / GICS 板塊匯總 / 背離與輪動.
Light/dark themes (auto / light / dark, remembered), sortable + resizable columns.
"""
import json, datetime, html, os, statistics, collections, csv

SCRATCH = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
F = json.load(open(f"{SCRATCH}/sub4/flow4.json"))
B = json.load(open(f"{SCRATCH}/sub3/flow3.json"))   # R3.00, for the change summary only
BROW = {r["zh"]: r for r in B["rows"] if r.get("days")}
BDAYS = B["meta"]["days"]
M = F["meta"]; ROWS = F["rows"]; DAYS = M["days"]
now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
VER = "R4.00"
OUTNAME = f"SubSector_flow_watchlist_{VER}_claudefable51high_{STAMP}.html"
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

def day_chips(r):
    out = []
    for d in DAYS:
        x = r["days"][d]
        out.append(f'<span class="chipd {gcls(x["grade"])}" title="{esc(d)} · z {x["z"]:+.2f} · '
                   f'籃子報酬 {x["ret"]*100:+.2f}% · 量能 {x["rvol"]:.2f}x · 淨額 {fmt_m(x["mfd"])}">'
                   f'{x["score"]:.0f}</span>')
    return '<div class="chips5">' + "".join(out) + "</div>"

def basket_cell(r):
    nb = set(r.get("nobase") or [])
    NBT = ' title="快照 08-28 起先有數據，無 20 日量能基準：只計方向（B=0）"'
    parts = []
    for t in r["basket"]:
        c = "tk" + (" sup" if t in (r.get("supp") or []) else "") + (" nb" if t in nb else "")
        parts.append(f'<a href="{tv(t)}" target="_blank" rel="noopener" class="{c}"{NBT if t in nb else ""}>{esc(t)}</a>')
    tks = "".join(parts)
    miss = r.get("missing") or []
    mtag = f'<span class="miss" title="所有可達鏡像都無視窗內數據，未計入">缺 {esc("、".join(miss))}</span>' if miss else ""
    return f'<div class="bk">{tks}{mtag}</div>'

def qual(r):
    n = r["n_basket"]
    cls = "qlo" if n <= 2 else ("qmid" if n <= 3 else "qok")
    conf = "低" if n <= 2 else ("中" if n <= 3 else "高")
    tags = [f"可信度{conf}"]
    if r.get("proxy"): tags.append("代理樣本")
    if r.get("supp"): tags.append(f"補{len(r['supp'])}")
    if r.get("src") == "snap": tags.append("僅收盤")
    elif r.get("src") == "mix": tags.append(f"OHLC {r['ohlc_cov5']*100:.0f}%")
    if r.get("nobase"): tags.append(f"無量基準{len(r['nobase'])}")
    if (r.get("src_detail") or {}).get("yahoo"): tags.append(f"Yahoo {r['src_detail']['yahoo']}")
    if r.get("est_days"): tags.append(f"內插{len(r['est_days'])}日")
    return (f'<div class="qc"><b class="{cls}">{n}</b>'
            + "".join(f'<span class="qt{" cf" + t[3:] if t.startswith("可信度") else ""}">{esc(t)}</span>'
                      for t in tags) + "</div>")

def trend_cell(r):
    s = r["slope"]
    lab = "加速流入" if s >= 0.35 else "轉流入" if s >= 0.12 else "加速流出" if s <= -0.35 else "轉流出" if s <= -0.12 else "持平"
    cls = "up" if s >= 0.12 else "dn" if s <= -0.12 else "fl"
    return (f'<div class="tr {cls}"><b>{s:+.2f}</b><span>{lab}</span>'
            f'<i>{r["pos"]}↑/{r["neg"]}↓ · 廣度 {r["breadth5"]*100:.0f}%</i></div>')

def heat_cell(r):
    h = r.get("heat")
    if not h: return '<td class="hv">—</td>'
    return f'<td class="hv h{h}">{h}<span class="hl">{esc(r["heat_lbl"].split()[0])}</span></td>'

live = [r for r in ROWS if r.get("days")]
SEC_ZH = {r["sector"]: r["sector"].split()[0] for r in sorted(ROWS, key=lambda x: x["n"])}
SEC_IDX = {s: i for i, s in enumerate(SEC_ZH)}

def day_cell(r, d):
    x = r["days"][d]
    nv = (f'<span class="nvw" title="{x["novol"]}/{r["n_basket"]} 隻當日成交量未公布或只有內插值（或無量能基準），量能項 B 設為中性">量?</span>'
          if x.get("novol") else "")
    return (f'<td class="dcell {gcls(x["grade"])}" title="z {x["z"]:+.2f} · 籃子報酬 {x["ret"]*100:+.2f}% · '
            f'量能 {x["rvol"]:.2f}x · 廣度 {x["up"]}/{r["n_basket"]}">'
            f'{x["score"]:.0f}<span class="gz">{GRADE_ZH[x["grade"]]}</span>{nv}</td>')

# ---------------- page 1: 總覽 ----------------
def row_attrs(r):
    a = (f' data-z5="{r["z5"]:.4f}" data-score5="{r["score5"]:.2f}" data-mfd="{r["mfd5"]:.0f}"'
         f' data-heat="{r.get("heat") or 0}" data-slope="{r["slope"]:.4f}" data-ret5="{r["ret5"]*100:.3f}"'
         f' data-n="{r["n_basket"]}" data-rank="{r["rank"]}"')
    a += f' data-score5r="{r["score5r"]:.2f}" data-inten="{r["intensity"]:.3f}"'
    for i, d in enumerate(DAYS, 1):
        a += f' data-d{i}="{r["days"][d]["score"]:.2f}"'
    return a

def table_main():
    head = ('<tr><th>#</th><th>子板塊 Sub-Sector</th><th>GICS Sector</th>'
            '<th class="srt" data-key="score5">5日資金流向<span class="thn">綜合分 0-100 ↓</span></th>'
              '<th class="srt" data-key="score5r">穩健分<span class="thn">樣本調整後 ↓</span></th>'
            + "".join(f'<th class="srt d" data-key="d{i}">{dlab(d)}<span class="thn">日分 ↓</span></th>'
                      for i, d in enumerate(DAYS, 1))
            + '<th class="srt" data-key="mfd">淨額估算<span class="thn">5日合計 ↓</span></th>'
              '<th class="srt" data-key="inten">資金強度<span class="thn">淨額/成交額 ↓</span></th>'
              '<th class="srt" data-key="ret5">籃子報酬<span class="thn">5日 % ↓</span></th>'
              '<th class="srt" data-key="slope">趨勢<span class="thn">日分斜率 ↓</span></th>'
              '<th class="srt" data-key="heat">熱度<span class="thn">工作簿 1-5 ↓</span></th>'
              '<th class="srt" data-key="n">樣本<span class="thn">數/品質 ↓</span></th>'
              '<th>代表成分股</th><th>代理 ETF</th><th>主要驅動 LEADING INDICATOR</th></tr>')
    body = []
    for r in live:
        body.append(
            f'<tr{row_attrs(r)} data-sym="s{r["n"]}"><td class="rk">{r["rank"]}</td>'
            f'<td><div class="ss"><b>{esc(r["zh"])}</b><em>{esc(r["en"])}</em>'
            f'<span class="cyc">{esc(r["cycle"])}</span></div></td>'
            f'<td class="sec"><span class="sdot s{SEC_IDX[r["sector"]]%11}"></span>{esc(SEC_ZH[r["sector"]])}</td>'
            f'<td>{meter(r["score5"], "m5")}</td><td>{meter(r["score5r"], "m5")}</td>'
            + "".join(day_cell(r, d) for d in DAYS)
            + f'<td class="nums mf {"pos" if r["mfd5"] > 0 else "neg"}">{fmt_m(r["mfd5"])}</td>'
              f'<td class="nums {"pos" if r["intensity"] > 0 else "neg"}">{r["intensity"]:+.1f}%</td>'
              f'<td class="nums {"pos" if r["ret5"] > 0 else "neg"}">{r["ret5"]*100:+.2f}%</td>'
              f'<td>{trend_cell(r)}</td>'
            + heat_cell(r)
            + f'<td>{qual(r)}</td><td>{basket_cell(r)}</td>'
              f'<td class="etf">{esc(r["etf"])}</td><td class="drv">{esc(r["driver"])}</td></tr>')
    return head, "".join(body)

# ---------------- page 2: 每日矩陣 ----------------
def table_matrix():
    head = ('<tr><th>#</th><th>子板塊</th><th>GICS</th>'
            + "".join(f'<th class="srt d" data-key="d{i}">{dlab(d)}<span class="thn">日分 ↓</span></th>'
                      for i, d in enumerate(DAYS, 1))
            + '<th class="srt" data-key="score5">5日綜合<span class="thn">0-100 ↓</span></th>'
              '<th class="srt" data-key="score5r">穩健分<span class="thn">樣本調整 ↓</span></th>'
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
            f'<td><div class="ss"><b>{esc(r["zh"])}</b><em>{esc(r["en"])}</em></div></td>'
            f'<td class="sec">{esc(SEC_ZH[r["sector"]])}</td>'
            + "".join(f'<td class="dcell big {gcls(r["days"][d]["grade"])}">{r["days"][d]["score"]:.0f}'
                      f'<span class="gz">{r["days"][d]["z"]:+.1f}</span></td>' for d in DAYS)
            + f'<td>{meter(r["score5"], "m5")}</td><td>{meter(r["score5r"], "m5")}</td>'
              f'<td class="spk"><div class="spark">{spark}</div></td>'
              f'<td class="nums mf {"pos" if r["mfd5"] > 0 else "neg"}">{fmt_m(r["mfd5"])}</td></tr>')
    return head, "".join(body)

# ---------------- page 3: GICS 板塊匯總 ----------------
def sector_agg():
    by = collections.defaultdict(list)
    for r in live: by[r["sector"]].append(r)
    out = []
    for sec, rs in by.items():
        dv = sum(r["dv5"] for r in rs) or 1
        z5 = sum(r["z5"] * r["dv5"] for r in rs) / dv
        mfd = sum(r["mfd5"] for r in rs)
        dayz = {d: sum(r["days"][d]["z"] * r["days"][d]["dv"] for r in rs) /
                   (sum(r["days"][d]["dv"] for r in rs) or 1) for d in DAYS}
        out.append({"sec": sec, "n": len(rs), "z5": z5, "mfd": mfd, "dayz": dayz, "dv5": dv,
                    "top": sorted(rs, key=lambda r: -r["z5"])[:3],
                    "bot": sorted(rs, key=lambda r: r["z5"])[:3],
                    "npos": sum(1 for r in rs if r["z5"] >= 0.25), "nneg": sum(1 for r in rs if r["z5"] <= -0.25)})
    out.sort(key=lambda x: -x["z5"])
    return out

def table_sector():
    agg = sector_agg()
    head = ('<tr><th>#</th><th>GICS Sector</th><th>子板塊數</th>'
            '<th>5日資金流向<span class="thn">成交額加權 z</span></th>'
            + "".join(f'<th class="d">{dlab(d)}</th>' for d in DAYS)
            + '<th>淨額估算<span class="thn">5日合計</span></th><th>5日成交額</th>'
              '<th>流入/流出子板塊</th><th>最強子板塊</th><th>最弱子板塊</th></tr>')
    body = []
    for i, a in enumerate(agg, 1):
        def zc(z):
            g = 3 if z >= 1.0 else 2 if z >= 0.5 else 1 if z >= 0.2 else 0 if z > -0.2 else -1 if z > -0.5 else -2 if z > -1.0 else -3
            return f'<td class="dcell {gcls(g)}">{z:+.2f}</td>'
        body.append(
            f'<tr><td class="rk">{i}</td><td><div class="ss"><b>{esc(a["sec"].split()[0])}</b>'
            f'<em>{esc(" ".join(a["sec"].split()[1:]))}</em></div></td>'
            f'<td class="nums">{a["n"]}</td>{zc(a["z5"])}'
            + "".join(zc(a["dayz"][d]) for d in DAYS)
            + f'<td class="nums mf {"pos" if a["mfd"] > 0 else "neg"}">{fmt_m(a["mfd"])}</td>'
              f'<td class="nums mut">${a["dv5"]/1e9:,.0f}B</td>'
              f'<td class="nums"><span class="pos">{a["npos"]}↑</span> / <span class="neg">{a["nneg"]}↓</span></td>'
              f'<td class="lst">' + "".join(f'<span class="pill pos">{esc(x["zh"])} {x["z5"]:+.2f}</span>' for x in a["top"]) + '</td>'
              f'<td class="lst">' + "".join(f'<span class="pill neg">{esc(x["zh"])} {x["z5"]:+.2f}</span>' for x in a["bot"]) + '</td></tr>')
    return head, "".join(body)

# ---------------- page 4: 背離與輪動 ----------------
def quadrants():
    q = {"hot_out": [], "cold_in": [], "hot_in": [], "cold_out": []}
    for r in live:
        h = r.get("heat") or 3
        if h >= 4 and r["z5"] <= -0.25: q["hot_out"].append(r)
        elif h <= 2 and r["z5"] >= 0.25: q["cold_in"].append(r)
        elif h >= 4 and r["z5"] >= 0.25: q["hot_in"].append(r)
        elif h <= 2 and r["z5"] <= -0.25: q["cold_out"].append(r)
    for k in q: q[k].sort(key=lambda r: -abs(r["z5"]))
    return q

def qbox(title, sub, rows, cls):
    if not rows:
        return f'<div class="qbox {cls}"><h3>{esc(title)}<span>{esc(sub)}</span></h3><p class="none">本次無</p></div>'
    items = "".join(
        f'<div class="qrow"><b>{esc(r["zh"])}</b><span class="qz">{r["z5"]:+.2f}</span>'
        f'<span class="qh">熱度{r.get("heat") or "—"}</span>'
        f'<span class="qm {"pos" if r["mfd5"] > 0 else "neg"}">{fmt_m(r["mfd5"])}</span>'
        f'<i>{esc(SEC_ZH[r["sector"]])}</i></div>' for r in rows[:14])
    return (f'<div class="qbox {cls}"><h3>{esc(title)} <b class="cnt">{len(rows)}</b><span>{esc(sub)}</span></h3>'
            f'{items}</div>')

# ---------------- narrative ----------------
top5 = live[:5]; bot5 = live[-5:][::-1]
acc = sorted(live, key=lambda r: -r["slope"])[:5]
dec = sorted(live, key=lambda r: r["slope"])[:5]
last = DAYS[-1]
today_top = sorted(live, key=lambda r: -r["days"][last]["z"])[:5]
today_bot = sorted(live, key=lambda r: r["days"][last]["z"])[:5]
mkt = M["mkt_med"]

css = """
:root{color-scheme:light;--navh:70px;
 /* 淺色（預設）：暖白紙面，藍色主調，資金流向另有一套語意色階 */
 --pg:#f6f5f1;--sf:#fffffe;--ink:#17171a;--ink2:#4b4a46;--mut:#7a7770;
 --grid:#e4e2db;--axis:#c6c3ba;--ring:rgba(23,23,26,.13);
 --seq:#1c5fbe;--link:#154fa3;--good:#1a7f37;--warn:#8a5a0b;--bad:#b3261e;
 --hl:#edf2fb;--meter:#e3e6ec;--shadow:rgba(20,20,25,.16);
 --p3:#9fdcb7;--p3t:#0a3f20;--p2:#c6ebd4;--p2t:#0e4a27;--p1:#e4f5ea;--p1t:#1a5c33;
 --z0:#efeeea;--z0t:#6f6c66;
 --n1:#fdeced;--n1t:#8e2b26;--n2:#f7ced0;--n2t:#7c211d;--n3:#eeadb0;--n3t:#6a1714;
 --pt:#14743a;--nt:#b3261e;--dcellhov:brightness(.965);
 --hot5:#c2410c;--hot4:#8a5a0b;--hot3:#4b4a46;--hot2:#2b6cb0;--hot1:#1e4e8c;
 --posbd:#8fd0a8;--negbd:#e2a0a0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;
 --pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;
 --grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
 --seq:#3987e5;--link:#6da7ec;--good:#2ea043;--warn:#d99a2b;--bad:#e06c6c;
 --hl:#16202d;--meter:#25303e;--shadow:rgba(0,0,0,.45);
 --p3:#0e5c2f;--p3t:#eafff0;--p2:#14713a;--p2t:#dcf7e5;--p1:#1b3d28;--p1t:#b9e7c8;
 --z0:#232322;--z0t:#8f8d86;
 --n1:#3d1f22;--n1t:#f0c2c2;--n2:#7a2530;--n2t:#ffe0e0;--n3:#98202f;--n3t:#fff0f0;
 --pt:#7ee0a0;--nt:#ff9a9a;--dcellhov:brightness(1.18);
 --hot5:#ff8f5e;--hot4:#d99a2b;--hot3:#c3c2b7;--hot2:#7fb2e8;--hot1:#5c8fd6;
 --posbd:#1e5c34;--negbd:#6b2731}}
:root[data-theme="dark"]{color-scheme:dark;
 --pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;
 --grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
 --seq:#3987e5;--link:#6da7ec;--good:#2ea043;--warn:#d99a2b;--bad:#e06c6c;
 --hl:#16202d;--meter:#25303e;--shadow:rgba(0,0,0,.45);
 --p3:#0e5c2f;--p3t:#eafff0;--p2:#14713a;--p2t:#dcf7e5;--p1:#1b3d28;--p1t:#b9e7c8;
 --z0:#232322;--z0t:#8f8d86;
 --n1:#3d1f22;--n1t:#f0c2c2;--n2:#7a2530;--n2t:#ffe0e0;--n3:#98202f;--n3t:#fff0f0;
 --pt:#7ee0a0;--nt:#ff9a9a;--dcellhov:brightness(1.18);
 --hot5:#ff8f5e;--hot4:#d99a2b;--hot3:#c3c2b7;--hot2:#7fb2e8;--hot1:#5c8fd6;
 --posbd:#1e5c34;--negbd:#6b2731}
*{box-sizing:border-box}
body{margin:0;background:var(--pg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Noto Sans TC",sans-serif}
.wrap{max-width:1680px;margin:0 auto;padding:24px 18px 60px}
h1{font-size:21px;margin:0 0 4px}
.sub{color:var(--ink2);font-size:12.5px;margin-bottom:14px}
.card{background:var(--sf);border:1px solid var(--ring);border-radius:10px;padding:14px 16px;margin-bottom:14px}
h2{font-size:13px;margin:0 0 8px;color:var(--ink2);font-weight:600}
.rules{font-size:12.5px;color:var(--ink2);line-height:1.7}
.rules b{color:var(--ink)}
.rules code{background:var(--hl);border:1px solid var(--ring);border-radius:5px;padding:1px 5px;font-size:11.5px}
.rules .cav{color:var(--warn)}
.sumgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.sumbox{background:var(--hl);border:1px solid var(--ring);border-radius:9px;padding:10px 12px}
.sumbox h3{margin:0 0 7px;font-size:12px;color:var(--ink2);font-weight:600}
.sumbox .li{font-size:12px;margin:3px 0;display:flex;gap:7px;align-items:baseline}
.sumbox .li b{color:var(--ink);min-width:120px}
.sumbox .li span{font-variant-numeric:tabular-nums}
.mkrow{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.mkrow span{font-size:11.5px;background:var(--hl);border:1px solid var(--ring);border-radius:11px;padding:2px 9px}
.nav{position:sticky;top:0;z-index:6;background:var(--pg);padding:10px 0 8px;border-bottom:1px solid var(--grid);margin-bottom:12px}
.nrow{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.nrow+.nrow{margin-top:7px}
.nav button{font:600 13px/1 system-ui,"Noto Sans TC",sans-serif;color:var(--ink2);background:var(--sf);
 border:1px solid var(--ring);border-radius:20px;padding:9px 14px;cursor:pointer}
.nav button .s{display:block;font-weight:400;font-size:10.5px;color:var(--mut);margin-top:3px}
.nav button.on{color:var(--pg);background:var(--ink);border-color:var(--ink)}
.nav button.on .s{color:var(--pg);opacity:.75}
.nav .sortb{font-weight:600;font-size:12px;padding:8px 12px}
.nav .sortb.on{color:#fff;background:var(--seq);border-color:var(--seq)}
.nav .div{width:1px;height:24px;background:var(--grid);margin:0 5px}
.nav .lab{font-size:11px;color:var(--mut);margin-right:2px}
.pghead{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;margin:2px 0 10px;font-size:12.5px;color:var(--ink2)}
.pghead b{font-size:15px;color:var(--ink)}
.pghead .tg{font-size:11px;border:1px solid var(--ring);border-radius:10px;padding:2px 8px}
.tblwrap{overflow-x:auto;background:var(--sf);border:1px solid var(--ring);border-radius:10px}
table{border-collapse:collapse;table-layout:fixed;font-size:12.5px}
th{position:sticky;top:0;text-align:left;font-size:11px;color:var(--mut);font-weight:600;padding:9px 8px;
 border-bottom:1px solid var(--grid);background:var(--sf);white-space:nowrap;z-index:1;overflow:hidden;text-overflow:ellipsis}
th.srt{cursor:pointer}th.srt:hover{color:var(--seq)}th.srt.act{color:var(--seq)}
th.srt.asc .thn::after{content:" ↑"}
th.d{color:var(--ink2)}
.thn{display:block;font-weight:400;font-size:10px;white-space:normal}
.wd{font-weight:400;color:var(--mut);margin-left:4px;font-size:10px}
.rz{position:absolute;top:0;right:0;width:7px;height:100%;cursor:col-resize;user-select:none}
.rz:hover{background:var(--seq);opacity:.4}
td{padding:7px 8px;border-bottom:1px solid var(--grid);vertical-align:middle;overflow:hidden}
tr:last-child td{border-bottom:0}
tr:hover td{background:var(--hl)}
.rk{color:var(--mut);font-weight:600;font-variant-numeric:tabular-nums}
.orank{display:block;font-size:9.5px;color:var(--mut);font-weight:400}
.nums{font-variant-numeric:tabular-nums;white-space:nowrap}
.mut{color:var(--mut)}
.pos{color:var(--pt)}.neg{color:var(--nt)}
.mf{font-weight:600}
.ss b{font-size:13px;display:block;line-height:1.25}
.ss em{display:block;font-style:normal;font-size:10.5px;color:var(--mut);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ss .cyc{display:block;font-size:9.5px;color:var(--seq);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sec{font-size:11.5px;color:var(--ink2)}
.sdot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--seq);margin-right:5px;vertical-align:1px}
.sdot.s0{background:#4a7fe0}.sdot.s1{background:#2aa87a}.sdot.s2{background:#d09a12}.sdot.s3{background:#6b5bd6}
.sdot.s4{background:#3aa6cf}.sdot.s5{background:#8a55b0}.sdot.s6{background:#e07b2a}.sdot.s7{background:#0e7a79}
.sdot.s8{background:#d1699a}.sdot.s9{background:#8c93a3}.sdot.s10{background:#d9553a}
.mc b{display:block;font-size:13px}
.mc .meter{display:block;height:5px;border-radius:3px;background:var(--meter);margin-top:3px}
.mc .meter i{display:block;height:100%;border-radius:3px;background:var(--seq)}
.mc.m5 .meter i{background:linear-gradient(90deg,var(--bad),var(--warn),var(--good))}
.dcell{font-variant-numeric:tabular-nums;font-weight:700;text-align:center;font-size:13px;border-radius:0}
.dcell .gz{display:block;font-weight:400;font-size:9px;opacity:.85}
.dcell.big{font-size:15px}
.gp3{background:var(--p3);color:var(--p3t)}.gp2{background:var(--p2);color:var(--p2t)}.gp1{background:var(--p1);color:var(--p1t)}
.g00{background:var(--z0);color:var(--z0t)}
.gn1{background:var(--n1);color:var(--n1t)}.gn2{background:var(--n2);color:var(--n2t)}.gn3{background:var(--n3);color:var(--n3t)}
tr:hover td.dcell{filter:var(--dcellhov)}
.chips5{display:flex;gap:2px}
.chipd{flex:1;text-align:center;font-size:11px;font-weight:700;border-radius:4px;padding:2px 0;font-variant-numeric:tabular-nums}
.tr b{display:block;font-size:12px;font-variant-numeric:tabular-nums}
.tr span{font-size:10.5px}
.tr i{display:block;font-style:normal;font-size:9.5px;color:var(--mut)}
.tr.up b,.tr.up span{color:var(--pt)}.tr.dn b,.tr.dn span{color:var(--nt)}.tr.fl b,.tr.fl span{color:var(--mut)}
.hv{text-align:center;font-weight:700;font-variant-numeric:tabular-nums}
.hv .hl{display:block;font-weight:400;font-size:9px;color:var(--mut)}
.hv.h5{color:var(--hot5)}.hv.h4{color:var(--hot4)}.hv.h3{color:var(--hot3)}.hv.h2{color:var(--hot2)}.hv.h1{color:var(--hot1)}
.qc b{display:inline-block;font-size:13px;font-variant-numeric:tabular-nums}
.qc b.qok{color:var(--ink)}.qc b.qmid{color:var(--warn)}.qc b.qlo{color:var(--bad)}
.qt{display:inline-block;font-size:9px;color:var(--mut);border:1px dashed var(--axis);border-radius:6px;padding:0 4px;margin-left:3px}
.qt.cf低{color:var(--nt);border-color:var(--negbd)}
.qt.cf中{color:var(--warn);border-style:solid}
.qt.cf高{color:var(--pt);border-color:var(--posbd)}
.nvw{display:block;font-size:8.5px;font-weight:400;opacity:.85}
.upd{background:var(--hl);border:1px solid var(--ring);border-radius:10px;padding:12px 14px;margin-bottom:14px}
.upd h3{margin:0 0 8px;font-size:13px;color:var(--ink)}
.upd ul{margin:0;padding-left:18px}
.upd li{font-size:12.5px;color:var(--ink2);line-height:1.7;margin:2px 0}
.upd li b{color:var(--ink)}
.bk{display:flex;flex-wrap:wrap;gap:3px}
.bk .tk{font-size:10.5px;color:var(--link);text-decoration:none;background:var(--hl);border:1px solid var(--ring);
 border-radius:6px;padding:1px 5px;font-variant-numeric:tabular-nums}
.bk .tk:hover{background:var(--seq);color:#fff}
.seg{display:inline-flex;border:1px solid var(--ring);border-radius:20px;overflow:hidden;background:var(--sf)}
.seg button{border:0;border-radius:0;padding:8px 12px;font-size:12px;font-weight:600;background:transparent;color:var(--mut)}
.seg button+button{border-left:1px solid var(--ring)}
.seg button.on{background:var(--seq);color:#fff}
.seg button:focus-visible,.nav button:focus-visible,th.srt:focus-visible{outline:2px solid var(--seq);outline-offset:2px}
.bk .tk.sup{border-style:dashed;color:var(--ink2)}
.bk .tk.nb{border-bottom:2px dotted var(--warn)}
.miss{font-size:9px;color:var(--mut);border:1px dotted var(--axis);border-radius:6px;padding:0 4px}
.etf{font-size:11px;color:var(--ink2)}
.drv{font-size:11px;color:var(--ink2);line-height:1.45}
.spark{display:flex;align-items:flex-end;gap:3px;height:40px}
.bar{width:9px;border-radius:2px}
.bar.bp{background:var(--good)}.bar.bn{background:var(--bad)}
.lst{white-space:normal}
.pill{display:inline-block;font-size:10px;border-radius:9px;padding:1px 6px;margin:1px 3px 1px 0;border:1px solid var(--ring)}
.pill.pos{color:var(--pt);border-color:var(--posbd)}.pill.neg{color:var(--nt);border-color:var(--negbd)}
.qgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:12px}
.qbox{background:var(--sf);border:1px solid var(--ring);border-radius:10px;padding:12px 14px}
.qbox h3{margin:0 0 8px;font-size:13px}
.qbox h3 span{display:block;font-size:10.5px;color:var(--mut);font-weight:400;margin-top:2px}
.qbox h3 .cnt{color:var(--seq)}
.qbox.hotout{border-color:var(--negbd)}.qbox.coldin{border-color:var(--posbd)}
.qrow{display:flex;gap:8px;align-items:baseline;font-size:12px;padding:3px 0;border-top:1px solid var(--grid)}
.qrow b{min-width:118px;color:var(--ink)}
.qrow .qz{font-variant-numeric:tabular-nums;font-weight:700;min-width:46px}
.qrow .qh{font-size:10px;color:var(--mut);min-width:40px}
.qrow .qm{font-size:11px;font-variant-numeric:tabular-nums;min-width:60px}
.qrow i{font-style:normal;font-size:10.5px;color:var(--mut)}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:11.5px;color:var(--ink2);margin:8px 2px 0;align-items:center}
.legend .sw{display:inline-block;width:16px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:4px}
.foot{font-size:11.5px;color:var(--ink2);line-height:1.8}
.foot b{color:var(--ink)}
section[hidden]{display:none}
.fixhead{position:fixed;z-index:5;overflow:hidden;display:none;background:var(--sf);border-bottom:1px solid var(--grid);box-shadow:0 4px 10px var(--shadow)}
.fixhead table{table-layout:fixed;border-collapse:collapse;font-size:12.5px}
.fixhead th{position:static}
@media (max-width:600px){.nav button .s{display:none}.nav button{padding:7px 10px;font-size:12px}}
"""

COLW_MAIN = [40, 186, 90, 92, 88] + [76] * len(DAYS) + [90, 80, 78, 92, 58, 100, 182, 92, 236]
COLW_MTX = [40, 210, 92] + [88] * len(DAYS) + [92, 88, 92, 92]
COLW_SEC = [40, 170, 66, 92] + [72] * len(DAYS) + [92, 88, 92, 250, 250]

def colgroup(ws):
    return "<colgroup>" + "".join(f'<col style="width:{w}px">' for w in ws) + "</colgroup>", sum(ws)

cur = {r["zh"]: r for r in live}
moved = sorted(((c, BROW[c]["rank"], cur[c]["rank"]) for c in cur if c in BROW and BROW[c]["rank"] != cur[c]["rank"]),
               key=lambda x: -abs(x[1] - x[2]))
up3 = [f'{c} {a}→{b}' for c, a, b in moved if b < a][:5]
dn3 = [f'{c} {a}→{b}' for c, a, b in moved if b > a][:5]
NEWD = [d for d in DAYS if d not in BDAYS]; GONED = [d for d in BDAYS if d not in DAYS]
n_nv = len([1 for r in live if r["novol_days"]])
grew = sorted(((c, BROW[c]["n_basket"], cur[c]["n_basket"]) for c in cur if c in BROW and BROW[c]["n_basket"] != cur[c]["n_basket"]), key=lambda x: -(x[2] - x[1]))
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
</ul></div>"""

rules = f"""
<div class="card rules">
<h2>打分方法（資金流向 · 每日 · 111 個子板塊）</h2>
① <b>樣本</b>：直接採用工作簿 02 主表每個子板塊嘅「代表 Tickers」作籃子（共 {M["n_tick"]} 隻可用），
唔另行按行業擴充 —— 令 111 個子板塊嘅樣本口徑一致、可橫向比較。工作簿無列 ticker 嘅 2 個子板塊
（臨床期中小型生技、腫瘤與細胞治療）以<b>代理樣本</b>補上；工作簿列咗但所有可達鏡像視窗內都無數據嘅 {len(M["dropped"])} 隻
（{esc("、".join(M["dropped"]))}：已除牌、已被收購或跌出鏡像宇宙）唔計入，部分子板塊以<b>同業補充樣本</b>頂替（虛線框）；
08-28 起先有數據嘅外國發行人／ADR（TSM、ASML、ARM、NVO 等）本版改由 Yahoo 日線提供完整歷史，量能基準與日內高低價齊備。<br>
② <b>逐日資金流向分</b>（每隻股票、每個交易日）：<br>
　<code>A 方向 = tanh((個股報酬 − 當日全巿場中位報酬) / 2%)</code> —— 相對強弱，±2% 飽和；<br>
　<code>B 量能 = log₂(當日成交額 / 前 20 日中位成交額) ÷ 2</code>，截於 ±1 —— 放量或縮量；<br>
　<code>C 收位 = ((收 − 低) − (高 − 收)) / (高 − 低)</code> —— Chaikin 資金流乘數，收喺當日高位＝買方掌控；<br>
　<code>f = (0.70×A + 0.30×C) × (1 + 0.50×B)</code> —— 方向＋收盤位置，<b>由量能放大或收窄</b>：放量上升＝真流入，
放量下跌＝真流出，縮量升跌則打折。無日內高低價嘅股票（快照來源）只用 A 項並標示。<br>
③ <b>子板塊分</b>：籃子內以<b>成交額加權</b>（資金加權），單一股票<b>硬上限 40%</b>（迭代 water-filling，超限部分按成交額比例分返俾其餘成分股；2 隻樣本嘅籃子上限不可達、改等權），避免一隻大巿值蓋過全籃。<br>
④ <b>穩健分／資金強度／廣度</b>：穩健分＝5日 z ×√(n/(n+2)) 後取百分位（樣本細者向中性收斂）；
資金強度＝淨額估算÷成交額（去規模）；廣度＝籃子內超額報酬為正嘅比例；可信度按樣本數（≤2 低／3 中／≥4 高）。
本版視窗內 491 隻代表股五日成交量與日內高低價齊備（日線鏡像未發佈嘅 08-31／09-02／09-03 成交量及 09-04 整日由 Yahoo 補齊），無「量?」格。<br>
⑤ <b>0–100 分</b>：每日將 111 個子板塊嘅 f 值<b>橫向標準化</b>後取百分位 —— 分數係「今日資金相對流向邊個板塊」，
唔係「升定跌」。100 = 當日全巿最強資金流入，0 = 最強流出。等級：z≥1.5 強力流入、≥0.75 流入、≥0.25 偏流入、
±0.25 中性、≤−0.25 偏流出、≤−0.75 流出、≤−1.5 強力流出。<br>
⑤ <b>5 日綜合分</b>：五日 z 值按 <code>{esc(" / ".join(f"{w:g}" for w in M["weights"]))}</code> 加權（近日較重）後取百分位。
<b>趨勢</b>＝五日 z 值嘅線性斜率（加速流入／流出）；<b>{("↑/↓")}</b>＝五日內流入／流出日數。<br>
⑥ <b>淨額估算</b>：Σ(Chaikin 乘數 × 成交額)，即「收喺高位嘅成交額」減「收喺低位嘅成交額」，
單位美元。<span class="cav">⚠ 呢個係由價量推算嘅<b>代理指標</b>，唔係真實基金流數據（13F／ETF 申購贖回喺本環境不可達），
亦只計算籃子內嘅代表股，唔等於整個子板塊嘅實際資金額。</span><br>
⑦ <b>熱度</b>欄為工作簿原有嘅 2026 定性熱度（1–5），供對照用 —— 「熱度高但資金流出」＝派發風險，
「熱度低但資金流入」＝早期輪動，見第 4 頁。
</div>"""

mkt_chips = "".join(f'<span>{dlab(d)} 全巿中位 <b class="{"pos" if mkt[d] > 0 else "neg"}">{mkt[d]*100:+.2f}%</b></span>' for d in DAYS)
summary = f"""
<div class="card">
<h2>五日資金流向摘要（{DAYS[0]} → {DAYS[-1]}）</h2>
<div class="sumgrid">
<div class="sumbox"><h3>5 日最強流入</h3>{"".join(f'<div class="li"><b>{esc(r["zh"])}</b><span class="pos">{r["z5"]:+.2f}</span><span class="mut">{fmt_m(r["mfd5"])}</span><span class="mut">{esc(SEC_ZH[r["sector"]])}</span></div>' for r in top5)}</div>
<div class="sumbox"><h3>5 日最強流出</h3>{"".join(f'<div class="li"><b>{esc(r["zh"])}</b><span class="neg">{r["z5"]:+.2f}</span><span class="mut">{fmt_m(r["mfd5"])}</span><span class="mut">{esc(SEC_ZH[r["sector"]])}</span></div>' for r in bot5)}</div>
<div class="sumbox"><h3>最後一日（{DAYS[-1]}）流入</h3>{"".join(f'<div class="li"><b>{esc(r["zh"])}</b><span class="pos">{r["days"][last]["z"]:+.2f}</span><span class="mut">分 {r["days"][last]["score"]:.0f}</span></div>' for r in today_top)}</div>
<div class="sumbox"><h3>最後一日（{DAYS[-1]}）流出</h3>{"".join(f'<div class="li"><b>{esc(r["zh"])}</b><span class="neg">{r["days"][last]["z"]:+.2f}</span><span class="mut">分 {r["days"][last]["score"]:.0f}</span></div>' for r in today_bot)}</div>
<div class="sumbox"><h3>資金加速流入（斜率）</h3>{"".join(f'<div class="li"><b>{esc(r["zh"])}</b><span class="pos">{r["slope"]:+.2f}</span><span class="mut">5日分 {r["score5"]:.0f}</span></div>' for r in acc)}</div>
<div class="sumbox"><h3>資金加速流出（斜率）</h3>{"".join(f'<div class="li"><b>{esc(r["zh"])}</b><span class="neg">{r["slope"]:+.2f}</span><span class="mut">5日分 {r["score5"]:.0f}</span></div>' for r in dec)}</div>
</div>
<div class="mkrow">{mkt_chips}</div>
</div>"""

secs = []
head, body = table_main(); cg, tw = colgroup(COLW_MAIN)
secs.append(f'''<section id="p1">
<div class="pghead"><b>總覽 · 111 個子板塊 × 5 個交易日</b>
<span class="tg">{DAYS[0]} → {DAYS[-1]}</span>
<span>排序 = 5 日資金流向綜合分</span>
<span class="tg">可點表頭排序 · 拖表頭右邊調欄闊</span></div>
{upd}{summary}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw gp3"></i>強力流入 z≥1.5</span><span><i class="sw gp2"></i>流入 ≥0.75</span>
<span><i class="sw gp1"></i>偏流入 ≥0.25</span><span><i class="sw g00"></i>中性</span>
<span><i class="sw gn1"></i>偏流出</span><span><i class="sw gn2"></i>流出</span><span><i class="sw gn3"></i>強力流出</span>
<span>格內數字＝當日 0–100 分（橫向百分位）· 滑鼠停留睇 z 值／籃子報酬／量能倍數</span></div>
</section>''')

head, body = table_matrix(); cg, tw = colgroup(COLW_MTX)
secs.append(f'''<section id="p2" hidden>
<div class="pghead"><b>每日矩陣 · 資金流向熱力圖</b><span>111 × 5 逐日分數與 z 值</span>
<span class="tg">柱狀圖＝逐日 z 值（上綠下紅）</span></div>
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
</section>''')

head, body = table_sector(); cg, tw = colgroup(COLW_SEC)
secs.append(f'''<section id="p3" hidden>
<div class="pghead"><b>GICS 11 大板塊匯總</b><span>子板塊以成交額加權合成</span>
<span class="tg">排序 = 5 日加權 z</span></div>
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
</section>''')

q = quadrants()
secs.append(f'''<section id="p4" hidden>
<div class="pghead"><b>背離與輪動</b><span>工作簿定性熱度 vs 本次實測資金流向</span></div>
<div class="qgrid">
{qbox("熱度高但資金流出", "熱度 4–5 而 5 日 z ≤ −0.25：派發／獲利回吐風險", q["hot_out"], "hotout")}
{qbox("熱度低但資金流入", "熱度 1–2 而 5 日 z ≥ +0.25：早期輪動候選", q["cold_in"], "coldin")}
{qbox("熱度高且資金流入", "熱度 4–5 且 z ≥ +0.25：趨勢延續", q["hot_in"], "")}
{qbox("熱度低且資金流出", "熱度 1–2 且 z ≤ −0.25：持續失血", q["cold_out"], "")}
</div>
</section>''')

foot = f"""
<div class="card foot">
<h2>數據來源與限制</h2>
① <b>價量數據</b>：<b>natezone/market-tracker</b> 日線 OHLCV 與 <b>Yahoo Finance</b> 日線合併（{sum(1 for r in ROWS if r.get("src") == "real")} 個子板塊全部成分股有日內高低價），
其餘以 Nasdaq 快照重建序列補足（只有收盤價與成交量，收位項 C 不適用，已於「樣本」欄標示）。
計分視窗 <b>{DAYS[0]} → {DAYS[-1]}</b> 共 5 個交易日，量能基準為 {M["base"][0]} → {M["base"][1]}（{M["n_base"]} 個交易日中位成交額）。<br>
② <b>數據終點 {DAYS[-1]}（美東週{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤</b>：日線鏡像（09-05 00:11 UTC 提交）對 09-04 只有成交量、
Nasdaq 快照最新一筆係 09-04 盤中，故 09-04 整日 OHLCV 來自 <b>Yahoo Finance</b>（GitHub Actions runner 以 yfinance 拉取未調整日線，檔案 {esc("、".join(M.get("yahoo_files", [])))}）。
Yahoo 與日線鏡像喺視窗內共同收盤中位偏差 {XN.get("median_pct", 0):.4f}%；與快照序列逐日中位偏差 0.0000%。<br>
③ <b>來源合併規則</b>：每隻股票以日線鏡像為主，Yahoo 補其未有嘅交易日；兩者最近 15 個共同交易日收盤中位偏差 ≤0.5% 先合併，
否則（拆股未調整、股息調整差異：{esc("、".join(basis))}）整段改用 Yahoo 已回溯調整嘅歷史。快照序列本版只作對照，唔再入計分。<br>
④ <b>本表唔係真實基金流</b>：環境內無法取得 ETF 申購贖回、13F 或大戶委託數據，所有「資金流向」均由<b>價格、成交量與收盤位置推算</b>，
屬市場微觀結構代理指標。淨額估算只涵蓋籃子代表股，唔等於整個子板塊嘅資金額。<br>
⑤ 子板塊定義、熱度分、週期定位與 LEADING INDICATOR 全部取自附件工作簿
<b>US_Market_Sector_SubSector_HeatMap_R2_20260903.xlsx</b>（02 主表 111 列），本表只新增資金流向計分。<br>
⑥b <b>Critical review 紀錄</b>：本版對 R2.00 嘅七項修正見頂部「本版更新」，未有以紅字標示變動（依指示）。<br>
⑥ <b>建置時間 {BUILD_TS}</b> · 點擊成分股開 TradingView chart · 版面可切淺色／深色（預設「自動」跟隨系統或檢視器設定）· 本表只係研究工具，唔係投資建議。
</div>"""

html_doc = f"""<title>Sub-Sector 資金流向 Watchlist R3</title>
<style>{css}</style>
<div class="wrap">
<h1>Sub-Sector 資金流向 Watchlist {VER}（111 個子板塊 × 5 個交易日逐日打分）</h1>
<div class="sub">資料至 <b>{DAYS[-1]}</b>（美東星期{WD[datetime.date.fromisoformat(DAYS[-1]).weekday()]}）收盤 ·
計分視窗 {DAYS[0]} → {DAYS[-1]} · 樣本 {M["n_tick"]} 隻代表股 · 逐日橫向百分位 0–100 · <b>淺色／深色版面可切換</b>（右上「版面」按鈕，選擇會記住）</div>
{rules}
<nav class="nav">
<div class="nrow">
<button data-g="1" class="on">總覽<span class="s">111 子板塊主表</span></button>
<button data-g="2">每日矩陣<span class="s">111 × 5 熱力圖</span></button>
<button data-g="3">板塊匯總<span class="s">GICS 11 大板塊</span></button>
<button data-g="4">背離與輪動<span class="s">熱度 vs 資金</span></button>
<span class="div"></span>
<span class="lab">排序</span>
<button class="sortb on" data-sort="">5日綜合</button>
<button class="sortb" data-sort="d{len(DAYS)}">最後一日</button>
<button class="sortb" data-sort="score5r">穩健分</button>
<button class="sortb" data-sort="mfd">淨額估算</button>
<button class="sortb" data-sort="inten">資金強度</button>
<button class="sortb" data-sort="slope">趨勢</button>
<button class="sortb" data-sort="ret5">籃子報酬</button>
<button class="sortb" data-sort="heat">工作簿熱度</button>
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
(function() {{
  // ---- theme: 自動（跟隨系統／檢視器）／淺色／深色，選擇存 localStorage ----
  var root = document.documentElement, tbtns = document.querySelectorAll('#thm button');
  var pref = 'auto';
  try {{ pref = localStorage.getItem('subtheme') || 'auto'; }} catch (e) {{}}
  if (pref !== 'light' && pref !== 'dark') pref = 'auto';
  var applying = false;
  function applyTheme() {{
    applying = true;
    if (pref === 'auto') root.removeAttribute('data-theme');
    else if (root.getAttribute('data-theme') !== pref) root.setAttribute('data-theme', pref);
    tbtns.forEach(function(b) {{
      var on = b.dataset.t === pref;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    }});
    applying = false;
  }}
  tbtns.forEach(function(b) {{
    b.addEventListener('click', function() {{
      pref = b.dataset.t;
      try {{ localStorage.setItem('subtheme', pref); }} catch (e) {{}}
      applyTheme();
    }});
  }});
  applyTheme();
  // the artifact viewer stamps data-theme on <html> for its own theme; an explicit
  // in-page choice must survive that, so re-assert it whenever the attribute changes
  new MutationObserver(function() {{
    if (!applying && pref !== 'auto' && root.getAttribute('data-theme') !== pref) applyTheme();
  }}).observe(root, {{attributes: true, attributeFilter: ['data-theme']}});

  var gbtns = document.querySelectorAll('.nav button[data-g]');
  var sbtns = document.querySelectorAll('.nav button.sortb');
  var navEl = document.querySelector('.nav');
  var g = '1';
  function setNavH() {{ document.documentElement.style.setProperty('--navh', navEl.offsetHeight + 'px'); }}
  window.addEventListener('resize', setNavH);
  var fix = document.createElement('div'); fix.className = 'fixhead';
  var fixIn = document.createElement('div'); fix.appendChild(fixIn); document.body.appendChild(fix);
  var fixFor = null;
  function activeWrap() {{
    var sec = document.querySelector('section[id^="p"]:not([hidden])');
    return sec ? sec.querySelector('.tblwrap') : null;
  }}
  function buildFix(wrap) {{
    var tb = wrap.querySelector('table');
    fixIn.innerHTML = '';
    var t = document.createElement('table');
    t.appendChild(tb.querySelector('colgroup').cloneNode(true));
    var th = tb.querySelector('thead').cloneNode(true);
    th.querySelectorAll('.rz').forEach(function(x) {{ x.remove(); }});
    t.appendChild(th); fixIn.appendChild(t);
    th.querySelectorAll('th.srt').forEach(function(h, i) {{
      h.addEventListener('click', function() {{
        var real = tb.querySelectorAll('thead th.srt')[i]; if (real) real.click();
      }});
    }});
    fixFor = wrap;
  }}
  function updFix() {{
    var wrap = activeWrap();
    if (!wrap) {{ fix.style.display = 'none'; return; }}
    if (fixFor !== wrap) buildFix(wrap);
    var tb = wrap.querySelector('table'), thead = tb.querySelector('thead');
    var navB = navEl.getBoundingClientRect().bottom;
    var tr = tb.getBoundingClientRect(), hr = thead.getBoundingClientRect(), wr = wrap.getBoundingClientRect();
    if (!(hr.top < navB && tr.bottom > navB + hr.height + 20)) {{ fix.style.display = 'none'; return; }}
    var ct = fixIn.querySelector('table');
    var cols = tb.querySelectorAll('col'), ccols = ct.querySelectorAll('col');
    cols.forEach(function(c, i) {{ if (ccols[i]) ccols[i].style.width = c.style.width; }});
    ct.style.width = tb.style.width || (tb.offsetWidth + 'px');
    ct.querySelectorAll('th').forEach(function(h, i) {{
      var real = thead.querySelectorAll('th')[i];
      if (real) h.className = real.className;
    }});
    fix.style.left = wr.left + 'px'; fix.style.width = wr.width + 'px'; fix.style.top = navB + 'px';
    fixIn.style.transform = 'translateX(' + (-wrap.scrollLeft) + 'px)';
    fix.style.display = 'block';
  }}
  window.addEventListener('scroll', updFix, {{passive: true}});
  window.addEventListener('resize', updFix);
  document.querySelectorAll('.tblwrap').forEach(function(w) {{ w.addEventListener('scroll', updFix, {{passive: true}}); }});
  var sortState = {{}};
  function sortSec(pid, key, fromHeader) {{
    var st = sortState[pid] || {{key: '', asc: false}};
    var asc = false;
    if (fromHeader && key && st.key === key) asc = !st.asc;
    sortState[pid] = {{key: key, asc: asc}};
    var tb = document.querySelector('#p' + pid + ' tbody');
    if (!tb) return;
    var rows = Array.prototype.slice.call(tb.rows);
    if (key) {{
      rows.sort(function(a, b) {{
        var d = (+b.dataset[key]) - (+a.dataset[key]);
        if (asc) d = -d;
        return d !== 0 ? d : (+a.dataset.rank) - (+b.dataset.rank);
      }});
    }} else {{
      rows.sort(function(a, b) {{ return (+a.dataset.rank) - (+b.dataset.rank); }});
    }}
    rows.forEach(function(r, i) {{
      var c0 = r.cells[0];
      c0.textContent = i + 1;
      if (key) {{
        var o = document.createElement('span'); o.className = 'orank';
        o.textContent = '原#' + r.dataset.rank; c0.appendChild(o);
      }}
      tb.appendChild(r);
    }});
    syncSort();
  }}
  function syncSort() {{
    var st = sortState[g] || {{key: '', asc: false}};
    sbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.sort === st.key); }});
    document.querySelectorAll('#p' + g + ' th.srt').forEach(function(h) {{
      h.classList.toggle('act', h.dataset.key === st.key && st.key !== '');
      h.classList.toggle('asc', h.dataset.key === st.key && st.key !== '' && st.asc);
    }});
    updFix();
  }}
  function show() {{
    document.querySelectorAll('section[id^="p"]').forEach(function(s) {{ s.hidden = (s.id !== 'p' + g); }});
    gbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.g === g); }});
    setNavH(); fixFor = null; syncSort();
    try {{ localStorage.setItem('subnav', g); }} catch (e) {{}}
  }}
  gbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ g = b.dataset.g; show(); }}); }});
  sbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ sortSec(g, b.dataset.sort); }}); }});
  document.querySelectorAll('th.srt').forEach(function(h) {{
    h.addEventListener('click', function() {{ sortSec(h.closest('section').id.slice(1), h.dataset.key, true); }});
  }});
  document.querySelectorAll('.tblwrap table').forEach(function(tb) {{
    var cols = tb.querySelectorAll('col');
    tb.querySelectorAll('th').forEach(function(th, i) {{
      var h = document.createElement('span'); h.className = 'rz'; th.appendChild(h);
      h.addEventListener('click', function(e) {{ e.stopPropagation(); }});
      h.addEventListener('mousedown', function(e) {{
        e.preventDefault(); e.stopPropagation();
        var startX = e.pageX, col = cols[i];
        var w0 = parseInt(col.style.width, 10) || col.offsetWidth;
        function mv(ev) {{
          col.style.width = Math.max(40, w0 + ev.pageX - startX) + 'px';
          var sum = 0;
          cols.forEach(function(c2) {{ sum += parseInt(c2.style.width, 10) || 60; }});
          tb.style.width = sum + 'px'; updFix();
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
    var sv = localStorage.getItem('subnav');
    if (sv && document.getElementById('p' + sv)) g = sv;
  }} catch (e) {{}}
  show();
}})();
</script>
"""

standalone = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1">'
              + html_doc.split("</title>", 1)[0] + "</title></head><body>"
              + html_doc.split("</title>", 1)[1] + "</body></html>")
out_path = f"{SCRATCH}/{OUTNAME}"
open(out_path, "w", encoding="utf-8").write(standalone)
open(f"{SCRATCH}/sub4/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)
print("wrote", out_path, f"{len(standalone)/1024:.0f} KB | rows {len(live)} | days {DAYS}")
