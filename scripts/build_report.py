#!/usr/bin/env python3
"""Build the R2 5-page HTML report from screen_results.json."""
import json, datetime, html, os, sys

SCRATCH = os.environ.get("WORK_DIR", "./data")
O = json.load(open(f"{SCRATCH}/screen_results.json"))
M = O["meta"]

now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
OUTNAME = f"20MA_uptrend_watchlistGit_R2.01_claudefable5xhigh_{STAMP}.html"

PAGE_DEFS = [
    ("1", "PAGE 1 · 總覽", "爆發潛力排名", None),
    ("2", "PAGE 2 · 1星期", "10MA · 5個交易日", 2),
    ("3", "PAGE 3 · 2星期", "20MA · 10個交易日", 3),
    ("4", "PAGE 4 · 1個月", "20MA · 21個交易日", 4),
    ("5", "PAGE 5 · 2個月", "20MA · 42個交易日", 5),
]

def esc(s): return html.escape(str(s), quote=True)

def spark_svg(sp, L):
    """closes + MA + bottom markers, 150x40."""
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

def vcp_bar(v, cls="vcpb"):
    return (f'<div class="{cls}"><div class="meter"><i style="width:{v:.0f}%"></i></div>'
            f'<b>{v:.1f}</b></div>')

def bottoms_chain(hl):
    parts = []
    shown = hl[-4:]
    for d, p in shown:
        mmdd = d[5:]
        parts.append(f'<span class="bot">{mmdd}<i>@{p:g}</i></span>')
    chain = '<span class="arr">→</span>'.join(parts)
    pre = '<span class="arr">…→</span>' if len(hl) > 4 else ""
    return f'<div class="botwrap">{pre}{chain}</div>'

def sector_cell(r):
    zh = r["sector_zh"]; en = r["sector"]
    sub = r["gsub"] if (r["sp500"] and r.get("gsub")) else r["industry"]
    gtag = f'<i class="gics">GICS·{esc(r["gsec"])}</i>' if (r["sp500"] and r.get("gsec")) else ""
    return f'<div class="sect"><b>{esc(zh)}</b> <span>{esc(en)}</span>{gtag}<em>{esc(sub)}</em></div>'

def tv_url(r):
    # user's TradingView chart layout, e.g. PARR -> .../chart/Q1c5VWwD/?symbol=nyse%3Aparr
    sym = r["sym"].replace("/", ".").lower()
    if r["exch"] != "—":
        return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={r["exch"].lower()}%3A{esc(sym)}'
    return f'https://www.tradingview.com/chart/Q1c5VWwD/?symbol={esc(sym)}'

def tick_cell(r):
    sp = '<span class="badge">S&amp;P500</span>' if r["sp500"] else ""
    return (f'<div class="tk"><a href="{tv_url(r)}" target="_blank" rel="noopener">{esc(r["sym"])}</a>'
            f'<span class="ex">{esc(r["exch"])}</span>{sp}<em>{esc(r["name"][:34])}</em></div>')

def price_cell(r):
    warn = ' <span class="warn">⚠價低於MA</span>' if r["below_ma"] else ""
    return f'<span class="nums">{r["close"]:g} <span class="mut">/ {r["ma"]:g}</span></span>{warn}'

def sector_chips(rows):
    cnt = {}
    for r in rows:
        k = (r["sector_zh"], r["sector"])
        cnt[k] = cnt.get(k, 0) + 1
    chips = "".join(f'<span class="chip"><b>{esc(z)}</b> {esc(e)} <i>{n}</i></span>'
                    for (z, e), n in sorted(cnt.items(), key=lambda x: -x[1]))
    return f'<div class="chips">{chips}</div>'

def table_page(p):
    pg = O["pages"][p]
    L, W = pg["L"], pg["W"]
    head = (f'<tr><th>#</th><th>Ticker</th><th>VCP指數<span class="thn">收縮度 0-100</span></th>'
            f'<th>MA{L}斜率<span class="thn">{W}日變幅</span></th><th>60日走勢</th>'
            f'<th>現價 / MA{L}</th><th>底部序列<span class="thn">45日內 · 遞升</span></th><th>類別</th></tr>')
    rows = []
    for i, r in enumerate(pg["rows"], 1):
        rows.append(
            f'<tr><td class="rk">{i}</td><td>{tick_cell(r)}</td>'
            f'<td>{vcp_bar(r["vcp"])}</td>'
            f'<td class="nums slope">{r["slope"]:+.2f}%</td>'
            f'<td>{spark_svg(r["spark"], L)}</td>'
            f'<td>{price_cell(r)}</td>'
            f'<td class="bots">{bottoms_chain(r["hl"])}</td>'
            f'<td>{sector_cell(r)}</td></tr>')
    return head, "".join(rows), pg

