# -*- coding: utf-8 -*-
"""Independent verification: recompute every cached value straight from the source
data (px.json / sec.json) and compare against what the workbook now contains."""
import json
from openpyxl import load_workbook
PX = json.load(open('data/ratehike_geo_px.json')); SEC = json.load(open('data/ratehike_geo_sec.json'))
FN = 'reports/RateHike_Geopolitical_3Day_Watchlist_R1.00_claudeopus5high_09.17_1247.xlsx'
V = load_workbook(FN, data_only=True)   # cached values
Fm = load_workbook(FN)                  # formulas
P = []
def bad(m): P.append(m); print("  PROBLEM:", m)
def close(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol * max(1, abs(b))

print("sheets:", V.sheetnames)

# 0. no error strings anywhere, no unresolved formula cells
errs = ('#REF!', '#NAME?', '#VALUE!', '#DIV/0!', '#N/A', '#NUM!', '#NULL!')
nf = nnone = 0
for wsF, wsV in zip(Fm.worksheets, V.worksheets):
    for rowF, rowV in zip(wsF.iter_rows(), wsV.iter_rows()):
        for cF, cV in zip(rowF, rowV):
            if isinstance(cV.value, str) and cV.value in errs:
                bad(f"{wsV.title}!{cV.coordinate} = {cV.value}")
            if isinstance(cF.value, str) and cF.value.startswith('='):
                nf += 1
                if cV.value is None:
                    nnone += 1; bad(f"{wsV.title}!{cF.coordinate} formula has no cached value")
print(f"formula cells: {nf}, without cached value: {nnone}")

# 1. Watchlist H/I/L/Q recomputed from px.json by ticker
w = V['3日受惠清單 Watchlist']
wts = [w.cell(6, c).value for c in (13, 14, 15, 16)]
if abs(sum(wts) - 1.0) > 1e-9: bad(f"weights sum {sum(wts)}")
print("weights:", wts, "sum cell Q6 =", w.cell(6, 17).value)
n = 0
r = 9
while w.cell(r, 3).value:
    tk = w.cell(r, 3).value; p = PX[tk]; n += 1
    if not close(w.cell(r, 5).value, p['c16']): bad(f"{tk} close")
    if not close(w.cell(r, 8).value,  p['c16']/p['c15'] - 1): bad(f"{tk} d16%")
    if not close(w.cell(r, 9).value,  p['c16']/p['c09'] - 1): bad(f"{tk} 5d%")
    if not close(w.cell(r, 12).value, p['v16']/p['vmed']):    bad(f"{tk} rvol")
    m, fl, fr, bd = (w.cell(r, c).value for c in (13, 14, 15, 16))
    exp = (m*wts[0] + fl*wts[1] + fr*wts[2] + bd*wts[3]) * 20
    if not close(w.cell(r, 17).value, exp): bad(f"{tk} composite {w.cell(r,17).value} != {exp}")
    if not (0 <= w.cell(r, 17).value <= 100): bad(f"{tk} composite out of range")
    r += 1
print(f"watchlist rows verified: {n}")
avg = sum(w.cell(x, 17).value for x in range(9, 9+n)) / n
if not close(w.cell(9+n, 17).value, avg): bad("watchlist footer avg")

# 2. Avoid sheet
a = V['迴避清單 Avoid']; r = 9; m = 0
while a.cell(r, 2).value:
    tk = a.cell(r, 2).value; p = PX[tk]; m += 1
    if not close(a.cell(r, 7).value,  p['c16']/p['c15'] - 1): bad(f"avoid {tk} d16%")
    if not close(a.cell(r, 8).value,  p['c16']/p['c09'] - 1): bad(f"avoid {tk} 5d%")
    if not close(a.cell(r, 11).value, p['v16']/p['vmed']):    bad(f"avoid {tk} rvol")
    r += 1
print(f"avoid rows verified: {m}")

# 3. Evidence sheet: 111 rows, values match sec.json, rank formula = 1..111
e = V['板塊資金流證據 Evidence']
for i, s in enumerate(SEC['rows'], 1):
    rr = 8 + i
    if e.cell(rr, 1).value != i: bad(f"evidence rank row {rr} = {e.cell(rr,1).value} != {i}")
    if e.cell(rr, 2).value != s['zh']: bad(f"evidence name row {rr}")
    if not close(e.cell(rr, 5).value, s['s5']): bad(f"evidence s5 {s['zh']}")
    if s['zh'] != 'LNG液化天然氣' and not close(e.cell(rr, 8).value, s['r5']): bad(f"evidence r5 {s['zh']}")
if e.cell(8 + len(SEC['rows']) + 1, 1).value is not None: bad("evidence has extra row")
print(f"evidence rows verified: {len(SEC['rows'])}")
if e.cell(9 + SEC['rows'].index(next(x for x in SEC['rows'] if x['zh']=='LNG液化天然氣')), 8).value != 'n/a（數據缺陷）':
    bad("LNG row not flagged n/a")

# 4. Scenarios: P(B)=1-P(A); expected value = P(A)*A + P(B)*B
s = V['情境矩陣 Scenarios']
pa = s['E4'].value
if not close(s['E5'].value, 1 - pa): bad("P(B)")
hdr = next(rr for rr in range(1, 30) if s.cell(rr, 1).value == '組別')
r = hdr + 1
cnt = 0
while s.cell(r, 2).value and s.cell(r, 4).value is not None:
    d, ee, f = s.cell(r, 4).value, s.cell(r, 5).value, s.cell(r, 6).value
    if not close(f, pa*d + (1-pa)*ee): bad(f"scenario row {r}: {f} != {pa*d+(1-pa)*ee}")
    cnt += 1; r += 1
print(f"scenario rows verified: {cnt} (P(A)={pa}, header row {hdr})")
if cnt != 10: bad(f"scenario row count {cnt} != 10")
if not close(s.cell(r,6).value, sum(s.cell(x,6).value for x in range(hdr+1,hdr+7))/6): bad("scenario benefit avg")
if not close(s.cell(r+1,6).value, sum(s.cell(x,6).value for x in range(hdr+7,hdr+11))/4): bad("scenario avoid avg")

# 5. Summary cross-sheet stats
su = V['摘要 Summary']
found = {}
for rr in range(1, 40):
    for cc in (1, 4):
        lab = su.cell(rr, cc).value
        if isinstance(lab, str) and lab in ('受惠股檔數','迴避股檔數','受惠股平均綜合分','綜合分 ≥ 80 檔數'):
            found[lab] = su.cell(rr, cc+1).value
if found.get('受惠股檔數') != n: bad(f"summary count {found.get('受惠股檔數')} != {n}")
if found.get('迴避股檔數') != m: bad(f"summary avoid count {found.get('迴避股檔數')} != {m}")
if not close(found.get('受惠股平均綜合分'), avg): bad("summary avg composite")
exp80 = sum(1 for x in range(9, 9+n) if w.cell(x, 17).value >= 80)
if found.get('綜合分 ≥ 80 檔數') != exp80: bad(f"summary >=80 {found.get('綜合分 ≥ 80 檔數')} != {exp80}")
print("summary stats:", found, " (>=80 expected", exp80, ")")

# 6. pandas can read every sheet
import pandas as pd
for sh in V.sheetnames:
    df = pd.read_excel(FN, sheet_name=sh, header=None)
    if df.empty: bad(f"pandas read {sh} empty")
print("pandas read all sheets OK")

print("\nPROBLEMS:", len(P))
