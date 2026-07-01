# -*- coding: utf-8 -*-
"""Detect underline strokes in a text-layer PDF and report the EXACT underlined text.
Usage: python extract_underlines.py YEAR [page1 page2 ...]

Underline = short/medium horizontal stroke with characters whose baseline sits
just above it (gap 0.5..8 pt) and whose x-center lies within the stroke span.
Box borders (full-column), headers, footers are filtered out.
"""
import os, sys, glob, io
import fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"E:\LEET\ra-project-vlm"
DOCS = os.path.join(ROOT, "docs_problems")

year = sys.argv[1]
pdf = glob.glob(os.path.join(DOCS, f"{year}_*.pdf"))[0]
doc = fitz.open(pdf)
sel = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else list(range(1, doc.page_count+1))

def hsegs(page):
    out = []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l":
                a, b = it[1], it[2]
                if abs(a.y-b.y) < 1.3 and abs(b.x-a.x) > 6:
                    out.append((min(a.x,b.x), max(a.x,b.x), (a.y+b.y)/2))
    return out

def chars(page):
    out = []
    d = page.get_text("rawdict")
    for blk in d.get("blocks", []):
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                for ch in sp.get("chars", []):
                    x0,y0,x1,y1 = ch["bbox"]
                    out.append((x0,y0,x1,y1, ch["c"]))
    return out

for pno in sel:
    page = doc[pno-1]
    segs = hsegs(page)
    chs = chars(page)
    cands = []
    for (x0, x1, y) in segs:
        L = x1-x0
        if L > 300: continue   # >300 => full-column box border; <=~292 => full-line underline
        if y < 160 or y > 1080: continue
        # exclude segments coinciding with column box edges (borders), keeping inset underlines
        if (x0 < 99.5 or abs(x0-444.8) < 1.2) and (abs(x1-406.1) < 1.2 or x1 > 752):
            continue
        picked = [c for c in chs if (y-9) < c[3] <= (y-0.2) and (c[0]+c[2])/2 >= x0-1 and (c[0]+c[2])/2 <= x1+1]
        if not picked: continue
        picked.sort(key=lambda c:c[0])
        txt = "".join(c[4] for c in picked).strip()
        if not txt: continue
        cands.append((round(y,1), round(x0,1), round(x1,1), round(L,1), txt))
    # dedupe identical (x0,x1,y)
    seen=set(); ded=[]
    for c in cands:
        k=(round(c[1]),round(c[2]),round(c[0]))
        if k in seen: continue
        seen.add(k); ded.append(c)
    # drop table grids: x-range shared by >=3 rows
    from collections import Counter
    xr=Counter((round(c[1]),round(c[2])) for c in ded)
    COVER={"제2교시","제2 교시","성명","수험번호","홀수형"}
    final=[c for c in ded if xr[(round(c[1]),round(c[2]))]<3 and c[4] not in COVER]
    if final:
        print(f"\n===== {year} page {pno} : {len(final)} underline(s) =====")
        for (y,x0,x1,L,txt) in sorted(final):
            print(f" y={y:>6} x=[{x0:>6},{x1:>6}] :: {txt}")
doc.close()
