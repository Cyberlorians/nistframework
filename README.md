# NIST 800-171 Alignment Framework

Community-driven mapping of **NIST 800-171 Rev.2** controls to **Microsoft Security** products, Sentinel tables, and KQL queries.

Every query includes **analyst-driven targeting** (Part 0) for both **GRC compliance** and **DFIR investigation** workflows.

## Structure

```
practices/           # One YAML file per NIST control (source of truth)
  3.1.1.yaml         # Each file contains product + table + KQL alignments
  3.1.2.yaml
  ...
scripts/             # Build and validation tooling
  validate.py        # Schema validation (runs on every PR)
  check_duplicates.py
  build_csv.py       # YAML → master CSV
  build_querypack.py # YAML → Sentinel Query Pack JSON
output/              # Auto-generated artifacts (never edit directly)
  NIST_800-171_Alignment.csv
  NIST_800-171_QueryPack.json
.github/workflows/   # CI/CD pipelines
  validate.yml       # PR validation
  build.yml          # Artifact generation on merge
```

## Coverage (Level 1 — 17 Controls)

| Family | Controls | Count |
|--------|----------|-------|
| Access Control | 3.1.1, 3.1.2, 3.1.20, 3.1.22 | 4 |
| Identification & Authentication | 3.5.1, 3.5.2 | 2 |
| Media Protection | 3.8.3, 3.8.4 | 2 |
| Physical Protection | 3.10.1, 3.10.3, 3.10.4, 3.10.5 | 4 |
| System & Communications Protection | 3.13.1, 3.13.5 | 2 |
| System & Information Integrity | 3.14.1, 3.14.2, 3.14.5 | 3 |

## Microsoft Products Covered

- Entra ID (SigninLogs, AuditLogs, Risk tables, Graph, ADFS, Provisioning)
- Microsoft Defender for Endpoint (MDE) — TVM, Process, Network, File, Device
- Microsoft Defender for Identity (MDI) — Logon, Directory events
- Microsoft Defender for Office 365 (MDO) — Email, Attachments, URLs, ZAP
- Microsoft Defender for Cloud Apps (MDCA) — Cloud events, Shadow IT
- Microsoft Defender for Cloud — Recommendations, Compliance, Secure Score
- Microsoft Purview — DLP, Sensitivity Labels, Information Protection
- Microsoft Intune — Device Compliance, Audit, Configuration
- Microsoft Sentinel — UEBA, Alerts, Incidents, TI, BehaviorAnalytics
- Azure — Firewall, NSG, Activity Log
- Windows — SecurityEvent (AD, Logon, USB)
- SharePoint Online — OfficeActivity
- Network Appliances — CommonSecurityLog (CEF)

## KQL Convention

Every query follows the same structure:

```kql
// Part 0: Analyst-Driven Targeting (GRC + DFIR)
let TargetUsers = dynamic(["*"]);      // Replace * with specific UPNs for investigation
let LookbackDays = 30;                 // Adjust for compliance window or incident timeline
// Part 1: Base Filter
TableName
| where TimeGenerated > ago(LookbackDays * 1d)
// Part 2: Enrichment
| extend ...
// Final Output
| project ...
| sort by TimeGenerated desc
| take 50
```

**For GRC**: Leave targets as `["*"]` — full-scope compliance audit.  
**For DFIR**: Replace targets with specific users, devices, IPs — scoped investigation.

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for details. The short version:

1. Fork this repo
2. Edit or add a practice YAML file under `practices/`
3. Open a Pull Request
4. CI validates your YAML automatically
5. Maintainer reviews and merges
6. CI rebuilds the master CSV and Query Pack

## Sentinel Integration

| Method | How |
|--------|-----|
| **Query Pack** | Deploy `output/NIST_800-171_QueryPack.json` as ARM template — queries appear in Logs blade |
| **Watchlist** | Upload `output/NIST_800-171_Alignment.csv` as a Sentinel Watchlist |
| **externaldata()** | `externaldata(...)[@"https://raw.githubusercontent.com/.../output/NIST_800-171_Alignment.csv"]` |
| **MCP** | Use Sentinel MCP to validate queries, deploy rules, and check coverage |
| **Security Copilot** | Reference the framework as context for compliance investigations |

## Roadmap

- [x] Level 1 — 17 NIST 800-171 controls
- [ ] Level 2 — 110 NIST 800-171 controls
- [ ] Level 3 — 35 NIST 800-172 controls
- [ ] Sentinel MCP validation (run all KQL, report coverage gaps)
- [ ] Security Copilot promptbook
- [ ] Analytics Rule templates (detection-worthy queries)

## License

MIT
