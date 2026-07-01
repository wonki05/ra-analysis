# -*- coding: utf-8 -*-
"""Probe text-layer quality of each year's PDF and dump full text to rendered_pdf."""
import os, io, sys, glob
import fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"E:\LEET\ra-project-vlm"
DOCS = os.path.join(ROOT, "docs_problems")
OUT = os.path.join(ROOT, "problem-set", "_audit", "rendered_pdf")

for y in range(2012, 2027):
    hits = glob.glob(os.path.join(DOCS, f"{y}_*.pdf"))
    if not hits:
        print(f"{y}: NO PDF"); continue
    doc = fitz.open(hits[0])
    total_chars = 0
    parts = []
    for p in doc:
        t = p.get_text()
        total_chars += len(t.strip())
        parts.append(t)
    npages = doc.page_count
    doc.close()
    # save text
    txtpath = os.path.join(OUT, f"{y}_pdftext.txt")
    with open(txtpath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    quality = "TEXT-LAYER" if total_chars > 2000 else "SCAN/NO-TEXT"
    print(f"{y}: pages={npages} chars={total_chars} -> {quality}")
