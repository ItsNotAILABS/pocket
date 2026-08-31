"""Render POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.md to PDF."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, Preformatted, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "research" / "POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.md"
OUT = ROOT / "docs" / "research" / "POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.pdf"
NOTES = Path.home() / ".pocket" / "notes"
INK = HexColor("#18181b")
ACCENT = HexColor("#0d9488")
MUTED = HexColor("#52525b")


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("T", parent=base["Title"], fontName="Times-Bold", fontSize=16, leading=20, alignment=TA_CENTER, textColor=INK, spaceAfter=8),
        "meta": ParagraphStyle("M", parent=base["Normal"], fontName="Times-Italic", fontSize=10, leading=13, alignment=TA_CENTER, textColor=MUTED, spaceAfter=14),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Times-Bold", fontSize=13, leading=16, textColor=ACCENT, spaceBefore=14, spaceAfter=8),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Times-Bold", fontSize=11.5, leading=14, textColor=INK, spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("B", parent=base["Normal"], fontName="Times-Roman", fontSize=10, leading=13, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6),
        "code": ParagraphStyle("C", parent=base["Code"], fontName="Courier", fontSize=8, leading=10, textColor=INK, backColor=HexColor("#f4f4f5"), spaceBefore=4, spaceAfter=8),
    }
    story = []
    buf: list[str] = []
    mode = "p"

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        block = "\n".join(buf).strip()
        buf = []
        if mode == "code":
            story.append(Preformatted(block[:4000], styles["code"]))
        elif mode == "ul":
            items = []
            for line in block.splitlines():
                line = re.sub(r"^[-*]\s+", "", line)
                items.append(ListItem(Paragraph(_esc(line), styles["body"])))
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
        else:
            story.append(Paragraph(_esc(block).replace("\n", " "), styles["body"]))
        mode = "p"

    lines = text.splitlines()
    i = 0
    if lines and lines[0].startswith("# "):
        story.append(Paragraph(_esc(lines[0][2:]), styles["title"]))
        i = 1
        meta = []
        while i < len(lines) and (lines[i].startswith("**") or not lines[i].strip()):
            if lines[i].strip():
                meta.append(_esc(lines[i]))
            i += 1
        if meta:
            story.append(Paragraph("<br/>".join(meta), styles["meta"]))
    for line in lines[i:]:
        if line.startswith("```"):
            if mode == "code":
                flush()
            else:
                flush()
                mode = "code"
            continue
        if mode == "code":
            buf.append(line)
            continue
        if line.startswith("## "):
            flush()
            story.append(Paragraph(_esc(line[3:]), styles["h1"]))
            continue
        if line.startswith("### "):
            flush()
            story.append(Paragraph(_esc(line[4:]), styles["h2"]))
            continue
        if re.match(r"^[-*]\s+", line):
            if mode != "ul":
                flush()
                mode = "ul"
            buf.append(line)
            continue
        if not line.strip():
            flush()
            continue
        if mode == "ul":
            flush()
        buf.append(line)
    flush()
    NOTES.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="POCKET × PhoneAI Network and WebMCP",
        author="ItsNotAI Labs",
    )
    doc.build(story)
    (NOTES / "POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.pdf").write_bytes(OUT.read_bytes())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
