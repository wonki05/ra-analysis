# -*- coding: utf-8 -*-
"""Scan each year's markdown for structural audit signals."""
import os, re, csv, glob, sys

ROOT = r"E:\LEET\ra-project-vlm"
PS = os.path.join(ROOT, "problem-set")
SRC = os.path.join(ROOT, "converted-files_GPTdraft")
DOCS = os.path.join(ROOT, "docs_problems")
YEARS = list(range(2012, 2027))

def find_pdf(year):
    pats = [f"{year}_LEET_추리논증_문제지(홀수형).pdf",
            f"{year}*추리논증*문제지*홀수형*.pdf",
            f"{year}*.pdf"]
    for p in pats:
        hits = glob.glob(os.path.join(DOCS, p))
        if hits:
            return hits[0]
    return None

def find_report(year):
    for f in glob.glob(os.path.join(SRC, "review-reports", "*_RA_review_report.md")):
        base = os.path.basename(f)
        m = re.match(r"(\d{4})-(\d{4})_", base)
        if m and int(m.group(1)) <= year <= int(m.group(2)):
            return f
    return None

inv_rows = []
print("=== PER-YEAR AUDIT SCAN ===")
for y in YEARS:
    ydir = os.path.join(PS, f"{y}_files")
    md_path = os.path.join(ydir, f"{y}_RA_problems.md")
    zip_path = os.path.join(SRC, f"{y}_RA_improved_outputs.zip")
    pdf_path = find_pdf(y)
    rep_path = find_report(y)
    if not os.path.exists(md_path):
        print(f"{y}: MD MISSING")
        continue
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    # question headings
    heads = re.findall(r"^# *0*(\d+) - RA", text, re.M)
    nums = [int(n) for n in heads]
    expected = 35 if y <= 2018 else 40
    dup = [n for n in set(nums) if nums.count(n) > 1]
    missing = [n for n in range(1, expected+1) if n not in nums]
    # image refs in md
    refs = re.findall(r"!\[[^\]]*\]\(\.?/?([^)]+)\)", text)
    refs += re.findall(r'<img[^>]+src=["\']\.?/?([^"\']+)["\']', text)
    refs = [os.path.basename(r) for r in refs]
    # images present on disk
    present = [f for f in os.listdir(ydir) if f.lower().endswith((".png",".jpg",".jpeg",".gif"))]
    missing_refs = [r for r in refs if r not in present]
    unref = [p for p in present if p not in refs]
    # signals
    img_meta = len(re.findall(r"<이미지\s*포함됨>", text))
    u_tags = len(re.findall(r"<u>", text))
    hangul_bullets = len(re.findall(r"^\s*ㅇ[ \t ]", text, re.M))
    print(f"{y}: Q={len(nums)}/{expected} dup={dup} missing={missing} "
          f"imgrefs={len(refs)} present={len(present)} brokenrefs={missing_refs} unref={unref} "
          f"<이미지포함됨>={img_meta} <u>={u_tags} ㅇbullets={hangul_bullets}")
    inv_rows.append({
        "year": y,
        "zip_present": os.path.exists(zip_path),
        "pdf_present": pdf_path is not None,
        "pdf_file": os.path.basename(pdf_path) if pdf_path else "",
        "report_file": os.path.basename(rep_path) if rep_path else "",
        "md_count": 1,
        "image_count": len(present),
        "question_count": len(nums),
        "expected_questions": expected,
        "duplicate_nums": ";".join(map(str,dup)),
        "missing_nums": ";".join(map(str,missing)),
        "broken_img_refs": ";".join(missing_refs),
        "unreferenced_imgs": ";".join(unref),
        "img_meta_phrase": img_meta,
        "u_tags": u_tags,
        "hangul_o_bullets": hangul_bullets,
    })

# write inventory
inv_csv = os.path.join(PS, "_audit", "file_inventory.csv")
with open(inv_csv, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(inv_rows[0].keys()))
    w.writeheader()
    for r in inv_rows:
        w.writerow(r)
print("\nWrote", inv_csv)
