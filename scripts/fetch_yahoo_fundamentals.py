#!/usr/bin/env python3
"""Pull income-statement fundamentals from Yahoo Finance for the tickers in
data/yahoo/fund_tickers.txt — run on a GitHub Actions runner (the research container's
egress proxy blocks Yahoo), see .github/workflows/fetch_yahoo_fundamentals.yml.

Writes two CSVs:
  data/yahoo/fundamentals_income.csv  one row per (symbol, period_type, period_end) with the
                                      revenue / profit line items of that income statement;
  data/yahoo/fundamentals_profile.csv one row per symbol with the descriptive fields and the
                                      trailing ratios Yahoo derives itself.

Annual statements are the audited full-year figures; quarterly are the last reported quarters.
Nothing is derived or estimated here — the report layer does the arithmetic, so a missing
line item stays empty rather than becoming a zero.
"""
import csv, os, sys, time

import yfinance as yf

LIST = os.environ.get("LIST", "data/yahoo/fund_tickers.txt")
OUT_INC = os.environ.get("OUT_INC", "data/yahoo/fundamentals_income.csv")
OUT_PRO = os.environ.get("OUT_PRO", "data/yahoo/fundamentals_profile.csv")

# Yahoo's row labels for what we want; first match wins (labels vary by filer).
ITEMS = {
    "total_revenue":    ["Total Revenue", "Operating Revenue"],
    "cost_of_revenue":  ["Cost Of Revenue"],
    "gross_profit":     ["Gross Profit"],
    "operating_expense": ["Operating Expense", "Total Expenses"],
    "operating_income": ["Operating Income", "Total Operating Income As Reported", "EBIT"],
    "pretax_income":    ["Pretax Income"],
    "net_income":       ["Net Income", "Net Income Common Stockholders",
                         "Net Income From Continuing Operation Net Minority Interest"],
    "ebitda":           ["EBITDA", "Normalized EBITDA"],
    "diluted_eps":      ["Diluted EPS"],
    "basic_eps":        ["Basic EPS"],
    "rnd":              ["Research And Development"],
}
PROFILE = ["longName", "sector", "industry", "country", "currency", "financialCurrency",
           "marketCap", "totalRevenue", "revenueGrowth", "earningsGrowth",
           "earningsQuarterlyGrowth", "grossMargins", "operatingMargins", "profitMargins",
           "ebitdaMargins", "returnOnEquity", "trailingEps", "forwardEps", "trailingPE",
           "forwardPE", "priceToSalesTrailing12Months", "mostRecentQuarter", "lastFiscalYearEnd"]

symbols = [s.strip() for s in open(LIST) if s.strip()]
ysym = {s: s.replace(".", "-").replace("/", "-") for s in symbols}   # Nasdaq BRK.B -> Yahoo BRK-B
print(f"{len(symbols)} symbols")

def grab(df, names):
    """Value of the first present row label, as {period_end: value}."""
    if df is None or df.empty:
        return {}
    for n in names:
        if n in df.index:
            row = df.loc[n]
            if hasattr(row, "iloc") and getattr(row, "ndim", 1) > 1:
                row = row.iloc[0]
            return {str(c)[:10]: (None if _isna(v) else float(v)) for c, v in row.items()}
    return {}

def _isna(v):
    try:
        return v is None or v != v
    except Exception:
        return True

inc_rows, pro_rows, failed = [], [], []
for i, s in enumerate(symbols, 1):
    t = yf.Ticker(ysym[s])
    got = 0
    for kind, getter in (("annual", "income_stmt"), ("quarterly", "quarterly_income_stmt")):
        for attempt in range(3):
            try:
                df = getattr(t, getter)
                break
            except Exception as e:
                print(f"{s} {kind}: attempt {attempt + 1} failed: {e}")
                time.sleep(10 * (attempt + 1))
        else:
            continue
        series = {k: grab(df, v) for k, v in ITEMS.items()}
        periods = sorted({p for m in series.values() for p in m}, reverse=True)
        for p in periods[:5]:
            row = {"symbol": s, "period_type": kind, "period_end": p}
            row.update({k: series[k].get(p) for k in ITEMS})
            if any(row[k] is not None for k in ITEMS):
                inc_rows.append(row); got += 1
    try:
        info = t.get_info() or {}
    except Exception:
        info = {}
    if info:
        pro_rows.append({"symbol": s, **{k: info.get(k) for k in PROFILE}})
    if not got and not info:
        failed.append(s)
    if i % 25 == 0:
        print(f"  {i}/{len(symbols)} — {len(inc_rows)} statement rows, {len(pro_rows)} profiles")
    time.sleep(0.4)

if not inc_rows:
    sys.exit("no fundamentals at all; refusing to write")
os.makedirs(os.path.dirname(OUT_INC), exist_ok=True)
with open(OUT_INC, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["symbol", "period_type", "period_end"] + list(ITEMS))
    w.writeheader(); w.writerows(inc_rows)
with open(OUT_PRO, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["symbol"] + PROFILE)
    w.writeheader(); w.writerows(pro_rows)
n_sym = len({r["symbol"] for r in inc_rows})
print(f"wrote {OUT_INC}: {len(inc_rows)} rows, {n_sym} symbols")
print(f"wrote {OUT_PRO}: {len(pro_rows)} rows")
if failed:
    print("no data:", " ".join(failed))
if n_sym < 0.7 * len(symbols):
    sys.exit(f"only {n_sym}/{len(symbols)} symbols returned; refusing to commit")
