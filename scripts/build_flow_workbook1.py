# -*- coding: utf-8 -*-
"""Render a money-flow watchlist as an Excel workbook (Sub-Sector or AI Sector).

Same content as the HTML report pages, one page per worksheet. Both watchlists share a
schema, so one builder serves both; MODE picks the labels, the extra AI-only sheets and
the output name.

    python3 scripts/build_flow_workbook1.py sub   # SubSector  R12.00
    python3 scripts/build_flow_workbook1.py ai    # AI Sector  R13.00
"""
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

MODE = (sys.argv[1] if len(sys.argv) > 1 else "sub").lower()
CFG = {
 "sub": dict(src="data/subsector_flow12.json", rev="R12.00", key="zh",
             title="Sub-Sector 資金流向 Watchlist", unit="子板塊", n_expect=111,
             out="reports/SubSector_flow_watchlist_R12.00_claudeopus5high_09.18_0937.xlsx"),
 "ai":  dict(src="data/ai_flow13.json", rev="R13.00", key="zh",
             title="AI Sector 資金流向 Watchlist", unit="AI 小群組", n_expect=41,
             out="reports/AI_Sector_watchlist_R13.00_claudeopus5high_09.18_0937.xlsx"),
}[MODE]

F = json.load(open(CFG["src"]))
M, ROWS = F["meta"], F["rows"]
DAYS = M["days"]
LIVE = [r for r in ROWS if r.get("days")]
LIVE.sort(key=lambda r: r["rank"])
BUILT = "2026-09-18 09:37 HKT"

FNT = "Arial"
NAVY, SLATE, BAND = "1F3864", "2E5A88", "F2F5F9"
INK  = Font(name=FNT, size=10)
BOLD = Font(name=FNT, size=10, bold=True)
BLUE = Font(name=FNT, size=10, color="0000FF")
RED  = Font(name=FNT, size=10, color="C00000", bold=True)
MUT  = Font(name=FNT, size=9,  color="595959")
HDR  = Font(name=FNT, size=10, bold=True, color="FFFFFF")
LINK = Font(name=FNT, size=10, bold=True, color="0563C1", underline="single")
T1   = Font(name=FNT, size=16, bold=True, color=NAVY)
T2   = Font(name=FNT, size=11, bold=True, color=SLATE)
FH, FH2 = PatternFill("solid", fgColor=NAVY), PatternFill("solid", fgColor=SLATE)
FG  = PatternFill("solid", fgColor="E2EFDA")
FR  = PatternFill("solid", fgColor="FCE4E4")
FA  = PatternFill("solid", fgColor="FFF2CC")
FB  = PatternFill("solid", fgColor=BAND)
WRAP = Alignment(wrap_text=True, vertical="top")
CTR  = Alignment(horizontal="center", vertical="center")
PCT, USD, NUM, SC1, MUL = '0.00%;[Red](0.00%);-', '$#,##0;($#,##0);-', '#,##0', '0.0', '0.00"x"'

wb = Workbook(); wb.remove(wb.active)

def tv(t): return f"https://www.tradingview.com/chart/Q1c5VWwD/?symbol={t.lower()}"

def sheet(name, widths, freeze=None, tab=None):
    ws = wb.create_sheet(name)
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    if freeze: ws.freeze_panes = freeze
    if tab: ws.sheet_properties.tabColor = tab
    return ws

def title(ws, t, sub, span):
    ws["A1"] = t; ws["A1"].font = T1
    ws["A2"] = sub; ws["A2"].font = MUT
    ws.merge_cells(f"A1:{get_column_letter(span)}1"); ws.merge_cells(f"A2:{get_column_letter(span)}2")
    ws.row_dimensions[1].height = 22

def header(ws, row, labels, fill=FH):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = HDR; c.fill = fill
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[row].height = 30

