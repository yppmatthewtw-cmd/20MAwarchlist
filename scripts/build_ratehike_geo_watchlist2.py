# -*- coding: utf-8 -*-
"""加息及地緣政治 3 日觀察清單 R2.00 — workbook builder.

Rebased on the 2026-09-17 close. R1.01's call covered 09-17/09-18/09-21; 09-17 is now
scored, so this revision carries a scorecard sheet for it and revises the list on what
that session showed rather than restating the thesis.
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
IDX = json.load(open('data/ratehike_geo_idx.json'))
MISS = json.load(open('data/ratehike_geo_missing.json'))

ASOF   = "2026-09-17 美東收市"
BUILT  = "2026-09-18 09:00 HKT"
REV    = "R2.00"

MAX_BASKET = 8            # widest basket among the 111 sub-sectors
NOTE_COL   = 14 + MAX_BASKET + 1

F   = "Arial"
NAVY= "1F3864"; SLATE="2E5A88"; BAND="F2F5F9"
INK = Font(name=F, size=10)
BOLD= Font(name=F, size=10, bold=True)
BLUE= Font(name=F, size=10, color="0000FF")          # hardcoded input
GRN = Font(name=F, size=10, color="008000")          # cross-sheet link
RED = Font(name=F, size=10, color="C00000", bold=True)
MUT = Font(name=F, size=9,  color="595959")
LINK= Font(name=F, size=10, bold=True, color="0563C1", underline="single")
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

def tv(t):
    """Same TradingView chart layout the HTML reports link their tickers to."""
    return f"https://www.tradingview.com/chart/Q1c5VWwD/?symbol={t.lower()}"

def putlink(ws, r, c, t):
    cell = put(ws, r, c, t, LINK, align=CTR)
    cell.hyperlink = tv(t)
    return cell

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
      f"基準：{ASOF}　·　涵蓋交易日：2026-09-18（五）、09-21（一）、09-22（二）　·　生成：{BUILT}　·　claude-opus-5 / high", 7)

r = 4
put(ws, r, 1, "一、當前 regime：三個同時發生的衝擊", T2); r += 1
header(ws, r, ["面向", "事件", "關鍵數字", "", "", "", "對股票的傳導"], FILL_H2); r += 1
SHOCK = [
 ("貨幣政策", "9/16 FOMC 加息 25bp 至 3.75–4.00%（2023 年 7 月以來首次，票數 12-0，主席 Kevin Warsh）。9/18 日本央行預期加息 25bp 至 1.25%，1993 年以來最高",
  "點陣圖：18 人中 16 人預期年內再加一次。但 9/17 十年期由 5.04% 的 19 年高位回落至 5.01%，**8 連升中斷**；兩年期 4.744% 仍為 2024 年 7 月以來最高",
  "9/16 與 9/17 是兩種相反的息率日：前者殺長久期資產，後者令同一批資產單日彈 1.3–8.0%。對息率方向下注 = 對這兩日的順序下注"),
 ("地緣政治", "沙特 East–West 輸油管（Hormuz 的替代路線）9/10 遇襲後關閉。Aramco 繞過受損段，數日內恢復約一半運能，全面復原約需六週；同時改以 Hormuz 外 Sohar 附近船對船轉運補充亞洲買家",
  "9/17 Brent −$1.01 收 $104.82、WTI −$0.52 收 $101.91。美伊進入「油輪換油輪」互擊，停火談判多次破裂；戰爭險保費為船體價值 7.5–10%（戰前 0.25%）",
  "原油供應在恢復，煉油產能沒有 —— 中東逾 20% 煉油產能實體損毀。這個落差就是裂解價差，也是本清單第①組的全部理由"),
 ("成品油", "柴油裂解價差本月創歷史新高（$102–108/桶，正常夏季約 $20）。俄羅斯柴油出口禁令延至 9/30，8 月煉油量 380 萬桶/日為二十年最低；烏克蘭無人機已打掉約 280 萬桶俄煉油產能",
  "美國煉廠開工率 >97%；MPC 年內 +157%、VLO +152%，兩者股價均高於分析員共識目標價，評級以 Hold 居多",
  "機制最強但估值已伸展 —— 本版維持第①組但把「未伸展度」由 4 分降至 2 分"),
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
 "R1.01 的 3 日窗口第一日（9/17）已有結果：兩個「兩態皆贏」的判斷完全兌現（煉油 +2.53% 名次升至第 2、診斷工具 +3.08% 連續兩版第 1），但四個依賴「息率續升」的判斷全部落空，而被列為迴避的長久期資產反而是當日最大贏家（SMR +8.01%、量子 +7.99%、數位資產 +5.30%）。逐項對照見「判斷記分卡」頁。",
 "結構性教訓：上一版把「收保費 vs 持久期」（保險 vs 銀行）當成兩態皆贏的價差，其實它不是 —— 它是對息率方向的單邊下注，只在息率續升時成立。真正的兩態價差只有一個：裂解價差 vs 原油。",
 "因此本版只在兩態皆贏的部位上維持信心（第①②組），把依賴息率方向的部位兩邊都減注（第⑦組防守、B 類中性），並把 9/17 證明自己的組別升級（第③晶圓代工、④太空、⑤鋼鐵）。",
 "未來 3 日的分岔點不再是油價，而是息率：9/18 日本央行若鷹派加息觸發日圓套息平倉，就回到 9/16 的形態；若被消化，9/17 的長久期反彈會延續。同日是四巫日，倉位驅動的急升最易在此回吐。",
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
  "來源：SubSector 資金流向 R12 引擎（本次重跑） 平衡市場面板"),
]
for i, (l1, f1, fm1, l2, f2, fm2, note) in enumerate(STAT):
    put(ws, r, 1, l1, BOLD)
    if f1 is None:
        put(ws, r, 2, SEC['mkt']['2026-09-17'], BLUE, fm1)
    else:
        put(ws, r, 2, f1, INK, fm1)
    put(ws, r, 4, l2, BOLD)
    if f2 is None:
        put(ws, r, 5, SEC['mktn']['2026-09-17'], BLUE, fm2)
    else:
        put(ws, r, 5, f2, INK, fm2)
    put(ws, r, 7, note, MUT, align=WRAP)
    r += 1

r += 1
put(ws, r, 1, "四、R1.01 判斷在 9/17 的結果與本版修正（逐項見「判斷記分卡」頁）", T2); r += 1
header(ws, r, ["R1.01 的判斷類別", "", "9/17 實際結果", "", "為何如此", "", "本版如何修正"], FILL_H2); r += 1
ERR = [
 ("兩態皆贏的判斷（煉油、診斷工具）", "煉油 +2.53%、廣度 1.00、名次 4→2；診斷工具 +3.08%、廣度 1.00、連續兩版第 1",
  "這兩組的多頭邏輯不需要猜息率或油價方向：一個做多裂解價差、一個沒有油品投入也沒有久期",
  "維持核心；煉油因估值已高於共識目標，未伸展度由 4 降至 2"),
 ("依賴「息率續升」的判斷（醫院、產險、電網）", "醫院 −0.63% 廣度 0.00、名次 3→20；產險 −0.10% 廣度 0.00、名次 6→16；電網 +0.90% 名次 14→21",
  "這些被寫成「防守」與「收息受惠」，實際是對息率方向的單邊下注。9/17 息率一停升，三組同時失去相對優勢",
  "全部降級：醫院與產險移至第⑦組（只在狀態 B 成立），電網降至第⑥組"),
 ("被低估的判斷（AI 半導體、鋼鐵）", "晶圓代工 +6.43% 名次 38→9；EDA +3.20% 名次 37→23；鋼鐵 +2.81% 廣度 1.00 名次 11→6",
  "上一版把 AI 半導體列為「戰術小注、不建議追」，鋼鐵列為「觀察不建倉」。兩者都是當日前列，鋼鐵更是升勢有廣度且未伸展",
  "AI 半導體升為第③組、鋼鐵升為第⑤組"),
 ("被推翻的迴避（SMR、數位資產、建商、鈾、稀土、再生能源）", "SMR +8.01% 名次 108→54；量子 +7.99% 名次 69→15；數位資產 +5.30% 名次 104→51；建商 +1.29% 廣度 1.00 名次 44→17",
  "迴避理由是「長久期、無盈利、加息周期最先被殺」。這個理由在息率上升時正確，在息率暫停時反向成立 —— 被殺得最重的，反彈也最烈",
  "改列 B 類中性：不建議新倉，亦不再視為迴避；孳息若重上 5.1%，迴避理由即時恢復"),
 ("已驗證的迴避（電信、油服、區域銀行、貨運）", "電信 −3.43% 廣度 0.00，為 9/17 全 111 組最差，名次 33→100；油服反彈日仍 −0.42%；區域銀行 +0.33%；貨運 +0.76%",
  "這四組在全巿反彈日依然落後 —— 機制不隨息率方向改變，是真正的結構性迴避",
  "維持 A 類迴避"),
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

# ───────────────────────── 2. 判斷記分卡 ─────────────────────────
# R1.01 called 09-17/09-18/09-21. 09-17 is now scored, so every line of that call is
# checked against it here. The move columns are read from the flow data, not retyped.
ws = sheet("判斷記分卡 Scorecard", [13, 20, 34, 10, 9, 8, 8, 9, 10, 44], freeze="C9", tab="B8860B")
title(ws, "R1.01 判斷記分卡（3 日窗口第 1 日：2026-09-17）",
      "D–H 欄直接讀自本次重跑的資金流數據，非人手填寫　·　名次為 111 個子板塊的 5 日綜合排名（1 = 最強）", 10)
header(ws, 8, ["R1.01 類別", "子板塊", "R1.01 當時的判斷", "9-17\n漲跌%", "9-17\n廣度",
               "R11\n名次", "R12\n名次", "名次\n變化", "判定", "本版如何處理"])

SECBY = {r['zh']: r for r in SEC['rows']}
RANK_NOW = {r['zh']: i for i, r in enumerate(sorted(SEC['rows'], key=lambda x: -x['s5']), 1)}
PREV_RANK = SEC['prev_rank']

CARD = [
 ("① 最高信心","煉油與成品油","做多裂解價差、做空原油；兩態皆贏","✓ 正確","維持第①組；未伸展度由 4 降至 2（VLO 年內 +152%、MPC +157%，已高於共識目標價）"),
 ("② 高信心","診斷與生命科學工具","無油品投入、本土收入、無久期","✓ 正確","維持第②組；已伸展（5 日 +11.46%），改以 DHR 作為未追高的參與方式"),
 ("② 高信心","醫院與醫療服務","資金流最確認的防守配置","✗ 錯誤","降級至第⑦組。這其實是對息率方向的下注，不是對機制的下注"),
 ("③ 買入","電氣設備與電網","AI 用電中有訂單、有定價權的一邊","✗ 偏錯","降至第⑥組；只有 ETN 單隻走強，組別廣度 0.60"),
 ("④ 買入","產險與再保","唯一「想要」5% 孳息的金融","✗ 錯誤","降級至第⑦組；浮存金邏輯在孳息見頂時失去邊際動力"),
 ("⑤ 戰術小注","晶圓代工/IDM","列為「反彈非趨勢、不建議追」","✗ 低估","升為第③組；9/17 為當日第 4 強，5 日綜合升 29 位"),
 ("⑤ 戰術小注","EDA與半導體IP","同上","✗ 低估","升為第③組"),
 ("⑥ 觀察不建倉","鋼鐵","「方向未確立」","✗ 低估","升為第⑤組；升勢有廣度（9/17 廣度 1.00）且未伸展"),
 ("未列入","太空與衛星","R1.01 完全未提及","✗ 遺漏","新增為第④組；斜率 +0.62 為全表第二高"),
 ("✕ 迴避","電信營運商","5% 無風險利率壓縮股息吸引力","✓ 完全正確","維持 A 類迴避；9/17 為全 111 組最差"),
 ("✕ 迴避","油田服務","擁擠多倉解除","✓ 正確","維持 A 類迴避；反彈日仍然下跌"),
 ("✕ 迴避","區域與社區銀行","持債虧損 + 存款成本 + CRE","✓ 正確","維持 A 類迴避"),
 ("✕ 迴避","投行與資本巿場","孳息 5% 下 deal flow 凍結","✓ 正確","維持 A 類迴避"),
 ("✕ 迴避","貨運與物流","FDX 指引屬多日重估","✓ 正確","維持 A 類迴避"),
 ("✕ 迴避","綜合油氣巨頭","上游佔比高、對沖不足","✓ 正確","維持 A 類迴避"),
 ("✕ 迴避","小型模組化核能SMR","零收入、長久期，加息周期最先被殺","✗✗ 嚴重錯誤","改列 B 類中性；斜率 +0.99 為全表最高"),
 ("✕ 迴避","量子運算","（同屬長久期主題）","✗✗ 嚴重錯誤","改列 B 類中性；9/17 為當日 111 組之冠"),
 ("✕ 迴避","數位資產金融與礦業轉HPC","實質利率 beta 最高","✗✗ 嚴重錯誤","改列 B 類中性；實質利率 beta 最高在息率回落時反向成立"),
 ("✕ 迴避","住宅建築商","9/17 新屋開工是向下催化劑","✗ 錯誤","改列 B 類中性；開工 1,275k 雖遜預期，但單戶 +7.6%，市場取了好的一面"),
 ("✕ 迴避","鈾與核燃料","長久期、無現金流","✗ 錯誤","改列 B 類中性"),
 ("✕ 迴避","稀土與關鍵礦產","長久期主題股","✗ 錯誤","改列 B 類中性"),
 ("✕ 迴避","再生能源與太陽能","公用事業 + 再生能源雙重久期","✗ 錯誤","改列 B 類中性"),
 ("✕ 迴避","頁岩E&P勘探生產","擁擠多倉在 8.31x 成交量下爆掉","○ 中性","9/17 只 +0.48%，名次 45→44；擠擁已解除，但未見新買盤"),
]
r = 9
for cat, zh, call, verdict, action in CARD:
    row = SECBY[zh]; d16 = '2026-09-17'
    pr, nr = PREV_RANK.get(zh), RANK_NOW[zh]
    put(ws, r, 1, cat, BOLD, align=WRAP)
    put(ws, r, 2, zh, BOLD, align=WRAP)
    put(ws, r, 3, call, INK, align=WRAP)
    put(ws, r, 4, row['r16'], INK, PCT)
    put(ws, r, 5, row['bd16'], INK, '0.00', None, CTR)
    put(ws, r, 6, pr, BLUE, NUM, None, CTR)
    put(ws, r, 7, nr, BLUE, NUM, None, CTR)
    put(ws, r, 8, f"=F{r}-G{r}", INK, '+0;-0;0', None, CTR)   # positive = moved up the table
    put(ws, r, 9, verdict, (RED if verdict.startswith("✗") else BOLD), align=CTR)
    put(ws, r, 10, action, INK, align=WRAP)
    band = FILL_G if verdict.startswith("✓") else FILL_R if verdict.startswith("✗") else FILL_A
    for c in range(1, 11): ws.cell(row=r, column=c).fill = band
    ws.row_dimensions[r].height = 40
    r += 1

end = r - 1
r += 1
put(ws, r, 2, "判定統計", T2)
for i, (lab, crit) in enumerate([("✓ 正確", '"✓*"'), ("✗ 錯誤", '"✗*"'), ("○ 中性", '"○*"')]):
    put(ws, r + 1 + i, 2, lab, BOLD)
    put(ws, r + 1 + i, 3, f'=COUNTIF(I9:I{end},{crit})', BOLD, NUM, None, CTR)
    put(ws, r + 1 + i, 4, f'=C{r + 1 + i}/COUNTA($I$9:$I${end})', INK, PCT)
put(ws, r + 5, 2,
    "本頁存在的理由：一份 3 日清單如果沒有逐日對照，就永遠不會知道自己錯在哪裡。9/17 的結論很集中 —— "
    "凡是「不需要猜息率方向」的判斷全部正確（煉油、診斷工具，以及五組結構性迴避），凡是「押注息率續升」的判斷全部落空"
    "（醫院、產險、電網），而凡是「因為息率上升而迴避」的，在息率一停升時就全部反彈。", MUT, align=WRAP)
ws.merge_cells(start_row=r + 5, start_column=2, end_row=r + 5, end_column=10)
ws.row_dimensions[r + 5].height = 46

# ───────────────────────── 3. 3日受惠清單 ─────────────────────────
ws = sheet("3日受惠清單 Watchlist",
           [9, 17, 8, 20, 10, 10, 10, 10, 10, 13, 13, 8, 7, 7, 7, 7, 9, 50, 22, 22, 34],
           freeze="E9", tab="2E7D32")
title(ws, "3 日受惠股清單　Rate-Hike & Geopolitical 3-Day Watchlist " + REV,
      f"基準 {ASOF}　·　H/I/L/Q 欄為公式，黑字＝公式、藍字＝輸入值、黃底＝可調整假設　·　代號可點擊開 TradingView 圖表", 21)

put(ws, 4, 13, "綜合分權重（黃底＝可調整輸入，改動後 Q 欄即時重算）", T2)
ws.merge_cells(start_row=4, start_column=13, end_row=4, end_column=17)
for col, lab, val in [(13, "機制強度", 0.40), (14, "資金流確認", 0.25), (15, "未伸展度", 0.20), (16, "廣度", 0.15)]:
    put(ws, 5, col, lab, MUT, align=CTR)
    put(ws, 6, col, val, BLUE, '0%', FILL_Y, CTR)
put(ws, 5, 17, "合計", MUT, align=CTR)
put(ws, 6, 17, "=SUM(M6:P6)", BOLD, '0%', None, CTR)

HDRW = ["組別", "主題板塊", "代號", "公司", "收市\n09-17", "前收\n09-16", "5日前收\n09-10",
        "09-17\n漲跌%", "5日\n漲跌%", "09-17\n成交量", "20日\n中位量", "相對量",
        "機制\n0-5", "資金流\n0-5", "未伸展\n0-5", "廣度\n0-5", "綜合分\n0-100",
        "受惠機制（為何這 3 日會贏）", "狀態A：油續跌", "狀態B：油再爆", "失效條件 / 注意"]
header(ws, 8, HDRW)

# tier, theme, ticker, company, mech, flow, fresh, breadth, mechanism, A, B, invalidation
W = [
("①","煉油與成品油","VLO","Valero Energy",5,5,2,5,
 "做多裂解價差、做空原油。9/17 組別 +2.53%、廣度 1.00，5 日綜合由第 4 升至第 2，斜率 +0.62。機制未變：Aramco 只能在數日內恢復約一半管線運能，全面復原約需六週；中東逾 20% 煉油產能實體損毀不會隨管線修復而回來",
 "強（原料成本回落、裂解維持）","強（成品油價領先原油）",
 "⚠ 已伸展：VLO 年內 +152%、MPC +157%，均高於分析員目標價（VLO $355 對 $405、MPC $370 對 $413），評級以 Hold 居多。俄羅斯柴油出口禁令 9/30 到期不續則裂解回落"),
("①","煉油與成品油","MPC","Marathon Petroleum",5,5,2,5,
 "美國煉油產能最大；9/17 同組齊升，5 日 +7.21%","強","強",
 "同上；年內 +157%，估值已高於共識目標"),
("①","煉油與成品油","DINO","HF Sinclair",5,5,2,5,
 "柴油佔比高，直接對應柴油裂解價差的歷史高位（本月曾見 $102–108/桶，正常夏季約 $20）","強","強",
 "同上；小型股波幅較大"),
("①","煉油與成品油","PSX","Phillips 66",4,4,3,5,
 "中游與化工佔比較高，純煉油度較低，相對未伸展","中強","中",
 "中游業務對沖掉部分裂解上行"),
("②","診斷與生命科學工具","TMO","Thermo Fisher Scientific",4,5,1,5,
 "5 日綜合連續兩版排第 1；9/17 +3.08%、廣度 1.00。零石油投入、收入本土、近期盈利無久期 —— 在 9/16（息率急升）與 9/17（息率回落）兩種日子都上升，是本清單少數真正兩態皆贏的組別",
 "強","強",
 "⚠ 組別 5 日已 +11.46%，為 111 組最大升幅之一，追價風險高"),
("②","診斷與生命科學工具","A","Agilent Technologies",4,5,2,5,
 "同組，9/17 同步上升；相對 TMO 較未伸展","強","強","同組伸展風險"),
("②","診斷與生命科學工具","DHR","Danaher",4,4,3,5,
 "組內最落後的一隻，是參與該組而不追高的方式","強","中強","中國採購與 NIH 預算消息"),
("③","晶圓代工與AI半導體","TSM","Taiwan Semiconductor",4,5,3,5,
 "9/17 晶圓代工 +6.43%、廣度 1.00，5 日綜合由第 38 急升至第 9，斜率 +0.44。息率 8 連升中斷當日，AI 資本開支的利率免疫性被重新定價",
 "強（息率見頂則最大受惠）","弱（高 beta，久期衝擊時最先被拋）",
 "⚠ 9/18 四巫日 + 日本央行議息：單日 +6% 之後撞正到期日，回吐風險高"),
("③","晶圓代工與AI半導體","SNPS","Synopsys",4,5,3,4,
 "EDA：現金流最穩、波幅最小的參與方式；9/17 +3.20%、廣度 1.00","強","中","同上"),
("③","晶圓代工與AI半導體","CDNS","Cadence Design Systems",4,5,3,4,
 "同上，EDA 雙雄","強","中","同上"),
("④","太空與衛星","RKLB","Rocket Lab",4,5,3,4,
 "9/17 +6.36%、廣度 1.00，5 日綜合由第 40 升至第 8，斜率 +0.62（全表第二高）。地緣衝突持續下的國防與衛星需求，加上息率回落對長久期成長股的解壓",
 "強","中（衝突升級有利訂單，但高 beta）",
 "小型高 beta，四巫日波幅放大；訂單消息驅動，單一合約新聞即可逆轉"),
("④","太空與衛星","ASTS","AST SpaceMobile",4,5,2,4,
 "同組，衛星直連手機","強","中","同上，且未有盈利"),
("⑤","鋼鐵","NUE","Nucor",4,4,4,5,
 "9/17 +2.81%、廣度 1.00，5 日綜合由第 11 升至第 6，ret5 +4.29%。本土、關稅保護、戰爭與基建需求，對利率不如建商敏感 —— 是本輪少數升勢有廣度且未伸展的組別",
 "中強","強（衝突與基建需求）",
 "能源成本上升侵蝕電爐煉鋼毛利"),
("⑤","鋼鐵","STLD","Steel Dynamics",4,4,4,5,
 "同組，成本結構最佳","中強","強","同上"),
("⑤","鋼鐵","RS","Reliance Inc",4,3,4,5,
 "金屬服務中心，加工毛利較穩","中強","中強","同上"),
("⑥","電氣設備與電網","GEV","GE Vernova",4,3,4,3,
 "AI 用電中有訂單、有定價權的一邊。但 9/17 組別只升 0.90%、廣度 0.60，名次由 14 跌至 21，斜率轉負 —— 表現未如 R1.01 預期，故降級",
 "中強","中",
 "組別內部分歧大（5 日廣度 0.48→0.60）；高 beta 工業股"),
("⑥","電氣設備與電網","ETN","Eaton",4,3,4,3,
 "資料中心配電；9/17 +2.91%，是組內唯一明確走強的一隻","中強","中","同上"),
("⑦","防守（已降級）","HCA","HCA Healthcare",3,2,4,3,
 "⚠ R1.01 列為第②組高信心，9/17 證伪：組別 −0.63%、廣度 0.00，名次由第 3 跌至第 20。原因是該組的多頭邏輯是「息率續升時的避險」，而 9/17 正是息率回落的一日",
 "弱（息率回落時防守性失去溢價）","強（息率再升時的避風港）",
 "保留但大幅降級；只在狀態 B 成立"),
("⑦","防守（已降級）","TRV","Travelers",3,2,4,4,
 "⚠ 同樣降級：9/17 產險 −0.10%、廣度 0.00，名次由第 6 跌至第 16。浮存金以 5% 再投資的邏輯，在 10 年期見頂回落時失去邊際動力",
 "弱","強（息率再升 + 戰爭險硬市場）",
 "10 年期若確認見頂，此組的相對優勢消失"),
("⑦","防守（已降級）","RNR","RenaissanceRe",3,2,4,4,
 "海事／戰爭再保仍是最直接的 Hormuz 受惠方式（戰爭險保費由船體價值 0.25% 升至 7.5–10%），但 9/17 未有反應",
 "弱","強",
 "颶風季 + 實際戰爭損失"),
]
r = 9
for (tier, theme, tk, comp, mech, flow, fresh, bd, mtxt, sa, sb, inval) in W:
    p = PX[tk]
    put(ws, r, 1, tier, BOLD, align=CTR)
    put(ws, r, 2, theme, INK, align=WRAP)
    putlink(ws, r, 3, tk)
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
title(ws, "3 日迴避／中性清單　Avoid & Stand-down List " + REV,
      f"基準 {ASOF}　·　G/H/K 欄為公式　·　代號可點擊開 TradingView 圖表　·　列出「有具體理由」的迴避標的，非泛泛看淡", 13)
header(ws, 8, ["類別", "代號", "公司", "收市\n09-17", "前收\n09-16", "5日前收\n09-10",
               "09-17\n漲跌%", "5日\n漲跌%", "09-17\n成交量", "20日\n中位量", "相對量",
               "迴避理由", "何時反手做多"])

A = [
("A 結構性迴避｜油田服務","SLB","SLB (Schlumberger)","5 日綜合第 103（111 組中），ret5 −6.54%、廣度 0.25。9/17 全巿反彈日仍然 −0.42% —— 反彈日跌，是機制仍然成立的最強證據","油價確立在 $110 以上且上游資本開支上調"),
("A 結構性迴避｜油田服務","HAL","Halliburton","同上","同上"),
("A 結構性迴避｜區域銀行","USB","U.S. Bancorp","5 日綜合由第 89 再跌至第 104，ret5 −4.15%。9/17 僅 +0.33%，遠遜大市 —— 即使息率回落亦未能吸引資金，存款成本與 CRE 曝險未解","孳息曲線明確轉陡"),
("A 結構性迴避｜區域銀行","PNC","PNC Financial","同上","同上"),
("A 結構性迴避｜區域銀行","ZION","Zions Bancorporation","同上","同上"),
("A 結構性迴避｜投行","GS","Goldman Sachs","5 日 ret5 −8.68%。9/17 僅 +0.43%。孳息 5% 下 IPO/M&A 窗口未開","孳息回落至 4.5% 以下且併購公告回升"),
("A 結構性迴避｜投行","MS","Morgan Stanley","同上","同上"),
("A 結構性迴避｜貨運物流","FDX","FedEx","指引下調屬多日重估；5 日綜合第 88，ret5 −3.93%，9/17 只 +0.76%","指引重設後首次上修"),
("A 結構性迴避｜貨運物流","UPS","United Parcel Service","同上","同上"),
("A 結構性迴避｜電信","T","AT&T","★ R1.01 的判斷已驗證：9/17 電信 −3.43%、廣度 0.00，為當日 111 組最差，名次由第 33 直插至第 100。5% 無風險利率下股息吸引力被壓縮","孳息明確見頂回落"),
("A 結構性迴避｜電信","VZ","Verizon","同上","同上"),
("A 結構性迴避｜綜合油氣","XOM","Exxon Mobil","9/17 −0.01%，反彈日零反應；上游佔比高，下游對沖不足","下游佔比提升"),
("A 結構性迴避｜綜合油氣","CVX","Chevron","同上","同上"),
("B 由迴避改為中性｜SMR","OKLO","Oklo","⚠ R1.01 判斷被推翻：9/17 +11.29%，組別 +8.01%、廣度 1.00，名次由第 108 急升至第 54，斜率 +0.99（全表最高）。10 年期 8 連升中斷，被息率殺得最兇的長久期無盈利資產反彈最烈","已改為中性：不建議新倉亦不再列為迴避；息率若再上則迴避理由恢復"),
("B 由迴避改為中性｜SMR","SMR","NuScale Power","同上","同上"),
("B 由迴避改為中性｜鈾","CCJ","Cameco","9/17 +2.06%，組別 +3.02%、廣度 1.00，名次由第 111 升至第 96","同上"),
("B 由迴避改為中性｜鈾","UEC","Uranium Energy","同上","同上"),
("B 由迴避改為中性｜稀土","MP","MP Materials","組別 9/17 +2.49%、廣度 1.00，名次由第 109 升至第 94","同上"),
("B 由迴避改為中性｜數位資產","COIN","Coinbase","⚠ 9/17 +5.76%，組別 +5.30%、廣度 1.00，名次由第 104 升至第 51。實質利率 beta 最高 —— 息率回落時升得最急，這正是把它列為迴避的鏡像風險","同上；實質利率方向是唯一決定因素"),
("B 由迴避改為中性｜數位資產","HOOD","Robinhood Markets","同上","同上"),
("B 由迴避改為中性｜住宅建商","DHI","D.R. Horton","⚠ 9/17 +1.49%、組別廣度 1.00，名次由第 44 升至第 17。8 月新屋開工雖然 1,275k 低於預期 1,320k，但單戶開工 +7.6% 至 918k，市場取了好的一面；30 年按揭 7.01%","同上；10 年期若重上 5.1% 則迴避理由恢復"),
("B 由迴避改為中性｜住宅建商","LEN","Lennar","同上","同上"),
("B 由迴避改為中性｜再生能源","NEE","NextEra Energy","組別 9/17 +4.01%、廣度 1.00，名次由第 97 升至第 71","同上"),
("B 由迴避改為中性｜再生能源","FSLR","First Solar","同上","同上"),
("B 由迴避改為中性｜量子運算","IONQ","IonQ","9/17 +9.57%，組別為當日 111 組之冠（+7.99%、廣度 1.00），名次由第 69 升至第 15","同上；純粹的息率久期交易，無基本面變化"),
]
r = 9
for cat, tk, comp, why, back in A:
    p = PX[tk]
    put(ws, r, 1, cat, BOLD, align=WRAP)
    putlink(ws, r, 2, tk)
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
put(ws, r, 1, "A 類＝機制仍然成立，9/17 全巿反彈日依然落後，未來 3 日不新增多倉（非建議沽空）。B 類＝R1.01 列為迴避但 9/17 大幅反彈，迴避理由已被「息率暫停上升」削弱，本版改列中性：既不建議新倉，亦不再視為迴避。10 年期由 5.04% 的 19 年高位回落、8 連升中斷，是 B 類全部反彈的單一共同原因；若孳息重上 5.1%，B 類的迴避理由即時恢復。", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=13)
ws.row_dimensions[r].height = 30

# ─────────────────────── 5. 板塊資金流證據 ───────────────────────
ws = sheet("板塊資金流證據 Evidence",
           [7, 22, 32, 14, 9, 9, 10, 10, 9, 9, 9, 8, 13, 13] + [9] * MAX_BASKET + [30],
           freeze="D9", tab=SLATE)
title(ws, "111 個子板塊資金流證據（可追溯全表）",
      f"來源：SubSector 資金流向 R12 引擎（本次重跑）　·　視窗 2026-09-11 → 2026-09-17　·　按 5 日綜合分排序　·　成分股可點擊　·　※ 淨額含 9/17 未結算成交量，屬臨時值", NOTE_COL)
header(ws, 8, ["5日\n排名", "子板塊", "English", "大板塊", "5日\n分數", "09-17\n分數",
               "09-17\n漲跌%", "5日\n漲跌%", "09-17\n廣度", "5日\n廣度", "09-17\n相對量",
               "斜率", "09-17 淨額※\n(US$ 百萬)", "5日 淨額※\n(US$ 百萬)"]
             + [f"成分股\n{i}" for i in range(1, MAX_BASKET + 1)] + ["備註"])
NOTE = {
 "煉油與成品油": "★ 第①組：9/17 +2.53%、廣度 1.00，名次 4→2，斜率 +0.62",
 "診斷與生命科學工具": "★ 第②組：連續兩版 5 日綜合第 1；9/16、9/17 兩種息率環境下都上升",
 "晶圓代工/IDM": "★ 第③組：9/17 +6.43%、廣度 1.00，名次 38→9",
 "EDA與半導體IP": "★ 第③組：9/17 +3.20%、廣度 1.00，名次 37→23",
 "太空與衛星": "★ 第④組：9/17 +6.36%、廣度 1.00，名次 40→8，斜率 +0.62",
 "鋼鐵": "★ 第⑤組：9/17 +2.81%、廣度 1.00，名次 11→6 —— 升勢有廣度且未伸展",
 "電氣設備與電網": "★ 第⑥組（已降級）：9/17 只 +0.90%、廣度 0.60，名次 14→21，斜率轉負",
 "醫院與醫療服務": "⚠ 第⑦組（已降級）：R1.01 列為高信心，9/17 −0.63%、廣度 0.00，名次 3→20",
 "產險與再保": "⚠ 第⑦組（已降級）：9/17 −0.10%、廣度 0.00，名次 6→16",
 "光通訊/CPO": "○ 9/17 +1.26%，名次 34→22",
 "AI加速晶片/GPU": "○ 9/17 +3.99%、廣度 1.00，名次 57→14",
 "記憶體/HBM": "○ 9/17 +3.81%，名次 99→42，斜率 +0.75",
 "油田服務": "✕ A 類迴避：9/17 反彈日仍 −0.42%，名次 101→103",
 "區域與社區銀行": "✕ A 類迴避：9/17 只 +0.33%，名次 89→104",
 "投行與資本巿場": "✕ A 類迴避：ret5 −8.68%",
 "貨運與物流": "✕ A 類迴避：9/17 只 +0.76%，名次 81→88",
 "電信營運商": "✕ A 類迴避（判斷已驗證）：9/17 −3.43%、廣度 0.00，當日 111 組最差，名次 33→100",
 "綜合油氣巨頭": "✕ A 類迴避：9/17 −0.01%，反彈日零反應",
 "小型模組化核能SMR": "△ B 類改中性：9/17 +8.01%、廣度 1.00，名次 108→54，斜率 +0.99（全表最高）",
 "鈾與核燃料": "△ B 類改中性：9/17 +3.02%、廣度 1.00，名次 111→96",
 "稀土與關鍵礦產": "△ B 類改中性：9/17 +2.49%、廣度 1.00，名次 109→94",
 "數位資產金融與礦業轉HPC": "△ B 類改中性：9/17 +5.30%、廣度 1.00，名次 104→51",
 "住宅建築商": "△ B 類改中性：9/17 +1.29%、廣度 1.00，名次 44→17",
 "再生能源與太陽能": "△ B 類改中性：9/17 +4.01%、廣度 1.00，名次 97→71",
 "量子運算": "△ B 類改中性：9/17 +7.99%，當日 111 組之冠，名次 69→15",
 "頁岩E&P勘探生產": "○ 9/17 +0.48%，名次 45→44；油價回落後已無 R11 時的擠擁多倉",
 "LNG液化天然氣": "⚠ 數據缺陷：成分股 NFE 反向拆股未還原（9/11 $0.33 → 9/15 $12.77），本列 5 日漲跌不可用。詳見「數據來源與限制」頁",
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
    bask = s['tick'].split(',')
    assert len(bask) <= MAX_BASKET, f"{s['zh']} basket of {len(bask)} exceeds MAX_BASKET"
    for j, t in enumerate(bask):
        putlink(ws, r, 15 + j, t)
    note = NOTE.get(s['zh'], "")
    put(ws, r, NOTE_COL, note, (RED if note.startswith("⚠") else INK), align=WRAP)
    band = FILL_G if note.startswith("★") else FILL_R if note.startswith("✕") else FILL_A if note.startswith("⚠") else None
    if band:
        for c in range(1, NOTE_COL + 1): ws.cell(row=r, column=c).fill = band
    r += 1
r += 1
put(ws, r, 2, "9/16 全市中位漲跌", BOLD)
put(ws, r, 7, SEC['mkt']['2026-09-17'], BLUE, PCT)
put(ws, r, 9, f"市場面板檔數 {SEC['mktn']['2026-09-17']:,}（平衡面板：僅計每個計分日及其前一日均有報價的股票）", MUT)
ws.merge_cells(start_row=r, start_column=9, end_row=r, end_column=NOTE_COL)

# ───────────────────────── 6. 代號索引 ─────────────────────────
# Every distinct ticker in the workbook gets its own linked row, so a name that only
# ever appears inside a 111-row basket is still one click from its chart.
ws = sheet("代號索引 Ticker Index",
           [9, 14, 20, 38, 11, 10, 10, 10, 10, 10, 13, 13, 9],
           freeze="B9", tab="0563C1")
title(ws, "代號索引　Ticker Index",
      f"基準 {ASOF}　·　工作簿內全部 {len(IDX)} 個代號，每個都可點擊開 TradingView 圖表　·　"
      "I/J/M 欄為公式　·　表頭可篩選排序", 13)
header(ws, 8, ["代號", "受惠清單", "迴避清單", "所屬子板塊（可多於一個）", "子板塊\n最佳5日排名",
               "收市\n09-17", "前收\n09-16", "5日前收\n09-10", "09-17\n漲跌%", "5日\n漲跌%",
               "09-17\n成交量", "20日\n中位量", "相對量"])

IN_W = {w[2]: w[0] for w in W}
IN_A = {}
for _cat, _tk, *_ in A:
    IN_A.setdefault(_tk, _cat)
SUB = {}
for _i, _s in enumerate(SEC['rows'], 1):
    for _t in _s['tick'].split(','):
        SUB.setdefault(_t, []).append((_i, _s['zh']))

r = 9
for tk in sorted(IDX):
    p = IDX[tk]
    subs = sorted(SUB.get(tk, []))
    putlink(ws, r, 1, tk)
    put(ws, r, 2, IN_W.get(tk, "—"), (BOLD if tk in IN_W else MUT), align=CTR)
    put(ws, r, 3, IN_A.get(tk, "—"), (BOLD if tk in IN_A else MUT), align=CTR)
    put(ws, r, 4, "、".join(z for _, z in subs) or "—", INK, align=WRAP)
    put(ws, r, 5, (subs[0][0] if subs else None), INK, NUM, None, CTR)
    put(ws, r, 6, p['c16'], BLUE, '#,##0.00')
    put(ws, r, 7, p['c15'], BLUE, '#,##0.00')
    put(ws, r, 8, p['c09'], BLUE, '#,##0.00')
    put(ws, r, 9,  f"=F{r}/G{r}-1", INK, PCT)
    put(ws, r, 10, f"=F{r}/H{r}-1", INK, PCT)
    put(ws, r, 11, p['v16'],  BLUE, NUM)
    put(ws, r, 12, p['vmed'], BLUE, NUM)
    put(ws, r, 13, f"=K{r}/L{r}", INK, MUL)
    if tk in IN_W:
        for c in range(1, 14): ws.cell(row=r, column=c).fill = FILL_G
    elif tk in IN_A:
        for c in range(1, 14): ws.cell(row=r, column=c).fill = FILL_R
    r += 1
ws.auto_filter.ref = f"A8:M{r - 1}"
put(ws, r + 1, 1,
    f"綠底＝在「3日受惠清單」內（{len(IN_W)} 檔）　紅底＝在「迴避清單」內（{len(IN_A)} 檔）　"
    f"其餘為 111 個子板塊籃子的成分股。子板塊排名為該代號所屬板塊中 5 日綜合分最高者的名次（1 = 最強）。", MUT, align=WRAP)
ws.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=13)

# ───────────────────────── 7. 催化劑日程 ─────────────────────────
MAX_CAT_TK = 7        # widest 相關代號 row below
ws = sheet("催化劑日程 Catalysts", [13, 10, 30, 13, 52, 34, 20] + [9] * MAX_CAT_TK,
           freeze="A9", tab="7B4F9D")
title(ws, "未來 3 個交易日催化劑日程",
      f"基準 {ASOF}　·　時間為美東時間　·　「相關代號」欄的代號可點擊開 TradingView 圖表", 7 + MAX_CAT_TK)
header(ws, 8, ["日期", "星期", "事件", "時間 (ET)", "為何重要", "衝擊哪些清單項目", "方向偏好"]
             + [f"相關代號\n{i}" for i in range(1, MAX_CAT_TK + 1)])
CAT = [
("2026-09-18","五","★ 日本央行議息 + 植田記者會","日本時間中午／02:30 ET",
 "市場預期加息 25bp 至 1.25%，1993 年以來最高，2024 年結束超寬鬆以來第 6 次。美 10 年期在 5.01% 之際，若措辭偏鷹 → 日圓套息平倉 → 全球久期衝擊，直接打擊 9/17 剛反彈的長久期資產",
 "第③組 TSM／SNPS／CDNS、第④組 RKLB／ASTS 最敏感；B 類全部","鷹派 → 狀態 B，本清單防守部位回升",["TSM","SNPS","CDNS","RKLB","ASTS"]),
("2026-09-18","五","★ 四巫日（季度期權期指同時到期）+ 標普季度再平衡","收市",
 "9 月第三個週五。9/17 多個組別單日升 6–8%（量子 +7.99%、SMR +8.01%、晶圓代工 +6.43%），這類倉位驅動的急升最容易在到期日被打回",
 "第③④組與全部 B 類；第①⑤組（煉油、鋼鐵）相對安全","波動放大；宜避免追高",["IONQ","OKLO","TSM","RKLB"]),
("2026-09-18","五","8 月經濟諮商局領先指標","10:00",
 "若領先指標走弱而聯儲仍鷹 → 滯脹定價；本清單的防守部位（第⑦組）只在此情境下才有相對優勢",
 "第⑦組 HCA／TRV／RNR","弱數據 → 第⑦組回升",["HCA","TRV","RNR"]),
("2026-09-21","一","到期後倉位重置","開市",
 "四巫日後第一個交易日，被 gamma 壓抑的走勢通常於此釋放。9/17 的反彈究竟是趨勢反轉還是空頭回補，這一日最能分辨",
 "全表","趨勢確認日",[]),
("2026-09-21","一","沙特 East–West 輸油管：一半運能是否如期恢復","不定",
 "Aramco 稱繞過受損段後可於數日內恢復約一半運能，全面復原約需六週。同時已改以 Hormuz 外 Sohar 附近的船對船轉運補充亞洲買家",
 "第①組全部：原油供應恢復而煉油產能未復，正是裂解價差擴張的條件","供應恢復 → 對煉油有利",["VLO","MPC","DINO","PSX"]),
("2026-09-22","二","聯儲官員發言密集期","全日",
 "9/16 點陣圖顯示 18 人中 16 人預期年內再加一次。9/17 的 8 連升中斷是否只是喘息，取決於官員如何描述「下一次」",
 "全表；第⑦組與 B 類方向完全相反","偏鷹 → 第⑦組；偏鴿 → B 類",["HCA","TRV","OKLO","COIN"]),
("2026-09-22","二","Hormuz 航運事件與戰爭險費率","不定",
 "美伊已進入「油輪換油輪」互擊，停火談判多次破裂；胡塞武裝亦持續襲擊沙特設施。戰爭險保費已由船體價值 0.25% 升至 7.5–10%",
 "第⑦組 RNR（戰爭再保）／第①組煉油","再有大規模襲擊 → 油價與裂解同升",["RNR","VLO","MPC"]),
("2026-09-30","（參考）","俄羅斯柴油出口禁令到期日","—",
 "禁令已延長至 9/30。俄佔全球柴油約 10%，8 月煉油量 380 萬桶/日為二十年最低。烏克蘭無人機已打掉約 280 萬桶俄煉油產能",
 "第①組全部：若不續期，柴油裂解可能回落","本清單 3 日窗口外，但屬第①組主要失效條件",["VLO","MPC","DINO","PSX"]),
]
r = 9
for d, wd, ev, tm, why, hit, bias, tks in CAT:
    assert len(tks) <= MAX_CAT_TK, f"{ev} names {len(tks)} tickers"
    put(ws, r, 1, d, BOLD); put(ws, r, 2, wd, INK, None, None, CTR)
    put(ws, r, 3, ev, BOLD, align=WRAP); put(ws, r, 4, tm, INK, None, None, CTR)
    put(ws, r, 5, why, INK, align=WRAP); put(ws, r, 6, hit, INK, align=WRAP)
    put(ws, r, 7, bias, INK, align=WRAP)
    for j, t in enumerate(tks):
        putlink(ws, r, 8 + j, t)
    if ev.startswith("★") or "輸油管" in ev:
        for c in range(1, 8 + MAX_CAT_TK): ws.cell(row=r, column=c).fill = FILL_A
    ws.row_dimensions[r].height = 44
    r += 1

# ───────────────────────── 8. 情境矩陣 ─────────────────────────
ws = sheet("情境矩陣 Scenarios", [6, 20, 46, 11, 11, 13, 46], tab="B8860B")
title(ws, "兩態情境矩陣　Scenario Matrix",
      "狀態機率為可調整輸入（黃底藍字）；期望值 ＝ P(A)×A 報酬 + P(B)×B 報酬，報酬分 −2 至 +2", 7)
r = 4
put(ws, r, 2, "狀態 A：息率見頂（9/17 的延續）", T2)
put(ws, r, 3, "10 年期由 5.04% 的 19 年高位回落至 5.01%，8 連升中斷；Brent 再跌 $1.01 至 $104.82、WTI 至 $101.91；Aramco 數日內恢復一半管線運能。實質利率見頂 → 被息率殺傷最重的長久期資產續彈", INK, align=WRAP)
put(ws, r, 4, "P(A)", MUT, None, None, CTR)
put(ws, r, 5, 0.50, BLUE, '0%', FILL_Y, CTR)
ws.row_dimensions[r].height = 32; r += 1
put(ws, r, 2, "狀態 B：息率再升（回到 9/16 的形態）", T2)
put(ws, r, 3, "日本央行鷹派加息（預期 +25bp 至 1.25%，1993 年來最高）觸發日圓套息平倉；或 Hormuz 再有大規模襲擊令油價重上；或聯儲官員確認年內再加一次。10 年期重上 5.1%", INK, align=WRAP)
put(ws, r, 4, "P(B)", MUT, None, None, CTR)
put(ws, r, 5, "=1-E4", BOLD, '0%', None, CTR)
ws.row_dimensions[r].height = 32; r += 2
put(ws, r, 1, "機率設為 50/50：9/17 的息率回落只是一日，而 9/18 日本央行預期鷹派加息、聯儲點陣圖仍指向年內再加一次，兩股力量方向相反。上一版把 P(A) 設為 0.55 並押注息率續升的結構，day 1 即被推翻，故本版不再對方向下重注，改為只持有兩態皆贏的部位。改動 E4 即可重算下表。", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7); r += 2

hrow = r
header(ws, hrow, ["組別", "主題", "在狀態 A 下的機制", "A 報酬\n−2~+2", "B 報酬\n−2~+2", "期望值", "在狀態 B 下的機制"])
r += 1
SCN = [
("①","煉油與成品油", "原料成本回落而中東逾 20% 煉油產能未復 → 裂解價差維持 → 毛利擴張", 2, 2,
 "成品油價領先原油上漲，裂解再擴；俄羅斯柴油禁令疊加"),
("②","診斷與生命科學工具", "無油品投入、本土收入、近期盈利無久期；9/16 與 9/17 兩種息率日都上升", 2, 2,
 "同一理由反向成立：息率再升時它仍然不受油價與久期傳導"),
("③","晶圓代工與AI半導體", "AI 資本開支的利率免疫性被重新定價，9/17 單日 +6.43%", 2, -1,
 "高 beta 長久期，日圓套息平倉或孳息重上時最先被拋"),
("④","太空與衛星", "地緣需求 + 息率回落對長久期成長股解壓，斜率全表第二高", 2, -1,
 "小型高 beta；四巫日與久期衝擊下回吐最快"),
("⑤","鋼鐵", "本土、關稅保護，對利率不如建商敏感；升勢有廣度", 1, 1,
 "戰爭與基建需求支撐；能源成本上升則侵蝕電爐毛利"),
("⑥","電氣設備與電網", "AI 用電訂單不受息率左右，但 9/17 表現已落後", 1, 0,
 "高 beta 工業股，全面去風險時同跌"),
("⑦","防守：醫院與產險（已降級）", "息率回落時防守性失去溢價 —— 這正是 9/17 發生的事", -1, 2,
 "息率再升時的避風港：浮存金以 5% 再投資、醫療需求剛性"),
("✕","A 類：油服／區域銀行／投行／貨運／電信", "9/17 全巿反彈日依然落後，機制不因息率方向改變", -1, -1,
 "孳息再升則持債虧損與 deal flow 問題加深"),
("△","B 類：SMR／鈾／稀土／數位資產／建商／量子", "實質利率見頂 → 反彈續延（9/17 單日 +1.3% 至 +8.0%）", 2, -2,
 "孳息重上 5.1% → 立即回到 9/16 的殺跌形態，這是本清單最大的單一反向風險"),
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
put(ws, r, 2, "迴避／中性組期望值平均", BOLD)
put(ws, r, 6, f"=AVERAGE(F{hrow+8}:F{hrow+9})", BOLD, '+0.00;-0.00;0.00', None, CTR)
r += 2
put(ws, r, 1, "讀法：只有第①組（煉油）與第②組（診斷工具）在兩態下都是 +2 —— 這是本清單唯一不需要猜息率方向的部分，也是 R1.01 唯一在 9/17 完全兌現的部分。第③④組在狀態 B 下轉負，第⑦組的 A/B 為 −1/+2，B 類的 A/B 為 +2/−2：後兩者是同一個賭注的兩面，方向相反，因此兩邊都只能小注。上一版的錯誤正是把第⑦組當成核心倉 —— 那其實是對息率方向下注，而不是對機制下注。", MUT, align=WRAP)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
ws.row_dimensions[r].height = 42

# ─────────────────── 9. 數據來源與限制 ───────────────────
ws = sheet("數據來源與限制 Sources", [22, 46, 66, 34], tab="595959")
title(ws, "數據來源、方法與已知限制",
      f"{REV}　·　生成 {BUILT}　·　模型 claude-opus-5（high effort）", 4)
r = 4
put(ws, r, 1, "一、價格與成交量", T2); r += 1
header(ws, r, ["項目", "內容", "說明", "欄位"], FILL_H2); r += 1
for a, b, c, d in [
 ("來源","Yahoo Finance 每日 OHLCV，經 GitHub Actions runner 以 yfinance 抓取後提交回倉庫",
  "本環境的出口代理封鎖所有財經網站，直接抓取不可行；故於 runner 上執行後將資料提交回 repo","data/yahoo/broad_2026-09-19.csv.gz"),
 ("基準日","2026-09-17（美東週四）收市","前收＝2026-09-16；5 日前收＝2026-09-10（5 個交易日）","清單頁 E/F/G 欄"),
 ("⚠ 9/17 的來源","日線鏡像把 2026-09-17 發佈為「只有成交量、完全沒有價格」的列 —— 1,499 個檔案的 Open/High/Low/Close 全部為空",
  "週轉率檢查看不到這種故障：成交量是完整發佈的（鏡像週轉率 1.0585，一個正常交易日），缺的是價格。這與 09-14 至 09-16 的盤中快照是兩種不同的故障。因此 9/17 的價格全部來自 Yahoo tail 抓取（tail.csv.gz 546 隻 + tail_broad.csv.gz 1,692 隻）",
  "引擎 meta 的 mirror_priceless"),
 ("9/17 價格的交叉驗證","tail 用的是小時線折疊成日線的路徑。在 Yahoo 已結算日線同時覆蓋的名字上，折疊收盤價偏差 0.0000%（成交量亦然）；兩次相隔數分鐘的獨立抓取在 257 個共同代號上偏差 0.00000%",
  "樣本雖小（結算重疊只有 5 隻），但與過去三版「收盤價永遠準確、成交量不準」的結論一致","—"),
 ("⚠ 市場面板縮小","平衡市場面板由上一版的 1,658 隻降至 1,109 隻。面板要求一隻股票在每個計分日都有報價，而 9/17 只有 Yahoo 小時線路徑覆蓋到的名字有價",
  "全巿中位回報因此建基於較小的樣本：9/11 +0.46%、9/14 −0.03%、9/15 −0.69%、9/16 −0.53%、9/17 +0.24%","板塊資金流證據頁"),
 ("⚠ 9/17 無成交量確認","小時線路徑的成交量不是結算印記，引擎因此把該日所有名字的量能項 B 歸零",
  "即 9/17 的分數只由方向（A）與收市位置（C）構成，沒有成交量確認；淨額估算亦屬臨時值並以 ≈ 標記","全部工作表"),
 ("⚠ 個別缺漏","PBF（PBF Energy）在兩次 tail 抓取中都沒有 9/17 的報價，已從工作簿剔除並記錄於 data/ratehike_geo_missing.json",
  "R1.01 曾把 PBF 列為第①組第 2 位。本版寧可剔除，也不用 9/16 的舊價充當 —— 否則百分比變動欄會讀成一個真實的走勢","—"),
 ("成交量基準","該股自身前 20 個交易日的成交量中位數","相對量 ＝ 9/17 成交量 ÷ 該中位數（9/17 因上述原因一律顯示 1.00）","清單頁 K/L 欄"),
 ("代號連結","工作簿內每一個代號都連結到 TradingView 圖表版面 chart/Q1c5VWwD，與本項目的 HTML 報告同一個版面",
  "「催化劑日程」的敘述欄仍以文字提及代號（Excel 每格只容許一個連結），該行右側的「相關代號」欄提供可點擊版本","全部工作表"),
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
 "全市中位採用「平衡面板」：僅計入每個計分日及其前一日均有報價的股票，2026-09-17 只有 1,109 檔（見上方限制）",
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
("9/17 收市：加息後納指回升、孳息 8 連升中斷","TheStreet","https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-sept-17-2026"),
("油價下跌：沙特改經 Hormuz 出口以補管線關閉","CNBC","https://www.cnbc.com/2026/09/17/oil-prices-today-wti-brent-hormuz-iran-war.html"),
("油價下挫：沙特着手修復關鍵管線","gCaptain","https://gcaptain.com/oil-extends-drop-as-saudi-arabia-moves-to-restore-vital-pipeline/"),
("8 月新屋開工 −2.6%，單戶開工 +7.6%","Reuters / Yahoo Finance","https://finance.yahoo.com/real-estate/articles/us-single-family-housing-starts-131652276.html"),
("按揭利率 9/17：30 年期 7.01%","Mortgage Daily","https://www.mortgagedaily.com/rates/mortgage-rates-today-2026-09-17/"),
("日本央行 9/18 預期加息 25bp 至 1.25%，1993 年來最高","Investing.com","https://in.investing.com/news/economy-news/boj-preview-september-25-bps-hike-expected-with-hawkish-outlook-5596110"),
("日本央行預期鷹派加息","FXStreet","https://www.fxstreet.com/news/bank-of-japan-is-expected-to-deliver-a-hawkish-hike-pressured-by-rising-inflation-202609172200"),
("煉油股估值：MPC/VLO 已高於共識目標價，評級以 Hold 居多","24/7 Wall St.","https://247wallst.com/investing/2026/09/17/think-its-too-late-to-buy-marathon-and-valero-heres-why-analysts-say-wait-instead/"),
("美伊「油輪換油輪」互擊，停火談判破裂","Al Jazeera","https://www.aljazeera.com/news/2026/9/6/us-iran-engaged-in-tanker-war-where-is-the-months-long-conflict-headed"),
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
    put(ws, r, 4, "2026-09-18", MUT)
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
OUT = "reports/RateHike_Geopolitical_3Day_Watchlist_R2.00_claudeopus5high_09.18_0900.xlsx"
wb.save(OUT)
print("saved", OUT)
