# FLLC Mission Upgrade — KALINALYSIS

## Role in the PersonFu/FLLC portfolio

KALINALYSIS should become the **defensive lab orchestration and Kali workspace catalog** for FLLC. It should not be presented as a grab-bag of offensive tooling. Its value is controlled lab setup, VM release tracking, blue-team validation, source inventory, and repeatable research environments.

## Upgrade direction

### 1. Mission-control dashboard

Build a small static dashboard that reads the existing JSON catalogs and renders:

- Kali VM release status.
- Source mirror freshness.
- YARA validation status.
- Lab modules available.
- Safety classification per source: `defensive`, `reference`, `dual-use`, `internal-only`.

### 2. Defensive lab profiles

Add lab profiles instead of vague tool lists:

| Profile | Purpose | Public-safe? |
| --- | --- | --- |
| SOC Analyst | PCAP/log review, Malcolm, detection exercises | Yes |
| Web App Defense | OWASP testing in local toy apps | Yes |
| Malware Triage | YARA/string analysis on benign samples | Gated |
| OSINT Source Review | Public-source collection workflow | Yes |
| Endpoint Hardening | Defender/Linux audit checklists | Yes |

### 3. Safety and scope metadata

Add a `data/kali/source-classification.json` file with fields:

```json
{
  "name": "example-source",
  "category": "defensive | reference | dual-use | internal-only",
  "public_showcase": true,
  "allowed_use": "controlled lab education",
  "blocked_use": "unauthorized access or live-target exploitation"
}
```

### 4. FLLC website integration

Use this repo to feed `/mission-systems` and member dashboards:

- `Kali Lab Catalog` card.
- `VM release tracker` card.
- `YARA validation` card.
- `Defensive lab profile` cards.

## Content outputs to produce

- Blog: “How to structure a Kali lab without turning it into tool spam.”
- Short video: “Your Kali VM needs a mission profile, not 200 random tools.”
- Member lesson: “Building a controlled defensive analysis VM.”
- GitHub badge: `defensive-lab-catalog`.

## Immediate quality checklist

- [ ] Ensure all external sources are labeled as upstream/reference/internal.
- [ ] Add generated catalog screenshots or diagrams.
- [ ] Add source freshness badges.
- [ ] Add explicit authorization boundary.
- [ ] Keep large binaries out of Git.
- [ ] Add CI validation for JSON and YARA rules.