def put(ws, r, c, v, font=INK, fmt=None, fill=None, align=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = font
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    if align: cell.alignment = align
    return cell

def putlink(ws, r, c, t):
    cell = put(ws, r, c, t, LINK, align=CTR); cell.hyperlink = tv(t); return cell

SUB = f"基準 {DAYS[-1]} 美東收市　·　視窗 {DAYS[0]} → {DAYS[-1]}　·　生成 {BUILT}　·　claude-opus-5 / high"
PROV = set(M.get("provisional_vol_days") or [])
MFD_MARK = "※" if PROV else ""

# ─────────────────────────── 1. 摘要 ───────────────────────────
ws = sheet("摘要 Summary", [22, 15, 15, 15, 15, 15, 46], tab=NAVY)
title(ws, f"{CFG['title']} {CFG['rev']}", SUB, 7)
r = 4
put(ws, r, 1, "一、全巿中位回報（平衡面板）", T2); r += 1
header(ws, r, ["交易日"] + DAYS + ["面板檔數"], FH2); r += 1
put(ws, r, 1, "中位回報", BOLD)
for i, d in enumerate(DAYS): put(ws, r, 2 + i, M["mkt_med"][d], INK, PCT)
put(ws, r, 2 + len(DAYS), M["mkt_n"][DAYS[-1]], BLUE, NUM, None, CTR)
r += 2

put(ws, r, 1, f"二、資金流入最強 12 個{CFG['unit']}", T2); r += 1
header(ws, r, ["名次", "名稱", "5日分數", "5日回報", "5日廣度", "斜率", f"5日淨額{MFD_MARK}"], FH2); r += 1
for x in LIVE[:12]:
    put(ws, r, 1, x["rank"], BOLD, NUM, None, CTR)
    put(ws, r, 2, x["zh"], BOLD, align=WRAP)
    put(ws, r, 3, x["score5"], INK, SC1, None, CTR)
    put(ws, r, 4, x["ret5"], INK, PCT)
    put(ws, r, 5, x["breadth5"], INK, '0.00', None, CTR)
    put(ws, r, 6, x["slope"], INK, '+0.00;-0.00;0.00', None, CTR)
    put(ws, r, 7, x["mfd5"] / 1e6, INK, USD)
    for c in range(1, 8): ws.cell(row=r, column=c).fill = FG
    r += 1
r += 1
put(ws, r, 1, f"三、資金流出最強 12 個{CFG['unit']}", T2); r += 1
header(ws, r, ["名次", "名稱", "5日分數", "5日回報", "5日廣度", "斜率", f"5日淨額{MFD_MARK}"], FH2); r += 1
for x in LIVE[-12:]:
    put(ws, r, 1, x["rank"], BOLD, NUM, None, CTR)
    put(ws, r, 2, x["zh"], BOLD, align=WRAP)
    put(ws, r, 3, x["score5"], INK, SC1, None, CTR)
    put(ws, r, 4, x["ret5"], INK, PCT)
    put(ws, r, 5, x["breadth5"], INK, '0.00', None, CTR)
    put(ws, r, 6, x["slope"], INK, '+0.00;-0.00;0.00', None, CTR)
    put(ws, r, 7, x["mfd5"] / 1e6, INK, USD)
    for c in range(1, 8): ws.cell(row=r, column=c).fill = FR
    r += 1
r += 1
put(ws, r, 1, "四、本版重點", T2); r += 1
NOTES = [
 f"視窗 {DAYS[0]} → {DAYS[-1]}，{len(LIVE)} 個{CFG['unit']}計分（共 {len(ROWS)} 個）。",
 "⚠ 2026-09-17：日線鏡像把該日發佈為只有成交量、沒有價格的列（1,499 個檔案 OHLC 全空），"
 "價格全部來自 Yahoo tail 抓取。週轉率檢查看不到這種故障 —— 成交量是完整的（鏡像週轉率 1.0585），缺的是價格。",
 "⚠ 2026-09-17 的成交量不是結算印記（結算佔比 0.6%），引擎把該日所有名字的量能項 B 歸零；"
 "當日分數只由方向與收市位置構成，淨額估算屬臨時值（以 ※ 標記）。",
 "✔ 本版修正 LNG 缺陷：成分股 NFE 做過反向拆股而 Yahoo 的 close 與 adj_close 都沒有還原"
 "（0.33 → 12.77），舊版讀成 +3771% 單日回報，令該組 5 日回報印成 +9111%。"
 "新增的企業行動防護已把 NFE 於 2026-09-14 剔除，該組 5 日回報回復為 −4.65%。",
 "所謂「資金流向」全部由價格、成交量與收盤位置推算 —— 環境內無法取得 ETF 申贖或 13F 數據。",
]
if MODE == "ai":
    NOTES.insert(1, f"⚠ 儀表板分類的 as-of 為 {M.get('asof_dash')}，距最新計分日 {M.get('asof_gap_sessions')} 個交易日；"
                    f"RS 象限等欄位屬該日數值，與資金流計分視窗時點不同。")
    NOTES.insert(2, f"{len(ROWS) - len(LIVE)} 個群組無法計分（成分股全部非美股上市／無 US ADR，或美股樣本不足），見「未能計分」頁。")
for line in NOTES:
    put(ws, r, 1, "• " + line, INK, align=WRAP)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    ws.row_dimensions[r].height = 30 if len(line) < 90 else 44
    r += 1
r += 1
put(ws, r, 1, "本表為研究紀錄，非投資建議。方法與限制見「方法與限制」頁。", MUT)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)

