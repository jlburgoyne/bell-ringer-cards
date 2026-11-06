"""Turn a bell ringer set (JSON) into a print-ready Word file: cards, then the answer key.

Usage:  python3 build_cards.py cards.json output.docx [--log "Bell ringer log.csv"]

With --log, a successful build also saves the set's JSON next to the Word file
(same name, .json) and adds one line to the log: date, grade, set, standards,
Regents tags, multiple choice, file, and a blank Used column for the teacher.

The cards print 8 to a letter page in a 2 x 4 grid of 4" x 2.4" cards with dashed
cut lines, so a paper cutter separates them in a few straight cuts and each card
fits on a 3x5 index card. Cards show only the number, focus, and content; the
standards and Regents tags are in the answer key, which follows on its own pages.

The script checks the set before building and stops with a list of problems if
anything is off (wrong card count, unknown standard or Regents ID, a card too long
to fit, a multiple-choice answer that isn't one of the choices, ...).

JSON shape (see SKILL.md for the full description):
{
  "title": "Parallel Structure",
  "grades": "10-11",                            # "10-11" (one set for both) or "9"
  "cards": [
    {
      "focus": "Correlative conjunctions",      # short name of what the card practices
      "standard": "L1",                         # anchor only; the key adds the grade band(s)
      "label_band": "11-12",                    # 10-11 sets only, for R3 and R7, whose labels differ by band
      "regents": ["CC"],                        # Regents vocabulary IDs, may be empty
      "passage": "text students read",          # optional
      "prompt": "what students do",
      "choices": ["...", "..."],                # optional: 2 to 4 choices, lettered A-D
      "answer": "B",                            # the letter if choices, else the answer or an exemplar
      "accept": "what else to accept / why"     # for the teacher
    }, ...
  ]
}
"""
import csv
import json
import math
from datetime import date
import re
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:  # claude.ai sandboxes usually have it, but just in case
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "python-docx"])
    from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

REF = Path(__file__).resolve().parent.parent / "references"
CARDS_PER_SET = 20
CARD_W, CARD_H = 4.0, 2.4           # inches; fits a 3x5 index card
COLS, ROWS = 2, 4
FONT = "Arial"
BODY_PT, HEAD_PT = 10, 8
LETTERS = "ABCD"
GRADES = {
    "10-11": {"bands": ["9-10", "11-12"],
              "note": "For 10th and 11th grade. Standards are NYS Next Generation ELA; each card practices the 9-10 and 11-12 version of the standard shown."},
    "9": {"bands": ["9-10"],
          "note": "For 9th grade. Standards are NYS Next Generation ELA, grades 9-10."},
}

# Rough fit check, calibrated for Arial 10 pt in a 4" card with small padding.
CHARS_PER_LINE = 52
BODY_LINES = 12


def load_refs():
    stds = json.loads((REF / "standards.json").read_text())
    vocab = json.loads((REF / "vocabulary.json").read_text())
    labels = {}
    for s in stds:
        labels.setdefault(s["Anchor"], {})[s["Band"]] = s["Label"]
    terms = {v["ID"]: v["Term"] for v in vocab}
    return labels, terms


def lines(text, width=CHARS_PER_LINE):
    return sum(max(1, math.ceil(len(p) / width)) for p in str(text).split("\n"))


PASSAGE_GAP = 12   # pt after the passage: a blank line before the question


def passage_parts(text):
    """Split a passage into lines: at line breaks, and before each numbered item like (2)."""
    text = re.sub(r"[ \t]+(?=\(\d+\)\s)", "\n", str(text).strip())
    return [p.strip() for p in text.split("\n") if p.strip()]


def card_lines(c):
    n = 0
    if c.get("passage"):
        parts = passage_parts(c["passage"])
        n += sum(lines(p) for p in parts) + 0.15 * (len(parts) - 1) + 1.0
    n += lines(c["prompt"])
    for ch in c.get("choices") or []:
        n += lines(ch, CHARS_PER_LINE - 5) + 0.1  # choices are indented and spaced
    return n


