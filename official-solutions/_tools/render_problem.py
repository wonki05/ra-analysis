# -*- coding: utf-8 -*-
"""문제지 PDF 페이지를 PNG로 렌더링.
사용법: python render_problem.py YEAR DPI [pages]
출력: official-solutions/_page_renders_problems/YEAR/pNNN.png
"""
import os, sys
import fitz

ROOT = r"E:\LEET\ra-project-vlm"

def parse_pages(spec, n):
    if spec == "all":
        return list(range(1, n + 1))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [p for p in out if 1 <= p <= n]

year = sys.argv[1]
dpi = int(sys.argv[2])
spec = sys.argv[3] if len(sys.argv) > 3 else "all"
pdf = os.path.join(ROOT, "docs_problems", f"{year}_LEET_추리논증_문제지(홀수형).pdf")
outdir = os.path.join(ROOT, "official-solutions", "_page_renders_problems", year)
os.makedirs(outdir, exist_ok=True)
doc = fitz.open(pdf)
pages = parse_pages(spec, doc.page_count)
for p in pages:
    out = os.path.join(outdir, f"p{p:03d}.png")
    if os.path.exists(out) and spec == "all":
        continue
    pix = doc[p - 1].get_pixmap(dpi=dpi)
    pix.save(out)
print(f"{year} problem: {len(pages)} pages rendered at {dpi}dpi -> {outdir}")
