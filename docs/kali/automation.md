# KALINALYSIS — Automation & Operations

## Overview

KALINALYSIS uses two GitHub Actions workflows to keep data files up to date automatically. Both workflows commit their outputs back to the `main` branch and can also be triggered on demand from the **Actions** tab.

---

## Workflow: `kali-vm-catalog-update.yml`

**File:** `.github/workflows/kali-vm-catalog-update.yml`  
**Schedule:** Every Sunday at 02:00 UTC (`cron: "0 2 * * 0"`)  
**Trigger:** `workflow_dispatch` with optional `dry_run` input

### What it does

1. Checks out the repository.
2. Installs Python 3.12 and dependencies from `scripts/kali/requirements.txt`.
3. Runs `update_kali_catalog.py` to:
   - Attempt to fetch the Kali Linux virtual machine download page.
   - Merge fetched data with existing `data/kali/vm-releases.json`.
   - Write an updated `vm-releases.json`.
   - Regenerate `docs/kali/catalog.md` from the combined release + source data.
4. Commits and pushes any changes with message `chore(catalog): auto-update VM releases and catalog [skip ci]`.

### Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `dry_run` | choice | `false` | If `true`, prints output but does not write or commit files |

### Outputs committed

- `data/kali/vm-releases.json`
- `docs/kali/catalog.md`

---

## Workflow: `kali-source-sync.yml`

**File:** `.github/workflows/kali-source-sync.yml`  
**Schedule:** Every Sunday at 04:00 UTC (`cron: "0 4 * * 0"`)  
**Trigger:** `workflow_dispatch` with optional `only_id` and `dry_run` inputs

### What it does

1. Checks out the repository.
2. Installs Python 3.12 and dependencies.
3. Runs `sync_external_sources.py` to:
   - Read `data/kali/source-mirrors.json` and `data/kali/sources.json`.
   - Clone or `git fetch` each enabled mirror into `external_sources/` (not committed).
   - Write updated `data/kali/source-sync-state.json`.
4. Commits and pushes the updated state file.
5. Uploads `source-sync-state.json` as a workflow artifact (retained for 30 days).

### Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `only_id` | string | `""` | If set, sync only the mirror with this `source_id` |
| `dry_run` | choice | `false` | If `true`, prints output but does not write or commit files |

### Outputs committed

- `data/kali/source-sync-state.json`

---

## Manual Trigger Instructions

1. Go to the repository on GitHub.
2. Click **Actions** in the top navigation bar.
3. Select the desired workflow from the left sidebar.
4. Click **Run workflow** (top-right of the workflow run list).
5. Set optional inputs and click **Run workflow**.

---

## Permissions

Both workflows require `contents: write` to commit back to the repository. This is configured in the workflow YAML under `permissions:`. No other GitHub token scopes are needed.

---

## Failure Handling

- If `update_kali_catalog.py` cannot reach the Kali download page (network timeout, etc.), it falls back to the existing `vm-releases.json` data. The catalog is still regenerated from that data, so the workflow exits successfully.
- If `sync_external_sources.py` encounters an error on one or more repos, it records the error in `source-sync-state.json` and exits with a non-zero code, causing the workflow run to be marked **failed** in GitHub Actions.
- Failed runs are visible in the Actions tab. No automatic retry is configured; re-trigger manually.

---

## Local Development

To run the automation scripts locally before pushing:

```bash
# Install deps
pip install -r scripts/kali/requirements.txt

# Dry-run catalog update
python scripts/kali/update_kali_catalog.py --dry-run --verbose

# Dry-run source sync
python scripts/kali/sync_external_sources.py --dry-run --verbose

# Validate YARA rules
python scripts/kali/validate_yara.py --rules-dir yara/rules/ --verbose
```
