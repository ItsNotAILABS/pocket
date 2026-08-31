# Promote: internal → public

Founder tree (`OneDrive/pocket-os`) never auto-publishes.

## When to promote

Charter: ship to `ItsNotAILABS/pocket` only when

> Open app → Codex or Grok → work → summary makes sense → team invite works.

## Path

1. Work on Owner `:8787`. Keep WIP on this disk.
2. Test **POCKET for Users** on `:8788` (`scripts\Open-POCKET-User.cmd`). Separate profile, separate login.
3. Confirm `/desk` login, one Grok/Codex turn, readable summary, `/join` seat.
4. Copy a clean tree (no `.data/`, no `ACCESS.txt`, no `~/.pocket` secrets).
5. Push that copy to the public repo. Tag the version (`3.7.0`).
6. Marketing uses [README.md](../README.md) and [DEMO_60S.md](DEMO_60S.md) only.

## Ports (do not mix)

| Port | Product |
|------|---------|
| 8787 | Owner |
| 8788 | Users |
| 8789 | SovereignForge (lab) |

## Do not promote

Internal GO/Power experiment notes, MESIE paths, founder shortcuts, untested vision dumps.