def check(data, labels, terms):
    problems = []
    cards = data.get("cards", [])
    if not data.get("title"):
        problems.append("The set needs a title.")
    grades = data.get("grades", "10-11")
    if grades not in GRADES:
        problems.append(f"'grades' must be \"10-11\" or \"9\", not {grades!r}.")
    if len(cards) != CARDS_PER_SET:
        problems.append(f"A set has exactly {CARDS_PER_SET} cards; this one has {len(cards)}.")
    for i, c in enumerate(cards, 1):
        where = f"Card {i}"
        for field in ("focus", "standard", "prompt", "answer"):
            if not str(c.get(field, "")).strip():
                problems.append(f"{where}: missing '{field}'.")
        if len(f"Card {i}: {c.get('focus', '')}") > 45:
            problems.append(f"{where}: the focus is too long to fit on one line; keep it to a few words.")
        a = str(c.get("standard", "")).strip().upper()
        if a not in labels:
            problems.append(f"{where}: standard '{c.get('standard')}' isn't on the list (use an anchor like R1, W1, L2).")
        else:
            both = labels[a]
            if grades == "10-11" and len(set(both.values())) > 1 and c.get("label_band") not in both:
                problems.append(f"{where}: {a} has a different label in each grade band, so set label_band to '9-10' or '11-12'.")
        for t in c.get("regents") or []:
            if t not in terms:
                problems.append(f"{where}: Regents ID '{t}' isn't in the vocabulary.")
        ch = c.get("choices")
        if ch:
            if not 2 <= len(ch) <= 4:
                problems.append(f"{where}: multiple choice needs 2 to 4 choices.")
            ans = str(c.get("answer", "")).strip().upper().rstrip(")")
            if ans not in LETTERS[: len(ch)]:
                problems.append(f"{where}: the answer should be one letter, {', '.join(LETTERS[:len(ch)])}.")
            if len(set(x.strip().lower() for x in ch)) != len(ch):
                problems.append(f"{where}: two choices are identical.")
        if card_lines(c) > BODY_LINES:
            problems.append(f"{where}: too long to fit on the card (about {card_lines(c):.0f} lines, max {int(BODY_LINES)}). Shorten the passage, prompt, or choices.")
        text = f"{c.get('passage','')} {c.get('prompt','')} {' '.join(c.get('choices') or [])}"
        for m in re.finditer(r"\bcard\s+(\d+)", text, re.I):
            problems.append(f"{where}: refers to Card {m.group(1)}. Cards are cut apart and used one at a time, so each card has to stand alone; repeat the passage or sentence instead.")
    return problems


def label_for(c, labels, grades="10-11"):
    a = c["standard"].strip().upper()
    both = labels[a]
    band = "9-10" if grades == "9" else c.get("label_band")
    lab = both.get(band) or next(iter(both.values()))
    return a, lab


def set_cell_borders(cell, style="dashed"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), style)
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "999999")
        borders.append(el)
    tcPr.append(borders)


def set_cell_margins(cell, inches=0.12):
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), str(int(inches * 1440)))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcPr.append(mar)


def para(cell_or_doc, text="", size=BODY_PT, bold=False, italic=False, color=None, after=2, first=False):
    p = cell_or_doc.paragraphs[0] if first else cell_or_doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if text:
        r = p.add_run(text)
        r.font.size, r.font.bold, r.font.italic, r.font.name = Pt(size), bold, italic, FONT
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
    return p


def fill_card(cell, n, c):
    # "Card N: focus" only; the standard lives in the teacher key. Students name
    # cards in full ("Card 7"), so the word Card is part of the label.
    p = para(cell, f"Card {n}: ", size=BODY_PT, bold=True, after=8, first=True)
    r = p.add_run(c["focus"])
    r.font.size, r.font.bold, r.font.name = Pt(BODY_PT), True, FONT
    if c.get("passage"):
        parts = passage_parts(c["passage"])
        for k, part in enumerate(parts):
            para(cell, part, italic=True, after=PASSAGE_GAP if k == len(parts) - 1 else 2)
    para(cell, c["prompt"], after=3)
    for i, ch in enumerate(c.get("choices") or []):
        para(cell, f"{LETTERS[i]})  {ch}", after=1)


