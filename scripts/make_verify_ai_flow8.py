S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/ai7/verify7.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:80]); src = src.replace(a, b, 1)

rep('F = json.load(open(f"{SCR}/ai7/flow7.json")', 'F = json.load(open(f"{SCR}/ai8/flow8.json")')

# --- own tail loader, own SOFTVOL rule (not read from the engine's meta) ---
rep('''def yh(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))''',
'''TAILP = "/home/user/20MAwarchlist/data/yahoo/tail.csv.gz"
SOFTVOL = set(); TAILN = collections.Counter()
if os.path.exists(TAILP):
    with gzip.open(TAILP, "rt", newline="") as f:
        for r in csv.DictReader(f):
            try: o, h, l, c, v = (float(r[k]) for k in ("open", "high", "low", "close", "volume"))
            except (ValueError, KeyError, TypeError): continue
            if c <= 0: continue
            sym = r["symbol"].replace("/", ".").replace("-", ".")
            if r["date"] in YH.get(sym, {}): continue
            YH.setdefault(sym, {})[r["date"]] = (o, h, l, c, v)
            TAILN[r["date"]] += 1
            if r.get("route") != "hist5d": SOFTVOL.add((sym, r["date"]))
print(f"tail bars merged: {dict(TAILN)}, soft-volume pairs {len(SOFTVOL)}")
def yh(sym): return YH.get(sym) or YH.get(sym.replace(".", "-"))''')

# --- calendar: per-source coverage, recomputed here from the raw files ---
rep('''# calendar around the window: sessions covered by >=80% of the scored names' merged bars
cov = collections.Counter()
NB = {}
for r in live:
    for t in r["basket"]:
        if t not in NB:
            NB[t] = merged(t)[0]
            for d in (NB[t] or {}): cov[d] += 1
full = sorted(d for d, n in cov.items() if n >= 0.8 * len(NB))''',
'''# calendar: each source measured against its OWN universe; a session counts when either is complete
NB = {}
nzc = collections.Counter(); yhc = collections.Counter(); nzu = yhu = 0
for r in live:
    for t in r["basket"]:
        if t in NB: continue
        NB[t] = merged(t)[0]
        a = nzraw(t); b = yh(t)
        if a:
            nzu += 1
            for d in a: nzc[d] += 1
        if b:
            yhu += 1
            for d in b: yhc[d] += 1
full = sorted({d for d in set(nzc) | set(yhc)
               if (nzu and nzc[d] >= 0.8 * nzu) or (yhu and yhc[d] >= 0.8 * yhu)})
print(f"calendar: mirror {nzu} names, yahoo {yhu} names, {len(full)} sessions")''')

# --- share-volume activity term, and the tail's soft volume ---
rep('''    bdv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(bdv) < 10
    if not nobase: med = statistics.median(bdv)
    else:
        a = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med = statistics.median(a) if a else None
    if not med: return None''',
'''    bdv = [data[d][3] * data[d][4] for d in BASE if d in data and data[d][4]]
    bsv = [data[d][4] for d in BASE if d in data and data[d][4]]
    nobase = len(bdv) < 10
    if not nobase:
        med = statistics.median(bdv); medsv = statistics.median(bsv)   # R7: activity in SHARES
    else:
        a = [data[d][3] * data[d][4] for d in LAST if d in data and data[d][4]]
        med = statistics.median(a) if a else None; medsv = None
    if not med: return None''')

rep('''        o, h, l, c, v = data[d]; pc = data[PREV[d]][3]
        ret = c / pc - 1; ex = ret - MKT[d]
        novol = v is None or nobase
        dv = c * v if v is not None else med
        rv = 1.0 if novol else dv / med''',
'''        o, h, l, c, v = data[d]; pc = data[PREV[d]][3]
        if (sym, d) in SOFTVOL and d not in (nzraw(sym) or {}): v = None   # tail-only bar
        ret = c / pc - 1; ex = ret - MKT[d]
        novol = v is None or nobase
        dv = c * v if v is not None else med
        rv = 1.0 if novol else (v / medsv if medsv else 1.0)''')

# --- check the engine's own claims about the newest session ---
rep('''prov = [d for d in DAYS if nzc[d] < 0.5 * typ]
if sorted(prov) != sorted(M.get("provisional_vol_days") or []):
    bad(f"provisional list {M.get('provisional_vol_days')} != {prov}")''',
'''prov = [d for d in DAYS if nzc[d] < 0.5 * typ]      # coverage test only: kept as a diagnostic,
# superseded below by the settled-print test, which is what the engine now claims''')

rep('print("PROBLEMS:", len(P))',
'''# ---- R7 data-integrity claims, re-measured here ----
def rounded_share(day):
    tot = rnd = 0
    for t in NB:
        b = (nzraw(t) or {}).get(day)
        if not b or not b[4]: continue
        tot += 1
        if abs(b[4] - round(b[4] / 100.0) * 100.0) < 1e-6: rnd += 1
    return rnd / tot if tot else None
mine = sorted(d for d in DAYS if (rounded_share(d) or 1.0) < 0.5)
if mine != sorted(M.get("provisional_vol_days") or []):
    bad(f"provisional days {mine} != {M.get('provisional_vol_days')}")
for d in DAYS:
    sh = rounded_share(d)
    if sh is not None and abs(sh - M.get("settled_print_share", {}).get(d, -1)) > 0.002:
        bad(f"settled-print share {d}: {sh:.4f} vs {M.get('settled_print_share', {}).get(d)}")
# every tail-sourced day must be scored with B = 0
for t, td in TK.items():
    for d in DAYS:
        if (t, d) in SOFTVOL and d not in (nzraw(t) or {}) and abs(td["days"][d]["B"]) > 0:
            bad(f"{t} {d} B nonzero on a tail-only bar")
# the newest session must actually be the newest one either source has
newest = max(d for d in full)
if DAYS[-1] != newest: bad(f"window ends {DAYS[-1]} but the sources carry {newest}")
print(f"newest session available {newest}, scored {DAYS[-1]}; provisional {mine}")
print("PROBLEMS:", len(P))''')
open(f"{S}/ai8/verify8.py", "w", encoding="utf-8").write(src); print("ai8/verify8.py written")