# ─────────────────────────── 2. 總表 ───────────────────────────
NTK = max(len(x["basket"]) for x in LIVE) if LIVE else 0
ws = sheet("總表 All", [7, 24, 30, 16, 9, 9, 9, 9, 9, 8, 13, 13, 8] + [9] * NTK,
           freeze="D9", tab=SLATE)
title(ws, f"全部 {len(ROWS)} 個{CFG['unit']}（按 5 日綜合分排序）",
      SUB + f"　·　成分股可點擊開 TradingView　·　{MFD_MARK} 淨額含未結算成交量", 13 + NTK)
CAT = "大板塊" if MODE == "sub" else "分類"
header(ws, 8, ["名次", "名稱", "English", CAT, "5日\n分數", f"{DAYS[-1][5:]}\n分數",
               f"{DAYS[-1][5:]}\n漲跌%", "5日\n漲跌%", "5日\n廣度", "斜率",
               f"{DAYS[-1][5:]} 淨額{MFD_MARK}\n(US$ 百萬)", f"5日 淨額{MFD_MARK}\n(US$ 百萬)", "樣本"]
             + [f"成分股\n{i}" for i in range(1, NTK + 1)])
r = 9
for x in LIVE:
    d = x["days"].get(DAYS[-1])
    put(ws, r, 1, x["rank"], BOLD, NUM, None, CTR)
    put(ws, r, 2, x["zh"], BOLD, align=WRAP)
    put(ws, r, 3, (x.get("en") or x.get("sub") or ""), MUT, align=WRAP)
    put(ws, r, 4, (x.get("sector") or x.get("cat") or ""), MUT, align=WRAP)
    put(ws, r, 5, x["score5"], INK, SC1, None, CTR)
    put(ws, r, 6, (d["score"] if d else None), INK, SC1, None, CTR)
    put(ws, r, 7, (d["ret"] if d else None), INK, PCT)
    put(ws, r, 8, x["ret5"], INK, PCT)
    put(ws, r, 9, x["breadth5"], INK, '0.00', None, CTR)
    put(ws, r, 10, x["slope"], INK, '+0.00;-0.00;0.00', None, CTR)
    put(ws, r, 11, (d["mfd"] / 1e6 if d else None), INK, USD)
    put(ws, r, 12, x["mfd5"] / 1e6, INK, USD)
    put(ws, r, 13, x["n_basket"], INK, NUM, None, CTR)
    for j, t in enumerate(x["basket"]): putlink(ws, r, 14 + j, t)
    if x["rank"] <= 12:
        for c in range(1, 14 + NTK): ws.cell(row=r, column=c).fill = FG
    elif x["rank"] > len(LIVE) - 12:
        for c in range(1, 14 + NTK): ws.cell(row=r, column=c).fill = FR
    r += 1
ws.auto_filter.ref = f"A8:{get_column_letter(13 + NTK)}{r - 1}"

