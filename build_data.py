"""Rebuilds data.json (parts, contents, question list) from guide.pdf.
Run:  pip install pdfplumber && python build_data.py
Relies on the guide's formatting: bold 'Q123 ...' question lines and bold numbered topic headings."""
import json, re, sys
import pdfplumber

PDF = sys.argv[1] if len(sys.argv) > 1 else "guide.pdf"
HEAD = re.compile(r"^(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)\s+(\S.*)$")
PART = re.compile(r"MAY Part ([A-Z])\s*[–-]\s*(.+?)\s*[–-]\s*[A-Za-z]+ \d{4}")

parts, outline, questions, page_lines = [], [], [], {}
with pdfplumber.open(PDF) as _p:  # topic numbers listed in the guide's table of contents
    TOCREFS = {m.group(1) for pg in _p.pages[:8] for ln in (pg.extract_text() or "").split("\n")
               for m in [HEAD.match(ln.strip())] if m}
cur_q, sec = None, ("", "")
with pdfplumber.open(PDF) as pdf:
    total = len(pdf.pages)
    for pn, pg in enumerate(pdf.pages, 1):
        lines = pg.extract_text_lines(return_chars=True)
        for l in lines:
            m = PART.search(l["text"]) if l["top"] < 70 else None
            if m and (not parts or parts[-1]["key"] != m.group(1)):
                parts.append({"key": m.group(1), "name": m.group(2).strip(), "start": pn})
        page_lines[pn] = [l["text"].strip() for l in lines if l["top"] >= 70]
        if not parts:
            continue
        for l in lines:
            if l["top"] < 70:
                continue
            c = l["chars"][0]; t = l["text"].strip()
            bold = "Demibold" in c["fontname"]; size = c["size"]
            if bold and size >= 13.5:
                m = HEAD.match(t)
                if m and m.group(1) in TOCREFS and not any(o["r"] == m.group(1) for o in outline):
                    sec = (m.group(1), m.group(2)); cur_q = None
                    if not outline or outline[-1]["r"] != sec[0]:
                        outline.append({"r": sec[0], "t": sec[1], "p": pn,
                                        "l": 1 if sec[0].count(".") == 1 else 2})
                    continue
            if bold and re.match(r"^Q\d+\b", t):
                m = re.match(r"^Q(\d+)\s*(.*)$", t)
                cur_q = {"n": int(m.group(1)), "q": m.group(2), "p": pn, "s": sec[0], "st": sec[1]}
                questions.append(cur_q); continue
            if cur_q and bold and l["x0"] > 90 and size < 14.4 and not re.match(r"^\d", t):
                cur_q["q"] += " " + t; continue
            cur_q = None

# Use the guide's own table of contents for clean titles; headings give the page numbers.
found = {}
for o in outline:
    found.setdefault(o["r"], o["p"])
toc, seen = [], set()
with pdfplumber.open(PDF) as pdf:
    for pg in pdf.pages[: parts[0]["start"] - 1]:
        for line in (pg.extract_text() or "").split("\n"):
            m = HEAD.match(line.strip())
            if m and m.group(1) not in seen:
                seen.add(m.group(1)); toc.append((m.group(1), m.group(2).strip()))
if toc:
    outline, last = [], parts[0]["start"]
    for r, t in toc:
        if r not in found:  # heading not in bold style: look for "ref title" text from the previous topic onward
            key = r + " " + t[:10]
            for pn in range(last, total + 1):
                if any(x.startswith(key) for x in page_lines.get(pn, [])):
                    found[r] = pn; break
        last = max(last, found.get(r, last))
        outline.append({"r": r, "t": t, "p": last,
                        "l": 0 if r.endswith(".0") else (1 if r.count(".") == 1 else 2)})

for i, p in enumerate(parts):
    p["end"] = parts[i + 1]["start"] - 1 if i + 1 < len(parts) else total
json.dump({"pages": total, "parts": parts, "outline": outline, "questions": questions},
          open("data.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"{total} pages, {len(parts)} parts, {len(outline)} topics, {len(questions)} questions")