def table_page1():
    head = ('<tr><th>#</th><th>Ticker</th><th>爆發潛力分數<span class="thn">0.7×VCP + 0.3×覆蓋</span></th>'
            '<th>VCP指數</th><th>達標時間框<span class="thn">頁內排名</span></th><th>現價</th>'
            '<th>60日走勢</th><th>類別</th></tr>')
    rows = []
    for i, r in enumerate(O["page1"], 1):
        frames = []
        labels = {"2": "1週", "3": "2週", "4": "1月", "5": "2月"}
        for p in ("2", "3", "4", "5"):
            if p in r["ranks"]:
                frames.append(f'<span class="fr on">{labels[p]}<i>#{r["ranks"][p]}</i></span>')
            else:
                frames.append(f'<span class="fr">{labels[p]}</span>')
        rows.append(
            f'<tr><td class="rk">{i}</td><td>{tick_cell(r)}</td>'
            f'<td>{vcp_bar(r["score"], "vcpb score")}</td>'
            f'<td class="nums">{r["vcp"]:.1f}</td>'
            f'<td class="frs">{"".join(frames)}</td>'
            f'<td class="nums">{r["close"]:g}</td>'
            f'<td>{spark_svg(r["spark"], r["L"])}</td>'
            f'<td>{sector_cell(r)}</td></tr>')
    return head, "".join(rows)

c = M["counts"]
UNIVERSE_LINE = (f'Universe：全美上市普通股掃描 — 快照涵蓋 {c["total"]:,} 隻 · 現存續至 08-28 有報價 {c["current"]:,} 隻 · '
                 f'歷史 ≥90 交易日 {c["hist"]:,} 隻 · 價格 ≥$2 {c["price"]:,} 隻 · 流動性達標（20日中位成交額 ≥$1M）{c["liq"]:,} 隻合資格')

css = """
:root{color-scheme:light;--pg:#f9f9f7;--sf:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mut:#898781;
 --grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--seq:#2a78d6;--link:#1c5cab;--good:#006300;
 --warn:#8a5a00;--hl:#eef3fa;--meter:#dfe7f2}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;
 --pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;--grid:#2c2c2a;--axis:#383835;
 --ring:rgba(255,255,255,.10);--seq:#3987e5;--link:#6da7ec;--good:#0ca30c;--warn:#d99a2b;
 --hl:#16202d;--meter:#25303e}}
:root[data-theme="dark"]{color-scheme:dark;--pg:#0d0d0d;--sf:#1a1a19;--ink:#fff;--ink2:#c3c2b7;
 --mut:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--seq:#3987e5;
 --link:#6da7ec;--good:#0ca30c;--warn:#d99a2b;--hl:#16202d;--meter:#25303e}
*{box-sizing:border-box}
body{margin:0;background:var(--pg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Noto Sans TC",sans-serif}
.wrap{max-width:1280px;margin:0 auto;padding:26px 20px 60px}
h1{font-size:21px;margin:0 0 4px}
.sub{color:var(--ink2);font-size:12.5px;margin-bottom:14px}
.card{background:var(--sf);border:1px solid var(--ring);border-radius:10px;padding:14px 16px;margin-bottom:14px}
h2{font-size:13px;margin:0 0 8px;color:var(--ink2);font-weight:600}
.rules{font-size:12.5px;color:var(--ink2);line-height:1.65}
.rules b{color:var(--ink)}
.nav{position:sticky;top:0;z-index:5;display:flex;gap:6px;flex-wrap:wrap;background:var(--pg);
 padding:10px 0;border-bottom:1px solid var(--grid);margin-bottom:14px}
.nav button{font:600 13px/1 system-ui,"Noto Sans TC",sans-serif;color:var(--ink2);background:var(--sf);
 border:1px solid var(--ring);border-radius:20px;padding:9px 14px;cursor:pointer}
.nav button .s{display:block;font-weight:400;font-size:10.5px;color:var(--mut);margin-top:3px}
.nav button.on{color:var(--pg);background:var(--ink);border-color:var(--ink)}
.nav button.on .s{color:var(--pg);opacity:.75}
.pghead{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;margin:2px 0 10px;font-size:12.5px;color:var(--ink2)}
.pghead b{font-size:15px;color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.chip{font-size:11.5px;color:var(--ink2);background:var(--sf);border:1px solid var(--ring);
 border-radius:14px;padding:4px 10px}
.chip b{color:var(--ink)}
.chip i{font-style:normal;font-weight:700;color:var(--seq)}
.tblwrap{overflow-x:auto;background:var(--sf);border:1px solid var(--ring);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:1080px;font-size:12.5px}
th{position:sticky;top:0;text-align:left;font-size:11px;color:var(--mut);font-weight:600;
 padding:9px 10px;border-bottom:1px solid var(--grid);background:var(--sf);white-space:nowrap}
.thn{display:block;font-weight:400;font-size:10px}
td{padding:8px 10px;border-bottom:1px solid var(--grid);vertical-align:middle}
tr:last-child td{border-bottom:0}
tr:hover td{background:var(--hl)}
.rk{color:var(--mut);font-weight:600}
.nums{font-variant-numeric:tabular-nums;white-space:nowrap}
.mut{color:var(--mut)}
.slope{color:var(--good);font-weight:600}
.tk a{color:var(--link);font-weight:700;text-decoration:none;font-size:13.5px}
.tk a:hover{text-decoration:underline}
.tk .ex{font-size:10px;color:var(--mut);margin-left:6px}
.tk em{display:block;font-style:normal;font-size:10.5px;color:var(--mut);max-width:190px;
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.badge{font-size:9px;font-weight:700;color:var(--seq);border:1px solid var(--seq);
 border-radius:8px;padding:1px 5px;margin-left:6px;vertical-align:1px;white-space:nowrap}
.vcpb{display:flex;align-items:center;gap:8px;min-width:120px}
.vcpb .meter{flex:1;height:6px;border-radius:3px;background:var(--meter);min-width:60px}
.vcpb .meter i{display:block;height:100%;border-radius:3px;background:var(--seq)}
.vcpb b{font-variant-numeric:tabular-nums;font-size:12.5px}
.score .meter i{background:var(--good)}
.bots{max-width:280px}
.botwrap{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 4px;max-width:280px}
.bot{white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11.5px}
.bot i{font-style:normal;color:var(--mut);font-size:10.5px}
.arr{color:var(--axis);margin:0 4px}
.warn{color:var(--warn);font-size:10.5px;white-space:nowrap}
.sect b{font-size:12px}
.sect span{font-size:10.5px;color:var(--mut);margin-left:4px}
.sect em{display:block;font-style:normal;font-size:10.5px;color:var(--ink2)}
.gics{display:inline-block;font-style:normal;font-size:9px;color:var(--seq);border:1px solid var(--ring);border-radius:7px;padding:0 4px;margin-left:5px;vertical-align:1px}
.frs{white-space:nowrap}
.fr{display:inline-block;font-size:10.5px;color:var(--mut);border:1px dashed var(--axis);
 border-radius:9px;padding:2px 7px;margin-right:4px}
.fr.on{color:var(--ink);border:1px solid var(--seq);background:var(--hl)}
.fr.on i{font-style:normal;color:var(--seq);font-weight:700;margin-left:2px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11.5px;color:var(--ink2);margin:8px 2px 0}
.legend .sw{display:inline-block;width:14px;height:3px;vertical-align:3px;margin-right:5px;border-radius:2px}
.foot{font-size:11.5px;color:var(--ink2);line-height:1.7}
.foot b{color:var(--ink)}
section[hidden]{display:none}
@media (prefers-reduced-motion:no-preference){.nav button{transition:background .15s,color .15s}}
"""

