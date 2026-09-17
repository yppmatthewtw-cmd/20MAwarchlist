# -*- coding: utf-8 -*-
"""加息及地緣政治 3 日觀察清單 R1.00 — workbook builder.
Prices/volumes: Yahoo daily bars via GitHub Actions runner (data/yahoo/broad_2026-09-18.csv.gz).
Sector flow: data/subsector_flow11.json (SubSector 資金流向 Watchlist R11.00).
Judgment scores (機制/資金流/未伸展/廣度) are the analyst's, documented on the Sources sheet.
"""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PX  = json.load(open('data/ratehike_geo_px.json'))
SEC = json.load(open('data/ratehike_geo_sec.json'))

ASOF   = "2026-09-16 美東收市"
BUILT  = "2026-09-17 12:47 HKT"
REV    = "R1.00"

F   = "Arial"
NAVY= "1F3864"; SLATE="2E5A88"; BAND="F2F5F9"
INK = Font(name=F, size=10)
BOLD= Font(name=F, size=10, bold=True)
BLUE= Font(name=F, size=10, color="0000FF")          # hardcoded input
GRN = Font(name=F, size=10, color="008000")          # cross-sheet link
RED = Font(name=F, size=10, color="C00000", bold=True)
MUT = Font(name=F, size=9,  color="595959")
HDR = Font(name=F, size=10, bold=True, color="FFFFFF")
T1  = Font(name=F, size=16, bold=True, color=NAVY)
T2  = Font(name=F, size=11, bold=True, color=SLATE)
FILL_H  = PatternFill("solid", fgColor=NAVY)
FILL_H2 = PatternFill("solid", fgColor=SLATE)
FILL_Y  = PatternFill("solid", fgColor="FFFF00")
FILL_B  = PatternFill("solid", fgColor=BAND)
FILL_G  = PatternFill("solid", fgColor="E2EFDA")
FILL_R  = PatternFill("solid", fgColor="FCE4E4")
FILL_A  = PatternFill("solid", fgColor="FFF2CC")
THIN    = Side(style="thin", color="BFBFBF")
BOX     = Border(bottom=THIN)
WRAP    = Alignment(wrap_text=True, vertical="top")
CTR     = Alignment(horizontal="center", vertical="center")
PCT = '0.00%;[Red](0.00%);-'
USD = '$#,##0;($#,##0);-'
MUL = '0.00"x"'
NUM = '#,##0'
SC1 = '0.0'

wb = Workbook(); wb.remove(wb.active)

def sheet(name, widths, freeze=None, tab=None):
    ws = wb.create_sheet(name)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    if freeze: ws.freeze_panes = freeze
    if tab: ws.sheet_properties.tabColor = tab
    return ws

def title(ws, t, sub, span):
    ws["A1"] = t;   ws["A1"].font = T1
    ws["A2"] = sub; ws["A2"].font = MUT
    ws.merge_cells(f"A1:{get_column_letter(span)}1")
    ws.merge_cells(f"A2:{get_column_letter(span)}2")
    ws.row_dimensions[1].height = 22

def header(ws, row, labels, fill=FILL_H):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = HDR; c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[row].height = 30

def put(ws, r, c, v, font=INK, fmt=None, fill=None, align=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = font
    if fmt:   cell.number_format = fmt
    if fill:  cell.fill = fill
    if align: cell.alignment = align
    return cell

# ───────────────────────────────── 1. 摘要 ─────────────────────────────────
ws = sheet("摘要 Summary", [22, 16, 16, 16, 16, 16, 58], tab=NAVY)
title(ws, "加息及地緣政治 3 日觀察清單 " + REV,
      f"基準：{ASOF}　·　涵蓋交易日：2026-09-17（四）、09-18（五）、09-21（一）　·　生成：{BUILT}　·　claude-opus-5 / high", 7)

r = 4
put(ws, r, 1, "一、當前 regime：三個同時發生的衝擊", T2); r += 1
header(ws, r, ["面向", "事件", "關鍵數字", "", "", "", "對股票的傳導"], FILL_H2); r += 1
SHOCK = [
 ("貨幣政策", "9/16 FOMC 加息 25bp 至 3.75–4.00%，2023 年 7 月以來首次，票數 12-0。主席 Kevin Warsh（非 Powell）",
  "點陣圖：18 人中 16 人預期年內再加一次，4 人預期兩次；年底中位 4.1%，2027/9 約 4.5%",
  "折現率上升 → 無盈利長久期資產受創最深；收息型金融受惠，持久期型金融受損"),
 ("利率市場", "10 年期美債孳息突破 5%，19 年新高（2007 年以來最高）",
  "9/15 盤中 5.04%",
  "債券代理股（電信、公用、REIT）失去相對吸引力；按揭利率跟升壓住房地產"),
 ("地緣政治", "9/10 無人機（經伊拉克）襲擊沙特 East–West 輸油管。該管是 Hormuz 的替代路線，伊朗封鎖海峽後承載每日 4–5 百萬桶",
  "油價當周 +8% 破 $100；月內 +16%。9/16 美國能源部長稱「數日內」重啟 → Brent −2.7% 收 $105.83、WTI −3.2% 收 $102.43",
  "原油供應可望恢復，但中東逾 20% 煉油產能因實體損毀停擺 → 原油與成品油分道揚鑣"),
]
for a, b, c, d in SHOCK:
    put(ws, r, 1, a, BOLD, align=WRAP)
    put(ws, r, 2, b, INK, align=WRAP); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    put(ws, r, 4, c, INK, align=WRAP); ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
    put(ws, r, 7, d, INK, align=WRAP)
    ws.row_dimensions[r].height = 58
    r += 1

r += 1
put(ws, r, 1, "二、核心判斷", T2); r += 1
for line in [
 "未來 3 日只有兩種狀態：A＝輸油管如期重啟、油續回落、通脹預期降溫；B＝修復實際需 5–6 週（業界估計，與能源部長說法矛盾）或 Hormuz 再有船隻遇襲、油再爆上。",
 "本清單不賭油價方向，而是持有「在 A、B 兩態下都贏」的兩個價差：①裂解價差 vs 原油（煉油商做多裂解、做空原油）；②收保費 vs 持久期（保險 vs 銀行）。",
 "輸油管重啟恢復的是「原油供應」，不是「煉油產能」——後者因實體損毀無法隨管線修復而回來。這正是 9/16 能源板塊內部出現 7.4 個百分點分歧的原因。",
]:
    put(ws, r, 1, "• " + line, INK, align=WRAP)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    ws.row_dimensions[r].height = 30
    r += 1

r += 1
put(ws, r, 1, "三、清單統計（公式即時計算，隨清單頁改動更新）", T2); r += 1
header(ws, r, ["指標", "數值", "", "指標", "數值", "", "說明"], FILL_H2); r += 1
STAT = [
 ("受惠股檔數",  "=COUNT('3日受惠清單 Watchlist'!Q9:Q100)", NUM,
  "迴避股檔數",  "=COUNTA('迴避清單 Avoid'!B9:B100)", NUM,
  "兩表合計覆蓋的美股檔數"),
 ("受惠股平均綜合分", "=AVERAGE('3日受惠清單 Watchlist'!Q9:Q100)", SC1,
  "受惠股 9/16 平均漲跌", "=AVERAGE('3日受惠清單 Watchlist'!H9:H100)", PCT,
  "綜合分為 0–100，權重可於清單頁黃色格調整"),
 ("綜合分 ≥ 80 檔數", "=COUNTIF('3日受惠清單 Watchlist'!Q9:Q100,\">=80\")", NUM,
  "迴避股 9/16 平均漲跌", "=AVERAGE('迴避清單 Avoid'!G9:G100)", PCT,
  "當日兩表平均表現差距即為輪動幅度"),
 ("9/16 全市中位漲跌", None, PCT,
  "9/16 市場面板檔數", None, NUM,
  "來源：SubSector 資金流向 Watchlist R11.00 平衡市場面板"),
]
for i, (l1, f1, fm1, l2, f2, fm2, note) in enumerate(STAT):
    put(ws, r, 1, l1, BOLD)
    if f1 is None:
        put(ws, r, 2, SEC['mkt']['2026-09-16'], BLUE, fm1)
    else:
        put(ws, r, 2, f1, INK, fm1)
    put(ws, r, 4, l2, BOLD)
    if f2 is None:
        put(ws, r, 5, SEC['mktn']['2026-09-16'], BLUE, fm2)
    else:
        put(ws, r, 5, f2, INK, fm2)
    put(ws, r, 7, note, MUT, align=WRAP)
    r += 1

r += 1
put(ws, r, 1, "四、上一輪判斷的錯誤與修正（透明度）", T2); r += 1
header(ws, r, ["上一輪的判斷", "", "結果", "", "錯在哪裡", "", "本輪如何修正"], FILL_H2); r += 1
ERR = [
 ("能源上游列為順勢", "9/16 頁岩 E&P −6.42%（成交量 4.57x），為 111 組最差",
  "交易了「油價水平」而非「油價催化劑」。已 +16% 的倉位，真正風險是供應恢復的頭條，而該頭條 6 日內就出現",
  "改為持有煉油（裂解價差），其多頭邏輯不需要原油上漲，且供應恢復對它有利"),
 ("銀行列為順勢", "區域銀行 −3.91%（2.40x）、投行 −3.48%（1.91x）",
  "未區分「收息的金融」與「持久期的金融」。5% 的 10Y 對存款成本、持債虧損、deal flow 是利空",
  "改為產險與再保：浮存金以 5% 再投資，無存款 beta、無持債虧損，另加 Hormuz 戰爭險硬市場"),
 ("AI 基建列為避開", "9/16 光通訊/CPO +5.61%、AI 資料中心 +2.20%、晶圓代工 +2.47%",
  "低估了 AI 資本開支對利率的免疫性——Warsh 在聲明中親自點名該開支為通脹來源之一",
  "納入 AI 半導體，但僅列戰術小注並標註「5 日仍為負、屬反彈非趨勢」，不作核心倉"),
]
for a, b, c, d in ERR:
    put(ws, r, 1, a, BOLD, align=WRAP); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    put(ws, r, 3, b, INK, align=WRAP);  ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    put(ws, r, 5, c, INK, align=WRAP);  ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=6)
    put(ws, r, 7, d, INK, align=WRAP)
    ws.row_dimensions[r].height = 62
    r += 1