def build(data, out):
    labels, terms = load_refs()
    problems = check(data, labels, terms)
    if problems:
        print("Not built. Fix these first:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(BODY_PT)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(0.25)
    sec.top_margin = sec.bottom_margin = Inches(0.5)

    cards = data["cards"]
    per_page = COLS * ROWS
    for start in range(0, len(cards), per_page):
        if start:
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        chunk = cards[start:start + per_page]
        t = doc.add_table(rows=ROWS, cols=COLS)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        for col in t.columns:
            col.width = Inches(CARD_W)
        for r_i, row in enumerate(t.rows):
            row.height = Inches(CARD_H)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for c_i, cell in enumerate(row.cells):
                cell.width = Inches(CARD_W)
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                set_cell_borders(cell)
                set_cell_margins(cell)
                k = r_i * COLS + c_i
                if k < len(chunk):
                    fill_card(cell, start + k + 1, chunk[k])
    # Answer key
    key = doc.add_section()
    key.left_margin = key.right_margin = Inches(0.7)
    key.top_margin = key.bottom_margin = Inches(0.7)
    para(doc, f"Teacher Key: {data['title']}", size=14, bold=True, after=2)
    grades = data.get("grades", "10-11")
    para(doc, GRADES[grades]["note"], size=9, color="555555", after=8)
    t = doc.add_table(rows=1, cols=5)
    t.style = "Table Grid"
    t.autofit = False
    widths = [0.45, 1.45, 1.1, 2.15, 1.95]
    for col, w in zip(t.columns, widths):
        col.width = Inches(w)
    hdr = t.rows[0]._tr.get_or_add_trPr()
    rep_el = OxmlElement("w:tblHeader"); rep_el.set(qn("w:val"), "true"); hdr.append(rep_el)
    for cell, w, h in zip(t.rows[0].cells, widths, ["Card", "Skill and standard", "Regents", "Answer", "Why / what to accept"]):
        cell.width = Inches(w)
        para(cell, h, size=9, bold=True, after=0, first=True)
    for n, c in enumerate(cards, 1):
        a, lab = label_for(c, labels, grades)
        new = t.add_row()
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); new._tr.get_or_add_trPr().append(cs)
        row = new.cells
        for cell, w in zip(row, widths):
            cell.width = Inches(w)
        para(row[0], str(n), size=9, bold=True, after=0, first=True)
        para(row[1], c["focus"], size=9, after=0, first=True)
        codes = ", ".join(f"{b}{a}" for b in GRADES[grades]["bands"])
        para(row[1], f"{codes}: {lab}", size=8, color="555555", after=0)
        regents = ", ".join(f"{terms[x]} ({x})" for x in c.get("regents") or []) or "None"
        para(row[2], regents, size=8, after=0, first=True)
        ans = str(c["answer"]).strip()
        para(row[3], ans, size=9, bold=bool(c.get("choices")), after=0, first=True)
        para(row[4], c.get("accept", ""), size=9, after=0, first=True)
    doc.save(out)
    print(f"Built {out}: {len(cards)} cards on {math.ceil(len(cards)/per_page)} pages, then the key.")
    return labels, terms


LOG_FIELDS = ["Date", "Grade", "Set", "Standards", "Regents tags", "Multiple choice", "File", "Used"]


def log_set(data, out, log_path, terms):
    """Save the set's JSON beside the Word file and add a line to the log."""
    out = Path(out)
    out.with_suffix(".json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    cards = data["cards"]
    grades = data.get("grades", "10-11")
    seen = lambda xs: list(dict.fromkeys(xs))
    stds = seen(c["standard"].strip().upper() for c in cards)
    regents = seen(t for c in cards for t in (c.get("regents") or []))
    mc = sum(1 for c in cards if c.get("choices"))
    row = {
        "Date": date.today().isoformat(),
        "Grade": "9th" if grades == "9" else "10th and 11th",
        "Set": data["title"],
        "Standards": ", ".join(stds),
        "Regents tags": ", ".join(f"{terms[t]} ({t})" for t in regents),
        "Multiple choice": "All" if mc == len(cards) else ("None" if mc == 0 else f"{mc} of {len(cards)}"),
        "File": out.name,
        "Used": "",
    }
    log_path = Path(log_path)
    new = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"Logged in {log_path.name} and saved {out.with_suffix('.json').name}.")


if __name__ == "__main__":
    args = sys.argv[1:]
    log = None
    if "--log" in args:
        k = args.index("--log")
        log = args[k + 1]
        del args[k:k + 2]
    data = json.loads(Path(args[0]).read_text())
    labels, terms = build(data, args[1])
    if log:
        log_set(data, args[1], log, terms)
