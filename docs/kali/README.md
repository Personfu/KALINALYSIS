# KALINALYSIS Workspace

This repository is curated as the Kali Linux work hub for tracking:

- Kali VirtualBox VM release artifacts (metadata only)
- Local `.vbox` configuration samples
- Curated external tool and write-up sources

## Key Paths

- `data/kali/vm-releases.json` – generated Kali VM release/index metadata
- `data/kali/sources.json` – curated external source manifest
- `data/kali/source-mirrors.json` – source mirror definitions
- `data/kali/source-sync-state.json` – latest mirror sync results
- `docs/kali/catalog.md` – generated human-readable catalog
- `scripts/kali/update_kali_catalog.py` – automation entrypoint
- `scripts/kali/sync_external_sources.py` – external source mirror sync
- `.github/workflows/kali-vm-catalog-update.yml` – scheduled + manual update workflow
- `.github/workflows/kali-source-sync.yml` – scheduled + manual source sync workflow
- `samples/vbox/` – optional local `.vbox` sample inputs
- `external_sources/` – local mirrored source trees

## Update Flow

1. GitHub Actions (or local run) pulls `https://www.kali.org/get-kali/#kali-virtual-machines`.
2. VirtualBox artifacts are discovered and normalized into `data/kali/vm-releases.json`.
3. Local `.vbox` samples are parsed into `local_vbox_samples` metadata.
4. `docs/kali/catalog.md` is regenerated from machine-readable manifests.

## Local Usage

```bash
python scripts/kali/update_kali_catalog.py \
  --output data/kali/vm-releases.json \
  --sources data/kali/sources.json \
  --catalog docs/kali/catalog.md \
  --vbox-dir samples/vbox

python scripts/kali/sync_external_sources.py
```

## Scope

This repo tracks metadata, download URLs, and configuration information for Kali virtual machines. VM binaries are not committed into git.

External repositories can be mirrored locally into `external_sources/` with the source sync script for a combined demonstration workspace.