r += 1
put(ws, r, 1, "本表為研究紀錄，非投資建議。所有判斷分數為分析員主觀評分，方法與限制見「數據來源與限制」頁。", MUT)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)

# ───────────────────────── 2. 3日受惠清單 ─────────────────────────
ws = sheet("3日受惠清單 Watchlist",
           [9, 17, 8, 20, 10, 10, 10, 10, 10, 13, 13, 8, 7, 7, 7, 7, 9, 50, 22, 22, 34],
           freeze="E9", tab="2E7D32")
title(ws, "3 日受惠股清單　Rate-Hike & Geopolitical 3-Day Watchlist " + REV,
      f"基準 {ASOF}　·　H/I/L/Q 欄為公式，黑字＝公式、藍字＝輸入值、黃底＝可調整假設　·　綜合分 0–100", 21)

put(ws, 4, 13, "綜合分權重（黃底＝可調整輸入，改動後 Q 欄即時重算）", T2)
ws.merge_cells(start_row=4, start_column=13, end_row=4, end_column=17)
for col, lab, val in [(13, "機制強度", 0.40), (14, "資金流確認", 0.25), (15, "未伸展度", 0.20), (16, "廣度", 0.15)]:
    put(ws, 5, col, lab, MUT, align=CTR)
    put(ws, 6, col, val, BLUE, '0%', FILL_Y, CTR)
put(ws, 5, 17, "合計", MUT, align=CTR)
put(ws, 6, 17, "=SUM(M6:P6)", BOLD, '0%', None, CTR)

HDRW = ["組別", "主題板塊", "代號", "公司", "收市\n09-16", "前收\n09-15", "5日前收\n09-09",
        "09-16\n漲跌%", "5日\n漲跌%", "09-16\n成交量", "20日\n中位量", "相對量",
        "機制\n0-5", "資金流\n0-5", "未伸展\n0-5", "廣度\n0-5", "綜合分\n0-100",
        "受惠機制（為何這 3 日會贏）", "狀態A：油續跌", "狀態B：油再爆", "失效條件 / 注意"]
header(ws, 8, HDRW)

