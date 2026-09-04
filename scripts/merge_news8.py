#!/usr/bin/env python3
"""news8.json = R7 notes (news7.json) + R8 batch research (news8_*.json) + R8 corrections (news8_fix.json)."""
import glob, json, os
SCR = os.environ.get("WORK_DIR", "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad")
merged = json.load(open(f"{SCR}/news7.json"))
n0 = len(merged)
files = sorted(glob.glob(f"{SCR}/news8_*.json"))
added = 0
for f in files:
    try: d = json.load(open(f))
    except Exception as e: print("  skip", os.path.basename(f), e); continue
    for sym, e in d.items():
        if not isinstance(e, dict): continue
        merged[sym] = {"sym": sym, "decline_short": e.get("decline_short", "—"), "recovery_short": e.get("recovery_short", "—"),
                       "hype": bool(e.get("hype")), "hype_zh": e.get("hype_zh", "") or "", "confidence": e.get("confidence", "低"),
                       "tags": e.get("tags", []), "src": os.path.basename(f)}
        added += 1
print(f"base {n0}, batch files {len(files)}, entries applied {added}, total {len(merged)}")
json.dump(merged, open(f"{SCR}/news8.json", "w"), ensure_ascii=False)
res = f"{SCR}/screen_results8.json"
if os.path.exists(res):
    o = json.load(open(res)); listed = [r["sym"] for r in o["page1"]]
    missing = [s for s in listed if s not in merged]
    conf = {}; hype = 0
    for s in listed:
        e = merged.get(s)
        if not e: continue
        conf[e["confidence"]] = conf.get(e["confidence"], 0) + 1; hype += bool(e["hype"])
    print(f"listed {len(listed)}, covered {len(listed)-len(missing)}, missing {missing}; confidence {conf}; hype {hype}")
    over = [(s, len(merged[s]["decline_short"]), len(merged[s]["recovery_short"])) for s in listed if s in merged and (len(merged[s]["decline_short"]) > 46 or len(merged[s]["recovery_short"]) > 46)]
    print("overlong:", over)
