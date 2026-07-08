# -*- coding: utf-8 -*-
"""Reconstruct wrapped paragraphs from the ORIGINAL file characters.
Each edit = (start, end, code) where code is a string of length (end-start).
code[k] is the join between segment k and k+1 (1-indexed lines start+k-1 | start+k):
  'S' -> single space, 'N' -> no space (mid-word), 'P' -> paragraph break (\\n\\n).
Because segments come from the file itself, NO content can change; only whitespace.
A whitespace-stripped identity check is asserted per edit as a safety net.
"""
import re, io

def _strip(s): return re.sub(r'\s+', '', s)

def apply(path, edits):
    with io.open(path, encoding='utf-8-sig') as f:
        lines = f.read().split('\n')
    edits = sorted(edits, key=lambda e: e[0], reverse=True)
    # validate
    for start, end, code in edits:
        segs = [lines[i].strip() for i in range(start-1, end)]
        if len(code) != len(segs) - 1:
            print(f"!! L{start}-{end}: code len {len(code)} != boundaries {len(segs)-1}")
            return False
        for c in code:
            if c not in 'SNP':
                print(f"!! L{start}-{end}: bad code char {c!r}")
                return False
    for start, end, code in edits:
        segs = [lines[i].strip() for i in range(start-1, end)]
        res = segs[0]
        for k in range(1, len(segs)):
            sep = {'S': ' ', 'N': '', 'P': '\n\n'}[code[k-1]]
            res += sep + segs[k]
        orig = '\n'.join(lines[start-1:end])
        assert _strip(orig) == _strip(res), f"content drift L{start}-{end}"
        lines[start-1:end] = [res]
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines))
    print(f"OK: applied {len(edits)} block(s) to {path}")
    return True
