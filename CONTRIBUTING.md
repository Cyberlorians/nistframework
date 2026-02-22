# Contributing to NIST 800-171 Alignment Framework

Thanks for helping map NIST 800-171 controls to Microsoft Security. Every contribution makes the framework more complete.

## Quick Start

1. **Fork** this repository
2. **Edit** a practice file under `practices/` or create a new one
3. **Open a Pull Request** against `main`
4. CI runs validation automatically
5. A maintainer reviews and merges

## Practice File Format

Each file is named `{control_number}.yaml` (e.g., `3.1.1.yaml`):

```yaml
control: "3.1.1"
name: "Limit system access to authorized users"
family: "Access Control"

alignments:
  - product: "Entra ID"          # Microsoft product name
    workload: "Identity"          # Functional area within the product
    table: "SigninLogs"           # Sentinel/MDE table name
    kql: |                        # Full KQL query with targeting
      // NIST 3.1.1 - Description
      // Part 0: Analyst-Driven Targeting
      let TargetUsers = dynamic(["*"]);
      let LookbackDays = 30;
      // Part 1: Base Filter
      SigninLogs
      | where TimeGenerated > ago(LookbackDays * 1d)
      // Part 2: Enrichment (optional)
      | extend ...
      // Final Output
      | project ...
      | sort by TimeGenerated desc
      | take 50
```

## KQL Requirements

**Every KQL query MUST include:**

1. **Part 0: Analyst-Driven Targeting** — Dynamic variables for scoping
   - Use `let TargetUsers = dynamic(["*"]);` pattern
   - `["*"]` = full scope (GRC), specific values = scoped (DFIR)
   - Always include `let LookbackDays = ...;`

2. **Part 1: Base Filter** — Table name + time range + target filtering

3. **Part 2: Enrichment** (optional) — `extend`, `parse_json`, `summarize`

4. **Final Output** — `project` + `sort` + `take 50`

## What You Can Contribute

### Add a new alignment to an existing control
Add a new `- product: ...` block to an existing practice file. Great for adding coverage from products not yet mapped.

### Improve a KQL query
Fix a query, add better enrichment, improve targeting variables, add comment documentation.

### Create a new control file
For Level 2/3 expansion. File must be named `{control_number}.yaml` and follow the schema.

### Fix metadata
Correct control names, family names, product names, table names.

## Validation Rules

CI automatically checks:

- ✅ Valid YAML syntax
- ✅ Required top-level keys: `control`, `name`, `family`, `alignments`
- ✅ Required alignment keys: `product`, `workload`, `table`, `kql`
- ✅ Control number matches filename
- ✅ Family name is valid
- ✅ KQL contains Part 0 targeting
- ✅ No duplicate product+workload+table combos within a control

## Naming Conventions

### Product Names
Use the full official name:
- `Entra ID` (not Azure AD)
- `Microsoft Defender for Endpoint` (not MDE)
- `Microsoft Defender for Office 365` (not MDO)
- `Microsoft Defender for Cloud Apps` (not MCAS/MDCA)
- `Microsoft Defender for Identity` (not MDI)
- `Microsoft Defender for Cloud` (not ASC)
- `Microsoft Purview` (not MIP)
- `Microsoft Intune` (not MEM)
- `Microsoft Sentinel` (not Azure Sentinel)

### Table Names
Use the exact Sentinel/MDE table name as it appears in the schema (case-sensitive):
- `SigninLogs` not `signinlogs`
- `DeviceEvents` not `deviceevents`

## Don't Know Git/YAML?

No problem — use the **Issue Templates** to suggest an alignment. A maintainer will convert it to a PR for you.

## Code of Conduct

Be respectful. Focus on facts. Cite sources when possible (MS docs, KQL reference, etc.). This is a security community project.
