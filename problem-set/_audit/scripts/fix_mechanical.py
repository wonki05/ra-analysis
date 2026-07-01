# -*- coding: utf-8 -*-
"""Apply mechanical high-confidence fixes:
   1. Remove <이미지 포함됨> meta line + one following blank line (all years).
   2. 2025 Q28 ㄴ: 실험 2 결과 -> 실험 2의 결과.
   3. 2026 Q39: 생각해 보자.(단 -> 생각해 보자. (단.
   Logs every change and never touches raw_extracted.
"""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PS = r"E:\LEET\ra-project-vlm\problem-set"
META_RE = re.compile(r"<이미지\s*포함됨>")

def qnum_at(lines, idx):
    for j in range(idx, -1, -1):
        m = re.match(r"^# *0*(\d+) - RA", lines[j])
        if m:
            return int(m.group(1))
    return None

changes = []  # (year, q, kind, line_before_desc)

for y in range(2012, 2027):
    md = os.path.join(PS, f"{y}_files", f"{y}_RA_problems.md")
    with open(md, encoding="utf-8") as fh:
        text = fh.read()
    orig = text
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if META_RE.fullmatch(lines[i].strip()) and lines[i].strip().startswith("<이미지"):
            q = qnum_at(lines, i)
            changes.append((y, q, "remove <이미지 포함됨>", i+1))
            # skip this meta line; also drop exactly one following blank line if present
            if i+1 < len(lines) and lines[i+1].strip() == "":
                i += 2
            else:
                i += 1
            continue
        out.append(lines[i])
        i += 1
    text = "\n".join(out)

    # Year-specific text fixes
    if y == 2025:
        before = "ㄴ. 실험 2 결과, 두 집단의 기억률이 유사하다면 A는 약화된다."
        after  = "ㄴ. 실험 2의 결과, 두 집단의 기억률이 유사하다면 A는 약화된다."
        if before in text:
            text = text.replace(before, after, 1)
            changes.append((y, 28, "insert 조사 '의' (실험 2 결과 -> 실험 2의 결과)", None))
    if y == 2026:
        before = "생각해 보자.(단, 원통의 두께는 무시한다.)"
        after  = "생각해 보자. (단, 원통의 두께는 무시한다.)"
        if before in text:
            text = text.replace(before, after, 1)
            changes.append((y, 39, "insert space after '보자.' before '(단'", None))

    if text != orig:
        with open(md, "w", encoding="utf-8") as fh:
            fh.write(text)

# report
from collections import defaultdict
byyear = defaultdict(list)
for c in changes:
    byyear[c[0]].append(c)
for y in sorted(byyear):
    print(f"\n=== {y}: {len(byyear[y])} changes ===")
    for (_, q, kind, ln) in byyear[y]:
        loc = f"orig-line {ln}" if ln else ""
        print(f"  Q{q}: {kind} {loc}")
print(f"\nTOTAL changes: {len(changes)}")
