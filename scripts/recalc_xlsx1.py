# -*- coding: utf-8 -*-
"""In-process stand-in for the xlsx skill's scripts/recalc.py.

This container ships libreoffice-core WITHOUT libreoffice-calc, so soffice cannot
load a spreadsheet at all ("source file could not be loaded" on even a three-cell
workbook) and recalc.py can never run here.  This evaluates every formula in the
workbook itself and hands the results to the existing XML writer in
scripts/inject_cached_values.py, so pandas / data_only readers / previewers see the
right numbers while the formulas stay live (calcPr/fullCalcOnLoad makes Excel
recompute them on open).

Covers the formula vocabulary these workbooks use: arithmetic over cell and
cross-sheet references plus SUM / AVERAGE / COUNT / COUNTA / COUNTIF / ROW.
Anything outside that raises rather than guessing.

    python3 scripts/recalc_xlsx1.py <workbook.xlsx>
"""
import os, re, sys
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string, get_column_letter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inject_cached_values import inject

REF   = re.compile(r"(?:'([^']+)'!)?\$?([A-Z]{1,3})\$?(\d+)")
RANGE = re.compile(r"(?:'([^']+)'!)?\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)")
FUNC  = re.compile(r"\b(SUM|AVERAGE|COUNT|COUNTA|COUNTIF)\(([^()]*)\)")
MAX_PASSES = 12


def _cells(sheet, c1, r1, c2, r2):
    for cc in range(column_index_from_string(c1), column_index_from_string(c2) + 1):
        for rr in range(int(r1), int(r2) + 1):
            yield (sheet, f"{get_column_letter(cc)}{rr}")


def evaluate_workbook(path):
    wb = load_workbook(path)
    lit, fml = {}, {}
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                if isinstance(c.value, str) and c.value.startswith("="):
                    fml[(ws.title, c.coordinate)] = c.value[1:]
                else:
                    lit[(ws.title, c.coordinate)] = c.value
    VAL = dict(lit)
    cur = [None]

    def run(sheet, expr):
        def do_func(m):
            fn, arg = m.group(1), m.group(2)
            crit = None
            if "," in arg:
                arg, crit = arg.split(",", 1)
                crit = crit.strip().strip('"')
            rm = RANGE.fullmatch(arg.strip())
            if not rm:
                raise ValueError("unsupported range: " + arg)
            sh = rm.group(1) or sheet
            keys = list(_cells(sh, rm.group(2), rm.group(3), rm.group(4), rm.group(5)))
            # A range may cover cells that are themselves formulas.  Until those are
            # evaluated the range is not yet knowable -- defer, rather than silently
            # aggregating over a partial range and returning a plausible-looking 0.
            pend = [k for k in keys if k in fml and k not in VAL]
            if pend:
                raise KeyError("pending " + pend[0][1])
            vals = [VAL[k] for k in keys if k in VAL]
            nums = [float(v) for v in vals if isinstance(v, (int, float))]
            if fn == "SUM":     return repr(sum(nums))
            if fn == "AVERAGE": return repr(sum(nums) / len(nums)) if nums else "0"
            if fn == "COUNT":   return repr(float(len(nums)))
            if fn == "COUNTA":  return repr(float(len(vals)))
            op, num = re.match(r"(>=|<=|<>|>|<|=)?\s*(-?[\d.]+)", crit).groups()
            num, op = float(num), op or "="
            test = {">=": lambda v: v >= num, "<=": lambda v: v <= num, ">": lambda v: v > num,
                    "<": lambda v: v < num, "=": lambda v: v == num, "<>": lambda v: v != num}[op]
            return repr(float(sum(1 for v in nums if test(v))))

        e = expr
        while FUNC.search(e):
            e = FUNC.sub(do_func, e, count=1)
        e = re.sub(r"\bROW\(\)", re.search(r"\d+", cur[0][1]).group(), e)

        def do_ref(m):
            v = VAL[(m.group(1) or sheet, m.group(2) + m.group(3))]
            if not isinstance(v, (int, float)):
                raise ValueError("non-numeric reference " + m.group(0))
            return repr(float(v))

        return float(eval(REF.sub(do_ref, e), {"__builtins__": {}}, {}))

    pending = dict(fml)
    for _ in range(MAX_PASSES):
        if not pending:
            break
        nxt = {}
        for k, f in pending.items():
            cur[0] = k
            try:
                VAL[k] = run(k[0], f)
            except (KeyError, ValueError, ZeroDivisionError):
                nxt[k] = f
        if len(nxt) == len(pending):
            raise SystemExit(f"unresolved formulas: {list(nxt.items())[:5]}")
        pending = nxt

    cache = {}
    for (sh, ref) in fml:
        cache.setdefault(sh, {})[ref] = VAL[(sh, ref)]
    return wb.sheetnames, cache, len(fml)


if __name__ == "__main__":
    path = sys.argv[1]
    order, cache, n = evaluate_workbook(path)
    patched, missing = inject(path, cache, order)
    print(f"evaluated {n} formulas; injected {sum(patched.values())} cached values "
          f"({missing} not found in the sheet XML)")
