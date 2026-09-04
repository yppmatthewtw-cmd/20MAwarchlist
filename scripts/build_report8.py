#!/usr/bin/env python3
"""Build the R8 report: 12 market-cap-tiered timeframe pages + summary table, dark mode,
with EVERY change relative to the R7 baseline highlighted in red (new rows, rank moves,
changed scores / certainty evidence / bottoms / news / hype, rows removed from each page,
the merger-arbitrage exclusion box, and the updated data-lineage / market-context text)."""
import json, datetime, html, os, sys

SCRATCH = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
O = json.load(open(f"{SCRATCH}/screen_results8.json"))
NEWS = json.load(open(f"{SCRATCH}/news8.json")) if os.path.exists(f"{SCRATCH}/news8.json") else {}
MKT = json.load(open(f"{SCRATCH}/market.json")) if os.path.exists(f"{SCRATCH}/market.json") else None
# ---- R7 baseline (everything that differs from it is painted red) ----
B = json.load(open(f"{SCRATCH}/screen_results7.json"))
BNEWS = json.load(open(f"{SCRATCH}/r8/news7_baseline.json"))
BMKT = json.load(open(f"{SCRATCH}/r8/market7.json")) if os.path.exists(f"{SCRATCH}/r8/market7.json") else None
M = O["meta"]
BM = B["meta"]

now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
WD = "一二三四五六日"[datetime.date.fromisoformat(M["last_date"]).weekday()]
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
OUTNAME = f"20MA_uptrend_watchlistGit_R8.00_claudefable51xhigh_{STAMP}.html"

TF = [("2", "1星期", "10MA · 5個交易日"), ("3", "2星期", "20MA · 10個交易日"),
      ("4", "1個月", "20MA · 21個交易日"), ("5", "2個月", "20MA · 42個交易日")]
TIERS = [("a", "大型股", "Big cap", "≥$10B"), ("b", "中型股", "Mid cap", "$2B–$10B"),
         ("c", "小型股", "Small cap", "<$2B")]
TIER_ZH = {k: zh for k, zh, _, _ in TIERS}
TIER_RANGE = {k: rg for k, _, _, rg in TIERS}

def esc(s): return html.escape(str(s), quote=True)

import re as _re
_SUFFIX = _re.compile(r"\s*(Common Stock|Common Shares?|Ordinary Shares?|Common Units?( representing Limited Partner(ship)? Interests?)?|"
                      r"Class [A-C]( Common Stock)?|Depositary Shares?.*|Shares? of Beneficial Interest|American Depositary Shares?.*|"
                      r"\(.*?\)|Inc\.?|Corporation|Corp\.?|Incorporated|Holdings?|Ltd\.?|plc|N\.V\.|L\.P\.|LP)\s*$", _re.I)
def short_name(n):
    s = n
    for _ in range(3):
        s2 = _SUFFIX.sub("", s).rstrip(" ,.")
        if s2 == s or len(s2) < 5: break
        s = s2
    return s or n

# ---------------- baseline lookups ----------------
BROWS = {pid: {r["sym"]: (i + 1, r) for i, r in enumerate(B["pages"][pid]["rows"])} for pid in BM["page_ids"]}
BP1 = {r["sym"]: (i + 1, r) for i, r in enumerate(B["page1"])}
DEALS = {d["sym"]: d for d in O.get("deal_pinned", [])}
DIAG = M.get("diag", {})
ELIG = set(DIAG.get("eligible", [])); STRUCT = set(DIAG.get("struct", []))
FUNDS = set(M.get("unknown_cap", {}).get("funds", []))
GATED = set(DIAG.get("undercut_gate", []))
DUPES = {x["dropped"]: x["kept"] for x in M.get("class_dupes", [])}
SPLITS = M.get("data_fix", {}).get("splits", [])

def near(a, b, tol):
    try: return abs(float(a) - float(b)) < tol
    except (TypeError, ValueError): return a == b

CC_TOL = {"retrace_pct": 2.0, "dv_ratio": 0.02, "contr": 0.02, "rs21_pct": 0.5, "d_held": 0.5}
CC_COL = {"bbreak": ("broke", "retrace_pct"), "bretr": ("retrace_pct",), "btime": ("d_held", "undercut"),
          "bdv": ("dv_ratio",), "bcontr": ("contr",), "brs": ("rs21_pct",), "bma": ("ma_flags",)}

def diff_row(r, b):
    """What changed for this row vs the same ticker on the same R7 page (or R7 總表)."""
    d = {}
    if b is None:
        d["new"] = True
        return d
    # material-change thresholds: sub-point score drift from the data repair is not painted
    for k, tol in (("vcp", 1.0), ("cert", 1.0), ("combo", 1.0), ("score", 1.0),
                   ("slope", 0.05), ("close", 0.005)):
        if k in r and k in b and not near(r[k], b[k], tol): d[k] = b[k]
    if "ma" in r and "ma" in b and b["ma"] and abs(r["ma"] / b["ma"] - 1) >= 0.001: d["ma"] = b["ma"]
    if r["hl"] != b["hl"]: d["hl"] = b["hl"]
    c, bc = r["cert_c"], b["cert_c"]
    changed = set()
    clip = lambda v: max(0.0, min(100.0, float(v)))      # compare what is displayed (100%+ is one value)
    for k in ("broke", "retrace_pct", "d_held", "undercut", "dv_ratio", "contr", "rs21_pct", "ma_flags"):
        if k == "retrace_pct":
            if abs(clip(c[k]) - clip(bc[k])) >= CC_TOL[k]: changed.add(k)
        elif k in CC_TOL:
            if not near(c[k], bc[k], CC_TOL[k]): changed.add(k)
        elif c[k] != bc[k]: changed.add(k)
    cols = {col for col, keys in CC_COL.items() if any(k in changed for k in keys)}
    if cols: d["cc"] = cols
    if bool(r.get("below_ma")) != bool(b.get("below_ma")): d["below_ma"] = b.get("below_ma")
    if r.get("tier") != b.get("tier"): d["tier"] = b.get("tier")
    if r.get("ranks") and b.get("ranks") and r["ranks"] != b["ranks"]: d["ranks"] = b["ranks"]
    return d

def news_diff(sym):
    e = NEWS.get(sym) or {}; b = BNEWS.get(sym)
    if not e: return {}
    if b is None: return {"dn": True, "up": True, "hype": True, "conf": True}
    return {"dn": e.get("decline_short") != b.get("decline_short"),
            "up": e.get("recovery_short") != b.get("recovery_short"),
            "hype": bool(e.get("hype")) != bool(b.get("hype")) or (e.get("hype_zh") or "") != (b.get("hype_zh") or ""),
            "conf": e.get("confidence") != b.get("confidence")}

