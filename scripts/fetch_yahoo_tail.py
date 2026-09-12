#!/usr/bin/env python3
"""Pull the JUST-CLOSED session's bar from Yahoo for the report universe.

scripts/fetch_yahoo.py asks Yahoo for a date range, and Yahoo's consolidated daily
history does not carry the session that closed a few hours ago: the 2026-09-10
20:58 ET pull returned 09-09 for 532 of 535 symbols and 09-10 for 4.  That leaves
the newest close with only one source, and every name the daily-bar mirror does not
carry (129 of the sub-sector universe: ARM, ASML, TSM, IONQ, OKLO, RKLB, CRWV ...)
with no bar at all for it.

Yahoo does expose the live session through the quote/chart endpoints, so this script
tries three routes per symbol, newest-first, and keeps the first that yields a bar
dated after --since:

  1. history(period="5d")            -- the range call with a relative period
  2. history(period="1d", interval="1h") aggregated into a daily bar
  3. fast_info                       -- open/day_high/day_low/last_price/last_volume

Each row records which route produced it, so the engine can decide what to trust.

The hourly route sums regular-session hourly prints and therefore MISSES the closing
auction: measured against the daily-bar mirror on 402 names for 2026-09-10, its volume
runs a median 1.286x low with a wide spread (p05 1.105, p95 1.678).  The quote endpoint
reports regularMarketVolume, which is the exchange's running session total and does
include the auction once the session has closed.  So every row also carries the quote's
volume and price in separate columns (quote_volume / quote_price), letting the engine --
and the verifier -- check the quote total against the hourly sum before relying on it.
Prices are unadjusted, matching fetch_yahoo.py.
"""
import csv, gzip, os, sys, time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import yfinance as yf

SINCE = os.environ.get("SINCE")                    # only keep bars strictly after this date
LIST = os.environ.get("LIST", "data/yahoo/tickers.txt")
OUT = os.environ.get("OUT", "data/yahoo/tail.csv.gz")
WORKERS = int(os.environ.get("WORKERS", "8"))
if not SINCE:
    sys.exit("SINCE is required (the last session already covered by the history pull)")

symbols = [s.strip() for s in open(LIST) if s.strip()]
ysym = {s: s.replace(".", "-").replace("/", "-") for s in symbols}
print(f"{len(symbols)} symbols, want sessions after {SINCE}")


def quote_fields(t):
    """regularMarketVolume / last price from the quote endpoint, or (None, None)."""
    try:
        fi = t.fast_info
        v = fi.get("last_volume")
        c = fi.get("last_price")
        return (float(v) if v else None), (float(c) if c else None)
    except Exception:
        return None, None


def rows_from_frame(sub, sym, route):
    out = []
    if sub is None or sub.empty:
        return out
    sub = sub.dropna(subset=["Close"]).reset_index()
    dcol = "Date" if "Date" in sub.columns else sub.columns[0]
    for _, r in sub.iterrows():
        d = pd.to_datetime(r[dcol]).strftime("%Y-%m-%d")
        if d <= SINCE:
            continue
        try:
            o, h, l, c = (float(r[k]) for k in ("Open", "High", "Low", "Close"))
            v = float(r.get("Volume") or 0)
        except (TypeError, ValueError):
            continue
        if c > 0:
            out.append([sym, d, o, h, l, c, c, v, route])
    return out


def one(sym):
    y = ysym[sym]
    t = yf.Ticker(y)
    qv, qc = quote_fields(t)                        # session total incl. the closing auction
    def tag(rows):
        for r in rows:                              # only the newest row is "today" for the quote
            r += [qv if r is rows[-1] else None, qc if r is rows[-1] else None]
        return rows
    try:                                            # 1. relative-period daily history
        got = rows_from_frame(t.history(period="5d", interval="1d", auto_adjust=False,
                                        actions=False), sym, "hist5d")
        if got:
            return tag(got)
    except Exception:
        pass
    try:                                            # 2. hourly bars folded into a daily bar
        h = t.history(period="2d", interval="1h", auto_adjust=False, actions=False)
        if h is not None and not h.empty:
            h = h.dropna(subset=["Close"])
            h.index = pd.to_datetime(h.index)
            day = h.index.strftime("%Y-%m-%d")
            last = day[-1]
            if last > SINCE:
                sl = h[day == last]
                got = [[sym, last, float(sl["Open"].iloc[0]), float(sl["High"].max()),
                        float(sl["Low"].min()), float(sl["Close"].iloc[-1]),
                        float(sl["Close"].iloc[-1]), float(sl["Volume"].sum()), "hourly"]]
                return tag(got)
    except Exception:
        pass
    try:                                            # 3. quote snapshot
        fi = t.fast_info
        c = float(fi["last_price"])
        d = pd.Timestamp.utcnow().tz_localize("UTC").tz_convert("America/New_York").strftime("%Y-%m-%d")
        if c > 0 and d > SINCE:
            return tag([[sym, d, float(fi.get("open") or c), float(fi.get("day_high") or c),
                         float(fi.get("day_low") or c), c, c, float(fi.get("last_volume") or 0), "quote"]])
    except Exception:
        pass
    return []


rows = []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for i, got in enumerate(ex.map(one, symbols)):
        rows += got
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(symbols)} done, {len(rows)} bars")

if not rows:
    sys.exit("no tail bars at all; refusing to write")
by_route = {}
for r in rows:
    by_route[r[8]] = by_route.get(r[8], 0) + 1
dates = {}
for r in rows:
    dates[r[1]] = dates.get(r[1], 0) + 1
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with gzip.open(OUT, "wt", newline="") as f:
    w = csv.writer(f)
    w.writerow(["symbol", "date", "open", "high", "low", "close", "adj_close", "volume",
                "route", "quote_volume", "quote_price"])
    for r in sorted(rows, key=lambda x: (x[0], x[1])):
        w.writerow(r[:2] + [f"{x:.4f}" for x in r[2:8]] + [r[8]]
                   + ["" if r[9] is None else f"{r[9]:.4f}", "" if r[10] is None else f"{r[10]:.4f}"])
print(f"wrote {OUT}: {len(rows)} bars, {len({r[0] for r in rows})} symbols")
print("by route:", by_route)
print("by date:", dict(sorted(dates.items())))