# ─────────────────────────── 3. 逐日分數 ───────────────────────────
ws = sheet("逐日分數 Daily", [7, 26, 11, 11, 11, 11, 11, 10, 46], freeze="C9", tab="7B4F9D")
title(ws, "逐日資金流分數（0–100 橫截面百分位）",
      SUB + "　·　每日分數為該日全部計分單位的橫截面排名，100 = 當日最強", 9)
header(ws, 8, ["名次", "名稱"] + [d[5:] for d in DAYS] + ["5日\n綜合", "逐日等級（−3 … +3）"])
r = 9
for x in LIVE:
    put(ws, r, 1, x["rank"], BOLD, NUM, None, CTR)
    put(ws, r, 2, x["zh"], BOLD, align=WRAP)
    for i, d in enumerate(DAYS):
        v = x["days"].get(d)
        c = put(ws, r, 3 + i, (v["score"] if v else None), INK, SC1, None, CTR)
        if v:
            c.fill = FG if v["score"] >= 75 else FR if v["score"] <= 25 else FB
    put(ws, r, 3 + len(DAYS), x["score5"], BOLD, SC1, None, CTR)
    put(ws, r, 4 + len(DAYS), " ".join(f"{x['days'][d]['grade']:+d}" if x["days"].get(d) else " ." for d in DAYS),
        MUT, align=CTR)
    r += 1
ws.auto_filter.ref = f"A8:I{r - 1}"

# ─────────────────── 4. 成分股資金流（AI 版才有 ticks）───────────────────
if MODE == "ai":
    ws = sheet("成分股資金流 Constituents", [7, 24, 9, 22, 11, 11, 13, 13, 9, 9], freeze="D9", tab="2E7D32")
    title(ws, "成分股逐隻 5 日資金流（按組內強弱排序）",
          SUB + "　·　tf5 為該股 5 日加權強度（權重 1.0/1.15/1.35/1.6/1.9，越近越重）", 10)
    header(ws, 8, ["組別\n名次", "所屬群組", "代號", "來源", "5日\n強度 tf5", "5日\n漲跌%",
                   f"5日 淨額{MFD_MARK}\n(US$ 百萬)", "5日 成交金額\n(US$ 百萬)", "無量\n日數", "無基準"])
    r = 9
    for x in LIVE:
        for t in x["ticks"]:
            put(ws, r, 1, x["rank"], INK, NUM, None, CTR)
            put(ws, r, 2, x["zh"], INK, align=WRAP)
            putlink(ws, r, 3, t["sym"])
            put(ws, r, 4, t["src"], MUT, align=CTR)
            put(ws, r, 5, t["tf5"], BOLD, '+0.000;-0.000;0.000', None, CTR)
            put(ws, r, 6, t["ret5"], INK, PCT)
            put(ws, r, 7, t["mfd5"] / 1e6, INK, USD)
            put(ws, r, 8, t["dv5"] / 1e6, INK, USD)
            put(ws, r, 9, t["novol"], INK, NUM, None, CTR)
            put(ws, r, 10, ("是" if t["nobase"] else "—"), (RED if t["nobase"] else MUT), align=CTR)
            c = ws.cell(row=r, column=5)
            c.fill = FG if t["tf5"] > 0.25 else FR if t["tf5"] < -0.25 else FB
            r += 1
    ws.auto_filter.ref = f"A8:J{r - 1}"

    dead = [x for x in ROWS if not x.get("days")]
    ws = sheet("未能計分 Unscorable", [9, 28, 22, 14, 44, 40], tab="B71C1C")
    title(ws, f"{len(dead)} 個無法計分的群組", SUB + "　·　按規則不以其他股票代替，原因逐項列明", 6)
    header(ws, 8, ["代碼", "群組", "分類", "美股成分股", "原因", "非美股成分股（已排除）"])
    r = 9
    for x in dead:
        put(ws, r, 1, x.get("code", ""), BOLD, align=CTR)
        put(ws, r, 2, x["zh"], BOLD, align=WRAP)
        put(ws, r, 3, x.get("cat", ""), MUT, align=WRAP)
        put(ws, r, 4, len(x.get("us") or []), INK, NUM, None, CTR)
        put(ws, r, 5, x.get("note", ""), RED, align=WRAP)
        put(ws, r, 6, "、".join(x.get("nonus") or []) or "—", MUT, align=WRAP)
        for c in range(1, 7): ws.cell(row=r, column=c).fill = FR
        ws.row_dimensions[r].height = 30
        r += 1