# tier, theme, ticker, company, mech, flow, fresh, breadth, mechanism, A, B, invalidation
W = [
("①","煉油與成品油","VLO","Valero Energy",5,5,4,5,
 "最純粹的美國煉油商，墨西哥灣出口槓桿最高。做多裂解價差、做空原油：輸油管重啟降低原料成本，而中東逾20%煉油產能實體損毀無法隨之恢復",
 "強（原料成本下降、裂解維持）","強（成品油價領先原油上漲）",
 "Hormuz 停火且中東煉廠產能加速修復 → 裂解崩塌"),
("①","煉油與成品油","PBF","PBF Energy",5,5,5,3,
 "財務槓桿最高，對裂解價差的 beta 最大；5 日仍為 −0.76%，是組內最未伸展的一隻",
 "強（毛利彈性最大）","強（彈性最大，雙刃）",
 "小型股、波動最大；裂解回落時跌幅亦最大"),
("①","煉油與成品油","DINO","HF Sinclair",5,5,3,5,
 "中陸地區煉廠，柴油佔比高，直接對應柴油裂解創紀錄的 $108/桶與美國柴油首破 $6/加侖",
 "強","強",
 "5 日已 +5.39%，組內最伸展；俄羅斯柴油禁令若於 9/30 到期不續 → 柴油裂解回落"),
("①","煉油與成品油","MPC","Marathon Petroleum",5,4,4,5,
 "美國煉油產能最大，搭配零售網絡，規模最穩健的參與方式",
 "強","強",
 "同組風險；規模大 → 彈性小於 PBF/DINO"),
("①","煉油與成品油","PSX","Phillips 66",4,3,4,5,
 "中游與化工佔比較高，純煉油度較低；9/16 是組內唯一收跌（−0.11%）",
 "中","中",
 "中游業務使其部分對沖掉裂解上行，純度最低"),
("②","醫院與醫療服務","THC","Tenet Healthcare",4,5,5,5,
 "零石油投入、收入全數本土、近期盈利無久期。5 日仍為 −1.23%，是本組最未伸展的一隻",
 "強（防守性 + 資金回流）","強（唯一不受油價傳導的板塊）",
 "醫保報銷政策消息；週五四巫日引發全面去風險時仍會下跌"),
("②","醫院與醫療服務","UHS","Universal Health Services",4,5,4,5,
 "9/16 組內最強（+2.47%），成交 1.42x，行為醫療佔比高",
 "強","強",
 "同上；個別州份醫保費率消息"),
("②","醫院與醫療服務","HCA","HCA Healthcare",4,5,4,5,
 "規模最大、現金流最穩，是防守配置的核心持股",
 "強","強",
 "同上"),
("②","醫院與醫療服務","EHC","Encompass Health",4,4,4,5,
 "康復照護，需求剛性，與經濟周期關聯最低",
 "強","強",
 "同上"),
("②","診斷與生命科學工具","A","Agilent Technologies",4,4,3,4,
 "5 日分數 100.0（111 組之首）組別的成員；9/16 +2.28% 而 5 日 +6.18%，仍屬可接受",
 "強","中強",
 "5 日組別已 +6.65%，整組偏伸展；中國採購與 NIH 預算消息"),
("②","診斷與生命科學工具","TMO","Thermo Fisher Scientific",4,4,2,4,
 "組內權重最大；資金流確認明確（組別 5 日淨流入 +$45.2 億）",
 "強","中強",
 "5 日 +7.06%，已伸展；追價風險"),
("③","電氣設備與電網","GEV","GE Vernova",4,5,4,3,
 "9/16 +4.79%、成交 1.82x，組內最強。AI 用電中「有訂單、有定價權」的一邊——與零收入的 SMR/鈾形成鏡像（後者 5 日 −17.7%/−16.3%）",
 "強","中（高 beta，去風險時同跌）",
 "高 beta 工業股；9/18 日本央行鷹派 + 四巫日引發全面去槓桿時首當其衝"),
("③","電氣設備與電網","ETN","Eaton",4,4,4,3,
 "資料中心配電龍頭；5 日 −4.20% 代表動能已重置，非伸展狀態",
 "強","中",
 "同上；組別 5 日廣度僅 0.48，內部分歧大"),
("③","電氣設備與電網","PWR","Quanta Services",4,3,4,3,
 "電網施工訂單；9/16 +0.97%，成交量偏低（0.77x）確認度較弱",
 "中強","中",
 "成交量未確認；施工類對利率較敏感"),
("④","產險與再保","TRV","Travelers",5,4,4,5,
 "浮存金久期短 → 最快反映 5% 再投資收益。與銀行相反：無存款 beta、無持債虧損。5 日 +3.29% 為組內最佳",
 "強（息差收益不受油價影響）","強（戰爭險硬市場加碼）",
 "大西洋颶風季高峰：一次登陸颶風可一日抵銷三日息差收益"),
("④","產險與再保","RNR","RenaissanceRe",5,3,5,5,
 "海事／戰爭再保槓桿最直接：Hormuz 戰爭險保費由船體價值 0.25% 抽升至 7.5–10%（$1 億油輪由 $25 萬變 $300–1000 萬）",
 "中強","強（戰爭險最直接受惠）",
 "颶風季 + 實際戰爭損失（已有 UAE 超級油輪遇襲、一名船員身亡）"),
("④","產險與再保","AIG","American International Group",4,3,5,5,
 "商業險與特殊險；9/16 僅 +0.12%，屬「未伸展的做多利率」方式",
 "中強","強",
 "同組颶風風險"),
("④","產險與再保","CB","Chubb",4,3,5,5,
 "規模最大、最穩；組別 5 日廣度 0.84 為全表最高，代表整組齊上而非一兩隻拉動",
 "中強","強",
 "同組颶風風險"),
("⑤","AI半導體（戰術）","SNPS","Synopsys",3,5,3,3,
 "EDA：現金流最穩、波幅最小的參與方式。9/16 +2.93%。Warsh 在聲明中點名「強勁的 AI 資本開支」為通脹來源，等於官方確認該開支不受利率影響",
 "中","中",
 "僅建議小注。組別 5 日 −3.75%，屬反彈非趨勢"),
("⑤","AI半導體（戰術）","CDNS","Cadence Design Systems",3,5,3,3,
 "同上，EDA 雙雄；9/16 +2.17%",
 "中","中",
 "同上"),
("⑤","AI半導體（戰術）","COHR","Coherent",3,5,1,2,
 "光通訊/CPO：9/16 全表最強組別（+5.61%、廣度 1.00、成交 1.50x）",
 "中","中",
 "⚠ 不建議追：5 日仍 −4.46%，組別 5 日淨流出 −$132.9 億。單日彈 5–9% 撞正週五四巫日最易被打回"),
("⑤","AI半導體（戰術）","LITE","Lumentum",3,5,1,2,
 "9/16 +9.59%、成交 1.66x，當日全表個股最強",
 "中","中",
 "⚠ 不建議追：5 日 −7.04%，純粹壞週後的反彈"),
("⑤","AI半導體（戰術）","CRDO","Credo Technology",3,5,1,2,
 "9/16 +7.38%，AI 互連",
 "中","中",
 "⚠ 不建議追：5 日 −3.83%，小型高 beta"),
("⑥","鋼鐵（觀察）","NUE","Nucor",3,4,4,4,
 "本土、關稅保護、戰爭與基建需求，對利率不如建商敏感。9/16 +0.72%，組別廣度 1.00",
 "中","中強",
 "僅觀察不建議新倉：組別 5 日僅 +0.10%，方向未確立"),
("⑥","鋼鐵（觀察）","CLF","Cleveland-Cliffs",3,4,4,3,
 "9/16 +3.05%，組內最強；高槓桿小型股",
 "中","中強",
 "同上；高負債對 5% 利率敏感"),
]
r = 9
for (tier, theme, tk, comp, mech, flow, fresh, bd, mtxt, sa, sb, inval) in W:
    p = PX[tk]
    put(ws, r, 1, tier, BOLD, align=CTR)
    put(ws, r, 2, theme, INK, align=WRAP)
    put(ws, r, 3, tk, BOLD, align=CTR)
    put(ws, r, 4, comp, INK, align=WRAP)
    put(ws, r, 5, p['c16'],  BLUE, '#,##0.00')
    put(ws, r, 6, p['c15'],  BLUE, '#,##0.00')
    put(ws, r, 7, p['c09'],  BLUE, '#,##0.00')
    put(ws, r, 8,  f"=E{r}/F{r}-1", INK, PCT)
    put(ws, r, 9,  f"=E{r}/G{r}-1", INK, PCT)
    put(ws, r, 10, p['v16'],  BLUE, NUM)
    put(ws, r, 11, p['vmed'], BLUE, NUM)
    put(ws, r, 12, f"=J{r}/K{r}", INK, MUL)
    for col, v in ((13, mech), (14, flow), (15, fresh), (16, bd)):
        put(ws, r, col, v, BLUE, '0', None, CTR)
    put(ws, r, 17, f"=(M{r}*$M$6+N{r}*$N$6+O{r}*$O$6+P{r}*$P$6)*20", BOLD, SC1, None, CTR)
    put(ws, r, 18, mtxt,  INK, align=WRAP)
    put(ws, r, 19, sa,    INK, align=WRAP)
    put(ws, r, 20, sb,    INK, align=WRAP)
    put(ws, r, 21, inval, INK, align=WRAP)
    band = FILL_B if tier in ("②", "④", "⑥") else None
    if band:
        for c in range(1, 22):
            if ws.cell(row=r, column=c).fill.fgColor.rgb in (None, "00000000"):
                ws.cell(row=r, column=c).fill = band
    ws.row_dimensions[r].height = 56
    r += 1