def removal_reason(sym, pid):
    p = pid[0]
    if sym in DEALS:
        return "併購套利／價格釘死 → 移入獨立方框（規則⑪）"
    if sym in FUNDS:
        return "封閉式基金／royalty trust → 剔出分層頁（規則⑬）"
    if sym in GATED:
        return "現價已跌穿最後一個底，一底高於一底失效（規則⑤ R8 收緊）"
    if sym in DUPES:
        return f"同一發行人雙類別股份，只保留較高流動性嘅 {DUPES[sym]}（規則⑭）"
    ar = O["pages"][pid].get("all_ranks", {})
    if sym in ar:
        return f"跌出 top 50（本版第 {ar[sym]} 名）"
    if sym in STRUCT:
        return "MA 上升條件已不成立（修正後數據）"
    if sym in ELIG:
        return "一底高於一底結構已不成立（修正後數據）"
    cur_tier = next((r["tier"] for q in O["pages"].values() for r in q["rows"] if r["sym"] == sym), None)
    if cur_tier and cur_tier != pid[1]:
        return f"市值層級改為{TIER_ZH.get(cur_tier, cur_tier)}"
    return "不再合資格（流動性／價格／序列）"

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

def old(v, fmt="{:.1f}"):
    """Red 'R7 value' tag placed next to a changed number."""
    try: s = fmt.format(v)
    except (ValueError, TypeError): s = str(v)
    return f'<span class="old">R7 {esc(s)}</span>'

def meter_cell(v, cls="", prev=None):
    chg = " chg" if prev is not None else ""
    tag = old(prev) if prev is not None else ""
    return (f'<div class="mc {cls}{chg}"><b class="nums">{v:.1f}{tag}</b>'
            f'<span class="meter"><i style="width:{max(0, min(100, v)):.0f}%"></i></span></div>')

CERT_HEADS = [("bbreak", "突破", "中間高位"), ("bretr", "回補", "跌幅收復"), ("btime", "守底", "未破日數"),
              ("bdv", "量縮", "跌/升量比"), ("bcontr", "遞減", "末/首跌幅"),
              ("brs", "RS", "21日相對"), ("bma", "均線", "結構")]
CERT_KEYS = [("bbreak", "break"), ("bretr", "retr"), ("btime", "time"),
             ("bdv", "dv"), ("bcontr", "contr"), ("brs", "rs"), ("bma", "ma")]

def cert_ths():
    return "".join(f'<th class="srt" data-key="{k}">{t}<span class="thn">{n} ↓</span></th>'
                   for k, t, n in CERT_HEADS)

def cert_cells(r, d):
    c = r["cert_c"]; cc = d.get("cc", set())
    def td(col, cls, inner):
        k = " chg" if (col in cc or d.get("new")) else ""
        return f'<td class="cv{cls}{k}">{inner}</td>'
    brk = td("bbreak", " ok", "✓突破") if c["broke"] else td("bbreak", " no", f'{max(0, min(99, c["retrace_pct"])):.0f}%')
    retr = c["retrace_pct"]
    retr_s = "100%+" if retr >= 100 else f"{max(0.0, retr):.0f}%"
    held = td("btime", " wr" if c["undercut"] else "", f'{c["d_held"]}日{"⚠" if c["undercut"] else ""}{"<i class=just>剛確認</i>" if c["d_held"] <= 5 else ""}')
    maf = sum(c["ma_flags"])
    return (brk + td("bretr", "", retr_s) + held
            + td("bdv", " ok" if c["dv_ratio"] < 0.85 else "", f'{c["dv_ratio"]:.2f}')
            + td("bcontr", " ok" if c["contr"] < 0.6 else "", f'{c["contr"]:.2f}')
            + td("brs", " ok" if c["rs21_pct"] > 0 else "", f'{c["rs21_pct"]:+.1f}%')
            + td("bma", " ok" if maf == 3 else "", f'{maf}/3'))

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

def rank_cell(i, d, brank):
    if d.get("new"):
        return f'<td class="rk chg">{i}<span class="nb">新</span></td>'
    if brank is not None and brank != i:
        return f'<td class="rk chg">{i}<span class="old">R7 #{brank}</span></td>'
    return f'<td class="rk">{i}</td>'

def tick_cell(r, L, d):
    sp = '<span class="badge">S&amp;P500</span>' if r["sp500"] else ""
    warn = ''
    if r["below_ma"]:
        warn = f' <span class="warn{" chg" if "below_ma" in d else ""}">⚠低於MA</span>'
    elif "below_ma" in d:
        warn = ' <span class="old">R7 ⚠低於MA</span>'
    ma_s = f'{r["ma"]:g}' + (old(d["ma"], "{:g}") if "ma" in d else "")
    g = r.get("gap") or {}
    if g.get("max1d", 0) >= 20:
        warn += f' <span class="warn chg" title="30日內最大單日變動">⚡單日{g["max1d"]:+.0f}%（{g["max1d_date"][5:]}）</span>'
    elif g.get("gain20", 0) >= 40:
        warn += f' <span class="warn chg">⚡20日+{g["gain20"]:.0f}%</span>'
    if r.get("single_day"):
        warn += f' <span class="warn chg" title="10MA 升勢主要來自單日 {r.get("single_day_pct")}% 跳升">單日跳升推動</span>'
    if r.get("ma_turn") and not r["below_ma"]:
        warn += ' <span class="warn chg" title="再多一日平收 MA 便轉向下">MA將轉向</span>'
    elif r.get("ma_turn"):
        warn += ' <span class="warn chg">MA將轉向</span>' 
    ma_cls = " chg" if "ma" in d else ""
    return (f'<div class="tk"><a href="{tv_url(r)}" target="_blank" rel="noopener">{esc(r["sym"])}</a>'
            f'<span class="ex">{esc(r["exch"])}</span>{sp}<em title="{esc(r["name"])}">{esc(short_name(r["name"]))}</em>'
            f'<span class="pxl nums">{r["close"]:g} <span class="mut{ma_cls}">/ MA{L} {ma_s}</span>{warn}</span></div>')

def cap_cell(r, d):
    t = f'<span class="tierb t{r["tier"]}">{TIER_ZH[r["tier"]]}</span>'
    if "tier" in d: t += f'<span class="old">R7 {esc(TIER_ZH.get(d["tier"], d["tier"]))}</span>'
    return f'<div class="capc"><b class="nums">{fmt_cap(r.get("mcap", 0))}</b>{t}</div>'

def spark_cell(r, d):
    est = ""
    if r.get("est_bars"):
        est = f'<span class="est" title="估算 bar：{esc("、".join(x[5:] for x in r["est_bars"]))}">估{len(r["est_bars"])}</span>'
    scls = " chg" if "slope" in d else ""
    sl = f'MA{r["L"]} {r["slope"]:+.2f}%' + (old(d["slope"], "{:+.2f}%") if "slope" in d else "")
    return (f'{spark_svg(r["spark"])}'
            f'<div class="subsc nums slope{scls}">{sl} <span class="mut">/{r["W"]}日</span>{est}</div>')

