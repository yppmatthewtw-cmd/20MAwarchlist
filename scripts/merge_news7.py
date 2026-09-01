#!/usr/bin/env python3
"""Merge carried-over R5 notes with the R6 batch research."""
import glob, json, os

SCRATCH = os.environ.get("WORK_DIR", "./data")
merged = dict(json.load(open(f"{SCRATCH}/news6.json")))   # 221 names carried forward
for e in merged.values():
    e.setdefault("src", "R5")
carried = len(merged)

added = 0
files = sorted(glob.glob(f"{SCRATCH}/news7_*.json"))
for f in files:
    try:
        d = json.load(open(f))
    except Exception as ex:
        print("  skip", os.path.basename(f), ex); continue
    for sym, e in d.items():
        if not isinstance(e, dict): continue
        merged[sym] = {"sym": sym,
                       "decline_short": e.get("decline_short", "—"),
                       "recovery_short": e.get("recovery_short", "—"),
                       "hype": bool(e.get("hype")),
                       "hype_zh": e.get("hype_zh", "") or "",
                       "confidence": e.get("confidence", "低"),
                       "tags": e.get("tags", []),
                       "src": os.path.basename(f)}
        added += 1
print(f"carried forward: {carried} | R7 batch files: {len(files)} entries {added} | total {len(merged)}")
json.dump(merged, open(f"{SCRATCH}/news7.json", "w"), ensure_ascii=False)

o = json.load(open(f"{SCRATCH}/screen_results7.json"))
listed = [r["sym"] for r in o["page1"]]
missing = [s for s in listed if s not in merged]
conf, hype = {}, 0
for s in listed:
    e = merged.get(s)
    if not e: continue
    conf[e["confidence"]] = conf.get(e["confidence"], 0) + 1
    hype += bool(e["hype"])
print(f"listed {len(listed)}, covered {len(listed)-len(missing)}, missing {len(missing)}: {missing}")
print("confidence:", conf, "| hype:", hype)