put(ws, r, 2, "組合平均", BOLD)
put(ws, r, 8,  f"=AVERAGE(H9:H{r-1})", BOLD, PCT)
put(ws, r, 9,  f"=AVERAGE(I9:I{r-1})", BOLD, PCT)
put(ws, r, 12, f"=AVERAGE(L9:L{r-1})", BOLD, MUL)
put(ws, r, 17, f"=AVERAGE(Q9:Q{r-1})", BOLD, SC1, None, CTR)
for c in range(1, 22): ws.cell(row=r, column=c).border = Border(top=Side(style="medium", color=NAVY))
r += 2
put(ws, r, 1, "組別說明：① 煉油＝最高信心（兩態皆贏）　② 醫療服務／工具＝資金流最確認　③ 電網＝AI 用電中有收入的一邊　④ 產險再保＝唯一「想要」5% 孳息的金融　⑤ AI 半導體＝戰術小注　⑥ 鋼鐵＝觀察不建倉", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=21)

# ───────────────────────────── 3. 迴避清單 ─────────────────────────────
ws = sheet("迴避清單 Avoid",
           [20, 8, 24, 10, 10, 10, 10, 10, 13, 13, 8, 56, 34],
           freeze="D9", tab="B71C1C")
title(ws, "3 日迴避清單　Avoid List " + REV,
      f"基準 {ASOF}　·　G/H/K 欄為公式　·　列出「有具體理由」的迴避標的，非泛泛看淡", 13)
header(ws, 8, ["類別", "代號", "公司", "收市\n09-16", "前收\n09-15", "5日前收\n09-09",
               "09-16\n漲跌%", "5日\n漲跌%", "09-16\n成交量", "20日\n中位量", "相對量",
               "迴避理由", "何時反手做多"])

A = [
("頁岩E&P／油服","FANG","Diamondback Energy","擁擠多倉在 8.31x 成交量下爆掉——全表最極端的量能。前一交易日同組 APA 才創 52 週新高","輸油管修復證實需 5–6 週，且量能回落至 1.5x 以下"),
("頁岩E&P／油服","OXY","Occidental Petroleum","同上；−6.55%、成交 1.63x",""),
("頁岩E&P／油服","COP","ConocoPhillips","同上；−6.15%、成交 1.50x",""),
("頁岩E&P／油服","EOG","EOG Resources","同上；−5.73%、成交 1.53x",""),
("頁岩E&P／油服","DVN","Devon Energy","同上；−5.63%、成交 1.45x",""),
("頁岩E&P／油服","SLB","SLB (Schlumberger)","油服 5 日 −8.33%；上游資本開支預期隨油價回落而下修",""),
("頁岩E&P／油服","HAL","Halliburton","同上；5 日 −7.06%",""),
("頁岩E&P／油服","RIG","Transocean","海上鑽井組 9/16 −5.47%，為 111 組第 109 位",""),
("綜合油氣巨頭","XOM","Exxon Mobil","−3.54%；上游佔比高，與煉油分部的對沖不足以抵銷","下游佔比提升或裂解利潤入賬體現"),
("綜合油氣巨頭","CVX","Chevron","−2.86%；同上",""),
("區域銀行","USB","U.S. Bancorp","5% 的 10Y ＝ 持債未實現虧損擴大 + 存款成本上升 + CRE 曝險。−4.00%、成交 2.78x 屬明顯分派","孳息曲線轉陡（長端回落而短端不動）"),
("區域銀行","PNC","PNC Financial","同上；−3.86%、成交 1.89x",""),
("區域銀行","ZION","Zions Bancorporation","同上；−3.71%、成交 1.78x",""),
("投行與資本巿場","GS","Goldman Sachs","5 日 −8.83%；孳息 5% 下 IPO/M&A 窗口關閉，deal flow 凍結","孳息回落至 4.5% 以下且併購公告回升"),
("投行與資本巿場","MS","Morgan Stanley","同上；5 日 −6.00%",""),
("鈾與核燃料／SMR","OKLO","Oklo","零收入、長久期，加息周期中最先被殺。5 日 −16.33%（組別 −17.74%，111 組最差之一）","孳息見頂回落，或簽訂有實質現金流的 offtake"),
("鈾與核燃料／SMR","CCJ","Cameco","鈾組 5 日 −16.32%，廣度 0.04（幾乎全組下跌）",""),
("稀土與關鍵礦產","MP","MP Materials","5 日 −9.78%（組別 −13.96%）；同屬長久期主題股",""),
("住宅建築商","DHI","D.R. Horton","10Y 5% → 按揭利率跟升。已在 2.04x 成交量下下跌，而 9/17（週四）8 月新屋開工就是直接的向下催化劑","10Y 明確跌穿 4.5%"),
("住宅建築商","LEN","Lennar","同上；成交 2.50x",""),
("數位資產","COIN","Coinbase","實質利率 beta 最高的一類；−4.42%（組別 5 日 −8.10%、淨流出 −$81.2 億）","實質利率見頂"),
("貨運與物流","FDX","FedEx","指引下調屬多日重估而非一日事件；組別 9/16 −4.94%、成交 3.15x","指引重設後的首次上修"),
("貨運與物流","UPS","United Parcel Service","同上；−3.50%",""),
("電信／債券代理","T","AT&T","5% 無風險利率下股息吸引力被壓縮；−3.22%","孳息回落"),
("電信／債券代理","VZ","Verizon","同上；−3.28%",""),
("再生能源","NEE","NextEra Energy","公用事業 + 再生能源雙重久期曝險；組別 9/16 −2.67%","孳息回落 + 稅務抵免政策明朗"),
]
r = 9
for cat, tk, comp, why, back in A:
    p = PX[tk]
    put(ws, r, 1, cat, BOLD, align=WRAP)
    put(ws, r, 2, tk, BOLD, align=CTR)
    put(ws, r, 3, comp, INK, align=WRAP)
    put(ws, r, 4, p['c16'], BLUE, '#,##0.00')
    put(ws, r, 5, p['c15'], BLUE, '#,##0.00')
    put(ws, r, 6, p['c09'], BLUE, '#,##0.00')
    put(ws, r, 7, f"=D{r}/E{r}-1", INK, PCT)
    put(ws, r, 8, f"=D{r}/F{r}-1", INK, PCT)
    put(ws, r, 9,  p['v16'],  BLUE, NUM)
    put(ws, r, 10, p['vmed'], BLUE, NUM)
    put(ws, r, 11, f"=I{r}/J{r}", INK, MUL)
    put(ws, r, 12, why,  INK, align=WRAP)
    put(ws, r, 13, back, INK, align=WRAP)
    for c in range(1, 14):
        if ws.cell(row=r, column=c).fill.fgColor.rgb in (None, "00000000"):
            ws.cell(row=r, column=c).fill = FILL_R
    ws.row_dimensions[r].height = 46
    r += 1
