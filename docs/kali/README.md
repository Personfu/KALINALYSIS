# KALINALYSIS — Workspace Documentation

This document describes the purpose, layout, and conventions of the KALINALYSIS workspace.

---

## What is KALINALYSIS?

KALINALYSIS is a structured working environment for:

- **Tracking Kali Linux VirtualBox VM releases** — release versions, download URLs, SHA256 checksums, and release notes are maintained in `data/kali/vm-releases.json` and reflected in the generated catalog.
- **Curating external tool sources** — a registry of relevant repositories (offensive tooling, reference material, internal tooling) is maintained in `data/kali/sources.json`.
- **Mirroring source repositories locally** — selected repos are cloned into `external_sources/` via the sync automation, enabling fully offline demos.
- **Managing YARA rules** — a growing library of detection rules targeting Kali tooling artefacts and offensive indicators lives under `yara/rules/`.

---

## Directory Conventions

| Path | Purpose |
|---|---|
| `data/kali/` | All machine-readable JSON data files |
| `docs/kali/` | Human-readable documentation (this folder) |
| `scripts/kali/` | Python automation scripts |
| `external_sources/` | Locally mirrored repositories (not committed to git) |
| `samples/vbox/` | Optional local `.vbox` input files (not committed to git) |
| `templates/kali/` | JSON Schema and template files |
| `yara/rules/` | YARA detection rules |
| `.github/workflows/` | GitHub Actions automation |
| `keycloak/scripts/` | Keycloak realm and client setup scripts |

---

## Data File Reference

### `data/kali/vm-releases.json`

Schema version 1.2. Each entry in `releases[]` has:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier (e.g. `kali-2024-4-vbox-amd64`) |
| `version` | string | Kali version string (e.g. `2024.4`) |
| `platform` | string | Always `virtualbox` in this file |
| `architecture` | string | `amd64` or `arm64` |
| `release_date` | string | ISO 8601 date |
| `image_filename` | string | Archive filename |
| `download_url` | string | Direct download URL |
| `torrent_url` | string | Torrent file URL |
| `sha256` | string | SHA-256 of the downloaded archive |
| `sha256_url` | string | URL of the SHA256SUMS file |
| `size_bytes` | int | Approximate file size in bytes |
| `size_human` | string | Human-readable size |
| `vbox_version_tested` | string | Minimum recommended VirtualBox version |
| `notes` | string | Release summary |
| `tags` | string[] | e.g. `["latest", "stable"]` |

### `data/kali/sources.json`

Each entry in `sources[]` has:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique slug |
| `name` | string | Display name |
| `url` | string | Repository URL |
| `type` | string | `github` or `gitlab` |
| `description` | string | What this repo is and why it's included |
| `tags` | string[] | Categorisation tags |
| `license` | string | SPDX licence identifier |
| `mirror` | bool | Whether to clone locally |
| `mirror_depth` | string | `shallow` or `full` |
| `last_synced` | string? | ISO 8601 timestamp of last successful sync |
| `active` | bool | Whether to include in automation |

---

## Automation Overview

See [automation.md](automation.md) for full details.

- **`kali-vm-catalog-update.yml`** — Runs weekly (Sunday 02:00 UTC). Calls `update_kali_catalog.py`, commits changes to `vm-releases.json` and `catalog.md`.
- **`kali-source-sync.yml`** — Runs weekly (Sunday 04:00 UTC). Calls `sync_external_sources.py`, commits updated `source-sync-state.json`.

Both workflows can also be triggered manually from the Actions tab.

---

## Adding a New Source

1. Add an entry to `data/kali/sources.json` following the schema above.
2. If mirroring is desired, add a corresponding entry to `data/kali/source-mirrors.json`.
3. Run the catalog updater locally to verify the catalog regenerates correctly.
4. Submit a pull request.

---

## Adding a New YARA Rule

1. Create or edit a `.yar` file under `yara/rules/`.
2. Run `python scripts/kali/validate_yara.py --rules-dir yara/rules/` to check for syntax errors.
3. Submit a pull request.

---

## Contact / Issues

Open an issue on the [KALINALYSIS GitHub repository](https://github.com/Personfu/KALINALYSIS).
