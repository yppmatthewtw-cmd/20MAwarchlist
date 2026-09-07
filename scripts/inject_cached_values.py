#!/usr/bin/env python3
"""Write cached results next to the formulas openpyxl produced.

openpyxl emits <c><f>FORMULA</f></c> with no <v>, so until a spreadsheet application
recalculates the file, every formula cell reads back as empty to pandas, previewers and
anything else that trusts the cached value. LibreOffice cannot run in this container
(it times out at startup even on a three-cell workbook), so this patches the cached
values in directly: the formula stays live and recalculates on open, and readers that
only look at <v> now see the right number.
"""
import re, shutil, zipfile
from xml.etree import ElementTree as ET

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
ET.register_namespace("", NS)


def inject(path, cache, sheet_order):
    """cache: {sheet_name: {cell_ref: value}}; sheet_order: sheet names in workbook order."""
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin:
        names = zin.namelist()
        sheet_files = sorted((n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
                             key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[1]).group(1)))
        by_sheet = dict(zip(sheet_order, sheet_files))
        patched, missing = {}, 0
        for sname, fname in by_sheet.items():
            want = cache.get(sname)
            if not want:
                continue
            root = ET.fromstring(zin.read(fname))
            n = 0
            for c in root.iter(f"{{{NS}}}c"):
                ref = c.get("r")
                if ref not in want:
                    continue
                f = c.find(f"{{{NS}}}f")
                if f is None:
                    continue
                for v in c.findall(f"{{{NS}}}v"):
                    c.remove(v)
                val = want[ref]
                v = ET.SubElement(c, f"{{{NS}}}v")
                if isinstance(val, str):
                    c.set("t", "str")
                    v.text = val
                else:
                    c.attrib.pop("t", None)
                    v.text = repr(float(val)) if val is not None else ""
                n += 1
            missing += len(want) - n
            patched[sname] = n
            body = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
            by_sheet[sname] = (fname, body)
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            replace = {v[0]: v[1] for v in by_sheet.values() if isinstance(v, tuple)}
            for item in zin.infolist():
                data = replace.get(item.filename)
                zout.writestr(item, data if data is not None else zin.read(item.filename))
    shutil.move(tmp, path)
    return patched, missing