put(ws, r, 3, "組合平均", BOLD)
put(ws, r, 7,  f"=AVERAGE(G9:G{r-1})", BOLD, PCT)
put(ws, r, 8,  f"=AVERAGE(H9:H{r-1})", BOLD, PCT)
put(ws, r, 11, f"=AVERAGE(K9:K{r-1})", BOLD, MUL)
for c in range(1, 14): ws.cell(row=r, column=c).border = Border(top=Side(style="medium", color="B71C1C"))
r += 2
put(ws, r, 1, "註：迴避＝未來 3 日不新增多倉，非建議沽空。FANG 的 8.31x 成交量屬投降式放量，此類日子有時反而是階段底；但在 +16% 月線漲幅後遇上供應恢復頭條，3 日內的基準情境是震盪而非 V 型反彈。", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=13)
ws.row_dimensions[r].height = 30

# ─────────────────────── 4. 板塊資金流證據 ───────────────────────
ws = sheet("板塊資金流證據 Evidence",
           [7, 22, 32, 14, 9, 9, 10, 10, 9, 9, 9, 8, 13, 13, 40, 30],
           freeze="D9", tab=SLATE)
title(ws, "111 個子板塊資金流證據（可追溯全表）",
      f"來源：SubSector 資金流向 Watchlist R11.00　·　視窗 2026-09-10 → 2026-09-16　·　按 5 日綜合分排序　·　※ 淨額含 9/16 未結算成交量，屬臨時值", 16)
header(ws, 8, ["5日\n排名", "子板塊", "English", "大板塊", "5日\n分數", "09-16\n分數",
               "09-16\n漲跌%", "5日\n漲跌%", "09-16\n廣度", "5日\n廣度", "09-16\n相對量",
               "斜率", "09-16 淨額※\n(US$ 百萬)", "5日 淨額※\n(US$ 百萬)", "成分股", "備註"])
NOTE = {
 "煉油與成品油": "★ 本清單第①組：9/16 能源板塊中唯一上升，與頁岩 E&P 同日相差 7.4 個百分點",
 "醫院與醫療服務": "★ 第②組：9/16 廣度 1.00，5 日僅 +1.47% ＝ 未伸展",
 "診斷與生命科學工具": "★ 第②組：5 日分數 111 組之首，但 5 日已 +6.65%",
 "電氣設備與電網": "★ 第③組：9/16 單日 94.5 分而 5 日 −2.88% ＝ 動能已重置",
 "產險與再保": "★ 第④組：5 日廣度 0.84 為全表最高",
 "光通訊/CPO": "★ 第⑤組（戰術）：9/16 全表最強，但 5 日 −6.57%、淨流出 −$132.9 億",
 "EDA與半導體IP": "★ 第⑤組（戰術）",
 "鋼鐵": "★ 第⑥組：觀察，方向未確立",
 "頁岩E&P勘探生產": "✕ 迴避：9/16 111 組最差，成交 4.57x",
 "海上鑽井與設備": "✕ 迴避",
 "油田服務": "✕ 迴避",
 "綜合油氣巨頭": "✕ 迴避",
 "區域與社區銀行": "✕ 迴避：成交 2.40x",
 "投行與資本巿場": "✕ 迴避",
 "鈾與核燃料": "✕ 迴避：5 日廣度 0.04",
 "小型模組化核能SMR": "✕ 迴避：5 日 −17.74%",
 "稀土與關鍵礦產": "✕ 迴避",
 "住宅建築商": "✕ 迴避：9/17 新屋開工為向下催化劑",
 "數位資產金融與礦業轉HPC": "✕ 迴避",
 "貨運與物流": "✕ 迴避：FDX 指引，成交 3.15x",
 "電信營運商": "✕ 迴避：債券代理股",
 "再生能源與太陽能": "✕ 迴避",
 "LNG液化天然氣": "⚠ 數據缺陷：成分股 NFE 反向拆股未還原（9/11 $0.33 → 9/15 $12.77），本列 5 日漲跌與 9/10、9/14 分數不可用。詳見「數據來源與限制」頁",
}
r = 9
for i, s in enumerate(SEC['rows'], 1):
    put(ws, r, 1, f"=ROW()-8", INK, NUM, None, CTR)
    put(ws, r, 2, s['zh'], BOLD if s['zh'] in NOTE else INK, align=WRAP)
    put(ws, r, 3, s['en'], MUT, align=WRAP)
    put(ws, r, 4, s['sec'], MUT, align=WRAP)
    put(ws, r, 5, s['s5'],  INK, SC1, None, CTR)
    put(ws, r, 6, s['s16'], INK, SC1, None, CTR)
    bad = s['zh'] == "LNG液化天然氣"
    put(ws, r, 7, s['r16'], INK, PCT)
    put(ws, r, 8, ("n/a（數據缺陷）" if bad else s['r5']), (RED if bad else INK), (None if bad else PCT))
    put(ws, r, 9,  s['bd16'],  INK, '0.00', None, CTR)
    put(ws, r, 10, s['bd5'],   INK, '0.00', None, CTR)
    put(ws, r, 11, s['rvol16'],INK, MUL,    None, CTR)
    put(ws, r, 12, s['slope'], INK, '+0.00;-0.00;0.00', None, CTR)
    put(ws, r, 13, (s['mfd16'] or 0)/1e6, INK, USD)
    put(ws, r, 14, (s['mfd5']  or 0)/1e6, INK, USD)
    put(ws, r, 15, s['tick'], MUT, align=WRAP)
    note = NOTE.get(s['zh'], "")
    put(ws, r, 16, note, (RED if note.startswith("⚠") else INK), align=WRAP)
    if note.startswith("★"):
        for c in range(1, 17): ws.cell(row=r, column=c).fill = FILL_G
    elif note.startswith("✕"):
        for c in range(1, 17): ws.cell(row=r, column=c).fill = FILL_R
    elif note.startswith("⚠"):
        for c in range(1, 17): ws.cell(row=r, column=c).fill = FILL_A
    r += 1
r += 1
put(ws, r, 2, "9/16 全市中位漲跌", BOLD)
put(ws, r, 7, SEC['mkt']['2026-09-16'], BLUE, PCT)
put(ws, r, 15, f"市場面板檔數 {SEC['mktn']['2026-09-16']:,}（平衡面板：僅計每個計分日及其前一日均有報價的股票）", MUT)

