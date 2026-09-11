S="/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src=open(f"{S}/sub6/flow6.py",encoding="utf-8").read()
def rep(a,b):
    global src
    assert a in src, a[:80]; src=src.replace(a,b,1)
rep('"""Sub-sector money-flow scoring — R6.00 engine (111 sub-sectors of the R2 heat-map workbook).',
 '"""Sub-sector money-flow scoring — R7.00 engine (111 sub-sectors of the R2 heat-map workbook).\n\n'
 'R7 separates the two jobs dollar volume was doing. Up to R6 the activity term B compared today\'s\n'
 'DOLLAR volume with a 20-day DOLLAR-volume median, so a stock that had re-rated since the baseline\n'
 'registered as "heavier trading" on identical share turnover — price drift leaking into a term that\n'
 'is supposed to measure participation. Measured over the R6 window: the leak is unbiased on average\n'
 '(mean +0.007 on B) but moves B by more than 0.10 on 6.7% of ticker-days, worst cases ~0.27\n'
 '(CRCL, CRM), which is a 13% swing in the (1 + 0.5B) multiplier.\n'
 'So B now compares SHARE volume with the 20-day SHARE-volume median, while dollar volume keeps the\n'
 'jobs where money is the point: basket weighting and the 淨額估算 net-flow figure.')
rep('''    base_dv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(base_dv) < 10                             # F4: no 20-day volume baseline
    if not nobase:
        med_dv = statistics.median(base_dv)
    else:                                                  # weight proxy only; B is held at 0
        any_dv = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med_dv = statistics.median(any_dv) if any_dv else None
    if not med_dv or med_dv <= 0: return None''',
'''    base_dv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4]]
    base_sv = [data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(base_dv) < 10                             # F4: no 20-day volume baseline
    if not nobase:
        med_dv = statistics.median(base_dv)
        med_sv = statistics.median(base_sv)                 # R7: activity baseline in SHARES
    else:                                                  # weight proxy only; B is held at 0
        any_dv = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med_dv = statistics.median(any_dv) if any_dv else None
        med_sv = None
    if not med_dv or med_dv <= 0: return None''')
rep('''    out = {"sym": sym, "src": srctag, "med_dv": med_dv, "basis_dev": BASIS.get(sym),
           "nobase": nobase, "days": {}}''',
'''    out = {"sym": sym, "src": srctag, "med_dv": med_dv, "med_sv": med_sv,
           "basis_dev": BASIS.get(sym), "nobase": nobase, "days": {}}''')
rep('''        novol = v is None or nobase                        # B unusable: unknown volume or no baseline
        dv = c * v if v is not None else med_dv            # weighting proxy when volume is unusable
        rvol = (dv / med_dv if med_dv > 0 else 1.0) if not novol else 1.0''',
'''        novol = v is None or nobase                        # B unusable: unknown volume or no baseline
        dv = c * v if v is not None else med_dv            # money weight (and the 淨額估算 base)
        # R7: activity is share turnover against a share-turnover baseline, so a re-rated price
        # cannot masquerade as heavier trading.
        rvol = (v / med_sv if (med_sv and v is not None) else 1.0) if not novol else 1.0''')
rep('''                "panel_balanced": True, "panel_pool": len(allnz),''',
'''                "panel_balanced": True, "panel_pool": len(allnz),
                "activity_basis": "share_volume",   # R7: B uses share turnover, not dollar turnover''')
rep('json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub6/flow6.json"), "w"), ensure_ascii=False)',
    'json.dump(out, open(os.environ.get("OUT_JSON", f"{SCR}/sub7/flow7.json"), "w"), ensure_ascii=False)')
open(f"{S}/sub7/flow7.py","w",encoding="utf-8").write(src); print("sub7/flow7.py written")
