# Ultimate Kali Demonstration Blueprint

This blueprint combines mirrored sources and Kali release metadata into one operational workspace across your requested environments.

## 1) Raspberry Pi Demonstration

- Base: Raspberry Pi OS or Kali ARM image
- Integrate from mirrored sources:
  - `external_sources/kalitorify/`
  - `external_sources/theharvester/`
  - `external_sources/h4cker/` references
- Demonstrate lightweight recon + privacy workflow and runbook documentation from cheatsheets/writeups.

## 2) Windows + VirtualBox Demonstration

- Use tracked VM metadata in `data/kali/vm-releases.json`
- Import latest Kali VirtualBox artifacts from tracked URLs/checksums
- Map local `.vbox` samples via `samples/vbox/` to compare VM config profiles
- Cross-reference tool stacks from mirrored source folders.

## 3) Ubuntu/Fedora Host Demonstration

- Host systems run Kali VM (VirtualBox) and/or containerized components
- Use `external_sources/malcolm/` and `external_sources/kali-purple/` for defensive/monitoring lab design
- Use `external_sources/theharvester/` and `external_sources/kalitorify/` for offensive/recon workflows

## 4) Native Kali Linux Demonstration

- Use Kali as base environment and pull workflow references from:
  - `external_sources/kali-linux-cheatsheet/`
  - `external_sources/errors-ultimate/`
  - `external_sources/h4cker/`
  - `external_sources/centipede/`
  - `external_sources/yellowkey/`

## 5) Kali NetHunter Demonstration

- NetHunter source mirror:
  - `external_sources/kali-nethunter/`
- Build mobile-security demonstration paths and align with your Kali VM/native workflows.

## Operational cadence

- Refresh Kali VM metadata weekly via GitHub Actions
- Refresh mirrored source workspace manually or on schedule via source sync workflow
- Capture current sync status in `data/kali/source-sync-state.json`
