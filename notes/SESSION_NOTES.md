# NIST 800-171 / CMMC 2.0 Framework — Session Notes
# Last Updated: 2026-02-25 (Session 2)
# Purpose: Continuity notes for agent handoff if session is lost.

---

## PROJECT OVERVIEW

**Repo:** github.com/Cyberlorians/nistframework
**Local:** C:\tools\nistframework
**Stack:** YAML practices → Python build scripts → CI/CD → GitHub Pages SPA

This project maps NIST 800-171 Rev.2 and NIST 800-172 controls to Microsoft Security products
with KQL queries for CMMC 2.0 compliance (Levels 1–3) and DFIR investigation. The architecture:

1. **GitHub Repo** (source of truth) — community CRUD via PRs
2. **CI/CD** (GitHub Actions) — validates YAML, builds CSV + Query Pack JSON + HTML SPA
3. **GitHub Pages** — hosts interactive HTML reference (`docs/index.html`)
4. **Sentinel MCP** — validate queries, check coverage (configured, see MCP section)
5. **Security Copilot** — natural language compliance investigation (FUTURE)

---

## WHAT'S BUILT (as of 2026-02-25)

### Practice Files (`practices/*.yaml`) — ALL 17 L1 CONTROLS COMPLETE (119 alignments)
| Practice | Description | Alignments | M2131 Layout? |
|----------|-------------|------------|---------------|
| 3.1.1 | Limit system access to authorized users | 12 | YES |
| 3.1.2 | Limit system access to authorized functions | 9 | YES |
| 3.1.20 | Verify and control external connections | 8 | YES |
| 3.1.22 | Control public information | 7 | YES |
| 3.5.1 | Identify system users | 7 | no |
| 3.5.2 | Authenticate identities | 8 | no |
| 3.8.3 | Sanitize or destroy media before disposal | 5 | no |
| 3.8.4 | Mark media with CUI markings | 5 | no |
| 3.10.1 | Limit physical access | 3 | no |
| 3.10.3 | Escort and monitor visitors | 4 | no |
| 3.10.4 | Maintain audit logs of physical access | 5 | no |
| 3.10.5 | Control and manage physical access devices | 6 | no |
| 3.13.1 | Monitor and protect communications at boundaries | 8 | no |
| 3.13.5 | Implement subnetworks for public components | 4 | no |
| 3.14.1 | Identify, report, and correct system flaws | 7 | no |
| 3.14.2 | Provide protection from malicious code | 11 | no |
| 3.14.5 | Perform scans and real-time protection | 7 | no |

**6 NIST Families covered:** Access Control, Identification & Authentication,
Media Protection, Physical Protection, System & Communications Protection,
System & Information Integrity

### Scripts (`/scripts/`)
| Script | Purpose |
|--------|---------|
| `validate.py` | Schema validation for practice YAMLs. Skips `_`-prefixed files. REQUIRED_ALIGNMENT_KEYS = {product, workload, table, kql} |
| `build_csv.py` | Combines all YAML → `output/NIST_800-171_Alignment.csv` (119 rows, 11 columns) |
| `build_querypack.py` | Combines all YAML → `output/NIST_800-171_QueryPack.json` |
| `build_html.py` | **~1230 lines.** Generates self-contained interactive HTML SPA from practice YAMLs. THREE TABS: Browse, Validate, Contribute. Deployed via GitHub Pages. |

### CSV Columns (in order)
NIST 800-171, NIST 800-53, Family, Control Name, Function, Category, Workload,
Table, Workload Integration, Event Reference, KQL

### CI/CD (`/.github/workflows/`)
| Workflow | Trigger | Steps |
|----------|---------|-------|
| `validate.yml` | PR to main | `validate.py` + `check_duplicates.py` |
| `build.yml` | Push to main | `build_csv.py` → `build_querypack.py` → `build_html.py` → Deploy to GitHub Pages via `actions/deploy-pages@v4` |

**NOTE:** GitHub Pages must be manually enabled in repo Settings → Pages → Source: GitHub Actions.

### Community Scaffolding
- `README.md` — Full project overview, badge, coverage table, usage, contributing
- `CONTRIBUTING.md` — How to contribute, YAML schema, naming, rules
- `practices/_template.yaml` — Starter YAML (skipped by validate.py due to `_` prefix)
- `.github/ISSUE_TEMPLATE/suggest-alignment.md` — For non-git users to propose mappings
- `.github/ISSUE_TEMPLATE/fix-kql.md` — For reporting KQL bugs
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist

### HTML SPA (`output/index.html`) — 3 TABS

