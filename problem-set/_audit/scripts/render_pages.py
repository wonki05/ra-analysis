# -*- coding: utf-8 -*-
"""Render specified PDF pages to PNG.
Usage: python render_pages.py YEAR DPI PAGE [PAGE ...]
       python render_pages.py YEAR DPI all
Pages are 1-indexed. Output -> _audit/rendered_pdf/YEAR/pXX.png
"""
import os, sys, glob
import fitz
ROOT = r"E:\LEET\ra-project-vlm"
DOCS = os.path.join(ROOT, "docs_problems")
OUTBASE = os.path.join(ROOT, "problem-set", "_audit", "rendered_pdf")

year = sys.argv[1]
dpi = int(sys.argv[2])
pages_arg = sys.argv[3:]
pdf = glob.glob(os.path.join(DOCS, f"{year}_*.pdf"))[0]
doc = fitz.open(pdf)
outdir = os.path.join(OUTBASE, str(year))
os.makedirs(outdir, exist_ok=True)
if pages_arg == ["all"]:
    pages = list(range(1, doc.page_count+1))
else:
    pages = [int(p) for p in pages_arg]
zoom = dpi/72.0
mat = fitz.Matrix(zoom, zoom)
for pno in pages:
    page = doc[pno-1]
    pix = page.get_pixmap(matrix=mat)
    out = os.path.join(outdir, f"p{pno:02d}.png")
    pix.save(out)
    print(f"saved {out} ({pix.width}x{pix.height})")
doc.close()