rules_html = f"""
<div class="card rules">
<h2>篩選規則（R1 規則延伸至 4 個時間框 · 全美掃描）</h2>
① <b>{esc(UNIVERSE_LINE)}</b>。<br>
② <b>MA 上升</b>：各頁以自己的時間框比較 —— PAGE 2：<b>10 天 MA</b> 較 <b>5 個交易日</b>前高；PAGE 3/4/5：<b>20 天 MA</b> 分別較 <b>10 / 21 / 42 個交易日</b>前高；且 MA 最後 3 日逐日上升、期內 ≥70% 日子上升。<br>
③ <b>「底」</b>（用戶原話：「大約跌了三天，然後見底回升了大約三天」）：某日收盤係 ±3 日內最低，且 3 日前收盤高過佢（跌咗約三天）、3 日後收盤高過佢（回升約三天）；相鄰 ≤3 日重複底去重。<br>
④ <b>一底高於一底</b>：最後 45 個交易日內 ≥2 個底且逐個遞升；最近一個底喺 25 個交易日內（結構仍然活躍）。<br>
⑤ <b>VCP 指數（0–100，排名依據）</b>：波動越收縮分數越高 —— 10日波幅/前30日波幅（35%）＋ 近10日高低區間佔價（25%）＋ 近10日成交量/前30日成交量（乾涸，20%）＋ 近15日區間/前30–45日區間（逐段收縮，20%）；四項以全體合資格股票百分位排名合成。<br>
⑥ <b>爆發潛力分數（PAGE 1）</b>＝ 0.7 × VCP指數 ＋ 0.3 × 覆蓋度（達標時間框數 ÷ 4 × 100）—— 同時在多個時間框達標、而且波動最收縮嘅股票排最前。
</div>"""

