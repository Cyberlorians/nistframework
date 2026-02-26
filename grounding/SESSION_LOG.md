# NIST Framework Project — Session Log & Continuation Notes

> **Purpose**: When a session goes stale, tell the AI to read this file first. It contains everything needed to pick up where we left off.

---

## Project Overview

**Repo**: `github.com/Cyberlorians/nistframework` (local: `C:\tools\nistframework`)
**What it does**: Self-contained CMMC 2.0 HTML dashboard with KQL detection queries mapped to NIST 800-171 practices, filterable by level, family, workload, table, and coverage status.
**Build pipeline**: `scripts/build_cmmc_data.py` → `cmmc_data.json` → `scripts/build_html.py` → `docs/index.html`
**CI/CD**: `.github/workflows/build.yml` — triggers on `scripts/**` or `practices/*.yaml`, deploys via GitHub Pages

---

## Current State (as of 2026-02-25)

### Dashboard Stats
- **134 total practices**: 17 L1 (FAR 52.204-21) + 93 L2 (NIST 800-171 R2) + 24 L3 (NIST 800-172)
- **107 KQL queries** (all in L1 YAML files currently)
- **25 Log Tables** (M2131 authoritative)
- **8 Workloads** (M2131 authoritative)

### What's Been Done
1. **Dashboard UI**: Dark theme, Browse/Validate/Contribute tabs, KQL syntax highlighting, cumulative level filter, reference links, control names on cards
2. **Control ID format**: `Access Control 3.1.1` (family spelled out, no dot after family code, no level prefix)
3. **NIST 800-53 pills removed** from practice cards (AC-2, AC-3 etc. were confusing)
4. **Dynamic arrays cleaned**: All 64 pre-populated dynamic arrays across 17 YAML files changed to `dynamic([])` with `// e.g., [...]` comments and `array_length` guards
5. **M2131 workloads/tables hardcoded**: `M2131_WORKLOAD_TABLES` dict in `scripts/build_html.py` (lines 42-58) is the authoritative source for workload/table filter dropdowns
6. **L2/L3 alignments stripped**: `practices/3.8.4.yaml` and `practices/3.14.5.yaml` trimmed to headers only (the only L2/L3 files that had alignments)
7. **cmmc-compliance-ai-model repo cloned** to `grounding/cmmc-compliance-ai-model/` for CMMC v2 reference data

### Git State
- All changes committed and pushed to `main`
- Latest commit includes M2131 workload/table hardcoding and L2/L3 alignment stripping

---

## What's Next — L1 Alignment Cleanup (Family by Family)

### The Problem
L1 still has 107 alignments across 15 practices, but many use:
- **Non-M2131 workload names** (descriptive names like "AV Detections", "Conditional Access" instead of M2131 names like "Microsoft Defender for Endpoint", "Entra")
- **Non-M2131 tables** (some tables not in the M2131 authoritative set)

### The Plan
User wants to go through each L1 control family together to build proper mappings using M2131 as the source of truth, then potentially expand beyond M2131 using Sentinel MCP and Microsoft Learn MCP.

### L1 Control Families to Clean
| Family | Practices | Notes |
|--------|-----------|-------|
| **AC** (Access Control) | 3.1.1, 3.1.2, 3.1.20, 3.1.22 | Largest family |
| **IA** (Identification & Authentication) | 3.5.1, 3.5.2 | |
| **MP** (Media Protection) | 3.8.3 | |
| **PE** (Physical Protection) | 3.10.1, 3.10.3, 3.10.4, 3.10.5 | May have limited KQL applicability |
| **SC** (System & Comms Protection) | 3.13.1, 3.13.5 | |
| **SI** (System & Info Integrity) | 3.14.1, 3.14.2, 3.14.4, 3.14.5 | 3.14.4/3.14.5 added per § 170.15(c)(1)(ii) FAR b.1.xiv/xv |

### M2131 Authoritative Workload-Table Mapping
These are the ONLY valid workload-table pairs (from `grounding/m2131/M2131v0.2.0.csv`):

| Workload | Tables |
|----------|--------|
| **Entra** | AADManagedIdentitySignInLogs, AADNonInteractiveUserSignInLogs, AADProvisioningLogs, AADRiskyServicePrincipals, AADRiskyUsers, AADServicePrincipalRiskEvents, AADServicePrincipalSignInLogs, AADUserRiskEvents, ADFSSignInLogs, AuditLogs, IdentityInfo, ManagedIdentitySigninlogs, MicrosoftGraphActivityLogs, SigninLogs |
| **Azure** | AzureActivity, AzureDiagnostics |
| **Windows** | Event, SecurityEvent |
| **Microsoft Defender for Endpoint** | DeviceEvents |
| **Microsoft Defender for Identity** | IdentityDirectoryEvents, IdentityLogonEvents |
| **Microsoft Defender for Cloud Apps** | CloudAppEvents |
| **Microsoft Intune** | IntuneAuditLogs |
| **Sentinel** | BehaviorAnalytics, IdentityInfo, UserPeerAnalytics |

**25 unique tables, 26 workload-table pairs** (IdentityInfo appears under both Entra and Sentinel)

---

## Grounding Data Inventory