**Tab 1: Browse** — Interactive reference of all 119 KQL alignments
- Filter by family dropdown + free-text search
- Collapsible cards per practice
- Single-pass KQL syntax highlighter (keywords, strings, operators, comments)
- Copy-to-clipboard buttons per query
- Dark theme (#0d1117 surface)

**Tab 2: Validate** — Closed-loop tenant validation (THE BIG FEATURE)
- Step 1: Lists unique tables from framework → generates KQL to paste into Sentinel
- Step 2: User runs KQL in Sentinel, gets CSV with TableName + Status
- Step 3: User pastes CSV back (textarea paste or file upload button)
- Step 4: Dashboard renders with score ring, family bars, practice table, exports

**3-STATE VALIDATION MODEL (implemented 2026-02-24):**
| State | Meaning | Color | Covered? |
|-------|---------|-------|----------|
| Active | Table exists AND has data in last 30 days | Green | YES |
| Configured | Table exists but no recent data | Orange | YES |
| Not Found | Table doesn't exist in workspace | Red | NO |

Coverage = Active + Configured. Only "Not Found" is a gap.

KQL uses `getschema` to detect table existence (even without data), then
`TimeGenerated > ago(30d)` to check for recent data, then `case()` to produce status.

Dashboard includes:
- **Legend box** at top explaining Active/Configured/Not Found in plain English (5th-grade level)
- **Coverage formula explanation**: "Active + Configured = Covered. Only Not Found counts as a gap."
- Score ring (% covered = active + configured / total)
- **Plain-English score message** under ring (contextual: "Great coverage!", "Decent coverage", "Low coverage" based on %)
- Family bars (stacked green + orange segments with color legend)
- Practice-level table with colored dot headers (Control, Name, Family, Status, Active, Configured, Not Found)
- Practice-level subtitle explaining what "Covered" means
- "Tables Not Found" section (red, actionable: "enable the matching data connector")
- "Configured Tables" section (orange, informational: "connector is set up, validate data flow")
- Export: Power BI M query (.m file), Coverage CSV, Print Report (new window)

**PRACTICE STATUS LOGIC (updated 2026-02-25):**
- **Covered** (green) = at least ONE table is Active or Configured. Even if some
  tables are Not Found, the practice is covered because you have detection sources.
- **No Coverage** (red) = ALL tables are Not Found. No detection capability at all.
- There is NO "Partial" state. User feedback: partial implies failure when you
  actually have coverage. If any table works, you're covered.

**LAYOUT (updated 2026-02-25):**
- Content is left-aligned (not centered), max-width 1400px
- Practice table uses `table-layout: fixed` with explicit column widths:
  Control 7%, Name 12%, Family 10%, Status 8%, Active 25%, Configured 19%, Not Found 19%
- `word-break: break-word` on table cells so long table names wrap instead of truncating

**Tab 3: Contribute** — Community contribution form
- Form fields: NIST practice, product, workload, table, KQL, etc.
- Live YAML preview (updates as user types)
- "Open GitHub Issue" button (pre-populates suggest-alignment template)
- "Copy YAML" button
- "Edit on GitHub" link

### ATO Folder (`/ato/`)
- Contains ATO Logging Validation workbook (separate concern, may be moved out)

---

## KQL CONVENTION (CRITICAL — MAINTAIN THIS)

Every KQL query MUST follow this 5-part pattern (matches M-21-31 style):

```
// Part 0: Analyst-Driven Targeting
let TargetX = dynamic(["*"]);    // ["*"] = GRC full-scope, specific values = DFIR

// Part 1: Base Filter
TableName
| where TimeGenerated > ago(30d)
| where TargetX has "*" or ColumnName in (TargetX)

// Part 2: Enrichment (extend, parse_json, summarize — optional)

// Part 3: Final Output
| project RelevantColumns
| sort by TimeGenerated desc
| take 50
```

- `dynamic(["*"])` with `array_length() == 0` or `has "*"` pattern for wildcard
- GPO path comments where applicable

---

## MCP SERVERS CONFIGURED

File: `C:\Users\michaelcrane\AppData\Roaming\Code\User\mcp.json`

| Name | Type | URL/Command |
|------|------|-------------|
| Microsoft Enterprise | http | https://mcp.svc.cloud.microsoft/enterprise |
| microsoft-learn | http | https://learn.microsoft.com/api/mcp |
| sentinel-data-exploration | http | https://sentinel.microsoft.com/mcp/data-exploration |
| sentinel-agent-creation | http | https://sentinel.microsoft.com/mcp/security-copilot-agent-creation |
| sentinel-triage | http | https://sentinel.microsoft.com/mcp/triage |
| EnterpriseMCP | http | https://mcp.svc.cloud.microsoft/enterprise |
| Azure Diagram MCP Server | stdio | python -m azure_diagram_mcp_server.server (cwd: C:\tools\azure-diagram-mcp) |
| cyberlorian mcp | http | https://sentinel.microsoft.com/mcp/data-exploration |

---

## KEY DECISIONS MADE
- No workbook for NIST (ATO workbook is separate)
- No CMMC column: NIST 800-171 is the universal language
- YAML per practice (not one big CSV): granular PRs, clean diffs, schema validation
- Every KQL has targeting: supports both GRC and DFIR use cases
- CI rebuilds output on merge: contributors never touch CSV/HTML directly
- Issue templates for non-git users: lowers the barrier to contribute
- 3-state validation: table existence = configured/covered even without data
- `_`-prefixed files skipped by all build/validate scripts
- `String.fromCharCode(96)` used for backtick-in-f-string JS template literals

---

## KNOWN ISSUES / TODO (as of 2026-02-25)

### Verified: 3-State KQL Works
The CSV output from the 3-state KQL was tested against all 17 practice YAMLs on
2026-02-25 using the user's actual Sentinel workspace data (52 tables: 39 Active,
11 Configured, 2 Not Found). Results:
- All 52 YAML tables accounted for in CSV (no missing, no extras)
- NistControls column in CSV matches YAML mappings exactly
- 96% coverage (50/52 tables), 17/17 practices = Covered
- Only 2 Not Found: DLPActionEvents, InformationProtectionEvents_CL (both Purview)
- `getschema` approach confirmed working for table existence detection

