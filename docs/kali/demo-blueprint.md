# KALINALYSIS — Multi-Platform Demo Blueprint

## Purpose

This document describes how to run the full KALINALYSIS demo stack across multiple platforms, combining Kali Linux VirtualBox VMs with the Malcolm network analysis suite, local mirrored tools, and the Keycloak auth layer.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Host Machine (Linux / macOS / Windows with WSL2)           │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  VirtualBox          │  │  Docker Compose              │ │
│  │  ┌────────────────┐  │  │  ┌──────────┐ ┌───────────┐  │ │
│  │  │  Kali Linux VM │  │  │  │  Malcolm │ │ Keycloak  │  │ │
│  │  │  (attacker)    │  │  │  │  Stack   │ │  (SSO)    │  │ │
│  │  └────────────────┘  │  │  └──────────┘ └───────────┘  │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                             │
│  external_sources/   yara/rules/   data/kali/              │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| VirtualBox | 7.0+ (7.1+ for ARM64) | Install from virtualbox.org |
| Docker & Docker Compose | 24+ / 2.20+ | Docker Desktop on macOS/Windows |
| Python | 3.10+ | For automation scripts |
| Git | 2.40+ | For source sync |
| RAM | ≥ 16 GB | Kali VM (4 GB) + Malcolm stack (8 GB) + host overhead |
| Disk | ≥ 80 GB free | Kali VM image (~35 GB expanded) + Malcolm data |

---

## Step 1 — Import the Kali VM

1. Download the latest Kali VirtualBox image from `data/kali/vm-releases.json` (see `download_url` for the `latest` tag entry).
2. Verify the SHA256:
   ```bash
   sha256sum kali-linux-2024.4-virtualbox-amd64.7z
   # Compare to the sha256 field in vm-releases.json
   ```
3. Extract the archive:
   ```bash
   7z x kali-linux-2024.4-virtualbox-amd64.7z
   ```
4. In VirtualBox → **File → Import Appliance** → select the extracted `.ova` file.
5. Accept default settings. The VM will appear as **Kali-Linux-2024.4-vbox-amd64**.
6. Set the network adapter to **Host-Only Adapter** (`vboxnet0`) for isolated lab use.

---

## Step 2 — Start the Malcolm Stack

From the repository root:

```bash
docker compose up -d
```

Malcolm services come up on:

| Service | URL | Default credentials |
|---|---|---|
| OpenSearch Dashboards | https://localhost:443 | admin / changeme |
| Arkime | https://localhost:443/arkime | admin / changeme |
| NetBox | https://localhost:443/netbox | admin / changeme |
| Keycloak | https://localhost:443/auth | admin / changeme |

> **Change all default credentials before any internet-facing demo.**

---

## Step 3 — Configure Keycloak

```bash
# Bootstrap realm and OIDC clients
bash keycloak/scripts/configure-realm.sh
bash keycloak/scripts/create-client.sh
```

This creates the `kalinalysis` realm, a `malcolm` OIDC client, and initial demo users.

---

## Step 4 — Generate Traffic from the Kali VM

Boot the imported Kali VM and run a sample engagement against the Malcolm capture interface:

```bash
# From inside the Kali VM — example recon scan
nmap -sV -O -oX /tmp/nmap_scan.xml 192.168.56.1/24

# SYN scan
nmap -sS 192.168.56.1/24

# Harvest domains (requires network access)
theHarvester -d example.com -l 100 -b all
```

The `pcap-capture` service in the Malcolm stack captures this traffic automatically.

---

## Step 5 — Analyse in Malcolm

1. Open OpenSearch Dashboards at `https://localhost:443`.
2. Navigate to the **MALCOLM** dashboard.
3. Observe the traffic from the Kali VM classified by Zeek and Suricata.
4. Use the **File Upload** feature to import the Nmap XML for correlation.

---

## Step 6 — Apply YARA Rules

```bash
# Validate rules first
python scripts/kali/validate_yara.py --rules-dir yara/rules/

# Scan a sample file (requires yara-python or the yara CLI)
yara -r yara/rules/ /path/to/sample/
```

---

## Teardown

```bash
# Stop Malcolm stack
docker compose down

# Optionally remove all Malcolm data volumes
docker compose down -v

# Power off the Kali VM via VirtualBox GUI or:
VBoxManage controlvm "Kali-Linux-2024.4-vbox-amd64" poweroff
```

---

## Platform Notes

### macOS (Apple Silicon)

- Use the `arm64` Kali VirtualBox image (see `vm-releases.json` entry tagged `arm64`).
- Requires VirtualBox 7.1 or later.
- Docker Desktop on macOS allocates 8 GB RAM to Docker by default — increase to 10+ GB in Docker Desktop → Settings → Resources.

### Windows (WSL2)

- Run all `docker compose` and `python` commands from within WSL2.
- VirtualBox runs natively on Windows; use a **Host-Only** adapter shared between WSL2 and VirtualBox.
- Ensure Hyper-V and WSL2 compatibility mode is enabled in VirtualBox preferences.

### Linux

- Standard install of VirtualBox from the official `.deb` / `.rpm` packages.
- No special configuration needed; the setup above applies directly.