### `grounding/m2131/`
- `M2131v0.2.0.csv` — M-21-31 compliance mapping, 154 rows, 8 workloads, 26 workload-table pairs. Source of truth for workloads and Sentinel log tables.

### `grounding/cmmc-compliance-ai-model/`
Cloned from `github.com/NathanMaine/cmmc-compliance-ai-model` — A fine-tuned LLM suite for CMMC compliance (not the LLM itself, but valuable reference data).

**Key takeaways for our project:**

#### CMMC v2.0 Regulatory Updates (from their README)
| Update | Date | Significance |
|--------|------|-------------|
| NIST SP 800-171 Rev. 3 | May 2024 | **Replaces Rev. 2**. Consolidated from 110 to 97 controls. Adds 88 ODPs and 509 assessment objectives. New CMMC Level 2 foundation. |
| NIST CSF 2.0 | Feb 2024 | Adds GOVERN function (6 functions total). 34 categories, 174 subcategories. |
| CMMC Final Rule (32 CFR 170) | Dec 2024 | Actual regulation establishing the CMMC program. |
| DFARS 252.204-7021 | Nov 2025 | Acquisition rule requiring CMMC cert in DoD contracts. Phase-in timeline. |
| NIST SP 800-172 Rev. 3 | 2025 (FPD) | Enhanced CUI requirements (Level 3 delta). |
| DoD Assessment Guides | 2025 | Official L2/L3 assessment procedures, scoping guides, ODP values. |

#### Important: NIST 800-171 Rev 3 — NOT YET ADOPTED BY CMMC
- Rev 3 consolidated from 110 to 97 controls, but **32 CFR § 170.1(c) explicitly mandates Rev 2**
- Our dashboard correctly uses Rev. 2 (110 controls, 3.x.x format)
- Rev. 3 adoption would require a new rulemaking — no action needed now
- Verified 2026-02-25 against authoritative eCFR text
- The cmmc-compliance-ai-model was trained on BOTH Rev. 2 and Rev. 3

#### Framework Cross-Reference
The repo demonstrates mapping chains: CMMC → NIST 800-171 → NIST 800-53 → HIPAA. This is valuable for our future work expanding beyond M2131.

#### Authoritative Sources for Future Expansion
| Source | URL | Notes |
|--------|-----|-------|
| CMMC Assessment Guide L2 | dodcio.defense.gov/Portals/0/Documents/CMMC/AGLevel2.pdf | Official assessment procedures |
| CMMC Scoping Guide L2 | dodcio.defense.gov/Portals/0/Documents/CMMC/ScopingGuideLevel2.pdf | What's in/out of scope |
| CMMC ODP Values | dodcio.defense.gov/Portals/0/Documents/CMMC/ODPValues.pdf | Organization-defined parameters |
| NIST SP 800-171 R3 OSCAL | github.com/usnistgov/oscal-content | Machine-readable control catalog |
| NIST SP 800-53 R5 OSCAL | github.com/usnistgov/oscal-content | Full control catalog |
| 32 CFR Part 170 (CMMC Rule) | ecfr.gov/current/title-32/.../part-170 | The actual regulation |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `scripts/build_cmmc_data.py` | Generates `cmmc_data.json` from YAML practices. Contains `L1_CONTROLS` set (15 practice IDs). |
| `scripts/build_html.py` | Main build script (~1590 lines). Generates self-contained HTML dashboard. Contains `M2131_WORKLOAD_TABLES` dict (lines 42-58). |
| `practices/*.yaml` | YAML files per NIST 800-171 control with alignments (workload, table, KQL query). 17 files have KQL queries. |
| `docs/index.html` | Generated dashboard output. DO NOT edit directly — rebuild via `python scripts/build_html.py`. |
| `.github/workflows/build.yml` | CI/CD pipeline. Triggers on scripts/ or practices/*.yaml changes. |
| `grounding/SESSION_LOG.md` | THIS FILE — read first when resuming. |
| `grounding/m2131/M2131v0.2.0.csv` | M2131 source of truth for workloads and tables. |
| `grounding/cmmc-compliance-ai-model/` | Cloned reference repo for CMMC v2 updates and framework data. |

---

## Build & Deploy Commands

```powershell
cd C:\tools\nistframework

# Rebuild dashboard
python scripts/build_html.py

# Commit and push
git add -A
git commit -m "description"
git pull origin main --rebase
git push origin main
```

---

## User Preferences & Communication Style
- **Direct and impatient** — wants incremental progress, not long explanations
- **Prefers "take it slow"** approach — work through changes family by family
- **M2131 is source of truth** for workloads and tables
- **Wants to expand beyond M2131** using Sentinel MCP and Microsoft Learn MCP tools (after L1 cleanup)
- **Dynamic arrays should be empty** — `dynamic([])` with example comments, so analysts control filtering
- **No NIST 800-53 pills** on practice cards
- **Control ID format**: `Family Name X.X.X` (e.g., `Access Control 3.1.1`)

---

## Resume Instructions

When this session expires and user says to review notes:
1. Read this file (`grounding/SESSION_LOG.md`)
2. Check git log for any commits since this log was written: `git log --oneline -10`
3. Check current dashboard stats: `python scripts/build_html.py` output
4. Ask user which L1 family they want to work on next
5. For each family: review the YAML files, audit workload/table names against M2131, propose corrections