# ───────────────────────── 5. 催化劑日程 ─────────────────────────
ws = sheet("催化劑日程 Catalysts", [13, 10, 30, 13, 52, 34, 20], freeze="A9", tab="7B4F9D")
title(ws, "未來 3 個交易日催化劑日程", f"基準 {ASOF}　·　時間為美東時間", 7)
header(ws, 8, ["日期", "星期", "事件", "時間 (ET)", "為何重要", "衝擊哪些清單項目", "方向偏好"])
CAT = [
("2026-09-17","四","8 月新屋開工 + 營建許可","08:30",
 "10Y 在 5% ＝ 30 年按揭跟升。這是本週唯一直接針對利率敏感板塊的數據","迴避：DHI、LEN（已在 2.0–2.5x 量能下跌）","利空建商"),
("2026-09-17","四","初領失業救濟金","08:30",
 "Warsh 稱經濟「正在走強」並以就業數據佐證。強數據 ＝ 再加息機率上升 ＝ 孳息再上","受惠：TRV、RNR、AIG、CB（息差）／迴避：OKLO、CCJ、MP","強數據利好保險、利空長久期"),
("2026-09-17","四","FOMC 靜默期結束，官員開始發言","全日",
 "點陣圖顯示 16/18 預期年內再加一次——官員措辭將決定市場如何定價「下一次」","全表；尤其第④組保險與所有迴避項目","偏鷹 → 強化本清單配置"),
("2026-09-17","四","沙特 East–West 輸油管修復進展／衛星影像","不定",
 "★ 本清單最大單一變數。能源部長稱「數日」vs 業界估計 5–6 週，兩者矛盾","全表：決定狀態 A 或狀態 B","見「情境矩陣」頁"),
("2026-09-18","五","日本央行議息","日本時間上午，美股盤前",
 "美 10Y 在 5% 之際若 BOJ 轉鷹 → 日圓套息平倉 → 全球久期衝擊","第③組 GEV／ETN、第⑤組 AI 半導體（高 beta 最先被拋）","風險事件，非方向事件"),
("2026-09-18","五","四巫日（季度期權期指同時到期）+ 標普季度再平衡","收市",
 "9 月第三個週五。巨額 gamma 到期 → 當日走勢多由倉位而非基本面決定","第⑤組 AI 半導體（單日彈 5–9% 最易被打回）；低 beta 高廣度項目相對安全","波動放大；宜避免追高"),
("2026-09-18","五","8 月工業生產、經濟諮商局領先指標","09:15 / 10:00",
 "若領先指標走弱而 Fed 仍鷹 → 滯脹定價，利好防守性醫療","第②組 THC、UHS、HCA、EHC","弱數據利好醫療服務"),
("2026-09-21","一","到期後倉位重置","開市",
 "四巫日後的第一個交易日，被 gamma 壓抑的走勢通常於此釋放","全表","趨勢確認日"),
("2026-09-21","一","Hormuz 航運事件／戰爭險費率更新","不定",
 "自上週六起已有至少兩艘船隻在 Hormuz 遇襲。費率已由船體價值 0.25% 升至 7.5–10%","第④組 RNR（戰爭再保）／第①組煉油","再有襲擊 → 狀態 B"),
("2026-09-30","（參考）","俄羅斯柴油出口禁令到期日","—",
 "禁令已延長至 9/30。俄佔全球柴油約 10%，8 月煉油量 380 萬桶/日為二十年最低","第①組全部：若不續期，柴油裂解可能回落","本清單 3 日窗口外，但屬第①組主要失效條件"),
]
r = 9
for d, wd, ev, tm, why, hit, bias in CAT:
    put(ws, r, 1, d, BOLD); put(ws, r, 2, wd, INK, None, None, CTR)
    put(ws, r, 3, ev, BOLD, align=WRAP); put(ws, r, 4, tm, INK, None, None, CTR)
    put(ws, r, 5, why, INK, align=WRAP); put(ws, r, 6, hit, INK, align=WRAP)
    put(ws, r, 7, bias, INK, align=WRAP)
    if ev.startswith("★") or "輸油管" in ev:
        for c in range(1, 8): ws.cell(row=r, column=c).fill = FILL_A
    ws.row_dimensions[r].height = 44
    r += 1

# ───────────────────────── 6. 情境矩陣 ─────────────────────────
ws = sheet("情境矩陣 Scenarios", [6, 20, 46, 11, 11, 13, 46], tab="B8860B")
title(ws, "兩態情境矩陣　Scenario Matrix",
      "狀態機率為可調整輸入（黃底藍字）；期望值 ＝ P(A)×A 報酬 + P(B)×B 報酬，報酬分 −2 至 +2", 7)
r = 4
put(ws, r, 2, "狀態 A：輸油管如期重啟、油續回落", T2)
put(ws, r, 3, "美國能源部長 Chris Wright 稱沙特 East–West 管「數日內」恢復；油價自 $105.83 / $102.43 進一步回落，通脹預期降溫，長端孳息喘定", INK, align=WRAP)
put(ws, r, 4, "P(A)", MUT, None, None, CTR)
put(ws, r, 5, 0.55, BLUE, '0%', FILL_Y, CTR)
ws.row_dimensions[r].height = 32; r += 1
put(ws, r, 2, "狀態 B：修復需 5–6 週或再有襲擊、油再爆", T2)
put(ws, r, 3, "業界估計修復需 5–6 週，與官方說法矛盾；或 Hormuz 再有船隻遇襲（上週六以來已至少兩艘）。油再破頂，孳息續升", INK, align=WRAP)
put(ws, r, 4, "P(B)", MUT, None, None, CTR)
put(ws, r, 5, "=1-E4", BOLD, '0%', None, CTR)
ws.row_dimensions[r].height = 32; r += 2
put(ws, r, 1, "機率為分析員主觀設定：能源部長的公開表態具體且可證偽，但業界修復估計與之矛盾，故未給予壓倒性權重。改動 E4 即可重算下表。", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7); r += 2

