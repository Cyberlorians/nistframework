# Contributing to NIST 800-171 Alignment Framework

Thank you for contributing! This project maps NIST 800-171 controls to Microsoft Security KQL queries, and every contribution makes the community's compliance posture stronger.

## The Golden Rule

> **You only edit YAML files** — the CSV, Query Pack, and HTML reference page are rebuilt automatically by CI on merge.

---

## Ways to Contribute

| What | How |
|------|-----|
| **Add a new KQL mapping** to an existing control | Edit the practice YAML, add an alignment block |
| **Fix a KQL query** (schema change, bug, improvement) | Edit the existing alignment in the YAML |
| **Propose a new control** (Level 2 expansion) | Create a new YAML file from the template |
| **Don't know Git?** | [Open an issue](https://github.com/Cyberlorians/nistframework/issues/new/choose) — a maintainer will convert it to a PR |

---

## Step-by-Step

### 1. Fork & Clone

```bash
git clone https://github.com/<your-fork>/nistframework.git
cd nistframework
```

### 2. Find or Create the Practice YAML

Each NIST control has one file in `practices/`:

```
practices/3.1.1.yaml    ← Control 3.1.1
practices/3.14.2.yaml   ← Control 3.14.2
```

**New control?** Copy the template:

```bash
cp practices/_template.yaml practices/3.X.X.yaml
```

### 3. Edit the YAML

```yaml
control: "3.1.1"
name: "Limit system access to authorized users"
family: "Access Control"
nist_800_53: "AC-2, AC-3, AC-17"

alignments:
  - product: "Entra ID"
    function: "Identity"
    category: "Identity & Credential Management"
    workload: "Entra"
    table: "SigninLogs"
    workload_integration: "https://learn.microsoft.com/..."
    event_reference: "https://learn.microsoft.com/..."
    kql: |
      // Objective: What this query detects
      //
      // ----- Part 0: Analyst-Driven Targeting (Optional) -----
      let TargetUsers = dynamic([]);
      //
      // ----- Part 1: Base Filter -----
      SigninLogs
      | where TimeGenerated > ago(30d)
      //
      // ----- Part 2: Parse -----
      | extend ...
      //
      // ----- Part 3: Enrich -----
      | extend Description = case(...)
      //
      // ----- Part 4: Apply Dynamic Filters -----
      | where (array_length(TargetUsers) == 0 or UserPrincipalName in (TargetUsers))
      //
      // ----- Part 5: Final Output -----
      | distinct ...
      | sort by TimeGenerated desc
      | take 50
```

### 4. KQL Conventions

| Rule | Details |
|------|---------|
| **Targeting** | Use `dynamic([])` with `array_length() == 0` checks — empty = all results |
| **Time window** | `ago(30d)` default |
| **Structure** | Five-part: Objective → Part 0 → Part 1–3 → Part 4 filters → Part 5 output |
| **Dedup** | End with `| distinct` |
| **GPO paths** | SecurityEvent queries must include GPO audit path as a comment |
| **No hardcoding** | Use `let` variables for anything a user might change |
| **Tested** | Run KQL in Sentinel or MDE Advanced Hunting before submitting |

### 5. Validate Locally

```bash
pip install pyyaml
python scripts/validate.py
```

### 6. Open a Pull Request

```bash
git checkout -b add-signinlogs-alignment
git add practices/3.X.X.yaml
git commit -m "feat: add SigninLogs alignment for 3.X.X"
git push origin add-signinlogs-alignment
```

CI will validate your YAML automatically. A maintainer reviews and merges — then CI rebuilds the CSV, Query Pack, and HTML page.

---

## Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `product` | **Yes** | Microsoft product name (e.g., "Entra ID") |
| `workload` | **Yes** | Workload name (e.g., "Entra") |
| `table` | **Yes** | Sentinel/MDE table (e.g., "SigninLogs") |
| `kql` | **Yes** | The KQL query |
| `function` | Recommended | M-21-31 function (e.g., "Identity", "Device") |
| `category` | Recommended | Functional category |
| `workload_integration` | Recommended | URL to integration docs |
| `event_reference` | Recommended | URL to event schema docs |

## Product Names

Use official names:
- `Entra ID` (not Azure AD)
- `Microsoft Defender for Endpoint` (not MDE)
- `Microsoft Defender for Identity` (not MDI)
- `Microsoft Defender for Office 365` (not MDO)
- `Microsoft Defender for Cloud Apps` (not MDCA)
- `Microsoft Defender for Cloud` (not ASC)
- `Microsoft Purview` (not MIP)
- `Microsoft Intune` (not MEM)
- `Microsoft Sentinel` (not Azure Sentinel)

## Table Names

Use exact Sentinel schema casing: `SigninLogs`, `DeviceEvents`, `SecurityEvent`.

## Questions?

Open a [Discussion](https://github.com/Cyberlorians/nistframework/discussions) or [Issue](https://github.com/Cyberlorians/nistframework/issues).
