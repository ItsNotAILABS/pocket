# POCKET

**AI workspace on your computer.** Desk, phone, and API — your files stay yours.

You talk to Codex, Grok, or Claude on a local desk. Work runs on this machine. You sign in with a seat. Strangers cannot open the desk.

**Sign in on this PC (no Edge password box):** [http://127.0.0.1:8787/v1/auth/desktop/enter](http://127.0.0.1:8787/v1/auth/desktop/enter)

| Product | Who | Open |
|---------|-----|------|
| **POCKET Owner** | You, this PC | http://127.0.0.1:8787/desk |
| **PhoneAI** | Phone kernel + sessions | http://127.0.0.1:8787/phoneai |
| **POCKET for Users** | Customers / seats | http://127.0.0.1:8788/desk |
| **Phone / remote** | Same seat away from the desk | https://pocket.medinatechlabs.net/desk |

They do not share a window, a port, or a login.

## What you do

1. Open the Owner or Users shortcut.
2. Sign in (or create a seat on Users).
3. Pick **Codex** or **Grok**. Ask for work.
4. Read the summary. Invite teammates when you want a team seat.

Platform board: http://127.0.0.1:8787/os  
Command plane: http://127.0.0.1:8787/power  

## Plans

| Plan | USD / mo | Seats |
|------|----------|-------|
| Starter | $29 | 1 |
| Pro | $99 | 5 |
| Team | $299 | 20 |

Create a seat: [/join](http://127.0.0.1:8787/join) · plain list: [/pricing](http://127.0.0.1:8787/pricing)

Never auto-pay. You confirm checkout.

## Two rules

- **Owner `:8787`** is this machine. Do not put it on the public hostname.
- **Users `:8788`** is the customer product. Forge / lab tools use **`:8789`**, not Users.

More: [docs/WHICH_POCKET.md](docs/WHICH_POCKET.md) · [docs/SHIP_FOR_USERS.md](docs/SHIP_FOR_USERS.md) · [docs/DEMO_60S.md](docs/DEMO_60S.md)

---

### Developers

Build and internals: [docs/POCKET_PRODUCT_CHANNELS_V3.md](docs/POCKET_PRODUCT_CHANNELS_V3.md) · [docs/PROMOTE.md](docs/PROMOTE.md)
