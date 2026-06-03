# KALINALYSIS — External Source Sync

## Purpose

The source sync system mirrors selected external repositories locally under `external_sources/`. This enables:

- **Offline demos** — run tool walkthroughs without internet access.
- **Snapshot consistency** — pin a known commit for reproducible demos.
- **Combined analysis** — cross-reference content from multiple tools in one local workspace.

> **Note:** `external_sources/` is excluded from git via `.gitignore`. Only the sync state (`data/kali/source-sync-state.json`) and configuration (`data/kali/source-mirrors.json`) are committed.

---

## Configuration Files

### `data/kali/source-mirrors.json`

Defines which sources to mirror and how.

```jsonc
{
  "mirrors": [
    {
      "source_id": "cisagov-malcolm",      // Must match an id in sources.json
      "local_path": "external_sources/cisagov-malcolm",
      "strategy": "shallow",               // "shallow" or "full"
      "depth": 1,                          // Only used for "shallow"
      "branch": "main",                    // Branch to track
      "sparse_checkout": false,            // Reserved for future use
      "post_sync_hook": null,              // Optional shell script to run after sync
      "enabled": true                      // Set false to skip without deleting the entry
    }
  ]
}
```

### `data/kali/source-sync-state.json`

Written by `sync_external_sources.py` after each run. Records timestamp, commit SHA, and status for every synced repo. **Do not edit manually.**

---

## Sync Strategies

| Strategy | Description | When to use |
|---|---|---|
| `shallow` | Clones with `--depth 1`, keeping only the latest commit | Large repos you only need to browse (Malcolm, Kali Purple) |
| `full` | Full clone with complete history | Small repos or repos you diff across versions |

---

## Running the Sync

### Via GitHub Actions

See [automation.md](automation.md). Runs weekly or on demand via `workflow_dispatch`.

### Locally

```bash
# Sync all enabled mirrors
python scripts/kali/sync_external_sources.py \
  --mirrors data/kali/source-mirrors.json \
  --state   data/kali/source-sync-state.json \
  --dest    external_sources/ \
  --verbose

# Sync a single mirror by source_id
python scripts/kali/sync_external_sources.py \
  --only brainfucksec-kalitorify \
  --verbose

# Dry run — print what would happen without cloning anything
python scripts/kali/sync_external_sources.py --dry-run --verbose
```

---

## Adding a New Mirror

1. **Add a source entry** in `data/kali/sources.json` with `"mirror": true`.
2. **Add a mirror entry** in `data/kali/source-mirrors.json` using the same `source_id`.
3. Choose `strategy` (`shallow` for large repos, `full` for small ones).
4. Set `enabled: true`.
5. Run `sync_external_sources.py` locally to verify it clones correctly.
6. Commit both JSON files and submit a PR.

---

## Removing a Mirror

1. Set `"enabled": false` in the mirror entry in `source-mirrors.json` (preferred — preserves history).
2. Or delete the entry entirely.
3. Optionally delete the local clone from `external_sources/` on your machine (it won't be re-created if disabled).

---

## Post-Sync Hooks

If a mirror defines a `post_sync_hook` path, that script is executed after a successful sync with the repo directory as the working directory. The script must be executable (`chmod +x`).

Example use cases:
- Regenerating an index file after cloning a cheatsheet repo.
- Running `pip install -e .` on an internal tool.
- Extracting a specific subdirectory to another location.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Repository not found` | URL in `sources.json` is wrong or repo is private | Update the URL; add SSH key for private repos |
| `shallow update not allowed` | Already cloned as full; trying to switch to shallow | Delete the local clone and re-sync |
| State file shows `"status": "error"` | Network failure or auth error | Check `error` field; re-sync manually with `--only <id>` |
| Hook script not found | Path in `post_sync_hook` is wrong | Verify the path relative to the repo root; make executable |