hrow = r
header(ws, hrow, ["組別", "主題", "在狀態 A 下的機制", "A 報酬\n−2~+2", "B 報酬\n−2~+2", "期望值", "在狀態 B 下的機制"])
r += 1
SCN = [
("①","煉油與成品油", "原料成本下降而中東逾 20% 煉油產能實體損毀未復 → 裂解價差維持 → 毛利擴張", 2, 2,
 "成品油價領先原油上漲，裂解再擴；俄羅斯柴油禁令疊加 → 毛利同樣擴張"),
("②","醫療服務／工具", "無油品投入、本土收入；資金自能源與銀行流入的主要去處", 2, 2,
 "唯一完全不受油價傳導的板塊；滯脹環境下的防守核心"),
("③","電氣設備與電網", "AI 資本開支不受利率影響（Warsh 親自點名為通脹來源），訂單與定價權俱在", 2, 0,
 "高 beta 工業股，全面去風險時同跌；但訂單不受油價直接影響"),
("④","產險與再保", "浮存金以 5% 再投資，無存款 beta、無持債虧損", 1, 2,
 "戰爭險保費由船體價值 0.25% 升至 7.5–10%，硬市場加碼；息差收益不變"),
("⑤","AI 半導體（戰術）", "利率免疫敘事延續，但 5 日仍為負 → 屬反彈非趨勢", 1, 0,
 "四巫日 + BOJ 疊加時最先被拋；單日 5–9% 漲幅最易回吐"),
("⑥","鋼鐵（觀察）", "本土、關稅保護，對利率不如建商敏感；但 5 日僅 +0.10%，方向未確立", 0, 1,
 "戰爭與基建需求支撐；能源成本上升則侵蝕電爐煉鋼毛利"),
("✕","頁岩 E&P／油服", "供應恢復直擊多頭核心，擁擠倉位續解", -2, 2,
 "油再爆則大幅反彈——這是本清單最大的反向風險"),
("✕","區域銀行／投行", "長端孳息喘定可帶來技術反彈，但存款成本與 CRE 問題不變", -1, -2,
 "孳息再升 → 持債虧損擴大、deal flow 續凍"),
("✕","鈾／SMR／稀土", "孳息喘定可帶來超跌反彈，但無現金流的估值問題不變", -1, -2,
 "實質利率再升 → 長久期無盈利資產續殺"),
("✕","住宅建商／債券代理", "孳息回落是唯一救贖，但 9/17 新屋開工先行", -1, -2,
 "按揭利率續升 → 需求與估值雙殺"),
]
for tier, theme, ma, ra, rb, mb in SCN:
    put(ws, r, 1, tier, BOLD, None, None, CTR)
    put(ws, r, 2, theme, BOLD, align=WRAP)
    put(ws, r, 3, ma, INK, align=WRAP)
    put(ws, r, 4, ra, BLUE, '+0;-0;0', None, CTR)
    put(ws, r, 5, rb, BLUE, '+0;-0;0', None, CTR)
    put(ws, r, 6, f"=$E$4*D{r}+(1-$E$4)*E{r}", BOLD, '+0.00;-0.00;0.00', None, CTR)
    put(ws, r, 7, mb, INK, align=WRAP)
    fill = FILL_G if tier != "✕" else FILL_R
    for c in range(1, 8):
        if ws.cell(row=r, column=c).fill.fgColor.rgb in (None, "00000000"):
            ws.cell(row=r, column=c).fill = fill
    ws.row_dimensions[r].height = 46
    r += 1
