#!/usr/bin/env python3
"""Revenue / profit workbook for every ticker in the Sub-Sector R4.00 and AI Sector R5.00
money-flow watchlists, laid out the way AI_Growth_Breakeven_Watchlist_R7.xlsx is.

Inputs  : data/subsector_flow4.json, data/ai_flow5.json (membership),
          data/yahoo/fundamentals_income.csv, data/yahoo/fundamentals_profile.csv
Output  : Watchlist_Revenue_Profit_R1.00_<model>_<mm.dd_HHMM>.xlsx

Reported line items are written as values (they are the workbook's inputs); every derived
figure — growth, margins, grade, group totals — is an Excel formula, so the sheet recomputes
if a number is corrected.
"""
import csv, collections, datetime, json, os, re

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inject_cached import inject

CACHE = {}
def F(ws, row, col, formula, value):
    """Write a live formula and remember what it evaluates to, so the saved file also
    carries the cached result (LibreOffice cannot run here to compute them)."""
    ws.cell(row=row, column=col, value=formula)
    CACHE.setdefault(ws.title, {})[f"{get_column_letter(col)}{row}"] = value
    return value

def div(a, b):
    return (a / b) if (a is not None and b not in (None, 0)) else ""


REPO = os.environ.get("REPO_DIR", "/home/user/20MAwarchlist")
OUT_DIR = os.environ.get("OUT_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
now_hkt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
STAMP = now_hkt.strftime("%m.%d_%H%M")
BUILD_TS = now_hkt.strftime("%Y-%m-%d %H:%M HKT")
VER = "R1.00"
OUT = f"{OUT_DIR}/Watchlist_Revenue_Profit_{VER}_claudeopus5high_{STAMP}.xlsx"

# ---------------- palette lifted from the template ----------------
NAVY, GREY, BLUE, TEAL = "FF1F4E78", "FF404040", "FF2E75B6", "FF1F7A8C"
REV_FILL, PRF_FILL = "FFEAF1F8", "FFFCEAEA"
GRADE_FILL = {"A": "FFC6EFCE", "B": "FFFFEB9C", "C": "FFFFD8A8", "D": "FFFFC7CE", "—": "FFF2F2F2"}
FONT = "Arial"
THIN = Side(style="thin", color="FFD9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def hfill(c, colour):
    c.fill = PatternFill("solid", fgColor=colour)
    c.font = Font(name=FONT, bold=True, size=9.5, color="FFFFFFFF")
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = BORDER

# ---------------- membership ----------------
SUB = json.load(open(f"{REPO}/data/subsector_flow4.json"))
AI = json.load(open(f"{REPO}/data/ai_flow5.json"))
sub_of, ai_of = collections.defaultdict(list), collections.defaultdict(list)
sub_rows, ai_rows = {}, {}
for r in SUB["rows"]:
    if not r.get("basket"): continue
    sub_rows[r["zh"]] = r
    for t in r["basket"]: sub_of[t].append(r["zh"])
for r in AI["rows"]:
    if not r.get("basket"): continue
    ai_rows[r["code"]] = r
    for t in r["basket"]: ai_of[t].append(r["code"])
UNIVERSE = sorted(set(sub_of) | set(ai_of))
WIN = SUB["meta"]["days"][-1]

# ---------------- fundamentals ----------------
inc = collections.defaultdict(lambda: {"annual": {}, "quarterly": {}})
with open(f"{REPO}/data/yahoo/fundamentals_income.csv", newline="") as f:
    for r in csv.DictReader(f):
        def num(k):
            v = r.get(k)
            try: return float(v) if v not in (None, "", "None") else None
            except ValueError: return None
        inc[r["symbol"]][r["period_type"]][r["period_end"]] = {
            k: num(k) for k in ("total_revenue", "gross_profit", "operating_income",
                                "net_income", "ebitda", "diluted_eps", "rnd")}
pro = {}
with open(f"{REPO}/data/yahoo/fundamentals_profile.csv", newline="") as f:
    for r in csv.DictReader(f): pro[r["symbol"]] = r

M = 1e6
def q_series(sym, key, n=5):
    """The n most recent quarters, oldest first, as (period_end, value in millions)."""
    q = inc.get(sym, {}).get("quarterly", {})
    per = sorted(q, reverse=True)[:n][::-1]
    return [(p, (q[p][key] / M if q[p][key] is not None else None)) for p in per]

def annual_latest(sym):
    a = inc.get(sym, {}).get("annual", {})
    if not a: return None, {}
    p = sorted(a, reverse=True)[0]
    return p, a[p]

def qlabel(p):
    """2026-06-30 -> 26Q2 (calendar quarter of the period end)."""
    try:
        d = datetime.date.fromisoformat(p)
    except ValueError:
        return p
    return f"{d.year % 100:02d}Q{(d.month - 1) // 3 + 1}"

# ---------------- workbook ----------------
wb = openpyxl.Workbook()

# ============ 1. 說明 ============
ws = wb.active; ws.title = "說明"
ws.column_dimensions["A"].width = 124
EXPL = [
 (f"美股觀察名單 — 全體成分股「營收 / 營利」對照表 {VER}", 14, True, NAVY),
 (f"編製時間 {BUILD_TS} ｜ {len(UNIVERSE)} 隻 ｜ 涵蓋 Sub-Sector Watchlist R4.00（491 隻）與 AI Sector Watchlist R5.00（111 隻），70 隻兩表重疊", 10, False, None),
 ("", 10, False, None),
 ("【本表用途】", 11, True, None),
 ("• 兩份資金流向報告只看價量，唔睇基本面。本表補上每隻成分股嘅「賺唔賺到錢」——最近五個季度營收、四個季度營業利益、",
  10, False, None),
 ("  以及最新一季嘅毛利率／營業利益率／淨利率，令「資金流入邊個板塊」可以同「邊個板塊真係有盈利」對照睇。", 10, False, None),
 ("", 10, False, None),
 ("【版面沿用 AI_Growth_Breakeven_Watchlist_R7.xlsx】", 11, True, None),
 ("• 同樣係「說明 / 主表 / 分級彙總 / 圖表連結 / 資料來源」結構；主表凍結窗格、開篩選、營收欄淺藍底、營利欄淺紅底、級別欄按等級上色。", 10, False, None),
 ("• 同樣將營收寫成純數字（單位「百萬」寫喺表頭），可直接排序、計算按季變動、畫圖；幣別與季度對照獨立成欄。", 10, False, None),
 ("• 不同之處（因為資料來源唔同，必須講清楚）：", 10, True, None),
 ("   R7 嘅「淨利｜經常｜一次」三行拆解、「一次性項目清單」、「經常性軌跡」係逐間公司人手查財報寫出嚟嘅。", 10, False, None),
 ("   本表 532 隻全部由 Yahoo Finance 財報 API 自動抓取，冇人手核實每間公司嘅一次性項目，所以唔會憑空寫呢三欄。", 10, False, None),
 ("   取而代之，本表用「營業利益」(Operating Income) 作為經常性盈利嘅代理 —— 佢本身已剔除大部分投資收益、", 10, False, None),
 ("   資產出售、稅務等非營運項目，係喺無人手核實嘅前提下最接近 R7「經常」口徑嘅公開數字。", 10, False, None),
 ("   如果需要 R7 式嘅逐隻一次性項目拆解，要另行逐間公司查財報，唔可以由本表自動生成。", 10, False, None),
 ("", 10, False, None),
 ("【欄位說明 — 主表「觀察名單」】", 11, True, None),
 ("• B 美股 Ticker：按落去開 TradingView 圖表（沿用 /chart/Q1c5VWwD/ layout）。", 10, False, None),
 ("• C 子板塊：Sub-Sector Watchlist R4.00 入面呢隻股所屬嘅子板塊；一隻股可屬多個子板塊，以「、」分隔。空白 = 只喺 AI 表。", 10, False, None),
 ("• E AI 小群組：AI Sector Watchlist R5.00 嘅小群組代號與名稱；若唔喺 AI 表，改為顯示 Yahoo 嘅行業分類。", 10, False, None),
 ("• F 幣別：財報呈報幣別（financialCurrency）。並非全部都係美元 —— 部分 ADR 以本國幣別呈報，跨股比較金額前要睇呢欄。", 10, False, None),
 ("• G 季度對照：H–L 五欄實際對應嘅五個財季（按財報期末日換算成日曆季）。各公司財政年度唔同，冇呢欄就會拿錯期比較。", 10, False, None),
 ("• H–L 營收 Q-4→Q0：五個季度營業收入，單位百萬（幣別見 F 欄）。Q0 = 最新已公布季度。", 10, False, None),
 ("• M 營收按年 %：公式 = Q0 ÷ Q-4 − 1，即最新季對上年同季（五季相隔四季）。", 10, False, None),
 ("• N–Q 營業利益 Q-3→Q0：四個季度營業利益（Operating Income），單位百萬。負數以括號顯示。", 10, False, None),
 ("• R 營業利益率、T 毛利率、V 淨利率：公式 = 對應損益項 ÷ 同季營收。", 10, False, None),
 ("• W–Y 年度數字：最近一個完整財政年度嘅營收、營業利益與利益率（年報口徑，非四季加總）。", 10, False, None),
 ("• Z 盈利狀態 / AA 級：由 N–Q 四季營業利益用公式判定，定義見下。", 10, False, None),
 ("• AB 資料截至：Q0 嘅財報期末日。", 10, False, None),
 ("", 10, False, None),
 ("【分級定義 — 全部由公式計算，非人手評級】", 11, True, None),
 ("  A  四季營業利益全部為正 —— 持續盈利", 10, False, None),
 ("  B  最新季營業利益為正，但四季之中有負 —— 剛轉正或有波動", 10, False, None),
 ("  C  最新季營業利益為負，但較 Q-3 收窄 —— 虧損收窄", 10, False, None),
 ("  D  最新季營業利益為負且較 Q-3 擴大（或由正轉負） —— 惡化", 10, False, None),
 ("  —  四季營業利益唔齊，無法判定", 10, False, None),
 ("", 10, False, None),
 ("【必須留意嘅限制】", 11, True, None),
 ("• 本表數字係 Yahoo Finance 整理嘅財報數據，非直接讀取 SEC 原文；個別公司嘅重分類、重述或非標準列報可能同公告有出入，", 10, False, None),
 ("  重大決定前請以公司正式公告為準。", 10, False, None),
 ("• 銀行、保險、REIT 等行業嘅「營業利益」定義同製造業唔同（部分甚至冇呢一項），跨行業比較利益率要小心。", 10, False, None),
 ("• 空白 = Yahoo 無提供該項目，並非零。所有衍生欄（%、級別、彙總）遇到空白會顯示空白而唔會當零計。", 10, False, None),
 ("• 幣別：532 隻之中 519 隻以美元呈報，13 隻以本國幣別呈報（ASML EUR；TSM／UMC／ASX TWD；BABA／BIDU／TCEHY CNY；", 10, False, None),
 ("  CCJ／DNN／TECK CAD；NVO DKK；ONON CHF；SBGSY EUR）。本容器無可靠匯率來源，唔會擅自換算，", 10, False, None),
 ("  所以「子板塊彙總」與「AI小群組彙總」嘅金額合計<b>只計美元呈報者</b>，並喺「非美元呈報」欄列明每組被撇除幾多隻。", 10, False, None),
 ("  主表逐隻嘅數字全部照原幣呈現（見 F 欄），跨股比較金額前必須睇幣別。", 10, False, None),
 ("• 財政年度非曆年嘅公司（如 1 月底結算），G 欄嘅日曆季標籤同公司自稱嘅「FY Q1」會唔同，以 G 欄期末日為準。", 10, False, None),
 ("• 本表為公開資料整理與研究參考，非投資建議。", 10, False, None),
]
for i, (txt, sz, bold, colour) in enumerate(EXPL, 1):
    c = ws.cell(row=i, column=1, value=txt)
    c.font = Font(name=FONT, size=sz, bold=bold, color=(colour or "FF000000"))
    c.alignment = Alignment(wrap_text=True, vertical="top")

# ============ 2. 觀察名單 ============
ws = wb.create_sheet("觀察名單")
HEAD = [
    ("#", NAVY, 4.5), ("美股 Ticker\n(按=開圖)", GREY, 11), ("子板塊 SubSector\n(R4.00)", NAVY, 22),
    ("公司", NAVY, 26), ("AI 小群組 (R5.00)\n／行業", NAVY, 24), ("幣別", NAVY, 7),
    ("季度對照 (Q-4 → Q0)", NAVY, 30),
    ("營收 Q-4\n(百萬)", BLUE, 11), ("營收 Q-3\n(百萬)", BLUE, 11), ("營收 Q-2\n(百萬)", BLUE, 11),
    ("營收 Q-1\n(百萬)", BLUE, 11), ("營收 Q0 最新\n(百萬)", BLUE, 12), ("營收按年 %\n(Q0/Q-4)", BLUE, 11),
    ("營業利益 Q-3\n(百萬)", TEAL, 12), ("營業利益 Q-2\n(百萬)", TEAL, 12),
    ("營業利益 Q-1\n(百萬)", TEAL, 12), ("營業利益 Q0\n(百萬)", TEAL, 12),
    ("營業利益率\nQ0 %", TEAL, 11), ("毛利 Q0\n(百萬)", TEAL, 11), ("毛利率\nQ0 %", TEAL, 10),
    ("淨利 Q0\n(百萬)", TEAL, 11), ("淨利率\nQ0 %", TEAL, 10),
    ("年度營收\n(最近財年, 百萬)", NAVY, 14), ("年度營業利益\n(最近財年, 百萬)", NAVY, 14),
    ("年度營業\n利益率 %", NAVY, 11),
    ("盈利狀態", NAVY, 16), ("級", NAVY, 5), ("資料截至", NAVY, 11),
]
for j, (t, colour, w) in enumerate(HEAD, 1):
    hfill(ws.cell(row=1, column=j, value=t), colour)
    ws.column_dimensions[get_column_letter(j)].width = w
ws.row_dimensions[1].height = 46
ws.freeze_panes = "C2"

GRADES, QREV, QOPI, CCY = {}, {}, {}, {}
NUM = '#,##0.0;(#,##0.0);-'
PCT = '0.0%;(0.0%);-'
rows_written = 0
for i, t in enumerate(UNIVERSE, start=2):
    p = pro.get(t, {})
    rev = q_series(t, "total_revenue", 5)
    opi = q_series(t, "operating_income", 5)
    gp = q_series(t, "gross_profit", 5)
    ni = q_series(t, "net_income", 5)
    ay, ad = annual_latest(t)
    labels = " / ".join(qlabel(pp) for pp, _ in rev) if rev else ""
    ai_lbl = "、".join(f'{c} {ai_rows[c]["zh"].split(" ")[0]}' for c in ai_of.get(t, []))
    ws.cell(row=i, column=1, value=i - 1)
    c = ws.cell(row=i, column=2, value=t)
    c.hyperlink = f"https://www.tradingview.com/chart/Q1c5VWwD/?symbol={t.lower()}"
    c.font = Font(name=FONT, size=9, bold=True, color="FF1155CC", underline="single")
    ws.cell(row=i, column=3, value="、".join(sub_of.get(t, [])) or "—")
    ws.cell(row=i, column=4, value=p.get("longName") or "—")
    ws.cell(row=i, column=5, value=ai_lbl or (p.get("industry") or "—"))
    ws.cell(row=i, column=6, value=p.get("financialCurrency") or p.get("currency") or "—")
    ws.cell(row=i, column=7, value=labels or "—")
    for k in range(5):                                   # H..L revenue Q-4..Q0
        v = rev[k][1] if k < len(rev) else None
        ws.cell(row=i, column=8 + k, value=v)
    rQ4 = rev[0][1] if len(rev) >= 5 else None
    rQ0 = rev[-1][1] if rev else None
    F(ws, i, 13, f'=IF(OR(N(H{i})=0,L{i}=""),"",L{i}/H{i}-1)',
      (rQ0 / rQ4 - 1) if (rQ0 is not None and rQ4) else "")
    for k in range(4):                                   # N..Q operating income Q-3..Q0
        v = opi[k + 1][1] if len(opi) >= 5 else (opi[k][1] if k < len(opi) else None)
        ws.cell(row=i, column=14 + k, value=v)
    oQ = (opi[-1][1] if opi else None)
    F(ws, i, 18, f'=IF(OR(N(L{i})=0,Q{i}=""),"",Q{i}/L{i})', div(oQ, rQ0))
    ws.cell(row=i, column=19, value=gp[-1][1] if gp else None)
    gQ = gp[-1][1] if gp else None
    F(ws, i, 20, f'=IF(OR(N(L{i})=0,S{i}=""),"",S{i}/L{i})', div(gQ, rQ0))
    ws.cell(row=i, column=21, value=ni[-1][1] if ni else None)
    nQ = ni[-1][1] if ni else None
    F(ws, i, 22, f'=IF(OR(N(L{i})=0,U{i}=""),"",U{i}/L{i})', div(nQ, rQ0))
    ws.cell(row=i, column=23, value=(ad.get("total_revenue") / M) if ad.get("total_revenue") is not None else None)
    ws.cell(row=i, column=24, value=(ad.get("operating_income") / M) if ad.get("operating_income") is not None else None)
    aR = (ad.get("total_revenue") / M) if ad.get("total_revenue") is not None else None
    aO = (ad.get("operating_income") / M) if ad.get("operating_income") is not None else None
    F(ws, i, 25, f'=IF(OR(N(W{i})=0,X{i}=""),"",X{i}/W{i})', div(aO, aR))
    o4 = [opi[k + 1][1] if len(opi) >= 5 else (opi[k][1] if k < len(opi) else None) for k in range(4)]
    if len(o4) < 4 or any(v is None for v in o4):
        gr = "—"
    elif min(o4) > 0:
        gr = "A"
    elif o4[-1] > 0:
        gr = "B"
    else:
        gr = "C" if o4[-1] > o4[0] else "D"
    STATE = {"A": "四季持續盈利", "B": "最新季為正/波動", "C": "虧損收窄",
             "D": "虧損擴大或轉虧", "—": "數據不足"}
    F(ws, i, 26, f'=IF(AA{i}="A","四季持續盈利",IF(AA{i}="B","最新季為正/波動",'
                 f'IF(AA{i}="C","虧損收窄",IF(AA{i}="D","虧損擴大或轉虧","數據不足"))))', STATE[gr])
    F(ws, i, 27, f'=IF(COUNT(N{i}:Q{i})<4,"—",IF(MIN(N{i}:Q{i})>0,"A",'
                 f'IF(Q{i}>0,"B",IF(Q{i}>N{i},"C","D"))))', gr)
    GRADES[t] = gr; QREV[t] = rQ0; QOPI[t] = oQ
    CCY[t] = p.get("financialCurrency") or p.get("currency") or "—" 
    ws.cell(row=i, column=28, value=(rev[-1][0] if rev else "—"))
    rows_written += 1

LAST = 1 + rows_written
for r in range(2, LAST + 1):
    ws.row_dimensions[r].height = 15
    for j in range(1, len(HEAD) + 1):
        c = ws.cell(row=r, column=j)
        c.border = BORDER
        c.font = Font(name=FONT, size=9)
        if j in (1, 6, 27, 28):
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif j in (3, 4, 5, 7, 26):
            c.alignment = Alignment(horizontal="left", vertical="center")
        else:
            c.alignment = Alignment(horizontal="right", vertical="center")
        if 8 <= j <= 12:
            c.fill = PatternFill("solid", fgColor=REV_FILL); c.number_format = NUM
        elif j == 13 or j in (18, 20, 22, 25):
            c.number_format = PCT
        elif 14 <= j <= 24:
            c.fill = PatternFill("solid", fgColor=PRF_FILL); c.number_format = NUM
    ws.cell(row=r, column=2).font = Font(name=FONT, size=9, bold=True, color="FF1155CC", underline="single")
ws.auto_filter.ref = f"A1:{get_column_letter(len(HEAD))}{LAST}"
for g, colour in GRADE_FILL.items():
    ws.conditional_formatting.add(
        f"AA2:AA{LAST}",
        openpyxl.formatting.rule.CellIsRule(operator="equal", formula=[f'"{g}"'],
                                            fill=PatternFill("solid", fgColor=colour)))

# ============ 3. 明細對照 (normalised membership: one row per group x ticker) ============
wd = wb.create_sheet("明細對照")
for j, (t, w) in enumerate([("類別", 12), ("群組", 30), ("Ticker", 10), ("幣別", 7),
                            ("營收 Q0\n(百萬美元, 只計美元呈報)", 17),
                            ("營業利益 Q0\n(百萬美元, 只計美元呈報)", 19)], 1):
    hfill(wd.cell(row=1, column=j, value=t), NAVY)
    wd.column_dimensions[get_column_letter(j)].width = w
wd.freeze_panes = "A2"
pairs = [("子板塊", g, t) for t, gs in sorted(sub_of.items()) for g in gs] + \
        [("AI 小群組", f'{g} {ai_rows[g]["zh"].split(" ")[0]}', t) for t, gs in sorted(ai_of.items()) for g in gs]
for i, (kind, grp, t) in enumerate(pairs, start=2):
    wd.cell(row=i, column=1, value=kind); wd.cell(row=i, column=2, value=grp); wd.cell(row=i, column=3, value=t)
    usd = CCY.get(t) == "USD"
    F(wd, i, 4, f'=IFERROR(INDEX(觀察名單!$F$2:$F${LAST},MATCH($C{i},觀察名單!$B$2:$B${LAST},0)),"")',
      CCY.get(t, "—"))
    F(wd, i, 5, f'=IF($D{i}<>"USD","",IFERROR(INDEX(觀察名單!$L$2:$L${LAST},MATCH($C{i},觀察名單!$B$2:$B${LAST},0)),""))',
      QREV.get(t) if (usd and QREV.get(t) is not None) else "")
    F(wd, i, 6, f'=IF($D{i}<>"USD","",IFERROR(INDEX(觀察名單!$Q$2:$Q${LAST},MATCH($C{i},觀察名單!$B$2:$B${LAST},0)),""))',
      QOPI.get(t) if (usd and QOPI.get(t) is not None) else "")
    for j in range(1, 7):
        c = wd.cell(row=i, column=j); c.border = BORDER; c.font = Font(name=FONT, size=9)
        if j >= 5: c.number_format = NUM
PLAST = 1 + len(pairs)

# ============ 4/5. 群組彙總 ============
def group_sheet(title, kind, groups, extra):
    w = wb.create_sheet(title)
    cols = [("#", 4.5), ("群組", 30), ("成分股數", 9), ("營收 Q0 合計\n(百萬美元)", 16),
            ("營業利益 Q0 合計\n(百萬美元)", 18), ("合計營業利益率 %", 15),
            ("盈利成分股數\n(營業利益 > 0)", 15), ("非美元呈報\n(不計入合計)", 14),
            (extra[0], extra[1]), ("成分股", 60)]
    for j, (t, wd_) in enumerate(cols, 1):
        hfill(w.cell(row=1, column=j, value=t), NAVY)
        w.column_dimensions[get_column_letter(j)].width = wd_
    w.row_dimensions[1].height = 40
    w.freeze_panes = "C2"
    for i, (g, members, ex) in enumerate(groups, start=2):
        w.cell(row=i, column=1, value=i - 1)
        w.cell(row=i, column=2, value=g)
        w.cell(row=i, column=3, value=len(members))
        usd = [t for t in members if CCY.get(t) == "USD"]
        srev = sum(QREV[t] for t in usd if QREV.get(t) is not None)
        sopi = sum(QOPI[t] for t in usd if QOPI.get(t) is not None)
        npos = sum(1 for t in usd if (QOPI.get(t) or 0) > 0)
        nfx = len(members) - len(usd)
        F(w, i, 4, f'=SUMIFS(明細對照!$E$2:$E${PLAST},明細對照!$A$2:$A${PLAST},"{kind}",明細對照!$B$2:$B${PLAST},$B{i})', srev)
        F(w, i, 5, f'=SUMIFS(明細對照!$F$2:$F${PLAST},明細對照!$A$2:$A${PLAST},"{kind}",明細對照!$B$2:$B${PLAST},$B{i})', sopi)
        F(w, i, 6, f'=IF(N(D{i})=0,"",E{i}/D{i})', div(sopi, srev))
        F(w, i, 7, f'=COUNTIFS(明細對照!$A$2:$A${PLAST},"{kind}",明細對照!$B$2:$B${PLAST},$B{i},明細對照!$F$2:$F${PLAST},">0")', npos)
        F(w, i, 8, f'=COUNTIFS(明細對照!$A$2:$A${PLAST},"{kind}",明細對照!$B$2:$B${PLAST},$B{i})-'
                   f'COUNTIFS(明細對照!$A$2:$A${PLAST},"{kind}",明細對照!$B$2:$B${PLAST},$B{i},明細對照!$D$2:$D${PLAST},"USD")', nfx)
        w.cell(row=i, column=9, value=ex)
        w.cell(row=i, column=10, value="、".join(members))
        for j in range(1, 11):
            c = w.cell(row=i, column=j); c.border = BORDER; c.font = Font(name=FONT, size=9)
            c.alignment = Alignment(horizontal="center" if j in (1, 3, 7, 8) else
                                    ("right" if j in (4, 5, 6, 9) else "left"), vertical="center", wrap_text=(j == 10))
            if j in (4, 5): c.number_format = NUM; c.fill = PatternFill("solid", fgColor=REV_FILL if j == 4 else PRF_FILL)
            if j == 6: c.number_format = PCT
            if j == 9 and isinstance(ex, float): c.number_format = '0.00'
    w.auto_filter.ref = f"A1:J{1 + len(groups)}"
    return w

sub_groups = [(r["zh"], r["basket"], round(r["z5"], 2)) for r in
              sorted((x for x in SUB["rows"] if x.get("basket")), key=lambda x: x["rank"])]
ai_groups = [(f'{r["code"]} {r["zh"].split(" ")[0]}', r["basket"], round(r["z5"], 2)) for r in
             sorted((x for x in AI["rows"] if x.get("basket")), key=lambda x: x["rank"])]
group_sheet("子板塊彙總", "子板塊", sub_groups, ("R4.00 5日資金流向 z", 16))
group_sheet("AI小群組彙總", "AI 小群組", ai_groups, ("R5.00 5日資金流向 z", 16))

# ============ 6. 分級彙總 ============
wg = wb.create_sheet("分級彙總")
for j, (t, w) in enumerate([("級", 6), ("定義（營業利益口徑）", 46), ("數量", 8), ("佔比", 9), ("Tickers", 96)], 1):
    hfill(wg.cell(row=1, column=j, value=t), NAVY)
    wg.column_dimensions[get_column_letter(j)].width = w
DEFS = [("A", "四季營業利益全部為正 —— 持續盈利"),
        ("B", "最新季營業利益為正，但四季之中有負 —— 剛轉正或有波動"),
        ("C", "最新季營業利益為負，但較 Q-3 收窄 —— 虧損收窄"),
        ("D", "最新季營業利益為負且較 Q-3 擴大（或由正轉負） —— 惡化"),
        ("—", "四季營業利益唔齊，無法判定")]
def grade_of(t):
    o = [v for _, v in q_series(t, "operating_income", 5)]
    o = o[1:] if len(o) >= 5 else o
    if len(o) < 4 or any(v is None for v in o): return "—"
    if min(o) > 0: return "A"
    if o[-1] > 0: return "B"
    return "C" if o[-1] > o[0] else "D"
grades = GRADES
for i, (g, d) in enumerate(DEFS, start=2):
    wg.cell(row=i, column=1, value=g).fill = PatternFill("solid", fgColor=GRADE_FILL[g])
    wg.cell(row=i, column=2, value=d)
    cnt = sum(1 for t in UNIVERSE if grades[t] == g)
    F(wg, i, 3, f'=COUNTIF(觀察名單!$AA$2:$AA${LAST},$A{i})', cnt)
    F(wg, i, 4, f'=IF(N($C$7)=0,"",C{i}/$C$7)', cnt / len(UNIVERSE))
    wg.cell(row=i, column=5, value="、".join(t for t in UNIVERSE if grades[t] == g))
    for j in range(1, 6):
        c = wg.cell(row=i, column=j); c.border = BORDER; c.font = Font(name=FONT, size=9)
        c.alignment = Alignment(horizontal="center" if j in (1, 3, 4) else "left", vertical="top", wrap_text=(j == 5))
        if j == 4: c.number_format = PCT
    wg.row_dimensions[i].height = 42
wg.cell(row=7, column=2, value="合計").font = Font(name=FONT, size=9, bold=True)
F(wg, 7, 3, "=SUM(C2:C6)", float(len(UNIVERSE)))
wg.cell(row=7, column=3).font = Font(name=FONT, size=9, bold=True)

# ============ 7. 圖表連結 ============
wl = wb.create_sheet("圖表連結")
for j, (t, w) in enumerate([("#", 4.5), ("美股", 10), ("公司", 30), ("級", 5), ("純文字 URL", 66)], 1):
    hfill(wl.cell(row=1, column=j, value=t), NAVY)
    wl.column_dimensions[get_column_letter(j)].width = w
wl.freeze_panes = "A2"
for i, t in enumerate(UNIVERSE, start=2):
    url = f"https://www.tradingview.com/chart/Q1c5VWwD/?symbol={t.lower()}"
    wl.cell(row=i, column=1, value=i - 1)
    c = wl.cell(row=i, column=2, value=t); c.hyperlink = url
    c.font = Font(name=FONT, size=9, bold=True, color="FF1155CC", underline="single")
    wl.cell(row=i, column=3, value=pro.get(t, {}).get("longName") or "—")
    F(wl, i, 4, f'=IFERROR(INDEX(觀察名單!$AA$2:$AA${LAST},MATCH($B{i},觀察名單!$B$2:$B${LAST},0)),"")',
      GRADES.get(t, "—"))
    wl.cell(row=i, column=5, value=url)
    for j in range(1, 6):
        cc = wl.cell(row=i, column=j); cc.border = BORDER
        if j != 2: cc.font = Font(name=FONT, size=9)

# ============ 8. 資料來源 ============
wsrc = wb.create_sheet("資料來源")
for j, (t, w) in enumerate([("類別", 18), ("來源", 34), ("用途", 40), ("備註 / 連結", 60)], 1):
    hfill(wsrc.cell(row=1, column=j, value=t), NAVY)
    wsrc.column_dimensions[get_column_letter(j)].width = w
SRC = [
 ("財報數字", "Yahoo Finance（yfinance income_stmt / quarterly_income_stmt）",
  "營收、毛利、營業利益、淨利、年度數字", "由 GitHub Actions runner 拉取（研究容器無法連 Yahoo），檔案 data/yahoo/fundamentals_income.csv"),
 ("公司資料", "Yahoo Finance（yfinance info）", "公司名稱、呈報幣別、行業分類", "data/yahoo/fundamentals_profile.csv"),
 ("成分股名單", "Sub-Sector 資金流向 Watchlist R4.00", "C 欄子板塊歸屬（491 隻）", f"計分視窗至 {WIN} 收盤；data/subsector_flow4.json"),
 ("成分股名單", "AI Sector 資金流向 Watchlist R5.00", "E 欄 AI 小群組歸屬（111 隻）", f"計分視窗至 {WIN} 收盤；data/ai_flow5.json"),
 ("圖表", "TradingView", "B 欄與「圖表連結」分頁", "沿用 layout /chart/Q1c5VWwD/"),
 ("免責", "—", "—", "本表為公開資料整理與研究參考，非投資建議；財務數據以各公司正式公告為準。"),
]
for i, row in enumerate(SRC, start=2):
    for j, v in enumerate(row, 1):
        c = wsrc.cell(row=i, column=j, value=v)
        c.border = BORDER; c.font = Font(name=FONT, size=9)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    wsrc.row_dimensions[i].height = 34

wb.save(OUT)
patched, missing = inject(OUT, CACHE, wb.sheetnames)
print("cached values injected:", patched, "| unmatched:", missing)
cov = sum(1 for t in UNIVERSE if inc.get(t, {}).get("quarterly"))
print(f"wrote {OUT}")
print(f"universe {len(UNIVERSE)} | with quarterly statements {cov} | profiles {len(pro)} | pairs {len(pairs)}")
print("grades:", collections.Counter(grades.values()))
