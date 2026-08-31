#!/usr/bin/env python3
"""Merge R4's condensed notes with the R5 batch research into one news5.json."""
import glob, json, os

SCRATCH = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")

merged = {}

# 1) the 74 tickers researched for R3/R4: condensed text + confidence/tags from the long notes
long_notes = json.load(open(f"{SCRATCH}/news.json"))
short_notes = json.load(open(f"{SCRATCH}/news_short.json"))
for sym, s in short_notes.items():
    ln = long_notes.get(sym, {})
    merged[sym] = {
        "sym": sym,
        "decline_short": s.get("decline_short") or ln.get("decline_zh", "—"),
        "recovery_short": s.get("recovery_short") or ln.get("recovery_zh", "—"),
        "hype": bool(s.get("hype")),
        "hype_zh": s.get("hype_zh", ""),
        "confidence": ln.get("confidence", "低"),
        "tags": ln.get("tags", []),
        "src": "R4",
    }

# 2) the R5 batch files
files = sorted(glob.glob(f"{SCRATCH}/news5_*.json"))
added = 0
for f in files:
    try:
        d = json.load(open(f))
    except Exception as e:
        print("  skip", os.path.basename(f), e)
        continue
    for sym, e in d.items():
        if not isinstance(e, dict):
            continue
        merged[sym] = {
            "sym": sym,
            "decline_short": e.get("decline_short", "—"),
            "recovery_short": e.get("recovery_short", "—"),
            "hype": bool(e.get("hype")),
            "hype_zh": e.get("hype_zh", "") or "",
            "confidence": e.get("confidence", "低"),
            "tags": e.get("tags", []),
            "src": os.path.basename(f),
        }
        added += 1
print(f"batch files: {len(files)}, entries from batches: {added}, total merged: {len(merged)}")

json.dump(merged, open(f"{SCRATCH}/news5.json", "w"), ensure_ascii=False)

# coverage report against the R5 listing
o = json.load(open(f"{SCRATCH}/screen_results5.json"))
listed = [r["sym"] for r in o["page1"]]
missing = [s for s in listed if s not in merged]
conf = {}
hype = 0
for s in listed:
    e = merged.get(s)
    if not e:
        continue
    conf[e["confidence"]] = conf.get(e["confidence"], 0) + 1
    if e["hype"]:
        hype += 1
print(f"listed {len(listed)}, covered {len(listed) - len(missing)}, missing {len(missing)}: {missing}")
print("confidence:", conf, "| hype flagged:", hype)
over = [(s, len(merged[s]["decline_short"]), len(merged[s]["recovery_short"]))
        for s in listed if s in merged
        and (len(merged[s]["decline_short"]) > 46 or len(merged[s]["recovery_short"]) > 46)]
print("overlong:", len(over), over[:6])
