# -*- coding: utf-8 -*-
"""Detect underline strokes in a SCANNED page raster and save zoomed crops of the
text line just above each, for visual transcription.
Usage: python scan_underlines.py YEAR PAGE [PAGE ...]
Renders page at 300 DPI, finds thin long horizontal dark runs with whitespace below,
filters box/table borders, saves crops to rendered_pdf/YEAR/uXX/.
"""
import os, sys, glob
import fitz
import numpy as np
from PIL import Image

ROOT = r"E:\LEET\ra-project-vlm"
DOCS = os.path.join(ROOT, "docs_problems")
OUT = os.path.join(ROOT, "problem-set", "_audit", "rendered_pdf")

year = sys.argv[1]
pages = [int(x) for x in sys.argv[2:]]
pdf = glob.glob(os.path.join(DOCS, f"{year}_*.pdf"))[0]
doc = fitz.open(pdf)
DPI = 300
zoom = DPI/72.0

for pno in pages:
    page = doc[pno-1]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
    a = np.asarray(img)
    H, W = a.shape
    dark = a < 110  # black pixels
    # candidate underline rows: a run of black pixels, thin, with whitespace below
    segs = []
    y = 2
    while y < H-4:
        row = dark[y]
        # find horizontal runs in this row
        xs = np.where(row)[0]
        if xs.size >= 40:
            # group into runs
            splits = np.where(np.diff(xs) > 3)[0]
            groups = np.split(xs, splits+1)
            for g in groups:
                if g.size < 40:
                    continue
                x0, x1 = g[0], g[-1]
                length = x1-x0
                if length < 40 or length > 0.9*W:
                    continue
                # fill ratio: mostly continuous
                if g.size < 0.75*length:
                    continue
                # thin: rows y+2..y+4 mostly white beneath; y-1 (line thickness) small
                below = dark[y+2:y+6, x0:x1+1].mean()
                above_gap = dark[y-6:y-2, x0:x1+1].mean()  # small gap between text and line
                thick = dark[y:y+3, x0:x1+1].mean()
                if below < 0.06 and thick > 0.4:
                    segs.append([x0, x1, y, length])
            # skip ahead to avoid duplicate rows of same line
        y += 1
    # merge segments that are vertically adjacent & overlapping (same underline detected on 2-3 rows)
    segs.sort(key=lambda s:(s[2], s[0]))
    merged = []
    for s in segs:
        placed = False
        for m in merged:
            if abs(s[2]-m[2]) <= 4 and not (s[1] < m[0]-5 or s[0] > m[1]+5):
                m[0] = min(m[0], s[0]); m[1] = max(m[1], s[1]); m[3] = m[1]-m[0]
                placed = True; break
        if not placed:
            merged.append(s)
    outdir = os.path.join(OUT, str(year), f"u{pno:02d}")
    os.makedirs(outdir, exist_ok=True)
    print(f"\n== {year} p{pno}: {len(merged)} underline strokes ==")
    for i, (x0, x1, y, L) in enumerate(sorted(merged, key=lambda s:(s[2], s[0]))):
        # crop the text line above the underline
        cy0 = max(0, y-46); cy1 = min(H, y+8)
        cx0 = max(0, x0-15); cx1 = min(W, x1+15)
        crop = img.crop((cx0, cy0, cx1, cy1))
        crop.save(os.path.join(outdir, f"{i:02d}_y{y}.png"))
        print(f"  #{i:02d} y={y} x=[{x0},{x1}] L={L}")
doc.close()