put(ws, r, 2, "受惠組期望值平均", BOLD)
put(ws, r, 6, f"=AVERAGE(F{hrow+1}:F{hrow+6})", BOLD, '+0.00;-0.00;0.00', None, CTR)
r += 1
put(ws, r, 2, "迴避組期望值平均", BOLD)
put(ws, r, 6, f"=AVERAGE(F{hrow+7}:F{hrow+10})", BOLD, '+0.00;-0.00;0.00', None, CTR)
r += 2
put(ws, r, 1, "讀法：只有第①組與第②組在兩態下都是 +2 ——這就是「不賭油價方向」的具體意思。第③、⑤組在狀態 B 下歸零，故列為次級與戰術倉。頁岩 E&P 的 A/B 報酬為 −2/+2，是本清單最大的單一反向風險：若輸油管修復證實需 5–6 週，該組會強勢反彈。", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
ws.row_dimensions[r].height = 42

# ─────────────────── 7. 數據來源與限制 ───────────────────
ws = sheet("數據來源與限制 Sources", [22, 46, 66, 34], tab="595959")
title(ws, "數據來源、方法與已知限制",
      f"{REV}　·　生成 {BUILT}　·　模型 claude-opus-5（high effort）", 4)
r = 4
put(ws, r, 1, "一、價格與成交量", T2); r += 1
header(ws, r, ["項目", "內容", "說明", "欄位"], FILL_H2); r += 1
for a, b, c, d in [
 ("來源","Yahoo Finance 每日 OHLCV，經 GitHub Actions runner 以 yfinance 抓取後提交回倉庫",
  "本環境的出口代理封鎖所有財經網站，直接抓取不可行；故於 runner 上執行後將資料提交回 repo","data/yahoo/broad_2026-09-18.csv.gz"),
 ("基準日","2026-09-16（美東週三，FOMC 決議日）收市","前收＝2026-09-15；5 日前收＝2026-09-09（5 個交易日）","清單頁 E/F/G 欄"),
 ("成交量基準","該股自身前 20 個交易日的成交量中位數","相對量 ＝ 9/16 成交量 ÷ 該中位數。1.0 ＝ 正常","清單頁 K/L 欄"),
 ("9/16 結算狀態","9/16 由 Yahoo 收市後日線提供；日線鏡像當日 14:15 ET（收市前）提交，經跨來源裁決剔除",
  "9/16 成交量尚未結算（結算印記佔比 1.8%）。實測：收盤價誤差中位/p95 皆為 0.0000%；成交量 p95 約 15%","影響淨額，不影響收盤價"),
]:
    put(ws, r, 1, a, BOLD, align=WRAP); put(ws, r, 2, b, INK, align=WRAP)
    put(ws, r, 3, c, INK, align=WRAP);  put(ws, r, 4, d, MUT, align=WRAP)
    ws.row_dimensions[r].height = 44; r += 1

r += 1
put(ws, r, 1, "二、資金流分數方法（「板塊資金流證據」頁）", T2); r += 1
for line in [
 "方向 A ＝ tanh((個股回報 − 全市中位回報) / 0.02)；量能 B ＝ clip(log2(clip(成交量/20日中位量, 0.25, 4))/2, −1, 1)；收位 C ＝ ((收−低)−(高−收))/(高−低)",
 "單股強度 f ＝ (0.70A + 0.30C) × (1 + 0.50B)；籃子以成交金額加權，並用逐次注水法將單一成分上限壓至 40%",
 "每日作橫截面 z 分數後轉百分位（0–100）；5 日綜合採用權重 [1.0, 1.15, 1.35, 1.6, 1.9]（越近權重越高）",
 "淨額估算（mfd）＝ Σ(收位 C × 成交金額)。★ 這是價量代理，不是真實資金流：13F 與 ETF 申贖資料在本環境不可達",
 "全市中位採用「平衡面板」：僅計入每個計分日及其前一日均有報價的股票，2026-09-16 為 1,658 檔",
]:
    put(ws, r, 1, "• " + line, INK, align=WRAP)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    ws.row_dimensions[r].height = 26; r += 1

r += 1
put(ws, r, 1, "三、已知限制與缺陷（必讀）", T2); r += 1
header(ws, r, ["項目", "內容", "影響範圍", "狀態"], FILL_H2); r += 1
for a, b, c, d, hl in [
 ("⚠ LNG 組別數據缺陷",
  "「LNG液化天然氣」組的成分股 NFE（New Fortress Energy）做了反向拆股：收市價由 9/11 的 $0.33 跳至 9/15 的 $12.77。Yahoo 的 close 欄未還原拆股（adj_close 有），引擎使用 raw close，產生 +3771% 的單日回報",
  "該組 5 日回報顯示 +9111%（垃圾值），且 9/10 與 9/14 兩日分數因 tanh 飽和被高估為滿分上升日。111 組中僅此 1 組受影響（現排第 72 位），其餘 110 組不受影響。本清單所推薦與迴避的標的均不在該組",
  "已在「板塊資金流證據」頁標記為 n/a；修正版待用戶確認", True),
 ("※ 淨額估算為臨時值",
  "9/16 成交量尚未結算。實測未結算 vs 結算：分數 p95 差 1.82 分（滿分 100）、名次最多差 4；但淨額估算中位差 1.22%、p95 16.3%、最大 75.4%",
  "「板塊資金流證據」頁 M、N 欄的美元金額屬臨時值；分數與排名不受影響",
  "已於頁首與欄標題以「※」標註", False),
 ("資金流為價量代理",
  "無真實基金流向資料（13F、ETF 申贖在本環境不可達）",
  "所有「資金流入／流出」均為價格與成交量推算，非實際申贖",
  "設計限制，非缺陷", False),
 ("判斷分數為主觀",
  "清單頁 M–P 欄（機制／資金流／未伸展／廣度，各 0–5）為分析員主觀評分，非計算所得",
  "綜合分 Q 欄由這四項加權而成；權重列於該頁黃色格，可自行調整重算",
  "已以藍字標示為輸入值", False),
 ("油輪／航運未納入追蹤範圍",
  "Hormuz 最直接的受惠者為油輪（戰爭險費率由船體價值 0.25% 升至 7.5–10%，VLCC 日租金曾破 $100 萬），但 111 個子板塊中的「貨運與物流」僅涵蓋 UPS/FDX/ODFL 等包裹與陸運，不含油輪",
  "FRO、DHT、INSW、TNK、STNG 等油輪股不在本追蹤宇宙內，故未列入清單。另需注意：油輪相關 ETF 年內已漲逾 3,600%，屬極度伸展",
  "已知覆蓋缺口", False),
 ("本表性質",
  "研究紀錄，非投資建議。3 日為極短線窗口，個股結果由倉位與流動性主導的成分高於基本面",
  "全表",
  "—", False),
]:
    put(ws, r, 1, a, (RED if hl else BOLD), align=WRAP)
    put(ws, r, 2, b, INK, align=WRAP)
    put(ws, r, 3, c, INK, align=WRAP)
    put(ws, r, 4, d, INK, align=WRAP)
    if hl:
        for cc in range(1, 5): ws.cell(row=r, column=cc).fill = FILL_A
    ws.row_dimensions[r].height = 76; r += 1

r += 1
put(ws, r, 1, "四、新聞與宏觀資料來源", T2); r += 1
header(ws, r, ["主題", "出處", "連結", "取用日期"], FILL_H2); r += 1
SRC = [
("FOMC 9/16 加息 25bp 至 3.75–4.00%","CNBC","https://www.cnbc.com/2026/09/16/fed-rate-decision-september-2026.html"),
("Warsh：通脹仍然過高（會議實錄）","CNBC","https://www.cnbc.com/2026/09/16/fed-meeting-today-live-updates.html"),
("2023 年以來首次加息","Fox Business","https://www.foxbusiness.com/economy/federal-reserve-interest-rate-decision-september-16-2026"),
("9/16 收市：加息後道指標普急跌","TheStreet","https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-sept-16-2026"),
("9/15：孳息創 19 年新高","TheStreet","https://www.thestreet.com/stock-market-today/stock-market-today-sept-15-2026-dow-futures-slide-as-oil-prices-surge-and-treasury-yields-hit-2007-highs"),
("油價下跌：沙特輸油管將於數日內重啟","CNBC","https://www.cnbc.com/2026/09/16/oil-prices-today-brent-wti-hormuz-iran-war.html"),
("沙特關閉繞道 Hormuz 的關鍵輸油管","CNBC","https://www.cnbc.com/2026/09/13/oil-price-iran-war-strait-hormuz-saudi-pipeline.html"),
("East–West 輸油管為何攸關全球石油","Al Jazeera","https://www.aljazeera.com/news/2026/9/14/why-saudi-arabias-east-west-pipeline-matters-for-global-oil"),
("2026 年 East–West 輸油管襲擊事件","Wikipedia","https://en.wikipedia.org/wiki/2026_East%E2%80%93West_Crude_Oil_Pipeline_attack"),
("$100/桶柴油裂解價差：2026 年全球煉油的脆弱性","RBN Energy","https://rbnenergy.com/daily-posts/blog/100bbl-diesel-crack-or-how-2026-exposed-fragility-global-refining"),
("美國柴油價創紀錄、煉油毛利飆升","Discovery Alert","https://discoveryalert.com/analysis/us-diesel-prices-record-september-2026/"),
("俄羅斯延長柴油出口禁令至 9/30","Ukrainska Pravda","https://www.pravda.com.ua/eng/news/2026/08/29/8050963/"),
("無人機打擊迫使俄六大柴油煉廠半數減產","Kyiv Post","https://www.kyivpost.com/post/84579"),
("Hormuz 航運戰爭險再度飆升","The National","https://www.thenationalnews.com/business/2026/07/17/war-risk-shipping-premium-surges-again-as-tensions-escalate-at-strait-of-hormuz/"),
("中東航運保險成本上升（Marsh）","S&P Global","https://www.spglobal.com/energy/en/news-research/latest-news/shipping/072226-middle-east-shipping-insurance-costs-rise-on-hormuz-risks-marsh"),
("本週經濟數據日程（9/14–18）","Kiplinger","https://www.kiplinger.com/investing/economy/this-weeks-economic-calendar"),
("9 月加息機率與利率期貨定價","Yahoo Finance","https://finance.yahoo.com/economy/policy/articles/fomc-september-2026-odds-rate-201618784.html"),
]
for t, pub, url in SRC:
    put(ws, r, 1, t, INK, align=WRAP)
    put(ws, r, 2, pub, INK)
    c = put(ws, r, 3, url, Font(name=F, size=9, color="0563C1", underline="single"), align=WRAP)
    c.hyperlink = url
    put(ws, r, 4, "2026-09-17", MUT)
    r += 1

# The 摘要 block is written before the two list sheets exist, so its cross-sheet
# ranges are opened to row 100 and tightened here to the real last data row --
# otherwise COUNT also picks up each list's "組合平均" footer formula.
WL_LAST, AV_LAST = 8 + len(W), 8 + len(A)
_su = wb["摘要 Summary"]
for _row in _su.iter_rows():
    for _c in _row:
        if isinstance(_c.value, str) and _c.value.startswith("="):
            _c.value = (_c.value
                        .replace("Watchlist'!Q9:Q100", f"Watchlist'!Q9:Q{WL_LAST}")
                        .replace("Watchlist'!H9:H100", f"Watchlist'!H9:H{WL_LAST}")
                        .replace("Avoid'!B9:B100",     f"Avoid'!B9:B{AV_LAST}")
                        .replace("Avoid'!G9:G100",     f"Avoid'!G9:G{AV_LAST}"))

wb.calculation.fullCalcOnLoad = True   # Excel recalculates every formula on open
OUT = "reports/RateHike_Geopolitical_3Day_Watchlist_R1.00_claudeopus5high_09.17_1247.xlsx"
wb.save(OUT)
print("saved", OUT)
