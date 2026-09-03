# POCKET — Terms, Privacy, Trust model

**Last updated:** 2026-07-27  
**Operator product:** Medinatech Labs / POCKET host owner

## Trust model (read this)

POCKET is an **invite-only multi-agent desk** that runs on the **operator’s computer**.  
It is **not** a fully isolated multi-tenant cloud SaaS.

- Jobs (Codex, Grok, shell, desktop, NEXUS) execute **on the host PC**.
- Invited **members** share that host under role limits (no raw shell by default).
- **Admin** has full host power — treat admin credentials like root.

By creating an account or API key you accept this model.

## Terms of use (summary)

1. **Authorized use only** — invite or operator permission required.  
2. **No abuse** — no malware, crypto-mining, spam, illegal content, or attacks.  
3. **Host safety** — do not attempt to bypass allowlists, roles, or rate limits.  
4. **API keys** are secrets; you are responsible for usage under your key.  
5. **Credits (POCK)** meter use; prices in USD are marketing hints unless a signed contract says otherwise.  
6. **Availability** — service depends on the operator PC being awake and runtime + tunnel healthy. No SLA unless contracted.  
7. **Termination** — operator may revoke invites, keys, or access at any time.  
8. **Liability** — software provided as-is; operator not liable for data loss or agent mistakes. Back up your work.

## Privacy

- Account usernames, hashed passwords, sessions, jobs, and API key metadata are stored under the operator’s `~/.pocket/` directory.  
- Agent prompts and outputs may be written to job/session files on the host.  
- Public tunnel traffic is protected by auth; prefer Cloudflare Access for stronger edge auth.  
- Do not submit secrets you cannot afford to store on the host.  
- Operator can see all host activity; members should assume admin can audit.

## Intellectual property (defensive)

Inventions are published under Alfredo Medina / ItsNotAI Labs:

- [INL-2026-CLAIMS.PORTAL.PHONEAI.001](research/INVENTION_CLAIMS_2026.md) (31 Aug 2026)
- [INL-2026-CLAIMS.PORTAL.PHONEAI.002](research/INVENTION_CLAIMS_2026.002.md) (2 Sep 2026)
- [Trademark and patent memo](research/TRADEMARK_AND_PATENT_MEMO_2026.md)

Live: `/claims` · `/v1/marks`. PhoneAI Kernel™ is a phone OS seat — not a receptionist. Do not assign these claims without a written instrument from the inventor. This host is not a law firm; the memo is not legal advice.

## Support

Contact the operator who invited you (invite issuer).  
For self-host ops: see `docs/SECURITY.md`, `PRODUCT.md`, `docs/AI_API.md`.

## Selling the AI API

If you resell POCKET AI API access:

- Issue per-customer API keys.  
- Enforce quotas and tiers.  
- Provide this trust model + your own refund/SLA terms.  
- Do not imply isolated multi-tenant cloud unless you deploy per-customer hosts.