### Power BI Export — DONE
CSV export with 11 columns, .pbip project with 10 visuals, 3 DAX measures,
slicers, dual-score model (Technical Coverage vs Compliance Score), and manual
compliance override support. See `powerbi/README.md` for full documentation.

### Remaining Work
2. **13 practices not yet rebuilt with M2131 layout** — Only 4 AC practices (3.1.1,
   3.1.2, 3.1.20, 3.1.22) use the full M-21-31 KQL convention with `dynamic(["*"])`
   targeting. The other 13 still use the original simpler format. These still validate
   and build correctly but don't have the analyst-targeting pattern.
3. **GitHub Pages manual enable** — User needs to go to repo Settings → Pages →
   Source: GitHub Actions. Without this, the build.yml deploy step will fail.
4. **Level 2 expansion** — 110 additional NIST 800-171 controls (use MCP to scale)
5. **Level 3 expansion** — 35 NIST 800-172 controls
6. **Security Copilot promptbook** — For natural-language compliance queries
7. **Analytics Rule templates** — For detection-worthy queries
8. **Move ATO workbook** — `/ato/` folder may belong in a separate repo
9. **Sentinel MCP integration** — Use MCP to validate KQL queries against live workspace

---

## M-21-31 REFERENCE

The M-21-31 project (separate from this repo) is at:
- Master CSV: `C:\tools\M2131v0.2.0.csv` (154 rows)
- KQL files: `C:\tools\Identity\` (67 files)
- Convention used as template for the 4 rebuilt AC practices

---

## FILE STRUCTURE
```
C:\tools\nistframework\
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── suggest-alignment.md
│   │   └── fix-kql.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── validate.yml    (PR gate)
│       └── build.yml       (merge → build → Pages deploy)
├── ato/                    (ATO workbook — separate concern)
├── notes/
│   └── SESSION_NOTES.md    (this file)
├── output/
│   ├── index.html          (generated SPA)
│   ├── NIST_800-171_Alignment.csv
│   └── NIST_800-171_QueryPack.json
├── practices/
│   ├── _template.yaml      (skipped by scripts)
│   ├── 3.1.1.yaml
│   ├── ... (17 practice files)
│   └── 3.14.5.yaml
├── scripts/
│   ├── validate.py
│   ├── check_duplicates.py
│   ├── build_csv.py
│   ├── build_querypack.py
│   └── build_html.py       (~1200 lines, generates the SPA)
├── CONTRIBUTING.md
└── README.md
```

---

## CSS THEME VARS (for build_html.py reference)
```
--bg: #0d1117
--surface: #161b22
--accent: #58a6ff
--green: #3fb950
--orange: #d29922
--red: #f85149
--purple: #bc8cff
--text: #e6edf3
--text-muted: #8b949e
--border: #30363d
```

---

## CHANGES LOG (2026-02-25 session)

1. **Removed "Partial" status** — Practice status is now binary: Covered (any table
   active/configured) or No Coverage (all tables not found). User feedback: "partial"
   implies failure when you actually have detection coverage.
2. **Added legend box** — Plain-English explanation of Active/Configured/Not Found
   with colored indicators, plus coverage formula explanation.
3. **Added plain-English score message** — Contextual text under the score ring
   based on coverage percentage.
4. **Added practice table subtitle** — Explains what "Covered" means at a glance.
5. **Colored column headers** — Active/Configured/Not Found headers have matching
   colored dot indicators.
6. **Improved bottom sections** — "Tables Not Found" and "Configured Tables" have
   clearer actionable language and emoji indicators.
7. **Fixed column widths** — Practice table uses `table-layout: fixed` with explicit
   percentages so red/orange columns don't get truncated.
8. **Left-aligned layout** — Content starts from left edge instead of centering.
   Max-width 1400px preserved to prevent full-page stretch.
9. **Tested real CSV** — Ran user's actual Sentinel output (52 tables) through
   Python test script verifying all 17 practices map correctly.
10. **Power BI M query export** — Discussed replacing with Power BI-ready CSV.
    Decision pending.

### Power BI Dashboard (2026-02-25)
11. **CSV export replaces M query** — Export button now produces a denormalized CSV
    (one row per practice-table) instead of an M query .m file. Renamed button from
    "Export Power BI (M Query)" to "Export Power BI CSV".
12. **powerbi/ folder created** — Contains sample CSV, README, and .pbip project.
13. **.pbip project** — Full Power BI Project (editable JSON/TMDL, not binary .pbix).
    Schema versions: visual 2.0.0, report 3.2.0, page 2.1.0. Compatible with PBI 2.152+.
14. **10 visuals**: Title, Technical Coverage % card, Compliance Score % card,
    Manual Overrides card, Active card, Configured card, Family slicer, TableStatus
    slicer, per-practice stacked bar chart, detail table with full columns.
15. **3 DAX measures**: Technical Coverage %, Compliance Score %, Manual Overrides.
16. **11-column CSV schema**: Added `Compliant` (int, defaults = Covered) and
    `ComplianceNote` (text, defaults empty). Users edit CSV to override compliance.
17. **Dual-score model**: Technical Coverage (KQL-only, can't override) vs
    Compliance Score (includes manual overrides). Overrides card shows count of
    practices marked compliant without KQL coverage.
18. **Slicers**: Family and TableStatus slicers act as cross-filters for all visuals.

---

## PREVIOUS FILES (can be cleaned up)
- C:\tools\CMMC_L1_NIST171.csv — Original CSV with CMMC column (superseded)
- C:\tools\NIST_800-171_L1.csv — Cleaned CSV without CMMC column (superseded)

---

## CMMC 2.0 EXPANSION (Session 2 — 2026-02-25)

### What Changed
Expanded dashboard from 17 L1-only practices to **full CMMC 2.0 Levels 1–3 (134 practices)**
using authoritative sources: NIST SP 800-171 R2, NIST SP 800-172, and 32 CFR § 170.14.

### Practice Counts (Official DoD CIO / 32 CFR)
| Level | Count | Source | Data Classification |
|-------|-------|--------|---------------------|
| Level 1 | 15 practices | FAR 52.204-21 §(b)(1)(i)-(xv) | FCI |
| Level 2 | 110 cumulative (15 L1 + 95 L2-only) | All NIST SP 800-171 R2 controls | CUI |
| Level 3 | 134 cumulative (110 L2 + 24 L3-only) | 32 CFR § 170.14(c)(4) Table 1 selects from NIST SP 800-172 | CUI+ |

**14 families:** AC(24), AT(5), AU(9), CA(5), CM(12), IA(13), IR(5), MA(6), MP(9), PE(6), PS(3), RA(10), SC(17), SI(10)

### New Files
| File | Purpose |
|------|---------|
| `scripts/build_cmmc_data.py` | Authoritative data generator — hardcoded correct 134 practices from NIST/32 CFR |
| `cmmc_data.json` | Generated practice data (134 records) consumed by `build_html.py` |

### Level Filter (Cumulative)
The level dropdown is **cumulative** to match CMMC certification model:
- Level 1 → shows 15 practices (L1 only)
- Level 2 → shows 110 practices (L1 + L2) — because L2 certification requires L1
- Level 3 → shows 134 practices (all) — L3 requires L1 + L2 + L3
Filter logic: `p.level <= parseInt(level)` (not `===`)

### Removed
- CISA ZTMM mappings (removed from dashboard)
- DoD Zero Trust mappings (removed from dashboard)

### Dashboard UX Enhancements
1. **Title** → "CMMC 2.0 Compliance Dashboard" with CMMC shield SVG icon
2. **Subtitle** → references NIST SP 800-171 R2 & 800-172, includes build timestamp
3. **Header reference links** → DoD CIO CMMC, NIST SP 800-171 R2, NIST SP 800-172, 32 CFR § 170.14
4. **Family dropdown** → "AC — Access Control (24)" format with counts
5. **Level dropdown** → "Level 2 (110) — CUI" with data classification context
6. **Coverage filter** → All / With KQL / Without KQL
7. **Sticky filter bar** → stays visible when scrolling
8. **Expand All / Collapse All** buttons
9. **Coverage percentage** in stats bar
10. **Keyboard shortcut** → `/` to focus search, Escape to blur
11. **Control names spelled out** → Each practice card shows:
    - Top row: chevron + `AC.L1-3.1.1` (monospace, blue accent) + pills (L1, AC, query count)
    - Second row: full control name with blue left border accent, full width (no truncation)
12. **Build timestamp** → faint "build YYYY-MM-DD HH:MM UTC" in subtitle

### Practice Card Layout (Current)
```
┌──────────────────────────────────────────────────┐
│ ▶  AC.L1-3.1.1                    [L1] [AC] [13] │
│    │ Limit system access to authorized users,     │
│    │ processes acting on behalf of authorized      │
│    │ users, and devices (including other systems)  │
└──────────────────────────────────────────────────┘
```
- Top row: `.practice-top-row` — flex with chevron, `.control-id`, `.practice-pills` (margin-left: auto)
- Second row: `.control-name` — full width, with `border-left: 2px solid rgba(88,166,255,0.3)` accent

### CI/CD Fix
- **Race condition**: Pushing two commits quickly caused CI `git push` to fail (remote moved ahead)
- **Fix**: Added `git pull --rebase origin main || true` before `git push` in `build.yml`
- **Path filter**: Workflow only triggers on `practices/*.yaml` or `scripts/**` changes

### Key Git Commits (Session 2)
| Hash | Description |
|------|-------------|
| 2c13694 | fix: remove CISA ZTMM and DoD Zero Trust mappings |
| 387f5a1 | fix: correct CMMC 2.0 practice counts to 134 (15/110/24) |
| 896ee32 | fix: make Level filter cumulative |
| d2f9df4 | feat: UX enhancements (title, filters, keyboard shortcuts) |
| 349f951 | feat: spell out control names, add reference links |
| f52fc03 | fix: make control name visually prominent |
| 0fb83ac | fix: add build timestamp, accent border for control names |
| 881dcb4 | chore: remove debug files |
| 26f4de6 | fix: CI race condition (git pull --rebase) |

### File Structure (Updated)
```
C:\tools\nistframework\
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── suggest-alignment.md
│   │   └── fix-kql.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── validate.yml    (PR gate)
│       └── build.yml       (merge → build → Pages deploy, with rebase fix)
├── ato/                    (ATO workbook — separate concern)
├── cmmc_data.json          (134 CMMC practices — generated by build_cmmc_data.py)
├── cmmc_ref.md             (CMMC reference — partially outdated, data in cmmc_data.json is authoritative)
├── notes/
│   └── SESSION_NOTES.md    (this file)
├── docs/
│   ├── index.html          (generated SPA — CMMC 2.0 dashboard)
│   ├── NIST_800-171_Alignment.csv
│   └── NIST_800-171_QueryPack.json
├── practices/
│   ├── _template.yaml      (skipped by scripts)
│   └── ... (17 practice YAML files with 119 KQL queries)
├── powerbi/                (Power BI export templates)
├── scripts/
│   ├── validate.py
│   ├── check_duplicates.py
│   ├── build_csv.py
│   ├── build_querypack.py
│   ├── build_cmmc_data.py  (NEW — authoritative CMMC data generator)
│   └── build_html.py       (~1576 lines, generates the CMMC 2.0 SPA)
├── CONTRIBUTING.md
└── README.md
```

### Remaining Work (Updated)
1. **KQL for L2/L3 practices** — Only 17 of 134 practices have KQL queries (13% coverage). Need to add queries for the remaining 117 practices.
2. **Verify NIST 800-171 R2 control names** — Names were hardcoded from build_cmmc_data.py. Official NIST CSV download returned empty. Should verify against NIST SP 800-171 R2 PDF or official XLSX.
3. **M-21-31 layout for remaining practices** — Only 4 AC practices use the full M-21-31 KQL convention.
4. **Security Copilot promptbook** — For natural-language compliance queries.
5. **Analytics Rule templates** — For detection-worthy queries.
