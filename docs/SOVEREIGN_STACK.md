# Sovereign stack doctrine

## What we mean (not “never cloud”)

| Pillar | Product truth |
|--------|----------------|
| **1. Our remote browser** | Must **beat theirs** on every test/benchmark. Signed-in **host Edge** + Fusion sense + Control/VComp + evidence. Remote users drive **our** host via tunnel — not a vendor browser farm that stores their logins. |
| **2. Phone + home IoT** | Phone is first-class remote desk **and** connects devices around the home (pair, LAN, device registry, HZ BLE mesh). |
| **3. Remote** | Always required. Named tunnel `pocket.medinatechlabs.net`, LAN, seats, node pair. |
| **4. Our computing clouds + models** | When work runs on **our** host + **our** clouds (deploys, edge tunnel, Auro, NEXUS, mesh vdisk), that **is** our version of cloud. Prompts are not “leaking to Connected Apps third parties” as the product identity — they execute under **our** perimeter. Vendor model APIs are optional adapters. |

## Why “prompts leave” was the wrong frame

- **Their** product: multi-tenant cloud owns the session, remote browser, and often the tools.  
- **Ours**: session + browser + tools run on **lab host / lab clouds we operate**.  
- Remote ≠ their custody. Remote = **reach our host**.  
- Cloud models (Auro on host, our deploys, our edge) = **our cloud**, not ChatGPT Connected Apps.

## APIs

| Endpoint | Role |
|----------|------|
| `GET /v1/sovereign` | Full stack status |
| `GET /v1/computing-clouds` | Inventory of OUR clouds |
| `GET /v1/remote-browser` | Remote browser status |
| `GET /v1/remote-browser/benchmark` | Hard suite (must pass) |
| `POST /v1/remote-browser/open` | Signed-in Edge |
| `POST /v1/remote-browser/sense` | Fusion pack |
| `POST /v1/remote-browser/act` | Host control |
| `GET /v1/iot` | Home IoT + phone bridge |
| `POST /v1/iot/devices` | Register / seed devices |

## Skills

`sovereign_stack` · `computing_clouds` · `remote_browser_benchmark` · `remote_browser_open` · `iot_status` · `iot_register` · `iot_phone` · `iot_hz_status`

## Code

- `sovereign_stack.py` — doctrine + cloud inventory  
- `remote_browser.py` — competitive remote browser + benchmarks  
- `iot_home.py` — devices + phone bridge + HZ  
- `browser_mode.py` — Edge host actions  
- `hz-offline` — BLE / offline mesh (sibling lab stack)  
