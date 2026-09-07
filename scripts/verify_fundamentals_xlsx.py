#!/usr/bin/env python3
"""Independent check of the revenue/profit workbook: re-derives every number straight from
data/yahoo/fundamentals_income.csv and the two watchlist JSONs, without importing the builder."""
import csv, collections, json, os, sys
import openpyxl

REPO = "/home/user/20MAwarchlist"
XLSX = sys.argv[1]
P = []
def bad(m): P.append(m)

inc = collections.defaultdict(lambda: collections.defaultdict(dict))
for r in csv.DictReader(open(f"{REPO}/data/yahoo/fundamentals_income.csv")):
    def num(k):
        v = r.get(k)
        try: return float(v) if v not in (None, "", "None") else None
        except ValueError: return None
    inc[r["symbol"]][r["period_type"]][r["period_end"]] = {k: num(k) for k in
        ("total_revenue", "gross_profit", "operating_income", "net_income")}
SUB = json.load(open(f"{REPO}/data/subsector_flow4.json")); AI = json.load(open(f"{REPO}/data/ai_flow5.json"))
sub_of, ai_of = collections.defaultdict(list), collections.defaultdict(list)
for r in SUB["rows"]:
    for t in (r.get("basket") or []): sub_of[t].append(r["zh"])
for r in AI["rows"]:
    for t in (r.get("basket") or []): ai_of[t].append(r["code"])
UNI = sorted(set(sub_of) | set(ai_of))
M = 1e6
def qs(sym, key, n=5):
    q = inc[sym]["quarterly"]; per = sorted(q, reverse=True)[:n][::-1]
    return [(p, (q[p][key] / M if q[p][key] is not None else None)) for p in per]

wbv = openpyxl.load_workbook(XLSX, data_only=True)
wbf = openpyxl.load_workbook(XLSX)
if wbv.sheetnames != ["說明", "觀察名單", "明細對照", "子板塊彙總", "AI小群組彙總", "分級彙總", "圖表連結", "資料來源"]:
    bad(f"sheet names {wbv.sheetnames}")
wv, wf = wbv["觀察名單"], wbf["觀察名單"]
if wv.max_row - 1 != len(UNI): bad(f"rows {wv.max_row-1} != universe {len(UNI)}")

def close(a, b, tol=5e-4):
    if a is None or a == "": return b is None
    if b is None: return False
    return abs(a - b) <= tol * max(1.0, abs(b))

grade_count = collections.Counter()
for i, t in enumerate(UNI, start=2):
    if wv.cell(i, 2).value != t: bad(f"row {i} ticker {wv.cell(i,2).value} != {t}")
    rev, opi = qs(t, "total_revenue"), qs(t, "operating_income")
    gp, ni = qs(t, "gross_profit"), qs(t, "net_income")
    for k in range(5):                                   # H..L
        exp = rev[k][1] if k < len(rev) else None
        got = wv.cell(i, 8 + k).value
        if not close(got, exp): bad(f"{t} revenue Q-{4-k}: {got} != {exp}")
    o4 = [opi[k + 1][1] if len(opi) >= 5 else (opi[k][1] if k < len(opi) else None) for k in range(4)]
    for k in range(4):
        got = wv.cell(i, 14 + k).value
        if not close(got, o4[k]): bad(f"{t} operating income Q-{3-k}: {got} != {o4[k]}")
    rQ0 = rev[-1][1] if rev else None
    rQ4 = rev[0][1] if len(rev) >= 5 else None
    exp_yoy = (rQ0 / rQ4 - 1) if (rQ0 is not None and rQ4) else ""
    got = wv.cell(i, 13).value
    if exp_yoy == "":
        if got not in (None, ""): bad(f"{t} yoy should be blank, got {got}")
    elif not close(got, exp_yoy, 1e-9): bad(f"{t} yoy {got} != {exp_yoy}")
    for col, num_, den in ((18, o4[-1], rQ0), (20, gp[-1][1] if gp else None, rQ0),
                           (22, ni[-1][1] if ni else None, rQ0)):
        exp = (num_ / den) if (num_ is not None and den) else ""
        got = wv.cell(i, col).value
        if exp == "":
            if got not in (None, ""): bad(f"{t} col{col} should be blank, got {got}")
        elif not close(got, exp, 1e-9): bad(f"{t} col{col} {got} != {exp}")
    if any(v is None for v in o4) or len(o4) < 4: g = "—"
    elif min(o4) > 0: g = "A"
    elif o4[-1] > 0: g = "B"
    else: g = "C" if o4[-1] > o4[0] else "D"
    if wv.cell(i, 27).value != g: bad(f"{t} grade {wv.cell(i,27).value} != {g}")
    grade_count[g] += 1
    if not str(wf.cell(i, 27).value or "").startswith("="): bad(f"{t} grade cell lost its formula")
    subs = "、".join(sub_of.get(t, [])) or "—"
    if wv.cell(i, 3).value != subs: bad(f"{t} subsector cell")
    link = wf.cell(i, 2).hyperlink
    if not link or t.lower() not in link.target: bad(f"{t} hyperlink")

