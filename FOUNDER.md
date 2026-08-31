# Founder desk vs public product face

Two products: **POCKET Owner** on `:8787`, **POCKET for Users** on `:8788`.  
[docs/WHICH_POCKET.md](docs/WHICH_POCKET.md)

## The split (simple)

| | **You (founder)** | **Customers (public face)** |
|--|-------------------|-----------------------------|
| **Code** | This folder (`pocket-os`) | GitHub `ItsNotAILABS/pocket` |
| **Git remote** | `internal` only (local disk) | Public GitHub — **not** attached here |
| **App URL** | `http://127.0.0.1:8787` | Marketing site / releases when you ship |
| **Optional public host** | Off by default | `pocket.medinatechlabs.net` only if you run the tunnel |

Daily development and “the app on my desk” live **only** in the founder tree.  
Public GitHub is the **marketing and product face** — update it when you release, not on every experiment.

## One-time setup

```powershell
cd C:\Users\Medin\OneDrive\pocket-os
.\scripts\Setup-Internal-Repo.ps1
.\scripts\Ensure-POCKET-Up.ps1
```

That:

1. Removes `origin` → public GitHub from this tree  
2. Adds `internal` → `%USERPROFILE%\.pocket\repos\pocket-internal.git`  
3. Writes `founder.env` so links stay local  

## Every day

1. Start host: `.\scripts\Ensure-POCKET-Up.ps1` or Desktop POCKET shortcut  
2. Open: **http://127.0.0.1:8787/desk**  
3. Commit / push only to `internal`  

## When you market / sell

- Landing, README, releases: **public GitHub** (separate promote)  
- Optional live demo host: tunnel + `pocket.medinatechlabs.net` (not required for your desk)  
- Do **not** push WIP from this tree to public GitHub  

## Links are separate on purpose

- **App you use:** `POCKET_PUBLIC_URL=http://127.0.0.1:8787` (in `founder.env`)  
- **Marketing host customers may see:** `POCKET_MARKETING_URL=https://pocket.medinatechlabs.net`  
- They are **not** the same thing unless you deliberately make them the same  

## Vision / “nothing running”

If the desk feels dead:

1. `Ensure-POCKET-Up.ps1`  
2. Hard-refresh desk (`Ctrl+Shift+R`)  
3. Sign in if asked  
4. Workspace → status should show App ready  

Vision needs the host process healthy; a hung Python on port 8787 times out even when “listening.” Restart the host when that happens.