# ─────────────────────────── 5. 資料品質 ───────────────────────────
ws = sheet("資料品質 Data Quality", [30, 60, 62], tab="B8860B")
title(ws, "資料品質與本次抓取的實際狀況", SUB, 3)
r = 4
put(ws, r, 1, "一、逐個交易日的來源與判定", T2); r += 1
header(ws, r, ["項目"] + DAYS[-3:] + [""], FH2)
for i, d in enumerate(DAYS[-3:]): ws.cell(row=r, column=2 + i, value=d)
r += 1
REL = M.get("relvol_by_source") or {}
for lab, get in [
    ("鏡像週轉率（對自身 20 日中位）", lambda d: (REL.get("mirror") or {}).get(d)),
    ("Yahoo 週轉率", lambda d: (REL.get("yahoo") or {}).get(d)),
    ("結算印記佔比", lambda d: (M.get("settled_print_share") or {}).get(d)),
    ("鏡像覆蓋（報表宇宙）", lambda d: (M.get("mirror_coverage") or {}).get(d)),
    ("鏡像「有量無價」列數", lambda d: (M.get("mirror_priceless") or {}).get(d)),
]:
    put(ws, r, 1, lab, BOLD, align=WRAP)
    for i, d in enumerate(DAYS[-3:]):
        v = get(d)
        put(ws, r, 2 + i, v, (RED if lab.startswith("鏡像「有量無價」") and v else INK),
            ('0.000' if "率" in lab or "佔比" in lab else NUM), None, CTR)
    r += 1
r += 1
put(ws, r, 1, "二、引擎的判定結果", T2); r += 1
header(ws, r, ["判定", "結果", "說明"], FH2); r += 1
VER = [
 ("計分交易日", "、".join(DAYS), "每個來源以自身宇宙量度覆蓋率，任一來源完整即計入"),
 ("盤中快照剔除", str(M.get("mid_session_dropped")), "跨來源裁決：一個來源低於另一個來源的 0.75 倍才算盤中"),
 ("無法裁決而拒用", str(M.get("unadjudicated_sessions") or "無"), "只有單一來源而該來源偏輕的交易日，寧可拒用"),
 ("成交量未結算", str(M.get("provisional_vol_days") or "無"), "結算印記（成交量為 100 的整數倍）佔比低於 50% 即判未結算"),
 ("淨額估算是否結算", str(M.get("mfd_settled")), "False 的交易日，該日淨額屬臨時值"),
 ("鏡像有量無價", str(M.get("mirror_priceless") or "無"), "★ 本版新增偵測：成交量完整而 OHLC 全空，週轉率檢查看不到"),
 ("企業行動剔除", str(M.get("split_dropped") or "無"), "★ 本版新增防護：close 未還原拆股，該股該日及之前的歷史一併剔除"),
 ("tail 抓取檔案", str(M.get("tail_files") or "無"), "★ 本版起可合併多於一次 tail 抓取（報表名單 + broad 名單）"),
 ("平衡市場面板", f"{M['mkt_n'][DAYS[-1]]:,} 檔（未平衡池 {M.get('panel_pool'):,}）", "只計每個計分日及其前一日均有報價的股票"),
 ("已計分 / 已剔除", f"{M.get('n_tick')} 隻計分，{len(M.get('dropped') or [])} 隻剔除", "剔除＝視窗內無可用價量"),
]
for a, b, c in VER:
    put(ws, r, 1, a, BOLD, align=WRAP)
    put(ws, r, 2, b, (RED if a.startswith("★") or "有量無價" in a else INK), align=WRAP)
    put(ws, r, 3, c, MUT, align=WRAP)
    if "★" in c: 
        for cc in range(1, 4): ws.cell(row=r, column=cc).fill = FA
    ws.row_dimensions[r].height = 32
    r += 1

