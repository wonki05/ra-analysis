# -*- coding: utf-8 -*-
"""Apply <u>...</u> underlines to a year's markdown, matching whitespace-insensitively
within each question block. Dry-run by default; pass --write to save.

Config below lists, per (year, qnum), the underline targets:
  - ('content', compact_text)  -> wrap the span matching compact_text (spaces ignored)
    within the question block. compact_text may include an anchor prefix separated by
    '|' : 'anchor|underline' wraps only the underline part located right after anchor.
  - ('stem', 'X')              -> wrap literal X only within the question prompt line.
"""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
PS = r"E:\LEET\ra-project-vlm\problem-set"

CONFIG = {
 2018: {
   6:  [('stem','않은')],
   9:  [('stem','않은')],
   30: [('stem','않은')],
   10: [('content','곤란한상황')],
   11: [('content','동물에게도도덕적지위를인정해야한다'),
        ('content','로봇에게도덕적지위를부여하지못할이유는없을것같다')],
   15: [('content','“어제K공항에서비행기가이륙했다면,1번활주로로이륙하지않았다.”'),
        ('content','“어제K공항에서비행기가이륙했다면,1번활주로로이륙했다.”'),
        ('content','(가)|방식')],
   17: [('content','이대화의녹취록에서찾아낸근거')],
   20: [('content','시간해석이론')],
   23: [('content','㉠|플라시보효과'),('content','㉡|피험자보고편향'),
        ('content','기대성효과'),('content','실험자보고편향')],
   24: [('content','희생자가생존해있을때에화재가발생하여화재의기전에의해사망하였다고판단')],
   32: [('content','대뇌피질의전담영역은각영역이가진고유한물리적특징에의해결정되는것이아니라다른영역들과의연결양상에의해결정된다'),
        ('content','대뇌피질로들어오는입력의유형은근본적으로똑같다'),
        ('content','뇌에의해파악된외부세계와몸사이의경계는바뀔수있다')],
   34: [('content','발현량이증가된p53단백질의물질대사억제기능이암발생을억제한다는가설')],
 },
 2019: {
   3:  [('content','장사신을 교형으로 처벌해야 합니다.'),
        ('content','사안에 들어맞는 유사한 사례를 다룬 판결이')],
   7:  [('content','"저는 주변에서 매우 조심성 있는 사람이라는 평을 듣습니다."'),
        ('content','"예전에 마당쇠가 을순이에게 거짓말을 해서 을순이 아버지에게 크게 혼난 일이 있었지요."'),
        ('content','"예전에 을돌이가 아랫동네 살인 사건 재판에서 거짓말을 하여 곤장 다섯 대를 맞은 적이 있습니다."'),
        ('content','"을돌이가 매우 진실하다는 소문이 윗마을까지 나 있습니다."')],
   10: [("content","'의심스러울 때에는 가볍게 처벌한다'는 원칙")],
   14: [('content','보험사의 고의, 중대한 과실, 경미한 과실 여하에 대한 아무런 언급이 없이 보험사의 모든 책임을 면제하는 내용의 약관조항'),
        ('content','"무면허운전은 누가 운전을 하더라도 보험사는 아무런 책임이 없습니다."'),
        ('content','보험계약자의 지배와 관리가 불가능하였으므로')],
   22: [('content','미적 취향의 보편적 기준을 부정하고 모든 이의 미적 취향을 동등하게 인정하는 태도')],
   39: [("content","'초파리의 장세포가 분비하는 활성산소는 병독균의 성장을 저해한다'는 가설")],
 },
}

def compact(s): return re.sub(r"\s","",s)

def wrap_ws_insensitive(block, target_compact, anchor_compact=None):
    """Find span in `block` whose non-space chars == target_compact (optionally right
    after anchor_compact) and wrap it with <u></u>. Returns (newblock, status)."""
    # build mapping of index-in-compact -> index-in-block
    idxmap=[]; comp=[]
    for i,ch in enumerate(block):
        if not ch.isspace():
            idxmap.append(i); comp.append(ch)
    comp="".join(comp)
    search = (anchor_compact or "")+target_compact
    positions=[m.start() for m in re.finditer(re.escape(search), comp)]
    if len(positions)!=1:
        return block, f"AMBIGUOUS/NOTFOUND ({len(positions)} matches)"
    start_comp=positions[0]+len(anchor_compact or "")
    end_comp=start_comp+len(target_compact)
    s=idxmap[start_comp]; e=idxmap[end_comp-1]+1
    # don't include trailing spaces
    seg=block[s:e]
    if "<u>" in seg or "</u>" in seg or block[max(0,s-3):s] == "<u>":
        return block, "ALREADY WRAPPED"
    newblock=block[:s]+"<u>"+seg+"</u>"+block[e:]
    return newblock, f"OK :: {seg}"

def split_blocks(text):
    # returns list of (qnum or None, start, end) by heading
    parts=[]
    matches=list(re.finditer(r"^# (\d+) - RA.*$", text, re.M))
    for i,m in enumerate(matches):
        q=int(m.group(1))
        s=m.start()
        e=matches[i+1].start() if i+1<len(matches) else len(text)
        parts.append((q,s,e))
    return parts

def prompt_line_span(block):
    # first non-empty line after the heading line
    lines=block.split("\n")
    for i in range(1,len(lines)):
        if lines[i].strip():
            return i
    return None

def main(year, write):
    md=os.path.join(PS, f"{year}_files", f"{year}_RA_problems.md")
    text=open(md,encoding="utf-8").read()
    blocks=split_blocks(text)
    cfg=CONFIG[year]
    # process from last block to first so offsets stay valid
    newtext=text
    report=[]
    for (q,s,e) in reversed(blocks):   # reverse so earlier offsets stay valid after edits
        if q not in cfg: continue
        block=newtext[s:e]
        for kind,tgt in cfg[q]:
            if kind=='stem':
                lines=block.split("\n")
                li=prompt_line_span(block)
                line=lines[li]
                if tgt in line and "<u>"+tgt not in line:
                    # wrap first occurrence in prompt line
                    lines[li]=line.replace(tgt, "<u>"+tgt+"</u>", 1)
                    block="\n".join(lines)
                    report.append((q,'stem',f"OK :: {tgt}"))
                else:
                    report.append((q,'stem',"NOTFOUND in prompt"))
            else:
                anchor=None; t=tgt
                if '|' in tgt:
                    anchor,t=tgt.split('|',1)
                    anchor=compact(anchor)
                block,st=wrap_ws_insensitive(block, compact(t), anchor)
                report.append((q,'content',st))
        newtext=newtext[:s]+block+newtext[e:]
    print(f"===== {year} underline application ({'WRITE' if write else 'DRY'}) =====")
    for q,k,st in report:
        print(f" Q{q:>2} [{k}] {st}")
    total=sum(1 for _,_,st in report if st.startswith('OK'))
    prob=[r for r in report if not (r[2].startswith('OK') or r[2]=='ALREADY WRAPPED')]
    print(f"\n applied OK: {total} ; problems: {len(prob)}")
    if write and not prob:
        open(md,"w",encoding="utf-8").write(newtext)
        print(" >> written")
    elif write and prob:
        print(" >> NOT written due to problems")

if __name__=="__main__":
    year=int(sys.argv[1]); write="--write" in sys.argv
    main(year, write)
