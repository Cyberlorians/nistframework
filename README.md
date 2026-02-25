# NIST 800-171 Alignment Framework

Community-driven mapping of **NIST 800-171 Rev.2** controls to **Microsoft Security** products, Sentinel tables, and KQL queries.

> **[Live Dashboard →](https://cyberlorians.github.io/nistframework/)** Browse every control, filter by family or workload, and copy KQL straight into Sentinel.

---

## Why This Exists

Most compliance frameworks give you a checklist — this one gives you **working KQL**.  Every NIST 800-171 Level 1 control is mapped to the Microsoft Sentinel tables and queries that prove you meet it.  The entire project is open-source and built so the community can contribute new mappings, fix queries, and extend coverage together.

## Getting Started

**No install required.** Open the live dashboard and start exploring:

**[cyberlorians.github.io/nistframework](https://cyberlorians.github.io/nistframework/)**

The dashboard lets you:
- **Browse** all 17 Level 1 controls grouped by family
- **Filter** by Microsoft product, Sentinel table, or compliance family
- **Copy** any KQL query with one click and paste it into Sentinel
- **Search** across 119 queries instantly
- **Contribute** — use the built-in YAML generator to create new mappings

Everything on the dashboard is auto-generated from YAML source files. Contributors only edit YAML — CI rebuilds everything else on merge.

## How It Works

```
practices/*.yaml            ← You edit these (source of truth)
       │
       │  CI on merge
       ▼
┌──────────────────────────────────────────────┐
│  validate.py   →  Schema gate (must pass)    │
│  build_html.py →  Interactive HTML dashboard │
│  build_csv.py  →  Alignment CSV              │
│  build_querypack.py → Query Pack JSON        │
└──────────────────────────────────────────────┘
       │
       ▼
  GitHub Pages  →  cyberlorians.github.io/nistframework
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

**119 KQL queries** across **11 Microsoft products** and **56+ Sentinel tables**.

## Project Structure

```
practices/                  # Source of truth — one YAML per NIST control
  3.1.1.yaml                #   Control metadata + KQL alignments
  _template.yaml             #   Start here when contributing
scripts/                    # Build & validation tooling
  validate.py               #   YAML schema validation (CI gate)
  build_html.py             #   YAML → interactive HTML dashboard
  build_csv.py              #   YAML → master alignment CSV
  build_querypack.py        #   YAML → Sentinel Query Pack JSON
  check_duplicates.py       #   Duplicate detection
ato/                        # ATO validation workbook
  ato_workbook.json          #   Sentinel workbook (74 table/data checks)
docs/                       # Auto-generated — never edit directly
  index.html                 #   Interactive dashboard (GitHub Pages)
  NIST_800-171_Alignment.csv #   Master CSV for auditors / watchlists
  NIST_800-171_QueryPack.json#   Importable Sentinel Query Pack
```

## How to Contribute

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide. The short version:

1. **Fork** this repo
2. **Copy** `practices/_template.yaml` to a new file (e.g. `3.x.x.yaml`)
3. **Fill in** control metadata and KQL queries
4. **Open a Pull Request** — CI validates automatically
5. **Maintainer reviews** and merges
6. **CI rebuilds** the dashboard and deploys to GitHub Pages

> You only edit YAML — the dashboard, CSV, and Query Pack are rebuilt automatically.

## Additional Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **ATO Workbook** | Import into Sentinel to verify your workspace has the required tables and data | [Available](ato/) |
| **Alignment CSV** | Upload as a Sentinel Watchlist or use with `externaldata()` | [Available](docs/NIST_800-171_Alignment.csv) |
| **Query Pack** | Deploy as ARM template to add all queries to your workspace | [Available](docs/NIST_800-171_QueryPack.json) |
| **Power BI Dashboard** | Visual compliance reporting | Planned |

## KQL Convention

Every query follows the **M-21-31 five-part structure**:

```kql
// Objective: What this query detects
// ----- Part 0: Analyst-Driven Targeting -----
let TargetUsers = dynamic([]);
// ----- Part 1: Base Filter -----
TableName | where TimeGenerated > ago(30d)
// ----- Part 2: Parse & Extend -----
| extend ...
// ----- Part 3: Enrich -----
| extend Description = case(...)
// ----- Part 4: Dynamic Filters -----
| where (array_length(TargetUsers) == 0 or UserPrincipalName in (TargetUsers))
// ----- Part 5: Final Output -----
| distinct ... | sort by TimeGenerated desc | take 50
```

## Roadmap

- [x] Level 1 — 17 NIST 800-171 controls (119 KQL queries)
- [x] Interactive HTML dashboard with GitHub Pages
- [x] ATO validation workbook (74 table/data checks)
- [ ] Level 2 — 110 NIST 800-171 controls
- [ ] Level 3 — 35 NIST 800-172 controls
- [ ] Power BI compliance dashboard
- [ ] Security Copilot promptbook
- [ ] Analytics Rule templates

## License

MIT
