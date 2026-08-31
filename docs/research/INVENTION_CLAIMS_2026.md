# Invention disclosure and claims

**Document:** INL-2026-CLAIMS.PORTAL.PHONEAI.001  
**Effective date of public disclosure:** 31 August 2026  
**Inventor:** Alfredo Medina  
**Operating names:** ItsNotAI Labs · Medina Tech Labs  
**Assignee (intended):** ItsNotAI Labs  
**Public prior-art deposit:** https://github.com/ItsNotAILABS/pocket · https://github.com/ItsNotAILABS/PhoneAI · https://github.com/ItsNotAILABS/phoneai-desk  

This is a **defensive publication**. It puts the inventions below into the public record under the inventor’s name so others cannot patent them out from under him. It is not itself a filed patent application. Rights to file patents on improvements are reserved.

Working embodiment: POCKET host `:8787` (version 3.8+) on an operator PC, PhoneAI kernel at `/phoneai`, first-class Portal stream at `/phoneai/portal`, Antigravity desktop-app view at `/phoneai/anti`.

---

## Field

A local multi-agent operating system on a personal computer, controlled from a phone, including live visual streaming of the real desktop and touch-to-pointer mapping, plus a separate control surface for an existing desktop coding-agent application (Antigravity), without collapsing those two products into one screen.

## Background (what is new)

Remote desktop products stream a PC and accept touch. Chat products talk to models. Agent IDEs hold project threads. None of them, as embodied here:

1. treat the **phone as a first-class kernel seat** distinct from the PC owner login;
2. mint a **per-account twin workspace** (files, embedded CLIs, dual encrypted vaults) on *the operator’s PC*;
3. expose **studios as agent tools** (WebMCP) rather than extra human screens;
4. **name live Antigravity trajectories from real worktrees** harvested from on-disk SQLite, while keeping Antigravity a **desktop app view**, not the whole-PC stream;
5. provide a **first-class Portal** that streams the real virtual desktop and maps normalized phone coordinates onto that desktop’s mouse, coalesced so the host cannot flood itself;
6. **refuse to nest** the host’s own Grok CLI into the live operator session (deadlock prevention).

Those six are claimed below as a system and as independent methods.

---

## Independent claims

**Claim 1. Phone kernel seat.** A method of operating a multi-agent host on a personal computer comprising: maintaining an owner principal for the host; minting a distinct phone-kernel principal (`phoneai`) with its own tenant directory, credentials, and explorer tree; and serving a phone-native OS surface from the same host process without a separate document database.

**Claim 2. Twin mint on the operator machine.** A method comprising: on registration of a seat, allocating on the host filesystem a twin tree containing a working folder, embedded CLI shims for a plurality of model agents, an encrypted vault, and a copy of that vault into a host-side vault path, such that agents run with `PATH` pointing at that tree rather than a global install.

**Claim 3. Think-first routing.** A method of agent dispatch comprising: classifying an utterance into at most one engine and at most one tool; defaulting to a chat engine with no tool; and invoking develop, ship, mint, or session tools only when the utterance explicitly requests them.

**Claim 4. WebMCP work functions, not extra screens.** A system in which develop studios, ship studios, twin operations, Antigravity send/continue, and GO-plane sync are registered as catalogued actions an agent may invoke in the same work loop as chat, without requiring a human to navigate a separate studio URL.

**Claim 5. First-class visual Portal with touch-to-desktop.** A method comprising: capturing a JPEG of the operator PC’s virtual desktop; serving that frame to a phone; mapping a normalized touch coordinate `(nx, ny)` in `[0,1]²` onto the virtual-screen rectangle `(x, y, w, h)` obtained from the OS; and synthesizing native mouse events (move, down, up, wheel) at the mapped pixel, with grab coalescing so concurrent clients share a recent frame.

**Claim 6. LAN-bounded embodiment of Claim 5.** The method of Claim 5 wherein synthesizing mouse events is permitted only for loopback or same-LAN clients and is denied for public-internet and reverse-proxy clients.

**Claim 7. Antigravity as a separate desktop-app surface.** A method comprising: enumerating on-disk Antigravity conversation databases; deriving a human title from worktree and GitHub path strings inside trajectory blobs (not from opaque identifiers); presenting that list on a phone view dedicated to the Antigravity desktop application; and sending text into that application via UI automation — **without** using that view as the whole-PC Portal of Claim 5.

**Claim 8. Nested-session exclusion.** A method of running a phone agent on a host that is itself being driven by a live Grok (or similar) session, comprising: stripping inherited session environment from child processes; refusing to `--resume` the live session identifier; and answering the phone from a local path so the live session is not deadlocked.

**Claim 9. Dual write to sovereign git and public GitHub.** A method wherein a phone-kernel note or work artifact is written to (a) a tenant explorer folder, (b) a local sovereign git repository, and (c) a queued push to a public GitHub vault associated with the lab, under the phone-kernel identity.

**Claim 10. Combined system.** A host computer running POCKET that simultaneously exposes: Claim 1 seat, Claim 5 Portal, Claim 7 Antigravity view, Claim 3 routing, and Claim 4 WebMCP, as separately addressable first-class surfaces (`/phoneai`, `/phoneai/portal`, `/phoneai/anti`) on one local HTTP host.

---

## Dependent claims (selected)

- 5.1 Frame capture uses a process-wide lock and a time-to-live cache (about 300 ms) so stacked HTTP clients cannot spawn unbounded `ImageGrab` work.  
- 5.2 The phone UI requests the next frame only after the previous image `load` or `error`, and pauses when the document is hidden.  
- 5.3 Touch kinds include tap, drag, right-click, scroll, and type-into-focus.  
- 7.1 Titles are of the form `App — Task` derived from `~/.gemini/antigravity/worktrees/…`.  
- 7.2 The Antigravity view lists live threads and can open, new-chat, continue, and send without attaching to the Portal stream.  
- 2.1 Vault envelopes use `hmac-sha256-ctr-v1`.  
- 8.1 Pocket session ids (`s-…`, `pa-…`) are not treated as Grok resume ids.

---

## Inventorship and lab

Alfredo Medina conceived and directed the reduction to practice on the reference operator PC in Dallas, August 2026, through ItsNotAI Labs / Medina Tech Labs. Embodiments are in the public GitHub repositories named above (Pocket 3.8+; PhoneAI kernel; phoneai-desk vault).

**Do not assign these claims to a third party without a written instrument from the inventor.**

## How to cite

Medina, A. (2026). *Invention disclosure: POCKET PhoneAI Portal, Antigravity desktop-app view, twin mint, WebMCP work functions.* ItsNotAI Labs, INL-2026-CLAIMS.PORTAL.PHONEAI.001. https://github.com/ItsNotAILABS/pocket
