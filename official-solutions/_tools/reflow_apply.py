# -*- coding: utf-8 -*-
"""Safe line-reflow: replace an inclusive 1-indexed line range [start,end] with a
single reflowed line, but ONLY if the whitespace-stripped content is byte-identical
to the original (so no character content can change; we only alter whitespace/newlines).

Usage: build a list EDITS = [(start, end, new_text), ...] for ONE file, call apply(path, EDITS).
Edits must be non-overlapping. They are applied bottom-up so earlier line numbers stay valid.
"""
import re, sys, io

def _strip(s):
    return re.sub(r'\s+', '', s)

def apply(path, edits):
    with io.open(path, encoding='utf-8-sig') as f:
        text = f.read()
    had_bom = False
    lines = text.split('\n')
    # validate + sort desc by start
    edits = sorted(edits, key=lambda e: e[0], reverse=True)
    errors = []
    for start, end, new_text in edits:
        orig = '\n'.join(lines[start-1:end])
        if _strip(orig) != _strip(new_text):
            errors.append((start, end, _strip(orig), _strip(new_text)))
    if errors:
        for start, end, o, n in errors:
            print(f"!! MISMATCH L{start}-L{end}")
            # show first differing position
            m = min(len(o), len(n))
            k = 0
            while k < m and o[k] == n[k]:
                k += 1
            print(f"   orig[{k}:]: ...{o[max(0,k-15):k+25]}")
            print(f"   new [{k}:]: ...{n[max(0,k-15):k+25]}")
        print(f"\nABORTED: {len(errors)} mismatch(es), no changes written.")
        return False
    for start, end, new_text in edits:
        lines[start-1:end] = [new_text]
    out = '\n'.join(lines)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    print(f"OK: applied {len(edits)} reflow edit(s) to {path}")
    return True
