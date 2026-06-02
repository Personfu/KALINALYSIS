# External Source Mirrors

This directory is the local workspace for mirrored source trees defined in:

- `data/kali/source-mirrors.json`

Populate it with:

```bash
python scripts/kali/sync_external_sources.py
```

To preview without downloading:

```bash
python scripts/kali/sync_external_sources.py --plan-only
```

The script writes sync status to `data/kali/source-sync-state.json`.
