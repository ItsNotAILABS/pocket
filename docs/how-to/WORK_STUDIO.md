# How-to: Work Studio

Surface: **http://127.0.0.1:8787/work**

Digital life assistant — separate from coding desk.

## Assist chat

Type a life request (research, draft, reserve, shop research). Engine routes automatically.

## Hand off to desk

- **Open on desk** — stores `pocket_work_handoff` and opens `/desk?agent=…`  
- Desk fills the composer; review and Send  

## Work loops

Power section lists design loops (code sprint, etc.).

- **Run on desk** on a loop card builds a structured prompt (goal + steps) and hands off to Build / Coding Swarm / Assist as appropriate  

## APIs

```http
GET  /v1/work-studio
POST /v1/work-studio/assist  {"text":"Plan my morning"}
POST /v1/work-loops/generate {"goal":"…"}
```
