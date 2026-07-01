# -*- coding: utf-8 -*-
"""Dump context around every <이미지 포함됨> meta phrase across all years."""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PS = r"E:\LEET\ra-project-vlm\problem-set"
META = "<이미지 포함됨>"
for y in range(2012, 2027):
    md = os.path.join(PS, f"{y}_files", f"{y}_RA_problems.md")
    with open(md, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    hits = [i for i,l in enumerate(lines) if "이미지 포함됨" in l or "이미지포함됨" in l]
    if not hits:
        continue
    print(f"\n########## {y}  ({len(hits)} occurrences) ##########")
    for i in hits:
        # find nearest preceding question heading
        qh = ""
        for j in range(i, -1, -1):
            m = re.match(r"^# *0*(\d+) - RA", lines[j])
            if m:
                qh = f"Q{int(m.group(1))} (line {j+1})"
                break
        print(f"\n--- {qh} :: meta at line {i+1} ---")
        lo = max(0, i-3); hi = min(len(lines), i+4)
        for k in range(lo, hi):
            mark = ">>" if k == i else "  "
            print(f"{mark}{k+1:5}: {lines[k]}")
