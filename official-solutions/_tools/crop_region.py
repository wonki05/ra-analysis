# -*- coding: utf-8 -*-
"""PDF 페이지의 특정 영역을 고해상도로 crop하여 PNG 저장.
사용법: python crop_region.py YEAR PAGE x0 y0 x1 y1 DPI OUT_PATH
좌표는 PDF 포인트 단위(72dpi 기준). PAGE는 1-기준.
"""
import os, sys
import fitz

ROOT = r"E:\LEET\ra-project-vlm"
year, page = sys.argv[1], int(sys.argv[2])
x0, y0, x1, y1 = map(float, sys.argv[3:7])
dpi = int(sys.argv[7])
out = sys.argv[8]
pdf = os.path.join(ROOT, "docs_solutions", f"법전협_{year} LEET 해설_추리논증.pdf")
doc = fitz.open(pdf)
pg = doc[page - 1]
clip = fitz.Rect(x0, y0, x1, y1)
pix = pg.get_pixmap(dpi=dpi, clip=clip)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
pix.save(out)
print(f"saved {out} ({pix.width}x{pix.height})")
