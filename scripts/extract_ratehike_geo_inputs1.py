# -*- coding: utf-8 -*-
"""Step 1/4 of the 加息及地緣政治 3 日觀察清單 pipeline.

Pulls the two inputs the workbook is built from, into px.json / sec.json:
  · per-ticker closes and volumes around the 2026-09-16 close, from the Yahoo
    broad pull committed by the Actions runner
  · the 111 sub-sector flow rows from SubSector 資金流向 Watchlist R11.00
Run from the repository root.
"""
import gzip, csv, collections, statistics, json

BROAD = 'data/yahoo/broad_2026-09-18.csv.gz'
FLOW  = 'data/subsector_flow11.json'
PX_OUT  = 'data/ratehike_geo_px.json'
SEC_OUT = 'data/ratehike_geo_sec.json'
IDX_OUT = 'data/ratehike_geo_idx.json'   # every distinct ticker in the workbook
D16   = '2026-09-16'
LOOKBACK = 20          # sessions behind D16 used for the volume baseline
BACK5    = 5           # sessions behind D16 for the 5-day return

WANT = """VLO MPC DINO PBF PSX UHS THC HCA EHC A TMO DHR ILMN GEV ETN PWR HUBB EMR TRV RNR AIG CB PGR
SNPS CDNS ARM COHR LITE CRDO TSM CLF NUE RS STLD
COP EOG FANG DVN OXY APA SLB HAL BKR RIG VAL NE XOM CVX
USB PNC ZION TFC MTB GS MS EVR JEF
CCJ UEC LEU OKLO SMR NNE MP USAR
DHI LEN PHM NVR TOL COIN HOOD MARA RIOT
FDX UPS ODFL XPO T VZ TMUS NEE FSLR ENPH RUN""".split()

S = collections.defaultdict(dict)
with gzip.open(BROAD, 'rt') as f:
    for r in csv.DictReader(f):
        if r['symbol'] in WANT:
            S[r['symbol']][r['date']] = (float(r['close']), float(r['volume']))

px, missing = {}, []
for s in WANT:
    b = S.get(s)
    if not b or D16 not in b:
        missing.append(s); continue
    ds = sorted(b); i = ds.index(D16)
    if i < LOOKBACK + 1:
        missing.append(s); continue
    vols = [b[d][1] for d in ds[i - LOOKBACK:i] if b[d][1]]
    px[s] = dict(c16=b[D16][0], c15=b[ds[i - 1]][0], c09=b[ds[i - BACK5]][0],
                 v16=b[D16][1], vmed=statistics.median(vols),
                 d15=ds[i - 1], d09=ds[i - BACK5])
if missing:
    raise SystemExit(f"no usable bars for: {missing}")
json.dump(px, open(PX_OUT, 'w'))
print(f"{PX_OUT}: {len(px)} tickers")

F = json.load(open(FLOW))
rows = []
for r in sorted(F['rows'], key=lambda x: -x['score5']):
    d = r['days'].get(D16)
    rows.append(dict(zh=r['zh'], en=r['en'], sec=r['sector'], s5=r['score5'],
                     s16=(d['score'] if d else None), r16=(d['ret'] if d else None),
                     r5=r['ret5'], bd5=r['breadth5'], bd16=(d['breadth'] if d else None),
                     rvol16=(d['rvol'] if d else None), slope=r['slope'], mfd5=r['mfd5'],
                     mfd16=(d['mfd'] if d else None), tick=','.join(r['basket'])))
json.dump(dict(rows=rows, mkt=F['meta']['mkt_med'], days=F['meta']['days'],
               mktn=F['meta']['mkt_n'], prov=F['meta'].get('provisional_vol_days')),
          open(SEC_OUT, 'w'))
print(f"{SEC_OUT}: {len(rows)} sub-sectors, provisional-volume days {F['meta'].get('provisional_vol_days')}")

# Every ticker that appears anywhere in the workbook -- the two lists plus all 111
# baskets -- so the 代號索引 sheet can give each one its own row, link and move.
universe = set(px)
for r in rows:
    universe |= set(r['tick'].split(','))
S2 = collections.defaultdict(dict)
with gzip.open(BROAD, 'rt') as f:
    for r in csv.DictReader(f):
        if r['symbol'] in universe:
            S2[r['symbol']][r['date']] = (float(r['close']), float(r['volume']))
idx, thin = {}, []
for s in sorted(universe):
    b = S2.get(s)
    if not b or D16 not in b:
        thin.append(s); continue
    ds = sorted(b); i = ds.index(D16)
    if i < LOOKBACK + 1:
        thin.append(s); continue
    vols = [b[d][1] for d in ds[i - LOOKBACK:i] if b[d][1]]
    idx[s] = dict(c16=b[D16][0], c15=b[ds[i - 1]][0], c09=b[ds[i - BACK5]][0],
                  v16=b[D16][1], vmed=statistics.median(vols))
json.dump(idx, open(IDX_OUT, 'w'))
print(f"{IDX_OUT}: {len(idx)} tickers" + (f", {len(thin)} without enough history: {thin}" if thin else ""))
