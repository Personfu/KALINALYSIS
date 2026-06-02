# External Source Synchronization

This project can mirror all requested external repositories into local folders for a full, hands-on Kali demonstration workspace.

## Manifest

Mirror targets are defined in:

- `data/kali/source-mirrors.json`

Included sources:

- cisagov/Malcolm
- kalilinux/kali-purple (GitLab)
- brainfucksec/kalitorify
- Gnosisone/ERR0RS-Ultimate
- NoorQureshi/kali-linux-cheatsheet
- The-Art-of-Hacking/h4cker
- CyberSecurityRepo/theHarvester
- Personfu/Centipede
- Personfu/YellowKey
- Personfu/kali-nethunter

## Local sync

```bash
python scripts/kali/sync_external_sources.py
```

Outputs:

- mirrored source trees under `external_sources/<source-id>/`
- sync metadata in `data/kali/source-sync-state.json`

## Selective sync

```bash
python scripts/kali/sync_external_sources.py --source kali-nethunter --source kali-purple
```

## Planning mode (no download)

```bash
python scripts/kali/sync_external_sources.py --plan-only
```

## Notes

- Sync uses source archives and does not require `git clone`.
- Review and comply with each upstream repository license before redistribution.
