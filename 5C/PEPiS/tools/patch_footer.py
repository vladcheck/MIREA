# -*- coding: utf-8 -*-
"""Patch report-pr1.docx: add footerReference to sectPr and re-add the
footer relationship removed by the docx-mcp save-time repair.

The docx-mcp server can create word/footer1.xml via write_part, but its
save-time repair strips the footer relationship because document.xml does
not reference it yet. This script performs the final wiring:
  1. inserts <w:footerReference w:type="default" r:id="rId9"/> as the first
     child of the only <w:sectPr> in word/document.xml;
  2. re-adds the rId9 footer Relationship in word/_rels/document.xml.rels.

Run with system python3 (stdlib only, no venv needed):
    python3 tools/patch_footer.py
"""

import re
import shutil
import zipfile
from pathlib import Path

DOCX = Path(__file__).resolve().parent.parent / "pr1-2" / "pr1" / "report-pr1.docx"
TMP = DOCX.with_suffix(".patched.docx")

FOOTER_REF = '<w:footerReference w:type="default" r:id="rId9"/>'
FOOTER_REL = (
    '<Relationship Id="rId9" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/footer" Target="footer1.xml"/>'
)

with zipfile.ZipFile(DOCX) as zin:
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}

doc = data["word/document.xml"].decode("utf-8")
assert "rId9" not in doc, "footerReference already present?"
# sectPr opening tag carries the namespace declarations; footerReference
# must be the FIRST child of sectPr per the OOXML sequence.
m = re.search(r"<w:sectPr[^>]*>", doc)
assert m, "sectPr not found"
doc = doc[: m.end()] + FOOTER_REF + doc[m.end() :]
data["word/document.xml"] = doc.encode("utf-8")

rels = data["word/_rels/document.xml.rels"].decode("utf-8")
assert 'Target="footer1.xml"' not in rels, "footer rel already present?"
rels = rels.replace("</Relationships>", FOOTER_REL + "</Relationships>")
data["word/_rels/document.xml.rels"] = rels.encode("utf-8")

with zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as zout:
    for n in names:
        zout.writestr(n, data[n])

shutil.move(str(TMP), str(DOCX))
print(f"patched OK: {DOCX}")
