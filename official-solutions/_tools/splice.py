# -*- coding: utf-8 -*-
"""MD 파일의 START 앵커(포함)부터 END 앵커(제외)까지를 새 내용으로 치환.
사용법: python splice.py MD_PATH NEW_CONTENT_FILE START_ANCHOR END_ANCHOR
END_ANCHOR가 "EOF"면 파일 끝까지 치환.
새 내용 파일은 UTF-8. 치환 후 앵커 개수 검증.
"""
import sys, io

md_path, new_path, start, end = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with io.open(md_path, encoding="utf-8") as f:
    text = f.read()
with io.open(new_path, encoding="utf-8") as f:
    new = f.read()

i = text.find(start)
if i < 0:
    sys.exit(f"START anchor not found: {start!r}")
if text.find(start, i + 1) >= 0:
    sys.exit(f"START anchor not unique: {start!r}")
if end == "EOF":
    j = len(text)
else:
    j = text.find(end, i)
    if j < 0:
        sys.exit(f"END anchor not found after start: {end!r}")

out = text[:i] + new + text[j:]
with io.open(md_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
print(f"spliced {j-i} -> {len(new)} chars")
