# KALINALYSIS

KALINALYSIS is the official Kali Linux work repository for this project, designed as a curated hub for:

- tracking Kali Linux VirtualBox VM releases and updates
- managing local `.vbox` sample metadata for weekly/updated VM workflows
- integrating external tooling and write-up sources in a maintainable catalog
- mirroring full external source trees locally for combined demos

> This repository tracks metadata, URLs, and configuration details only. Kali VM binaries are **not** committed.

## Quick Start

```bash
python scripts/kali/update_kali_catalog.py \
  --output data/kali/vm-releases.json \
  --sources data/kali/sources.json \
  --catalog docs/kali/catalog.md \
  --vbox-dir samples/vbox

python scripts/kali/sync_external_sources.py
```

## Repository Layout

- `scripts/kali/update_kali_catalog.py` – update automation
- `scripts/kali/sync_external_sources.py` – local source mirror sync automation
- `.github/workflows/kali-vm-catalog-update.yml` – scheduled/manual updater
- `.github/workflows/kali-source-sync.yml` – scheduled/manual source sync updater
- `data/kali/vm-releases.json` – machine-readable Kali VM release metadata
- `data/kali/sources.json` – curated external source inventory
- `data/kali/source-mirrors.json` – source mirror definitions
- `data/kali/source-sync-state.json` – latest sync metadata
- `external_sources/` – local mirrored source repositories
- `docs/kali/catalog.md` – generated source + release catalog
- `docs/kali/README.md` – workspace documentation
- `docs/kali/automation.md` – automation and operational details
- `docs/kali/source-sync.md` – external source sync usage
- `docs/kali/demo-blueprint.md` – multi-platform demonstration design
- `templates/kali/vbox-metadata.schema.json` – sample metadata schema
- `samples/vbox/` – optional local `.vbox` sample inputs

## Curated External Sources

- https://github.com/cisagov/Malcolm
- https://gitlab.com/kalilinux/kali-purple
- https://github.com/brainfucksec/kalitorify
- https://github.com/Gnosisone/ERR0RS-Ultimate
- https://github.com/NoorQureshi/kali-linux-cheatsheet
- https://github.com/The-Art-of-Hacking/h4cker
- https://github.com/CyberSecurityRepo/theHarvester
- https://github.com/Personfu/Centipede
- https://github.com/Personfu/YellowKey

For integration metadata and tags, see `data/kali/sources.json` and generated `docs/kali/catalog.md`.

## Automation

The workflow `.github/workflows/kali-vm-catalog-update.yml` runs weekly and on-demand to refresh tracked release metadata and regenerate the catalog.