# ─────────────────────────── 6. 方法與限制 ───────────────────────────
ws = sheet("方法與限制 Method", [26, 96], tab="595959")
title(ws, "計分方法與已知限制", SUB, 2)
r = 4
put(ws, r, 1, "計分公式", T2); r += 1
for a, b in [
 ("方向 A", "tanh((個股回報 − 全巿中位回報) / 0.02)"),
 ("量能 B", "clip(log2(clip(成交量 / 20 日中位量, 0.25, 4)) / 2, −1, 1)；成交量未知時 B held at 0"),
 ("收位 C", "((收 − 低) − (高 − 收)) / (高 − 低)"),
 ("單股強度 f", "(0.70·A + 0.30·C) × (1 + 0.50·B)"),
 ("籃子", "以成交金額加權，逐次注水法把單一成分上限壓至 40%"),
 ("每日分數", "橫截面 z 分數轉百分位（0–100）"),
 ("5 日綜合", "權重 [1.0, 1.15, 1.35, 1.6, 1.9]，越近的交易日權重越高"),
 ("淨額估算 mfd", "Σ(收位 C × 成交金額) —— 價量代理，不是實際資金申贖"),
]:
    put(ws, r, 1, a, BOLD); put(ws, r, 2, b, INK, align=WRAP); r += 1
r += 1
put(ws, r, 1, "已知限制", T2); r += 1
LIM = [
 ("無真實資金流數據", "13F、ETF 申購贖回、委託簿在本環境不可達，所有「資金流向」均由價格、成交量與收盤位置推算。"),
 ("最新交易日無量能確認", f"{DAYS[-1]} 的成交量來自 Yahoo 小時線折疊，不是結算印記，量能項 B 對該日所有名字歸零。"),
 ("市場面板縮小", f"平衡面板 {M['mkt_n'][DAYS[-1]]:,} 檔，低於鏡像正常運作時的約 1,658 檔 —— "
                 f"因為 {DAYS[-1]} 只有 Yahoo 小時線覆蓋到的名字有價。"),
 ("淨額估算對成交量誤差敏感", "實測未結算 vs 結算：分數 p95 差 1.82 分（滿分 100）、名次最多差 4；"
                 "但淨額估算中位差 1.22%、p95 16.3%、最大 75.4%。因為分數經 log 壓縮再橫向排名，淨額則是成交量的線性函數。"),
 ("企業行動", "close 未還原拆股的個股，其該日及之前的歷史會被整段剔除（見「資料品質」頁）。"
             "Yahoo 對某些代號連 adj_close 都沒有還原，所以除了 close/adj_close 比值外，另設單日 4 倍的絕對門檻。"),
]
if MODE == "ai":
    LIM.append(("AI 籃子偏薄", f"AI 供應鏈重心在亞洲，{len(ROWS) - len(LIVE)} 個群組因成分股全部非美股上市而無法計分；"
                              "其餘群組的美股樣本中位數亦偏低。按規則不以其他股票代替。"))
    LIM.append(("分類 as-of 不同步", f"儀表板分類的 as-of 為 {M.get('asof_dash')}，距最新計分日 {M.get('asof_gap_sessions')} 個交易日。"))
for a, b in LIM:
    put(ws, r, 1, a, BOLD, align=WRAP); put(ws, r, 2, b, INK, align=WRAP)
    ws.row_dimensions[r].height = 40; r += 1
r += 1
put(ws, r, 1, "資料來源", T2); r += 1
put(ws, r, 1, "價量", BOLD)
put(ws, r, 2, M.get("source_note", ""), INK, align=WRAP); r += 1
put(ws, r, 1, "本表性質", BOLD)
put(ws, r, 2, "研究紀錄，非投資建議。", INK)

wb.calculation.fullCalcOnLoad = True
wb.save(CFG["out"])
print("saved", CFG["out"], f"({len(wb.sheetnames)} sheets)")