def bottoms_chain(r, d):
    hl = r["hl"]
    shown = hl[-4:]
    estb = set(r.get("est_bottom") or [])
    parts = [f'<span class="bot{" estb" if dt in estb else ""}">{dt[5:]}<i>@{p:g}</i></span>' for dt, p in shown]
    sep = '<span class="arr">→</span>'
    pre = '<span class="arr">…→</span>' if len(hl) > 4 else ""
    cls = " chg" if ("hl" in d or d.get("new")) else ""
    tag = ""
    if "hl" in d:
        bh = d["hl"][-3:]
        tag = f'<span class="old">R7 {esc(" → ".join(f"{dt[5:]}@{p:g}" for dt, p in bh))}</span>'
    warn = '<span class="estw">⚠底部落在估算 bar</span>' if estb else ""
    return f'<div class="botwrap{cls}">{pre}{sep.join(parts)}{tag}{warn}</div>'

def off_high(r):
    """% below the 15-session closing high (only reported when >= 10%)."""
    cs = r["spark"]["closes"]
    hi = max(cs[-15:])
    off = (1 - cs[-1] / hi) * 100 if hi > 0 else 0
    return off if off >= 10 else 0

def hype_cell(sym, nd, r=None):
    e = NEWS.get(sym) or {}
    cls = " chg" if nd.get("hype") else ""
    if e.get("hype") and e.get("hype_zh"):
        oh = off_high(r) if r else 0
        tag = f'<span class="old">自高位−{oh:.0f}%</span>' if oh else ""
        return f'<td class="hypec{cls}"><span class="hype">🔥 {esc(e["hype_zh"])}</span>{tag}</td>'
    b = BNEWS.get(sym) or {}
    tag = f'<span class="old">R7 🔥{esc(b.get("hype_zh", ""))}</span>' if (nd.get("hype") and b.get("hype")) else ""
    return f'<td class="hypec{cls}"><span class="nohype">—</span>{tag}</td>'

CONF_CLS = {"高": "chi", "中": "cmid", "低": "clo"}

def news_cells(sym, nd, r=None):
    e = NEWS.get(sym) or {}
    dn = e.get("decline_short", "—")
    up = e.get("recovery_short", "—")
    oh = off_high(r) if r else 0
    note = f'<span class="chg" style="display:block;font-size:10.5px">近況：較15日收盤高位回落 {oh:.0f}%</span>' if oh else ""
    srcf = str(e.get("src", ""))
    asof = "" if (srcf.startswith("news8") or not srcf) else '<span class="asof" title="研究於 R4–R7 階段（8/28–9/2），本版未重查">查證 ≤9/2</span>'
    conf = e.get("confidence", "低")
    upcls = " hypebg" if e.get("hype") else ""
    lowcls = " lowconf" if conf == "低" else ""
    c1 = " chg" if nd.get("dn") else ""
    c2 = " chg" if (nd.get("up") or nd.get("conf")) else ""
    return (f'<td class="whyc{lowcls}{c1}"><div class="why">{esc(dn)}</div></td>'
            f'<td class="whyc{upcls}{lowcls}{c2}"><div class="why">{esc(up)}'
            f'<span class="conf {CONF_CLS.get(conf, "clo")}">信心{esc(conf)}</span>{asof}{note}</div></td>')

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
    hy = [(r["sym"], NEWS[r["sym"]]["hype_zh"], news_diff(r["sym"]).get("hype")) for r in rows
          if NEWS.get(r["sym"], {}).get("hype") and NEWS[r["sym"]].get("hype_zh")]
    if not hy:
        return '<div class="hbanner none">本頁未見市場熱炒 news-driven 催化劑（回升多屬業績穩健或跟隨大市）</div>'
    items = "".join(f'<a class="hitem{" chg" if c else ""}" href="#" data-sym="{esc(s)}"><b>{esc(s)}</b>{esc(t)}</a>'
                    for s, t, c in hy)
    return (f'<div class="hbanner"><span class="hlab">🔥 本頁熱炒催化 <b>{len(hy)}</b> 隻</span>{items}</div>')

def removed_card(pid, cur_syms):
    base = BROWS[pid] if pid != "1" else BP1
    gone = [(s, rk) for s, (rk, _) in base.items() if s not in cur_syms]
    if not gone:
        return '<div class="rmcard none">R7 本頁所有股票本版仍然上榜</div>'
    gone.sort(key=lambda x: x[1])
    items = "".join(f'<span class="rmi"><b>{esc(s)}</b><i>R7 #{rk}</i> {esc(removal_reason(s, pid if pid != "1" else next(iter(BP1[s][1]["ranks"]))))}</span>'
                    for s, rk in gone)
    return (f'<div class="rmcard"><span class="rmlab">R7 上榜、本版剔除 <b>{len(gone)}</b> 隻</span>{items}</div>')

def deal_card(pid):
    ds = [d for d in O.get("deal_pinned", []) if pid == "1" or pid in d.get("would_ranks", {})]
    if not ds:
        return ""
    items = []
    for d in ds:
        wr = d.get("would_ranks", {})
        if pid == "1":
            pos = "、".join(f'{p}#{n}' for p, n in sorted(wr.items()))
        else:
            pos = f'原可排第 {wr.get(pid)} 名'
        b7 = BP1.get(d["sym"]) if pid == "1" else BROWS[pid].get(d["sym"])
        r7 = f'<i>R7 #{b7[0]}</i>' if b7 else '<i>R7 未上榜</i>'
        terms = d.get("terms_zh") or d.get("reason_zh") or "價格釘死"
        dp = f' · 作價 ${d["deal_price"]:g}' if d.get("deal_price") else ""
        acq = f'（{esc(d["acquirer"])}）' if d.get("acquirer") else ""
        items.append(f'<span class="dli"><b>{esc(d["sym"])}</b>{r7} {esc(d["name"][:26])}{acq}：{esc(terms)}{dp} · 現價 {d["close"]:g} · VCP {d["vcp"]:.0f}／確定性 {d["cert"]:.0f} · {esc(pos)}</span>')
    return (f'<div class="dcard"><span class="dlab">🚫 併購套利／價格釘死 · 本版剔出排名 <b>{len(ds)}</b> 隻</span>'
            f'<span class="dnote">股價被現金收購作價釘住，波幅收縮係「假收縮」，冇突破空間 —— 以下只列出、唔參與排名及 top 50</span>{"".join(items)}</div>')

COLW_TIER = [50, 190, 78, 76, 76, 66, 66, 66, 66, 66, 66, 54, 152, 148, 128, 196, 210, 150]
COLW_P1 = [50, 190, 78, 118, 76, 76, 130, 66, 66, 66, 66, 66, 66, 54, 152, 128, 196, 210, 150]

def colgroup(ws):
    return "<colgroup>" + "".join(f'<col style="width:{w}px">' for w in ws) + "</colgroup>", sum(ws)

