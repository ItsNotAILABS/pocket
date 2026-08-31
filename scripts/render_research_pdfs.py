"""Render LOOMGRAPH + Integrations research papers to PDF (reportlab)."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs" / "research"
NOTES = Path.home() / ".pocket" / "notes"
NOTES.mkdir(parents=True, exist_ok=True)

ACCENT = HexColor("#0d9488")
INK = HexColor("#18181b")
MUTED = HexColor("#52525b")


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "WPTitle",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=16,
            leading=20,
            textColor=INK,
            spaceAfter=8,
            alignment=TA_CENTER,
        ),
        "meta": ParagraphStyle(
            "WPMeta",
            parent=base["Normal"],
            fontName="Times-Italic",
            fontSize=10,
            leading=13,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "WPH1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=13,
            leading=16,
            textColor=ACCENT,
            spaceBefore=16,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "WPH2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=11.5,
            leading=14,
            textColor=INK,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "WPH3",
            parent=base["Heading3"],
            fontName="Times-Bold",
            fontSize=10.5,
            leading=13,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "WPBody",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=10,
            leading=13,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "WPCode",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            textColor=INK,
            backColor=HexColor("#f4f4f5"),
            leftIndent=6,
            rightIndent=6,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "WPFooter",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }
    return styles


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _inline(s: str) -> str:
    s = _esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8">\1</font>', s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


def md_to_flowables(md: str, styles):
    story = []
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0
    in_code = False
    code_buf = []
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if not para_buf:
            return
        text = " ".join(para_buf).strip()
        para_buf = []
        if text:
            story.append(Paragraph(_inline(text), styles["body"]))

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush_para()
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                block = "\n".join(code_buf)
                story.append(Preformatted(block[:6000], styles["code"]))
                code_buf = []
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.startswith("# "):
            flush_para()
            story.append(Paragraph(_inline(line[2:].strip()), styles["title"]))
        elif line.startswith("## "):
            flush_para()
            story.append(Paragraph(_inline(line[3:].strip()), styles["h1"]))
        elif line.startswith("### "):
            flush_para()
            story.append(Paragraph(_inline(line[4:].strip()), styles["h2"]))
        elif line.startswith("#### "):
            flush_para()
            story.append(Paragraph(_inline(line[5:].strip()), styles["h3"]))
        elif line.strip() == "---":
            flush_para()
            story.append(Spacer(1, 8))
        elif line.startswith("|") and "|" in line[1:]:
            flush_para()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                row = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c or "") for c in row):
                    rows.append([Paragraph(_inline(c), styles["body"]) for c in row])
                i += 1
            if rows:
                n = len(rows[0])
                w = 6.5 * inch / max(n, 1)
                t = Table(rows, colWidths=[w] * n, repeatRows=1)
                t.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#ecfdf5")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                story.append(t)
                story.append(Spacer(1, 8))
            continue
        elif re.match(r"^[-*]\s+", line.strip()):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(
                    ListItem(
                        Paragraph(_inline(re.sub(r"^[-*]\s+", "", lines[i].strip())), styles["body"]),
                        leftIndent=12,
                    )
                )
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", start="•"))
            story.append(Spacer(1, 4))
            continue
        elif re.match(r"^\d+\.\s+", line.strip()):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(
                    ListItem(
                        Paragraph(_inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())), styles["body"]),
                        leftIndent=12,
                    )
                )
                i += 1
            story.append(ListFlowable(items, bulletType="1"))
            story.append(Spacer(1, 4))
            continue
        elif line.strip() == "":
            flush_para()
        else:
            # bold meta lines at top
            if line.startswith("**") and line.endswith("**") is False and ":**" in line:
                flush_para()
                story.append(Paragraph(_inline(line), styles["meta"]))
            else:
                para_buf.append(line.strip())
        i += 1
    flush_para()
    return story


def render_one(md_path: Path, out_pdf: Path, subtitle: str):
    styles = _styles()
    md = md_path.read_text(encoding="utf-8")

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(0.6)
        canvas.line(0.85 * inch, 0.65 * inch, letter[0] - 0.85 * inch, 0.65 * inch)
        canvas.setFont("Times-Roman", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.85 * inch, 0.45 * inch, "ItsNotAI Labs · POCKET Working Paper · Confidential host copy")
        canvas.drawRightString(letter[0] - 0.85 * inch, 0.45 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=letter,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.85 * inch,
        title=md_path.stem,
        author="ItsNotAI Labs",
    )
    story = [
        Paragraph("ItsNotAI Labs · POCKET Research", styles["meta"]),
        Paragraph(_inline(subtitle), styles["meta"]),
        Spacer(1, 6),
    ]
    story.extend(md_to_flowables(md, styles))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out_pdf


def main():
    papers = [
        (
            RESEARCH / "LOOMGRAPH_WORKING_PAPER.md",
            "LOOMGRAPH Working Paper — Protocol POCKET-LOOMGRAPH/1.0",
            "LOOMGRAPH_WORKING_PAPER.pdf",
        ),
        (
            RESEARCH / "POCKET_INTEGRATIONS_EXECUTE_PAPER.md",
            "Integrations Execute Working Paper — Schema pocket.integrations.execute.v1",
            "POCKET_INTEGRATIONS_EXECUTE_PAPER.pdf",
        ),
    ]
    outs = []
    for md, sub, name in papers:
        if not md.is_file():
            print("missing", md)
            continue
        out1 = RESEARCH / name
        out2 = NOTES / name
        render_one(md, out1, sub)
        render_one(md, out2, sub)
        # also copy md to notes
        (NOTES / md.name).write_text(md.read_text(encoding="utf-8"), encoding="utf-8")
        outs.append(str(out1))
        print("wrote", out1)
        print("wrote", out2)
    return outs


if __name__ == "__main__":
    main()
