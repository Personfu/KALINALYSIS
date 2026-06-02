# Automation Details

## Script: `scripts/kali/update_kali_catalog.py`

Capabilities:

- Fetches Kali's official VirtualBox page
- Extracts release artifacts (`.7z`, `.ova`, `.vbox`, `.vdi`, checksums, torrents)
- Groups artifacts by release identifier
- Parses local sample `.vbox` files for machine metadata
- Writes JSON manifest and generated markdown catalog

### Offline test mode

Use `--offline-html` to parse a local HTML fixture instead of performing an HTTP request.

## GitHub Actions Workflow

Workflow file: `.github/workflows/kali-vm-catalog-update.yml`

- Scheduled weekly (`cron: 15 6 * * 1`)
- Supports manual runs via `workflow_dispatch`
- Auto-commits updated files:
  - `data/kali/vm-releases.json`
  - `docs/kali/catalog.md`

## Source Mirror Automation

Workflow file: `.github/workflows/kali-source-sync.yml`

- Scheduled weekly and supports manual runs
- Runs `scripts/kali/sync_external_sources.py` to mirror all configured external repositories
- Writes sync results to `data/kali/source-sync-state.json`

## Notes

- Parsing is metadata-focused and resilient to minor layout changes by scanning links.
- If Kali's HTML structure changes significantly, update link matching in the script.