secs = []
nav_btns = []
for pid, tab, subt, pno in PAGE_DEFS:
    on_cls = ' class="on"' if pid == "1" else ""
    nav_btns.append(f'<button data-p="{pid}"{on_cls}>{tab}<span class="s">{subt}</span></button>')
    if pid == "1":
        head, body = table_page1()
        pghead = (f'<div class="pghead"><b>總覽 · 爆發潛力排名</b>'
                  f'<span>4 個時間框 top 50 合共 <b>{len(O["page1"])}</b> 隻不重複股票</span>'
                  f'<span>排序 = 爆發潛力分數（VCP 收縮 × 時間框覆蓋）</span></div>')
        chips = sector_chips(O["page1"])
    else:
        head, body, pg = table_page(pid)
        pghead = (f'<div class="pghead"><b>{tab.split("·")[1].strip()} · {subt}</b>'
                  f'<span>合資格 <b>{pg["qualified"]}</b> 隻 → 按 VCP指數取 top 50</span>'
                  f'<span>MA{pg["L"]} 需較 {pg["W"]} 個交易日前高 + 一底高於一底</span></div>')
        chips = sector_chips(pg["rows"])
    secs.append(f'''<section id="p{pid}"{"" if pid == "1" else " hidden"}>
{pghead}{chips}
<div class="tblwrap"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>
<div class="legend"><span><i class="sw" style="background:var(--ink2)"></i>收盤</span>
<span><i class="sw" style="background:var(--seq)"></i>MA（頁面各自 10/20 天）</span>
<span><i class="sw" style="background:var(--good);height:8px;width:8px;border-radius:50%"></i>底部（最後60個交易日）</span></div>
</section>''')

foot = f"""
<div class="card foot">
<h2>備註 · 數據 lineage</h2>
① 覆蓋範圍：可達數據源覆蓋美國上市普通股 {c["total"]:,} 隻（含 S&amp;P 500 全部 503 隻）；外國註冊而非 S&amp;P 500 嘅美國上市股（部分 ADR）未有完整歷史，未納入掃描。價格未除息調整。<br>
② 數據重建：GitHub 每日 Nasdaq 快照鏡像（zyhe16/top-us-stock-tickers）逐 commit 重建每日收盤序列，共 {M["n_days"]} 個交易日（{M["cal_first"]} → {M["cal_last"]}）；其中 4 日（03-18、08-11、08-12、08-26）無快照，以前值填補；08-27 收盤以官方 net-change 校正。與 R1 報告抽樣核對：底部價格 10/10 完全一致，20MA 平均偏差 0.18%。<br>
③ 類別：Nasdaq 分類（全體）＋ GICS Sector / Sub-Industry（S&amp;P 500 成分股，klaywang24/market-chronicle）；交易所：irachex/open-stock-data。<br>
④ VCP 只用收盤/成交量計算（快照無日內高低價）；經 6 組獨立代理人對抗性驗證（lineage / 條件 / VCP 數學 / 規格）。<br>
⑤ <b>數據終點 {M["last_date"]}，建置時間 {BUILD_TS}</b> ·（週末，08-28 五係最後交易日）· 本表只係篩選工具，唔係投資建議。<br>
⑥ 連結格式：Ticker 點擊開 TradingView chart（https://www.tradingview.com/chart/Q1c5VWwD/?symbol=交易所%3Aticker）。
</div>"""

html_doc = f"""<title>20MA Uptrend Watchlist R2</title>
<style>{css}</style>
<div class="wrap">
<h1>20MA Uptrend Watchlist R2（一底高於一底 × VCP 收縮排名）</h1>
<div class="sub">數據至 <b>{M["last_date"]}</b> 收盤 · 全美掃描 {c["liq"]:,} 隻合資格 · 5 頁：總覽＋4 個時間框（1星期/2星期/1個月/2個月）· 排名 = VCP 收縮指數（越收縮越前，爆發機會越大）</div>
{rules_html}
<nav class="nav">{"".join(nav_btns)}</nav>
{"".join(secs)}
{foot}
</div>
<script>
(function() {{
  var btns = document.querySelectorAll('.nav button');
  function show(p) {{
    document.querySelectorAll('section[id^="p"]').forEach(function(s) {{ s.hidden = (s.id !== 'p' + p); }});
    btns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.p === p); }});
    try {{ localStorage.setItem('r2page', p); }} catch (e) {{}}
  }}
  btns.forEach(function(b) {{ b.addEventListener('click', function() {{ show(b.dataset.p); }}); }});
  var saved = null;
  try {{ saved = localStorage.getItem('r2page'); }} catch (e) {{}}
  if (saved && document.getElementById('p' + saved)) show(saved);
}})();
</script>
"""

out_path = f"{SCRATCH}/{OUTNAME}"
open(out_path, "w", encoding="utf-8").write(html_doc)
print("wrote", out_path, f"{len(html_doc)/1024:.0f} KB")
