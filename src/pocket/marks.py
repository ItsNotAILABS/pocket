"""Lab marks and invention-claim registry — public defensive surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SCHEMA = "inl.marks.v1"
DOC_TM = "INL-2026-TM.PATENT.MEMO.001"
DOC_001 = "INL-2026-CLAIMS.PORTAL.PHONEAI.001"
DOC_002 = "INL-2026-CLAIMS.PORTAL.PHONEAI.002"

# status: file = recommended USPTO filing; house = lab name; caution = crowded/conflict; never = third-party
MARKS: List[Dict[str, Any]] = [
    {
        "mark": "PHONEAI KERNEL",
        "use": "PhoneAI Kernel",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Primary product mark. One word + KERNEL. Distinct from Ad Hoc Labs PHONE.AI (SN 99230184, receptionist/voicemail).",
    },
    {
        "mark": "PHONEAI OS",
        "use": "PhoneAI OS",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Alternate for the phone-native OS surface.",
    },
    {
        "mark": "POCKET HOST",
        "use": "POCKET host",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Stronger than POCKET alone (Mozilla Pocket and others crowd the solo word).",
    },
    {
        "mark": "POCKET OS",
        "use": "POCKET OS",
        "status": "file",
        "classes": ["9", "42"],
        "note": "File with logo. Solo POCKET is weak.",
    },
    {
        "mark": "VLAPTOP",
        "use": "vLaptop",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Public agent screen-kernel client. https://github.com/ItsNotAILABS/vlaptop",
    },
    {
        "mark": "SCREEN-KERNEL",
        "use": "SCREEN-KERNEL/1.0",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Shared human/agent screen protocol.",
    },
    {
        "mark": "ITSNOTAI LABS",
        "use": "ItsNotAI Labs",
        "status": "house",
        "classes": ["42"],
        "note": "House mark.",
    },
    {
        "mark": "MEDINA TECH LABS",
        "use": "Medina Tech Labs",
        "status": "house",
        "classes": ["42"],
        "note": "Operating company.",
    },
    {
        "mark": "RESEARCHERSHUB",
        "use": "ResearchersHub",
        "status": "file",
        "classes": ["42"],
        "note": "Sovereign research desk fork.",
    },
    {
        "mark": "TWIN MINT",
        "use": "twin mint",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Per-seat workspace tree + dual vault.",
    },
    {
        "mark": "WORKGRANT",
        "use": "WorkGrant",
        "status": "file",
        "classes": ["9", "42"],
        "note": "Object required before RAH execute.",
    },
    {
        "mark": "POCKET",
        "use": "POCKET",
        "status": "caution",
        "classes": ["9", "42"],
        "note": "Crowded. Keep as product name; register POCKET HOST / POCKET OS.",
    },
    {
        "mark": "PORTAL",
        "use": "POCKET Portal",
        "status": "caution",
        "classes": ["9"],
        "note": "Generic. Do not file PORTAL alone.",
    },
    {
        "mark": "PHONE.AI",
        "use": None,
        "status": "never",
        "classes": ["9", "38", "42"],
        "note": "Third party: Ad Hoc Labs SN 99230184. Do not brand Phone AI / Phone.ai.",
    },
    {
        "mark": "FACE ID",
        "use": None,
        "status": "never",
        "note": "Apple. Product copy: passkey / WebAuthn / device pair.",
    },
    {
        "mark": "ANTIGRAVITY",
        "use": None,
        "status": "never",
        "note": "Google product we stream; not our mark.",
    },
    {
        "mark": "WEBMCP",
        "use": None,
        "status": "never",
        "note": "Chrome proposed standard. Implement, do not trademark.",
    },
]


def snapshot() -> Dict[str, Any]:
    fileable = [m for m in MARKS if m.get("status") in ("file", "house")]
    return {
        "ok": True,
        "schema": SCHEMA,
        "id": DOC_TM,
        "inventor": {"name": "Alfredo Medina", "lab": "ItsNotAI Labs", "company": "Medina Tech Labs"},
        "disclaimer": "Not legal advice. Defensive publication and clearance notes only.",
        "claims": {
            "parent": DOC_001,
            "supplement": DOC_002,
            "markdown": [
                "/docs/research/INVENTION_CLAIMS_2026.md",
                "/docs/research/INVENTION_CLAIMS_2026.002.md",
                "/docs/research/TRADEMARK_AND_PATENT_MEMO_2026.md",
            ],
            "json": "/docs/research/invention_claims.v1.json",
            "http": ["GET /v1/claims", "GET /v1/marks", "GET /claims", "GET /marks"],
        },
        "file": fileable,
        "all": MARKS,
        "never": [m["mark"] for m in MARKS if m.get("status") == "never"],
    }


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def claims_payload() -> Dict[str, Any]:
    js = _root() / "docs" / "research" / "invention_claims.v1.json"
    data: Dict[str, Any] = {}
    if js.is_file():
        data = json.loads(js.read_text(encoding="utf-8"))
    data.setdefault("ok", True)
    data["markdown"] = "/docs/research/INVENTION_CLAIMS_2026.md"
    data["supplement"] = "/docs/research/INVENTION_CLAIMS_2026.002.md"
    data["memo"] = "/docs/research/TRADEMARK_AND_PATENT_MEMO_2026.md"
    data["pdf"] = "/docs/research/INVENTION_CLAIMS_2026.pdf"
    data["inventor"] = data.get("inventor") or {"name": "Alfredo Medina", "lab": "ItsNotAI Labs"}
    data["marks"] = snapshot()
    return data


def page_html(*, kind: str = "claims") -> str:
    snap = snapshot()
    data = claims_payload()
    claims = data.get("claims") or []
    rows = "".join(
        f"<tr><td>{c.get('n')}</td><td>{_esc(c.get('title') or '')}</td>"
        f"<td>{_esc(c.get('doc') or DOC_001)}</td></tr>"
        for c in claims
    )
    mark_rows = "".join(
        f"<tr><td><strong>{_esc(m.get('use') or m.get('mark'))}</strong></td>"
        f"<td>{_esc(m.get('status'))}</td><td>{_esc(m.get('note'))}</td></tr>"
        for m in MARKS
        if m.get("status") != "never"
    )
    never = ", ".join(_esc(m) for m in snap.get("never") or [])
    title = "PhoneAI Kernel™ · claims" if kind == "claims" else "POCKET™ · marks"
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<style>
body{{margin:0;font:16px/1.45 ui-sans-serif,system-ui;background:#05060a;color:#f4f4f5}}
main{{max-width:720px;margin:0 auto;padding:28px 18px 64px}}
h1{{font-size:28px;letter-spacing:-.04em;margin:0 0 8px}}
.lead{{color:#8b8b98}}
a{{color:#58a6ff}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}}
td,th{{border-bottom:1px solid rgba(255,255,255,.1);padding:8px 6px;text-align:left;vertical-align:top}}
.badge{{display:inline-block;padding:2px 8px;border-radius:999px;background:#00ff86;color:#042;font-weight:800;font-size:11px}}
.foot{{color:#8b8b98;font-size:12px;margin-top:28px}}
</style></head><body><main>
<p class="badge">Defensive publication</p>
<h1>{title}</h1>
<p class="lead">Alfredo Medina · ItsNotAI Labs · Medina Tech Labs. Not legal advice.
PhoneAI is a <strong>phone kernel OS seat</strong> on the operator PC — not a receptionist.</p>
<p><a href="/v1/claims">JSON claims</a> · <a href="/v1/marks">JSON marks</a> ·
<a href="/docs/research/INVENTION_CLAIMS_2026.002.md">002</a> ·
<a href="/docs/research/TRADEMARK_AND_PATENT_MEMO_2026.md">memo</a></p>
<h2>Claims 1–{len(claims) or 28}</h2>
<table><thead><tr><th>#</th><th>Title</th><th>Doc</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Marks</h2>
<table><thead><tr><th>Use as</th><th>Status</th><th>Note</th></tr></thead><tbody>{mark_rows}</tbody></table>
<p class="foot">Do not brand: {never}. ™ until registered. {DOC_001} · {DOC_002} · {DOC_TM}</p>
<p class="foot"><a href="/phoneai/app">PhoneAI Kernel</a> · <a href="/phoneai/portal">Portal</a> · <a href="/v1/screen/kernel">Screen kernel</a></p>
</main></body></html>"""


def _esc(s: Any) -> str:
    t = str(s or "")
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
