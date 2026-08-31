"""Render invention claims markdown to PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "research" / "INVENTION_CLAIMS_2026.md"
OUT = ROOT / "docs" / "research" / "INVENTION_CLAIMS_2026.pdf"
NOTES = Path.home() / ".pocket" / "notes"
INK = HexColor("#18181b")
ACCENT = HexColor("#0d9488")


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    base = getSampleStyleSheet()
    title = ParagraphStyle("T", parent=base["Title"], fontName="Times-Bold", fontSize=16, leading=20, alignment=TA_CENTER, textColor=INK, spaceAfter=10)
    h = ParagraphStyle("H", parent=base["Heading1"], fontName="Times-Bold", fontSize=12, leading=15, textColor=ACCENT, spaceBefore=12, spaceAfter=6)
    body = ParagraphStyle("B", parent=base["Normal"], fontName="Times-Roman", fontSize=10, leading=13, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    story = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.startswith("# "):
            story.append(Paragraph(_esc(line[2:]), title))
        elif line.startswith("## "):
            story.append(Paragraph(_esc(line[3:]), h))
        elif line.startswith("---"):
            continue
        else:
            story.append(Paragraph(_esc(line).replace("**", ""), body))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.85 * inch, rightMargin=0.85 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch).build(story)
    NOTES.mkdir(parents=True, exist_ok=True)
    dest = NOTES / "INVENTION_CLAIMS_2026.pdf"
    dest.write_bytes(OUT.read_bytes())
    print("wrote", OUT)
    print("wrote", dest)


if __name__ == "__main__":
    main()
