# -*- coding: utf-8 -*-
"""전체 입력 인벤토리 작성: ZIP/PDF/검수보고서 존재 여부, ZIP 내용물 목록."""
import json, os, zipfile, sys
import fitz

ROOT = r"E:\LEET\ra-project-vlm"
ZIP_DIR = os.path.join(ROOT, "converted-solutions_GPTdraft")
REVIEW_DIR = os.path.join(ZIP_DIR, "review-reports")
PDF_DIR = os.path.join(ROOT, "docs_solutions")
OUT_DIR = os.path.join(ROOT, "official-solutions")
REPORT_DIR = os.path.join(OUT_DIR, "review-fix-reports")

YEARS = list(range(2012, 2027))
ZIP_PATTERNS = [
    "{y}_RA_official+solutions_package.zip",
    "{y}_RA_official_solutions_package.zip",
    "{y}_RA_official+solutions.zip",
    "{y}_RA_official_solutions.zip",
]
REVIEW_MAP = {
    "2012-2014": range(2012, 2015),
    "2015-2017": range(2015, 2018),
    "2018-2020": range(2018, 2021),
    "2021-2023": range(2021, 2024),
    "2024-2026": range(2024, 2027),
}

inv = {"years": {}}
for y in YEARS:
    e = {"year": y}
    zp = None
    for pat in ZIP_PATTERNS:
        cand = os.path.join(ZIP_DIR, pat.format(y=y))
        if os.path.exists(cand):
            zp = cand
            break
    e["zip"] = os.path.basename(zp) if zp else None
    if zp:
        with zipfile.ZipFile(zp) as z:
            names = z.namelist()
        e["zip_md"] = sorted(n for n in names if n.lower().endswith(".md"))
        e["zip_png"] = sorted(n for n in names if n.lower().endswith(".png"))
        e["zip_other"] = sorted(n for n in names if not n.lower().endswith((".md", ".png")) and not n.endswith("/"))
    pdf = os.path.join(PDF_DIR, f"법전협_{y} LEET 해설_추리논증.pdf")
    if os.path.exists(pdf):
        doc = fitz.open(pdf)
        e["pdf"] = os.path.basename(pdf)
        e["pdf_pages"] = doc.page_count
        # 텍스트 레이어 존재 여부 대략 확인 (앞 3페이지 텍스트 길이)
        tl = sum(len(doc[i].get_text()) for i in range(min(3, doc.page_count)))
        e["pdf_textlayer_chars_first3"] = tl
        doc.close()
    else:
        e["pdf"] = None
    rv = None
    for k, rng in REVIEW_MAP.items():
        if y in rng:
            cand = os.path.join(REVIEW_DIR, f"{k}_RA_solutions_review_report.md")
            rv = os.path.basename(cand) if os.path.exists(cand) else None
    e["review_report"] = rv
    e["existing_output"] = os.path.isdir(os.path.join(OUT_DIR, f"{y}_solution_files"))
    inv["years"][str(y)] = e

os.makedirs(REPORT_DIR, exist_ok=True)
with open(os.path.join(REPORT_DIR, "validation_inventory.json"), "w", encoding="utf-8") as f:
    json.dump(inv, f, ensure_ascii=False, indent=2)

lines = ["# 입력 인벤토리 (2012-2026 LEET RA 공식해설)", ""]
lines.append("| 연도 | ZIP | MD | PNG | PDF 페이지 | 텍스트레이어(앞3p 글자수) | 검수보고서 | 기존출력 |")
lines.append("|---:|---|---:|---:|---:|---:|---|---|")
for y in YEARS:
    e = inv["years"][str(y)]
    lines.append("| {y} | {z} | {md} | {png} | {pp} | {tl} | {rv} | {ex} |".format(
        y=y, z=e["zip"] or "누락", md=len(e.get("zip_md", [])), png=len(e.get("zip_png", [])),
        pp=e.get("pdf_pages", "누락"), tl=e.get("pdf_textlayer_chars_first3", "-"),
        rv=e["review_report"] or "누락", ex="있음" if e["existing_output"] else "없음"))
lines.append("")
lines.append("## ZIP 내용물 상세")
for y in YEARS:
    e = inv["years"][str(y)]
    lines.append(f"\n### {y}")
    if not e["zip"]:
        lines.append("- ZIP 누락")
        continue
    for n in e.get("zip_md", []):
        lines.append(f"- MD: `{n}`")
    lines.append(f"- PNG {len(e.get('zip_png', []))}개")
    for n in e.get("zip_other", []):
        lines.append(f"- 기타: `{n}`")
with open(os.path.join(REPORT_DIR, "input_inventory.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("OK")
for y in YEARS:
    e = inv["years"][str(y)]
    print(y, e["zip"] or "ZIP누락", f"md={len(e.get('zip_md',[]))}", f"png={len(e.get('zip_png',[]))}",
          f"pdf_pages={e.get('pdf_pages')}", f"tl3p={e.get('pdf_textlayer_chars_first3')}", e["review_report"] or "검수누락")