CHG_STATS = {"new": 0, "moved": 0, "removed": 0, "cells": 0, "news": 0}

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
        b = BROWS[pid].get(r["sym"])
        brank, brow = (b if b else (None, None))
        d = diff_row(r, brow); nd = news_diff(r["sym"])
        if d.get("new"): CHG_STATS["new"] += 1
        elif brank != i: CHG_STATS["moved"] += 1
        CHG_STATS["cells"] += sum(1 for k in d if k not in ("new",))
        CHG_STATS["news"] += 1 if any(nd.values()) else 0
        trc = ' class="newrow"' if d.get("new") else ""
        rows.append(
            f'<tr{trc}{row_attrs(r, i)} data-sym="{esc(r["sym"])}">{rank_cell(i, d, brank)}<td>{tick_cell(r, L, d)}</td>'
            f'<td>{cap_cell(r, d)}</td><td>{meter_cell(r["vcp"], "", d.get("vcp"))}</td><td>{meter_cell(r["cert"], "certm", d.get("cert"))}</td>'
            f'{cert_cells(r, d)}<td>{spark_cell(r, d)}</td><td class="bots">{bottoms_chain(r, d)}</td>'
            f'{hype_cell(r["sym"], nd, r)}{news_cells(r["sym"], nd, r)}<td>{sector_cell(r)}</td></tr>')
    cg, tw = colgroup(COLW_TIER)
    return head, "".join(rows), pg, cg, tw

def frs_cell(r, d):
    br = d.get("ranks") or {}
    out = []
    for p, n in sorted(r["ranks"].items()):
        c = ""
        if d.get("new") or p not in br: c = " chg"
        elif br.get(p) != n: c = " chg"
        tag = f'<u>R7 #{br[p]}</u>' if (p in br and br[p] != n) else ("<u>新</u>" if (p not in br and not d.get("new")) else "")
        out.append(f'<span class="fr on{c}">{p[0]}{TIER_ZH[p[1]][0]}<i>#{n}</i>{tag}</span>')
    for p, n in sorted(br.items()):
        if p not in r["ranks"]:
            out.append(f'<span class="fr off chg">{p[0]}{TIER_ZH[p[1]][0]}<i>R7 #{n}</i></span>')
    return "".join(out)

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
        b = BP1.get(r["sym"])
        brank, brow = (b if b else (None, None))
        d = diff_row(r, brow); nd = news_diff(r["sym"])
        if brow and brow.get("L") != r.get("L"):
            # the 總表 display row now comes from the 20MA page (R7 used the 10MA row):
            # MA / slope / below-MA are not comparable across MA lengths, so do not paint them
            for k in ("ma", "slope", "below_ma"): d.pop(k, None)
        trc = ' class="newrow"' if d.get("new") else ""
        rows.append(
            f'<tr{trc}{row_attrs(r, i, p1=True)} data-sym="{esc(r["sym"])}">{rank_cell(i, d, brank)}'
            f'<td>{tick_cell(r, r["L"], d)}</td><td>{cap_cell(r, d)}</td>'
            f'<td>{meter_cell(r["score"], "scorem", d.get("score"))}</td><td>{meter_cell(r["vcp"], "", d.get("vcp"))}</td>'
            f'<td>{meter_cell(r["cert"], "certm", d.get("cert"))}</td><td class="frs">{frs_cell(r, d)}</td>'
            f'{cert_cells(r, d)}<td>{spark_cell(r, d)}</td>'
            f'{hype_cell(r["sym"], nd, r)}{news_cells(r["sym"], nd, r)}<td>{sector_cell(r)}</td></tr>')
    cg, tw = colgroup(COLW_P1)
    return head, "".join(rows), cg, tw

c = M["counts"]; bc = BM["counts"]
def n_chg(cur, base, fmt="{:,}"):
    s = fmt.format(cur)
    return f'<span class="chg">{s}<span class="old">R7 {fmt.format(base)}</span></span>' if cur != base else s
UNIVERSE_LINE = (f'全美上市普通股掃描 —— 快照涵蓋 {n_chg(c["total"], bc["total"])} 隻 · 有 {M["last_date"]} 收盤報價 {n_chg(c["current"], bc["current"])} 隻 · '
                 f'歷史 ≥90 交易日 {n_chg(c["hist"], bc["hist"])} 隻 · 價格 ≥$2 {n_chg(c["price"], bc["price"])} 隻 · '
                 f'流動性達標（20日中位成交額 ≥$1M）{n_chg(c["liq"], bc["liq"])} 隻合資格')

