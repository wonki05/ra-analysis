# -*- coding: utf-8 -*-
"""전 연도 ZIP을 official-solutions/YYYY_solution_files 로 해제하고 평탄화."""
import os, shutil, zipfile, sys

ROOT = r"E:\LEET\ra-project-vlm"
ZIP_DIR = os.path.join(ROOT, "converted-solutions_GPTdraft")
OUT_DIR = os.path.join(ROOT, "official-solutions")
ZIP_PATTERNS = [
    "{y}_RA_official+solutions_package.zip",
    "{y}_RA_official_solutions_package.zip",
    "{y}_RA_official+solutions.zip",
    "{y}_RA_official_solutions.zip",
]

for y in range(2012, 2027):
    zp = None
    for pat in ZIP_PATTERNS:
        cand = os.path.join(ZIP_DIR, pat.format(y=y))
        if os.path.exists(cand):
            zp = cand
            break
    if not zp:
        print(y, "ZIP 누락 - 건너뜀")
        continue
    dest = os.path.join(OUT_DIR, f"{y}_solution_files")
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            # 평탄화: 중첩 폴더 무시하고 파일명만 사용
            base = os.path.basename(info.filename)
            if not base:
                continue
            target = os.path.join(dest, base)
            with z.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    # 표준 MD 파일명 확인/개명
    std = f"{y}_RA_official+solutions.md"
    mds = [f for f in os.listdir(dest) if f.lower().endswith(".md")]
    if std not in mds:
        # work_report 제외한 후보 중 solutions 포함 파일을 개명
        cands = [f for f in mds if "work_report" not in f and "report" not in f]
        if len(cands) == 1:
            os.rename(os.path.join(dest, cands[0]), os.path.join(dest, std))
            print(y, "개명:", cands[0], "->", std)
    files = sorted(os.listdir(dest))
    n_png = sum(1 for f in files if f.endswith(".png"))
    print(y, "OK md:", [f for f in files if f.endswith('.md')], "png:", n_png)
