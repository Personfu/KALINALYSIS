# KALINALYSIS

**KALINALYSIS** is the official Kali Linux work repository for this project — a curated hub for tracking Kali Linux VirtualBox VM releases, managing local `.vbox` sample metadata, integrating external tooling and write-up sources, and mirroring full external source trees locally for combined demos.

> **Note:** This repository tracks metadata, URLs, and configuration details only. Kali VM binaries are **not** committed to version control.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Repository Layout](#repository-layout)
- [Curated External Sources](#curated-external-sources)
- [Automation](#automation)
- [Data Files](#data-files)
- [Templates](#templates)
- [YARA Rules](#yara-rules)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

KALINALYSIS is designed around four core workflows:

1. **VM Release Tracking** — Fetches current Kali Linux VirtualBox release metadata from official and community sources, normalizes it, and writes structured JSON + a human-readable markdown catalog.
2. **External Source Sync** — Mirrors curated external repositories locally under `external_sources/` for offline demo and analysis use.
3. **YARA Rule Management** — Maintains a collection of YARA rules targeting Kali-specific artifacts, tooling signatures, and offensive security indicators.
4. **Keycloak Auth Integration** — Scripts and configuration for integrating Keycloak SSO into local KALINALYSIS lab deployments.

---

## Quick Start

### Prerequisites

- Python 3.10+
- `pip install -r scripts/kali/requirements.txt`
- `git` (for source sync)
- Optional: Docker (for containerised replay)

### Run the VM catalog updater

```bash
python scripts/kali/update_kali_catalog.py \
  --output data/kali/vm-releases.json \
  --sources data/kali/sources.json \
  --catalog docs/kali/catalog.md \
  --vbox-dir samples/vbox
```

### Run the external source sync

```bash
python scripts/kali/sync_external_sources.py \
  --mirrors data/kali/source-mirrors.json \
  --state   data/kali/source-sync-state.json \
  --dest    external_sources/
```

### Validate YARA rules

```bash
python scripts/kali/validate_yara.py --rules-dir yara/rules/
```

---

## Repository Layout

```
KALINALYSIS/
├── .github/
│   └── workflows/
│       ├── kali-vm-catalog-update.yml   # Scheduled/manual VM catalog refresh
│       └── kali-source-sync.yml         # Scheduled/manual source mirror sync
├── data/kali/
│   ├── vm-releases.json                 # Machine-readable Kali VM release metadata
│   ├── sources.json                     # Curated external source inventory
│   ├── source-mirrors.json              # Source mirror definitions
│   └── source-sync-state.json           # Latest sync metadata / timestamps
├── docs/kali/
│   ├── README.md                        # Workspace documentation
│   ├── catalog.md                       # Generated source + release catalog
│   ├── automation.md                    # Automation and operational details
│   ├── source-sync.md                   # External source sync usage
│   └── demo-blueprint.md                # Multi-platform demonstration design
├── external_sources/                    # Locally mirrored source repositories
│   └── .gitkeep
├── keycloak/
│   └── scripts/
│       ├── configure-realm.sh           # Realm bootstrap script
│       └── create-client.sh             # OIDC client registration helper
├── samples/
│   └── vbox/                            # Optional local .vbox sample inputs
│       └── .gitkeep
├── scripts/kali/
│   ├── requirements.txt                 # Python dependencies
│   ├── update_kali_catalog.py           # VM release catalog updater
│   ├── sync_external_sources.py         # Source mirror sync
│   └── validate_yara.py                 # YARA rule validator
├── templates/kali/
│   └── vbox-metadata.schema.json        # JSON Schema for .vbox sample metadata
├── yara/
│   └── rules/
│       ├── kali_tooling.yar             # Kali-specific tool signatures
│       ├── offensive_indicators.yar     # Generic offensive-security indicators
│       └── vm_artifacts.yar             # VirtualBox/VMware artifact signatures
├── README.md
└── LICENSE.txt
```

---

## Curated External Sources

| Repository | Description | Tags |
|---|---|---|
| [cisagov/Malcolm](https://github.com/cisagov/Malcolm) | Full-featured network traffic analysis platform | `network`, `pcap`, `analysis` |
| [kalilinux/kali-purple](https://gitlab.com/kalilinux/kali-purple) | Kali Purple defensive security edition | `kali`, `defensive`, `soc` |
| [brainfucksec/kalitorify](https://github.com/brainfucksec/kalitorify) | Transparent proxy through Tor for Kali | `tor`, `proxy`, `anonymity` |
| [Gnosisone/ERR0RS-Ultimate](https://github.com/Gnosisone/ERR0RS-Ultimate) | Multi-tool offensive framework | `offensive`, `enum` |
| [NoorQureshi/kali-linux-cheatsheet](https://github.com/NoorQureshi/kali-linux-cheatsheet) | Comprehensive Kali Linux command cheatsheet | `reference`, `cheatsheet` |
| [The-Art-of-Hacking/h4cker](https://github.com/The-Art-of-Hacking/h4cker) | Hacking / CTF resources collection | `ctf`, `reference` |
| [CyberSecurityRepo/theHarvester](https://github.com/CyberSecurityRepo/theHarvester) | OSINT email/domain harvesting tool | `osint`, `recon` |
| [Personfu/Centipede](https://github.com/Personfu/Centipede) | Custom automation tooling | `automation`, `internal` |
| [Personfu/YellowKey](https://github.com/Personfu/YellowKey) | Key management utilities | `crypto`, `internal` |

For full integration metadata and tags see [`data/kali/sources.json`](data/kali/sources.json) and the generated [`docs/kali/catalog.md`](docs/kali/catalog.md).

---

## Automation

| Workflow | Schedule | Trigger | Description |
|---|---|---|---|
| `kali-vm-catalog-update.yml` | Weekly (Sunday 02:00 UTC) | `workflow_dispatch` | Fetches latest Kali VM release metadata and regenerates catalog |
| `kali-source-sync.yml` | Weekly (Sunday 04:00 UTC) | `workflow_dispatch` | Syncs all mirrored external sources and updates sync state |

Both workflows commit any changes back to the repository automatically.

---

## Data Files

- **`data/kali/vm-releases.json`** — Normalised list of available Kali Linux VirtualBox releases, including version, SHA256, download URL, and release date.
- **`data/kali/sources.json`** — Inventory of curated external sources with metadata: URL, description, tags, last-synced timestamp.
- **`data/kali/source-mirrors.json`** — Mirror configuration: which repos to clone shallow vs. full, target subdirectory, sync strategy.
- **`data/kali/source-sync-state.json`** — Runtime state written by `sync_external_sources.py`; records last sync time and per-repo status.

---

## Templates

- **`templates/kali/vbox-metadata.schema.json`** — JSON Schema (draft-07) describing the expected structure for `.vbox` sample metadata files placed in `samples/vbox/`.

---

## YARA Rules

Rules live under `yara/rules/` and are validated on every push via the `validate_yara.py` script.

| Rule file | Coverage |
|---|---|
| `kali_tooling.yar` | String/byte signatures for common Kali tools (nmap, metasploit stagers, etc.) |
| `offensive_indicators.yar` | Generic indicators: reverse shell patterns, encoded payloads |
| `vm_artifacts.yar` | VirtualBox Guest Additions artefacts, `.vbox` XML markers |

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-improvement`.
3. Commit with a clear message.
4. Open a pull request against `main`.

Please keep data files valid JSON and ensure YARA rules pass `validate_yara.py` before submitting.

---

## License

See [LICENSE.txt](LICENSE.txt). This project is a fork of [cisagov/Malcolm](https://github.com/cisagov/Malcolm) and inherits its Apache 2.0 licence for upstream components. KALINALYSIS-specific additions are released under the same licence.
