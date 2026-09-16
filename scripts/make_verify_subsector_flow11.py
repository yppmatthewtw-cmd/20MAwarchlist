S = "/tmp/claude-0/-home-user-20MAwarchlist/0f749aae-85b5-584c-9175-237303814dd9/scratchpad"
src = open(f"{S}/sub10/verify10.py", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:90]); src = src.replace(a, b, 1)
rep('F = json.load(open(f"{SCR}/sub10/flow10.json"))', 'F = json.load(open(f"{SCR}/sub11/flow11.json"))')
# F1: the settled/provisional mark on each session's net-flow figure must match the volume verdict
rep('''print("PROBLEMS:", len(P))''',
'''exp_mfd = {d: (d not in (M.get("provisional_vol_days") or [])) for d in DAYS}
if exp_mfd != (M.get("mfd_settled") or {}):
    bad(f"mfd_settled {M.get('mfd_settled')} != {exp_mfd}")
print(f"net-flow settled by session: {M.get('mfd_settled')}")
print("PROBLEMS:", len(P))''')
open(f"{S}/sub11/verify11.py", "w", encoding="utf-8").write(src); print("sub11/verify11.py written")
