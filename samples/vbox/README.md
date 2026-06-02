# VirtualBox Sample Configs

Drop sample `.vbox` files in this directory to have them parsed by:

- `scripts/kali/update_kali_catalog.py`

The parser extracts machine-level metadata (name, OSType, UUID, RAM/CPU, attached images) and writes it to `data/kali/vm-releases.json` under `local_vbox_samples`.