# group totals
wd = wbv["明細對照"]
pairs = collections.defaultdict(list)
for r in range(2, wd.max_row + 1):
    pairs[(wd.cell(r, 1).value, wd.cell(r, 2).value)].append(wd.cell(r, 3).value)
exp_pairs = len([1 for t, gs in sub_of.items() for _ in gs]) + len([1 for t, gs in ai_of.items() for _ in gs])
if wd.max_row - 1 != exp_pairs: bad(f"detail rows {wd.max_row-1} != {exp_pairs}")
CCY = {r["symbol"]: (r.get("financialCurrency") or r.get("currency") or "—")
       for r in csv.DictReader(open(f"{REPO}/data/yahoo/fundamentals_profile.csv"))}
for i, t in enumerate(UNI, start=2):
    if wv.cell(i, 6).value != CCY.get(t, "—"): bad(f"{t} currency cell")
for sheet, kind, of_ in (("子板塊彙總", "子板塊", sub_of), ("AI小群組彙總", "AI 小群組", ai_of)):
    w = wbv[sheet]
    for r in range(2, w.max_row + 1):
        grp = w.cell(r, 2).value
        members = pairs[(kind, grp)]
        if len(members) != w.cell(r, 3).value: bad(f"{sheet} {grp} member count")
        usd = [t for t in members if CCY.get(t) == "USD"]
        er = sum((qs(t, "total_revenue")[-1][1] or 0) for t in usd if qs(t, "total_revenue"))
        eo = 0.0
        for t in usd:
            o = qs(t, "operating_income")
            if o and o[-1][1] is not None: eo += o[-1][1]
        if not close(w.cell(r, 4).value, er, 1e-6): bad(f"{sheet} {grp} revenue sum {w.cell(r,4).value} != {er}")
        if not close(w.cell(r, 5).value, eo, 1e-6): bad(f"{sheet} {grp} opinc sum {w.cell(r,5).value} != {eo}")
        if w.cell(r, 8).value != len(members) - len(usd): bad(f"{sheet} {grp} non-USD count")
        # a non-USD member must never contribute to the totals
        for t in members:
            if CCY.get(t) != "USD" and (qs(t, "total_revenue") and (qs(t, "total_revenue")[-1][1] or 0) > 0):
                if close(w.cell(r, 4).value, er + qs(t, "total_revenue")[-1][1], 1e-6):
                    bad(f"{sheet} {grp} appears to include non-USD {t}")
wg = wbv["分級彙總"]
for r in range(2, 7):
    g = wg.cell(r, 1).value
    if wg.cell(r, 3).value != grade_count[g]: bad(f"grade summary {g}: {wg.cell(r,3).value} != {grade_count[g]}")
if wg.cell(7, 3).value != len(UNI): bad("grade total")
# every formula cell carries a cached value, except the ones that legitimately evaluate to ""
# (a missing input makes the guard return an empty string, which reads back as None)
blank_ok = blank_bad = 0
GUARD = {"觀察名單": {13: (12, 8), 18: (17, 12), 20: (19, 12), 22: (21, 12), 25: (24, 23)}}
for name in wbf.sheetnames:
    af, bv = wbf[name], wbv[name]
    for row in af.iter_rows():
        for c in row:
            if not (isinstance(c.value, str) and c.value.startswith("=")): continue
            if bv[c.coordinate].value is not None: continue
            g = GUARD.get(name, {}).get(c.column)
            if g and bv.cell(c.row, g[0]).value is not None and bv.cell(c.row, g[1]).value not in (None, 0):
                blank_bad += 1
            else:
                blank_ok += 1
if blank_bad: bad(f"{blank_bad} formula cells blank although their inputs are present")
print(f"formula cells blank because an input is missing: {blank_ok} (expected)")
print(f"checked {len(UNI)} tickers, {wd.max_row-1} membership pairs, grades {dict(grade_count)}")
print("PROBLEMS:", len(P))
for m in P[:25]: print("  -", m)
