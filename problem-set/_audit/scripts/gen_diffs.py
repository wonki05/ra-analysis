# -*- coding: utf-8 -*-
"""Generate unified diffs between the pristine raw_extracted markdown and the
edited problem-set markdown for each year. Saves _audit/diffs/[year].patch."""
import os, io, sys, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PS = r"E:\LEET\ra-project-vlm\problem-set"
RAW = os.path.join(PS, "_audit", "raw_extracted")
DIFF = os.path.join(PS, "_audit", "diffs")
os.makedirs(DIFF, exist_ok=True)

summary = []
for y in range(2012, 2027):
    fn = f"{y}_RA_problems.md"
    a = os.path.join(RAW, str(y), fn)
    b = os.path.join(PS, f"{y}_files", fn)
    al = open(a, encoding="utf-8").read().splitlines(keepends=True)
    bl = open(b, encoding="utf-8").read().splitlines(keepends=True)
    diff = list(difflib.unified_diff(al, bl, fromfile=f"raw/{y}/{fn}", tofile=f"{y}_files/{fn}", n=1))
    patch = os.path.join(DIFF, f"{y}.patch")
    with open(patch, "w", encoding="utf-8") as fh:
        fh.writelines(diff)
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    summary.append((y, added, removed, len(diff)))
    print(f"{y}: +{added} -{removed} lines, patch size {len(diff)}")
print("\nDiffs written to", DIFF)