css = """
/* Committed dark theme: the palette is defined once on :root and never flips. */
:root{color-scheme:dark;
 --pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;
 --grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
 --seq:#3987e5;--link:#6da7ec;--good:#0ca30c;--warn:#d99a2b;--bad:#e06c6c;
 --hl:#16202d;--meter:#25303e;--okbg:#15230f;--nobg:#2a1c1c;
 --hype:#f2b95f;--hypebg:#2d2211;--hypebd:#8f6d2c;
 --chg:#ff5c5c;--chgbg:#2a1111;--chgbd:#9b2f2f;
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
.mkt .mf span.chg{border-color:var(--chgbd);background:var(--chgbg)}
/* ---- red = changed versus R7 ---- */
.chg,.chg *{color:var(--chg)!important}
.chg b,.chg .why{color:var(--chg)!important}
.chg .meter i{background:var(--chg)!important}
td.chg{background:var(--chgbg)}
tr:hover td.chg{background:#3a1616}
.rk .old{display:block;margin:3px 0 0;padding:0 3px;font-size:9px}
.old{display:inline-block;font-size:9.5px;font-weight:400;color:var(--chg)!important;margin-left:4px;
 border:1px dashed var(--chgbd);border-radius:7px;padding:0 4px;white-space:nowrap;vertical-align:1px;font-style:normal}
.nb{display:inline-block;font-size:9.5px;font-weight:700;color:#fff!important;background:var(--chg);
 border-radius:7px;padding:0 5px;margin-left:4px;vertical-align:1px}
tr.newrow td:first-child{box-shadow:inset 3px 0 var(--chg)}
.summary{border-color:var(--chgbd);background:var(--chgbg)}
.summary h2{color:var(--chg)}
.summary li{color:var(--chg);font-size:12.5px;line-height:1.6;margin:2px 0}
.summary ul{margin:0;padding-left:18px}
.summary b{color:#fff}
.summary .pl{color:var(--ink2)}
.rmcard,.dcard{display:flex;flex-wrap:wrap;gap:5px 6px;align-items:center;border-radius:10px;padding:8px 12px;margin-bottom:12px;
 background:var(--chgbg);border:1px solid var(--chgbd)}
.rmcard.none{background:var(--sf);border-color:var(--ring);color:var(--mut);font-size:11.5px}
.rmlab,.dlab{font-size:12px;font-weight:700;color:var(--chg);margin-right:4px}
.rmlab b,.dlab b{color:#fff}
.rmi,.dli{font-size:11px;color:var(--chg);background:var(--sf);border:1px solid var(--chgbd);border-radius:9px;padding:2px 8px}
.rmi b,.dli b{color:#fff;margin-right:5px}
.rmi i,.dli i{font-style:normal;color:var(--mut);margin-right:5px}
.dli{display:block;width:100%;line-height:1.5}
.dnote{width:100%;font-size:11px;color:var(--ink2)}
.redleg{font-size:11.5px;color:var(--chg);margin:0 0 10px}
.redleg b{color:#fff}
.est{display:inline-block;font-size:9px;color:var(--mut);border:1px dashed var(--axis);border-radius:6px;padding:0 4px;margin-left:5px;cursor:help}
.estw{display:block;font-size:10px;color:var(--chg);white-space:nowrap}
.bot.estb i{border-bottom:1px dotted var(--chg)}
.fr.off{opacity:.8;border-style:dashed}
.fr u{text-decoration:none;font-size:9px;margin-left:3px}
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
.hitem.chg{border-color:var(--chgbd)}
.hitem:hover{background:var(--hypebd);color:var(--pg)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.chip{font-size:11.5px;color:var(--ink2);background:var(--sf);border:1px solid var(--ring);
 border-radius:14px;padding:4px 10px}
.chip b{color:var(--ink)}
.chip i{font-style:normal;font-weight:700;color:var(--seq)}
:root{--navh:70px}
.tblwrap{overflow-x:auto;background:var(--sf);border:1px solid var(--ring);border-radius:10px}
/* fixed clone of the active table's header row, shown once the real header scrolls under the nav */
.fixhead{position:fixed;z-index:5;overflow:hidden;display:none;background:var(--sf);border-bottom:1px solid var(--grid);box-shadow:0 4px 10px rgba(0,0,0,.45)}
.fixhead table{table-layout:fixed;border-collapse:collapse;font-size:12.5px}
.fixhead th{position:static}
table{border-collapse:collapse;table-layout:fixed;font-size:12.5px}
th{position:sticky;top:0;text-align:left;font-size:11px;color:var(--mut);font-weight:600;
 padding:9px 8px;border-bottom:1px solid var(--grid);background:var(--sf);white-space:nowrap;z-index:1;
 overflow:hidden;text-overflow:ellipsis}
th.srt{cursor:pointer}
th.srt:hover{color:var(--seq)}
th.srt.act{color:var(--seq)}
th.hy{color:var(--hype)}
.thn{display:block;font-weight:400;font-size:10px;white-space:normal}
.rz{position:absolute;top:0;right:0;width:7px;height:100%;cursor:col-resize;user-select:none}
.rz:hover{background:var(--seq);opacity:.4}
td{padding:8px 8px;border-bottom:1px solid var(--grid);vertical-align:middle;overflow:hidden}
tr:last-child td{border-bottom:0}
tr:hover td{background:var(--hl)}
td.hypebg,tr:hover td.hypebg{background:var(--hypebg)}
td.hypebg.chg{background:var(--chgbg)}
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
.tk .pxl{display:block;font-size:11px;margin-top:2px;white-space:normal}
.tk .pxl .old{display:inline-block;margin-left:2px}
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
.arr{color:var(--mut);margin:0 3px}
.warn{color:var(--warn);font-size:10.5px;white-space:nowrap}
.tk .pxl{white-space:normal}
.just{display:block;font-style:normal;font-size:9px;color:var(--mut)}
.hypec{text-align:left}
.hype{display:inline-block;font-size:11px;font-weight:700;color:var(--hype);background:var(--hypebg);
 border:1px solid var(--hypebd);border-radius:9px;padding:3px 8px;line-height:1.35}
.nohype{color:var(--mut);font-size:11px}
.asof{display:inline-block;font-size:9px;color:var(--mut);border:1px dotted var(--axis);border-radius:7px;padding:0 4px;margin-left:4px}
.orank{display:block;font-size:9.5px;color:var(--mut);font-weight:400}
th.srt.asc .thn::after{content:" ↑"}
@media (max-width:600px){.nav button .s{display:none}.nav button{padding:7px 10px;font-size:12px}.nav .tierb{padding:6px 9px}}
.why{font-size:11.5px;line-height:1.5;color:var(--ink2);overflow-wrap:break-word}
.conf{display:inline-block;font-size:9.5px;border-radius:8px;padding:0 5px;margin-left:4px;
 border:1px solid var(--ring);color:var(--mut)}
.conf.chi{color:var(--good);border-color:var(--good)}
.conf.cmid{color:var(--warn);border-color:var(--warn)}
.conf.clo{color:var(--mut);border-style:dashed}
.whyc.lowconf .why{color:var(--mut);font-style:italic}
.sect b{font-size:12px}
.sect span{font-size:10.5px;color:var(--mut);margin-left:4px}
.sect em{display:block;font-style:normal;font-size:10.5px;color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.gics{display:inline-block;font-style:normal;font-size:9px;color:var(--seq);border:1px solid var(--ring);
 border-radius:7px;padding:0 4px;margin-left:5px;vertical-align:1px}
.frs{white-space:normal}
.fr{display:inline-block;font-size:10px;color:var(--mut);border:1px dashed var(--axis);
 border-radius:9px;padding:1px 5px;margin:1px 3px 1px 0}
.fr.on{color:var(--ink);border:1px solid var(--seq);background:var(--hl)}
.fr.on i{font-style:normal;color:var(--seq);font-weight:700;margin-left:2px}
.fr.chg{border-color:var(--chgbd);background:var(--chgbg)}
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
_bl = [r["sym"] for r in B["page1"]]
_bconf = {"高": 0, "中": 0, "低": 0}; _bhy = 0
for _s in _bl:
    _e = BNEWS.get(_s)
    if not _e: _bconf["低"] += 1; continue
    _bconf[_e.get("confidence", "低")] = _bconf.get(_e.get("confidence", "低"), 0) + 1
    if _e.get("hype"): _bhy += 1
COVERAGE = (f'研究覆蓋 {n_chg(len(_listed), len(_bl))} 隻：<b>信心高 {n_chg(_conf["高"], _bconf["高"])}</b>（搵到明確個股消息）· '
            f'<b>中 {n_chg(_conf["中"], _bconf["中"])}</b>（板塊或部分證據）· <b>低 {n_chg(_conf["低"], _bconf["低"])}</b>（未搵到個股消息，只反映大市背景）· '
            f'其中 <b>🔥 {n_chg(_hy, _bhy)} 隻</b>屬市場熱炒 news-driven 催化')

DF = M.get("data_fix", {})
FS = DF.get("fill_stats", {})
def _fs(dd):
    s = FS.get(dd, {})
    return f'{dd[5:]}（真實日線 {s.get("real", 0):,}／官方收盤 {s.get("official", 0):,}／內插 {s.get("interp", 0):,}）'
DEAL_SYMS = M.get("deal_pinned", {}).get("symbols", [])
n_deal = len(DEAL_SYMS)

rules_html = f"""
<div class="card rules">
<h2>篩選規則（R8 · 數據更新至 9/1 收盤 · 全美掃描三層分榜 · <span class="chg">紅字＝本版相對 R7 的變更</span>）</h2>
① <b>Universe：{UNIVERSE_LINE}</b>。<br>
② <b>市值分層</b>：<b>大型股 ≥$10B</b> · <b>中型股 $2B–$10B</b> · <b>小型股 &lt;$2B</b>（含通過流動性門檻嘅微型股）。每個時間框各自分三層，<b>每層獨立取 top 50</b>，細價股唔會被大價股擠走。快照無市值數據嘅非普通股證券（優先股／存託股、SPAC、封閉式基金）唔會當成小型股，已剔出分層頁 —— 本次 <span class="chg">{esc(len(M.get("unknown_cap", {}).get("symbols", [])))} 隻（{esc("、".join(M.get("unknown_cap", {}).get("symbols", [])))}）</span>。<br>
③ <b>MA 上升</b>：PAGE 2a-c：<b>10 天 MA</b> 較 <b>5 個交易日</b>前高；PAGE 3/4/5：<b>20 天 MA</b> 分別較 <b>10 / 21 / 42 個交易日</b>前高；且 MA 最後 3 日逐日上升、期內 ≥70% 日子上升。<br>
④ <b>「底」</b>：某日收盤係 ±3 日內最低，且 3 日前收盤高過佢、3 日後收盤高過佢；相鄰 ≤3 日去重。 ⑤ <b>一底高於一底</b>：45 個交易日內 ≥2 個底逐個遞升，最近一個底喺 25 日內；<span class="chg"><b>R8 收緊：數據終點收盤必須仍高於最後一個底</b>（R7 有 19 隻現價已跌穿最後底仍上榜，只係守底分數打折）—— 本次因此剔除 {len(GATED)} 隻。盤中曾跌穿但收復者保留並以 ⚠ 標示。</span><br>
⑥ <b>VCP 指數（0–100）</b>：10日/前30日波幅（35%）＋近10日區間佔價（25%）＋近10日/前30日成交量（20%）＋近15日/前30–45日區間（20%），全體百分位合成。<br>
⑦ <b>確定性（0–100，7 欄）</b>：突破中間高位（25%）· 回補幅度（10%）· 守底時間（15日滿分，曾跌穿×0.25，15%）· 下試量縮（15%）· 回撤遞減（10%）· 相對強度（10%）· 均線位置（15%）。<br>
⑧ <b>排名</b>：各分層頁按綜合分數（0.5×VCP＋0.5×確定性）取 top 50；總表按爆發潛力分數（0.4×VCP＋0.4×確定性＋0.2×時間框覆蓋度）。<b>TOP BAR 及表頭可切換排序（市值／VCP／確定性／7 項證據／熱炒）</b>；<b>欄闊可拖拉表頭右邊調整</b>。<br>
⑨ <b>🔥 熱炒催化劑欄</b>：AI 代理經 <a href="https://bigdata.com" target="_blank" rel="noopener">Bigdata.com</a> 新聞索引＋公開網頁逐隻研究後，凡回升由<b>市場熱炒嘅 news-driven 事件</b>帶動（收購／私有化、爆炸性臨床數據、大幅盈喜引發急升、AI 熱潮、單日暴漲），以獨立一欄＋每頁頂部橫幅精簡標示；其餘顯示「—」。<br>
⑩ <b>{COVERAGE}</b>。<span class="cav">⚠ 信心低嘅股票代表「未查證」，唔代表「無消息」，欄位以斜體灰字標示。</span><br>
<span class="chg">⑪ <b>併購套利／價格釘死剔除（R8 新增）</b>：股價已被現金收購作價釘住（或近乎零波幅）嘅股票，VCP「收縮」屬假象、亦冇突破空間，本版唔再參與排名及 top 50，改列於各頁「🚫 併購套利」方框（連同原本可排名次）—— 本次 {n_deal} 隻：{esc("、".join(DEAL_SYMS)) if DEAL_SYMS else "無"}。</span><br>
<span class="chg">⑫ <b>缺快照交易日修補（R8 新增）</b>：快照鏡像漏咗 {esc("、".join(x[5:] for x in DF.get("missing_sessions", [])))} 共 {len(DF.get("missing_sessions", []))} 個交易日，R7 以前值填補（複製前一日收盤及成交量，令走勢出現假平台、VCP 被高估）。本版逐隻修補：有真實日線（natezone 鏡像，S&amp;P 1500）用真實 bar；8/31 其餘股票用 9/1 快照隱含嘅官方收盤（price − price_change）；其他缺日用前後收盤線性內插、成交量取前後平均；8/27 快照成交量係 16:05 ET 未完成數（中位只有真實嘅 {DF.get("vol_ratio_0827", 0):.2f}×），無真實 bar 嘅股票按中位比例放大。走勢圖下方「估n」＝該股最後 60 日內含 n 個估算 bar；底部若落喺估算 bar 會另外標示。另偵測到 {len(SPLITS)} 隻股票序列內有未調整拆股（快照價格未經拆股調整），已按拆股比例回溯調整（{esc("、".join(f"{s['sym']} {s['date'][5:]} {s['ratio']:g}x" for s in SPLITS[:6]))}{"…" if len(SPLITS) > 6 else ""}）。</span><br>
<span class="chg">⑬ <b>封閉式基金／royalty trust 剔出（R8 新增）</b>：淨值錨定嘅封閉式基金、市政／定期信託、royalty trust（快照有市值故 R7 未剔除）波幅收縮屬結構性，唔係底部，已剔出分層頁 —— 本次 {len(FUNDS)} 隻：{esc("、".join(sorted(FUNDS))) or "無"}。REIT／銀行／MLP／BDC 屬營運實體，保留。</span><br>
<span class="chg">⑭ <b>同一發行人多類別股份（R8 新增）</b>：只保留流動性較高嘅一個類別，避免一間公司佔兩個名額 —— 本次 {esc("、".join(f"{k}→保留 {v}" for k, v in DUPES.items())) or "無"}。</span>
</div>"""

def red_suffix(new, base):
    """Render text with the part that differs from the baseline in red (common prefix kept)."""
    if not base: return f'<span class="chg">{esc(new)}</span>'
    i = 0
    while i < min(len(new), len(base)) and new[i] == base[i]: i += 1
    j = 0
    while j < min(len(new), len(base)) - i and new[-1 - j] == base[-1 - j]: j += 1
    head, mid, tail = new[:i], new[i:len(new) - j], new[len(new) - j:] if j else ""
    if not mid: return esc(new)
    return f'{esc(head)}<span class="chg">{esc(mid)}</span>{esc(tail)}'

mkt_html = ""
if MKT:
    bset = {(f["period"], f["factor_zh"]) for f in (BMKT or {}).get("factors", [])}
    factors = "".join(f'<span{" class=chg" if (f["period"], f["factor_zh"]) not in bset else ""}><b>{esc(f["period"])}</b> {esc(f["factor_zh"])}</span>'
                      for f in MKT.get("factors", []))
    title = MKT.get("title_zh", "2026年6月–9月1日 市場背景（底部成因的共同分母）")
    mkt_html = (f'<div class="card mkt"><h2>{esc(title)}</h2>'
                f'{red_suffix(MKT["summary_zh"], (BMKT or {}).get("summary_zh", ""))}<div class="mf">{factors}</div></div>')

# ---- sections ----
secs = []
head, body, cg, tw = table_p1()
tier_n = {}
for r in O["page1"]:
    tier_n[r["tier"]] = tier_n.get(r["tier"], 0) + 1
btier_n = {}
for r in B["page1"]:
    btier_n[r["tier"]] = btier_n.get(r["tier"], 0) + 1
pghead = (f'<div class="pghead"><b>總表 · 全部分層數據</b>'
          f'<span>12 個分層榜合共 <b>{n_chg(len(O["page1"]), len(B["page1"]))}</b> 隻不重複股票</span>'
          f'<span class="tg">大型 {n_chg(tier_n.get("a", 0), btier_n.get("a", 0))}</span><span class="tg">中型 {n_chg(tier_n.get("b", 0), btier_n.get("b", 0))}</span>'
          f'<span class="tg">小型 {n_chg(tier_n.get("c", 0), btier_n.get("c", 0))}</span>'
          f'<span>排序 = 爆發潛力分數</span></div>')
REDLEG = ('<div class="redleg"><b>紅色＝相對 R7 的變更</b>：'
          '<span class="nb">新</span> 新上榜 · <span class="old">R7 #n</span> 名次／數值變動（括示 R7 舊值）· 紅底格＝該欄數值／原因／催化劑已更新 · '
          '下方紅框＝R7 上榜但本版剔除嘅股票及原因 · 🚫 框＝併購套利釘死價格股票（唔參與排名）</div>')
p1_syms = {r["sym"] for r in O["page1"]}
secs.append(f'''<section id="p1">
{pghead}{REDLEG}{mkt_html}{deal_card("1")}{removed_card("1", p1_syms)}{hype_banner(O["page1"])}{sector_chips(O["page1"])}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw" style="background:var(--ink2)"></i>收盤</span>
<span><i class="sw" style="background:var(--seq)"></i>MA</span>
<span><i class="sw" style="background:var(--good);height:8px;width:8px;border-radius:50%"></i>底部（最後60個交易日）</span>
<span>上榜分頁：2大 = PAGE 2a（1星期·大型股），如此類推；<span class="chg">紅框＝名次變動／新入榜／R7 有而本版無（虛線）</span></span>
<span class="chg">走勢圖／MA／斜率取 <b>1個月（20MA）</b> 分頁嘅數值（無則依次 2星期／2個月／1星期；R7 取最短時間框即 10MA）；爆發潛力嘅「覆蓋度」＝<b>合資格</b>時間框數（唔係上榜頁數）</span>
<span>「估n」＝含 n 個估算 bar（見規則⑫）· <span class="chg">⚡＝30日內單日變動 ≥20% 或 20日升幅 ≥40%（事件驅動，非收縮型底部）· 「單日跳升推動」＝1星期頁 10MA 升勢主要來自單日跳升 · 「MA將轉向」＝再多一日平收 MA 便轉向下</span></span></div>
</section>''')

for p, tf_zh, tf_sub in TF:
    for k, tzh, ten, rng in TIERS:
        pid = f"{p}{k}"
        head, body, pg, cg, tw = table_tier(pid)
        bq = B["pages"][pid]["qualified"]
        pghead = (f'<div class="pghead"><b>PAGE {pid} · {tf_zh} · {tzh}</b>'
                  f'<span class="tg">{ten} {rng}</span>'
                  f'<span>{tf_sub}</span>'
                  f'<span>該層合資格 <b>{n_chg(pg["qualified"], bq)}</b> 隻 → 按綜合分數取 top {len(pg["rows"])}</span></div>')
        cur = {r["sym"] for r in pg["rows"]}
        nb = sum(1 for r in pg["rows"] if r["below_ma"])
        pghead = pghead.replace("</div>", f'<span class="tg">現價低於MA{pg["L"]} <b>{nb}</b> 隻</span></div>')
        secs.append(f'''<section id="p{pid}" hidden>
{pghead}{REDLEG}{deal_card(pid)}{removed_card(pid, cur)}{hype_banner(pg["rows"])}{sector_chips(pg["rows"])}
<div class="tblwrap"><table style="width:{tw}px">{cg}<thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw" style="background:var(--ink2)"></i>收盤</span>
<span><i class="sw" style="background:var(--seq)"></i>MA{pg["L"]}</span>
<span><i class="sw" style="background:var(--good);height:8px;width:8px;border-radius:50%"></i>底部</span>
<span>突破欄：✓＝中間高位已升穿，百分比＝現價喺「底→中間高位」嘅位置 · 表頭 ↓＝可㩒排序 · 拖表頭右邊＝調欄闊</span>
<span class="chg">⚡＝30日內單日變動 ≥20% 或 20日升幅 ≥40%（事件驅動）· 「單日跳升推動」＝10MA 升勢主要來自單日跳升 · 「MA將轉向」＝再多一日平收 MA 便轉向下 · 守底「剛確認」＝底部確認未夠 5 日</span></div>
</section>''')

tf_btns = ('<button data-g="1" class="on">總表<span class="s">全部分層數據</span></button>'
           + "".join(f'<button data-g="{p}">{tf_zh}<span class="s">{tf_sub}</span></button>'
                     for p, tf_zh, tf_sub in TF))
tier_btns = "".join(f'<button class="tierb{" on" if k == "a" else ""}" data-t="{k}">{tzh}<span class="s">{rng}</span></button>'
                    for k, tzh, ten, rng in TIERS)

# ---- change summary (all red) ----
CH = O.get("changes", {})       # optional free-text bullets supplied by the pipeline
p1_new = sorted(p1_syms - set(BP1)); p1_gone = sorted(set(BP1) - p1_syms)
news_changed = sum(1 for s in _listed if any(news_diff(s).values()))
summary_items = [
    f'<b>數據修補</b>：{" · ".join(_fs(dd) for dd in DF.get("missing_sessions", []))}；8/27 成交量按 {DF.get("vol_ratio_0827", 0):.2f}× 中位比例校正（規則⑫）。R7 有 {n_chg(len(_listed), len(_bl))} 隻上榜股中，修補後 MA／底部／VCP／確定性數值有變嘅欄位全部標紅。',
    f'<b>併購套利／價格釘死剔除</b>：{n_deal} 隻（{esc("、".join(DEAL_SYMS)) if DEAL_SYMS else "無"}）移出排名（規則⑪），各頁 🚫 框列明原可排名次。',
    f'<b>名單變動</b>：12 個分層頁合共新上榜 {CHG_STATS["new"]} 行、名次變動 {CHG_STATS["moved"]} 行；總表 {len(B["page1"])} → {len(O["page1"])} 隻（新入 {len(p1_new)}：{esc("、".join(p1_new)) or "無"}；剔除 {len(p1_gone)}：{esc("、".join(p1_gone)) or "無"}）。',
    f'<b>原因／催化劑更新</b>：{news_changed} 隻上榜股嘅下跌／回升原因、信心度或 🔥 標記有更新（紅底格）；審視糾正咗 THC／MAN／RCEL／PESI／ITGR／ICE 等條目嘅數字或歸因，🔥 唔再標示併購套利股及信心低嘅不明急升；回升後已自 15 日高位回落 ≥10% 嘅股票加註「近況」。',
    f'<b>其他剔除</b>：封閉式基金／royalty trust {len(FUNDS)} 隻（規則⑬）、同一發行人重複類別 {len(DUPES)} 隻（規則⑭）、現價已跌穿最後底 {len(GATED)} 隻（規則⑤ 收緊）；未調整拆股回溯修正 {len(SPLITS)} 隻。',
    '<b>新增標示</b>：⚡ 事件驅動（單日 ≥20% 或 20日 ≥40%）、「單日跳升推動」（1星期頁）、「MA將轉向」、守底「剛確認」；總表改以 1個月（20MA）分頁數值顯示走勢／MA。',
]
summary_items += [esc(x) for x in CH.get("bullets", [])]
summary_html = ('<div class="card summary"><h2>本版更新摘要 R8（紅字＝相對 R7 的變更 · 經 7 組獨立審視：併購套利／數據完整性／新聞質量／篩選邊界／版面／市場背景／方法論）</h2><ul>'
                + "".join(f'<li>{x}</li>' for x in summary_items) + '</ul></div>')

foot_b2 = (f'② <b>數據來源（雙來源合成，R8 修補版）</b>：主線為 zyhe16/top-us-stock-tickers 嘅每日 Nasdaq 快照，逐 commit 重建收盤/成交量序列，本表取 {M["n_days"]} 個交易日（{M["cal_first"]} → {M["cal_last"]}）。'
           f'<span class="chg">審視發現快照鏡像除 8/31 外仲漏咗 8/11、8/12、8/26（及 3/18），R7 以前值填補；本版按規則⑫逐隻修補（真實日線 natezone/market-tracker → 9/1 快照隱含官方收盤 → 線性內插），並校正 8/27 未完成成交量。修補前後 5,336 隻股票嘅 8/31 收盤中位偏差 1.06%（1,632 隻偏差 >2%），係本版名單變動嘅主因。</span>'
           f'<b>9/1 收盤已與獨立日線鏡像交叉核對：重疊 1,498 隻全部吻合（偏差 0.000%）</b>。')

foot = f"""
<div class="card foot">
<h2>備註 · 數據 lineage</h2>
① <b>覆蓋範圍（全美掃描）</b>：本版覆蓋全美上市普通股（9/1 快照 7,153 行，重建出 {M["counts"]["total"]:,} 條序列、{M["counts"]["current"]:,} 隻有 9/1 收盤）。價格未除息調整。<br>{foot_b2}<br>③ 類別：Nasdaq 分類＋GICS（S&amp;P 500）；交易所：irachex/open-stock-data。VCP、確定性 7 項及排名邏輯沿用 R3–R5 定義（本版收緊規則⑤、新增規則⑪–⑭，計分公式未改動）。<br>
④ 原因及熱炒催化劑由 AI 代理經 <a href="https://bigdata.com" target="_blank" rel="noopener">Bigdata.com</a> 新聞索引及公開網頁研究後濃縮——係新聞摘要，可能有錯漏，請以原始公告為準。<br>
⑤ <b>數據終點 {M["last_date"]}（美東星期{WD}收盤，為最後交易日），建置時間 {BUILD_TS}</b> · 快照只有收盤/成交量 · 本表只係篩選工具，唔係投資建議。<br>
⑥ Ticker 點擊開 TradingView chart（https://www.tradingview.com/chart/Q1c5VWwD/?symbol=交易所%3Aticker）。
</div>"""

html_doc = f"""<title>20MA Uptrend Watchlist R8</title>
<style>{css}</style>
<div class="wrap">
<h1>20MA Uptrend Watchlist R8（全美掃描 × 市值分層 × VCP × 底部確定性 · <span class="chg">紅字＝本版變更</span>）</h1>
<div class="sub">數據至 <b>{M["last_date"]}</b>（美東星期{WD}）收盤 · 全美掃描 {c["liq"]:,} 隻合資格 · 12 個分層榜（4 時間框 × 大／中／小型股）＋總表 · 🔥 熱炒 news-driven 催化劑獨立成欄 · 固定深色版面 · <span class="chg">R7 經 7 組獨立審視後修正：數據修補＋併購套利剔除＋新聞／市場背景更新（全部以紅色標示）</span></div>
{summary_html}
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
    setNavH();
    syncSort();
    fixFor = null; updFix();
    try {{ localStorage.setItem('r8nav', g + '|' + t); }} catch (e) {{}}
  }}
  var navEl = document.querySelector('.nav');
  function setNavH() {{ document.documentElement.style.setProperty('--navh', navEl.offsetHeight + 'px'); }}
  window.addEventListener('resize', setNavH);
  // ---- fixed header clone ----
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
    var show = hr.top < navB && tr.bottom > navB + hr.height + 20;
    if (!show) {{ fix.style.display = 'none'; return; }}
    var ct = fixIn.querySelector('table');
    var cols = tb.querySelectorAll('col'), ccols = ct.querySelectorAll('col');
    cols.forEach(function(c, i) {{ if (ccols[i]) ccols[i].style.width = c.style.width; }});
    ct.style.width = tb.style.width || (tb.offsetWidth + 'px');
    ct.querySelectorAll('th').forEach(function(h, i) {{
      var real = thead.querySelectorAll('th')[i];
      if (real) {{ h.className = real.className; }}
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
    if (fromHeader && key && st.key === key) asc = !st.asc;   // second click on the same header flips direction
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
      var keep = c0.querySelector('.old,.nb');
      c0.textContent = i + 1;
      if (key) {{
        var o = document.createElement('span'); o.className = 'orank'; o.textContent = '原#' + r.dataset.rank; c0.appendChild(o);
      }}
      if (keep) c0.appendChild(keep);
      tb.appendChild(r);
    }});
    syncSort();
  }}
  function syncSort() {{
    var st = sortState[cur()] || {{key: '', asc: false}};
    var key = st.key;
    sbtns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.sort === key); }});
    document.querySelectorAll('#p' + cur() + ' th.srt').forEach(function(h) {{
      h.classList.toggle('act', h.dataset.key === key && key !== '');
      h.classList.toggle('asc', h.dataset.key === key && key !== '' && st.asc);
    }});
    if (typeof updFix === 'function') updFix();
  }}
  gbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ g = b.dataset.g; show(); }}); }});
  tbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ t = b.dataset.t; show(); }}); }});
  sbtns.forEach(function(b) {{ b.addEventListener('click', function() {{ sortSec(cur(), b.dataset.sort); }}); }});
  document.querySelectorAll('th.srt').forEach(function(h) {{
    h.addEventListener('click', function() {{ sortSec(h.closest('section').id.slice(1), h.dataset.key, true); }});
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
          updFix();
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
    var sv = localStorage.getItem('r8nav');
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

# The Artifact viewer injects its own <head>, so the fragment goes there; the standalone file
# (opened from disk) needs a real document head or Chromium decodes it as Latin-1 (mojibake).
out_path = f"{SCRATCH}/{OUTNAME}"
standalone = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1">' + html_doc.split("</title>", 1)[0] + "</title></head><body>"
              + html_doc.split("</title>", 1)[1] + "</body></html>")
open(out_path, "w", encoding="utf-8").write(standalone)
os.makedirs(f"{SCRATCH}/r8", exist_ok=True)
open(f"{SCRATCH}/r8/artifact_fragment.html", "w", encoding="utf-8").write(html_doc)
print("wrote", out_path, f"{len(standalone)/1024:.0f} KB", "| change stats:", CHG_STATS)
