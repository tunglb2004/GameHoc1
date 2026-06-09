#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract highlighted text regions from PDF and update questions.json answers.
It will:
 - backup questions.json -> questions.json.bak
 - parse PDF highlights (rects) and extract words inside rects
 - for each highlighted snippet, try to match to an option text in questions.json
 - update answer index where match is found
 - print report of matches, unmatched highlights, and missing question numbers
"""
import pdfplumber, json, re
from pathlib import Path

PDF = Path(r"c:\Users\ADMIN\Downloads\LAP TRINH C++ (co DA).pdf")
QFILE = Path(r"d:\game\questions.json")
BACKUP = QFILE.with_suffix('.json.bak')
OUTPUT = QFILE

if not PDF.exists():
    print('PDF not found:', PDF)
    raise SystemExit(1)
if not QFILE.exists():
    print('questions.json not found:', QFILE)
    raise SystemExit(1)

# backup
if not BACKUP.exists():
    BACKUP.write_bytes(QFILE.read_bytes())
    print('Backup saved to', BACKUP)
else:
    print('Backup already exists at', BACKUP)

with open(QFILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# helper to get question number from question text like '123. ...'
def qnum_from_text(s):
    m = re.match(r"\s*(\d+)\s*\.", s)
    return int(m.group(1)) if m else None

# collect all option texts mapping to (q_index, opt_index)
opt_map = {}
for qi, q in enumerate(questions):
    for oi, opt in enumerate(q.get('options', [])):
        text = opt.get('text','').strip()
        key = re.sub(r"\s+"," ", text).strip()
        opt_map.setdefault(key, []).append((qi, oi))

# function to normalize strings for fuzzy matching
import unicodedata

def norm(s):
    s = s or ''
    s = s.strip()
    s = re.sub(r"\s+"," ", s)
    s = unicodedata.normalize('NFKC', s)
    return s.lower()

norm_opt_map = {}
for k, vs in opt_map.items():
    norm_opt_map[norm(k)] = vs

# extract highlighted snippets from PDF
highlights = []
with pdfplumber.open(str(PDF)) as pdf:
    for pnum, page in enumerate(pdf.pages, start=1):
        words = page.extract_words()
        rects = getattr(page, 'rects', []) or []
        # also consider annots if present
        annots = []
        try:
            annots = page.annotations or []
        except Exception:
            annots = []
        all_rects = rects[:]
        # some PDFs use annots with 'rect' values
        for a in annots:
            r = a.get('rect')
            if r:
                # rect might be [x0,y0,x1,y1]
                try:
                    x0,y0,x1,y1 = r
                    all_rects.append({'x0': x0, 'x1': x1, 'top': y0, 'bottom': y1})
                except Exception:
                    pass
        if not all_rects:
            continue
        for ridx, rect in enumerate(all_rects):
            # normalize rect keys
            rx0 = rect.get('x0') or rect.get('x0', 0)
            rx1 = rect.get('x1') or rect.get('x1', 0)
            rtop = rect.get('top') if rect.get('top') is not None else rect.get('y0')
            rbot = rect.get('bottom') if rect.get('bottom') is not None else rect.get('y1')
            if rx0 is None or rx1 is None or rtop is None or rbot is None:
                continue
            # collect words whose center falls within rect
            collected = []
            for w in words:
                try:
                    wx0 = float(w.get('x0'))
                    wx1 = float(w.get('x1'))
                    wtop = float(w.get('top'))
                    wbot = float(w.get('bottom'))
                except Exception:
                    continue
                cx = (wx0 + wx1)/2
                cy = (wtop + wbot)/2
                if cx >= rx0-0.1 and cx <= rx1+0.1 and cy >= rtop-0.1 and cy <= rbot+0.1:
                    collected.append((wtop, w.get('text')))
            if collected:
                # sort by vertical position then join
                collected.sort(key=lambda x: x[0])
                txt = ' '.join([t for _,t in collected]).strip()
                if txt:
                    highlights.append({'page': pnum, 'rect': ridx, 'text': txt})

print(f'Found {len(highlights)} highlighted snippets in PDF')

# dedupe highlighted texts
seen = set()
hl_texts = []
for h in highlights:
    t = re.sub(r"\s+"," ", h['text']).strip()
    if t and t not in seen:
        seen.add(t)
        hl_texts.append(t)

print(f'{len(h1:=hl_texts)} unique highlighted texts')

# Try to match highlights to options
matches = []
unmatched = []
for t in hl_texts:
    tnorm = norm(t)
    found = False
    # exact normalized match
    if tnorm in norm_opt_map:
        for (qi,oi) in norm_opt_map[tnorm]:
            questions[qi]['answer'] = oi
            matches.append((t, qi+1, oi))
            found = True
    else:
        # try substring match: highlighted text might be part of option or vice versa
        for qi, q in enumerate(questions):
            for oi, opt in enumerate(q.get('options', [])):
                if norm(t) in norm(opt.get('text','')) or norm(opt.get('text','')) in norm(t):
                    questions[qi]['answer'] = oi
                    matches.append((t, qi+1, oi))
                    found = True
                    break
            if found:
                break
    if not found:
        unmatched.append(t)

print(f'Matched highlights to options: {len(matches)}')
print(f'Unmatched highlights: {len(unmatched)}')
if unmatched:
    for u in unmatched[:50]:
        print(' -', u)

# Now check missing question numbers up to 200
qnums = set()
for q in questions:
    n = qnum_from_text(q.get('question',''))
    if n:
        qnums.add(n)

missing = [i for i in range(1,201) if i not in qnums]
print(f'Missing questions (1..200): {len(missing)}')
if missing:
    print(missing[:50])

# Save updated questions.json
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print('Updated', OUTPUT)

# summary of changes: show sample matches
for m in matches[:50]:
    print('Matched highlight -> question', m[1], 'option', chr(65+m[2]), '| snippet:', m[0][:80])

print('Done')
