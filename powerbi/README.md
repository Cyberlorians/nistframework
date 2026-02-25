# Power BI Dashboard — NIST 800-171 Coverage & Compliance

## Quick Start

1. **Install Power BI Desktop** (free) from the [Microsoft Store](https://apps.microsoft.com/detail/9ntxr16hnw1t) or [powerbi.microsoft.com](https://powerbi.microsoft.com/desktop/)
2. **Export your CSV** from the NIST 800-171 dashboard → click **Export Power BI CSV** after analyzing your Sentinel environment
3. **Copy CSV** to `powerbi/NIST_Coverage_PowerBI.csv` in this repo
4. **Open** `NISTCoverage.pbip` in Power BI Desktop → click **Refresh**
5. Your dashboard is ready — 10 visuals including slicers, scores, and detail table

## .pbip Project (Pre-Built)

This folder contains a ready-to-use Power BI Project (`.pbip`) with:
- **3 DAX measures**: Technical Coverage %, Compliance Score %, Manual Overrides
- **2 Slicers**: Family and TableStatus (act as cross-filters)
- **3 Score cards**: Technical %, Compliance %, Override count
- **2 Context cards**: Active table count, Configured table count
- **1 Bar chart**: Per-practice table breakdown by status
- **1 Detail table**: All columns including Compliant and ComplianceNote

## CSV Schema (11 columns)

| Column | Type | Description | Power BI Use |
|--------|------|-------------|--------------|
| `Control` | Text | NIST control ID (e.g., 3.1.1) | Row label, axis |
| `ControlName` | Text | Plain-English control name | Detail table |
| `Family` | Text | NIST family (e.g., Access Control) | **Slicer**, group axis |
| `TableName` | Text | Sentinel log table name | Detail rows |
| `TableStatus` | Text | Active / Configured / Not Found | **Slicer**, bar legend |
| `StatusColor` | Text | Green / Orange / Red | Conditional formatting |
| `Covered` | Number | 1 = covered (KQL), 0 = gap | Technical Coverage % |
| `PracticeStatus` | Text | Covered / No Coverage | Filter |
| `FamilyCoveragePct` | Number | Per-family coverage % (0–100) | Reference |
| `Compliant` | Number | 1 = compliant (manual override), 0 = gap | **Compliance Score %** |
| `ComplianceNote` | Text | Justification for manual override | Detail table |

## Compliance Override Workflow

The dashboard supports **two scores**:

| Score | DAX Measure | Meaning |
|-------|-------------|---------|
| **Technical Coverage %** | `SUM(Covered) / COUNTROWS()` | Automated — based on KQL table detection. Cannot be overridden. |
| **Compliance Score %** | `SUM(Compliant) / COUNTROWS()` | Manual — includes overrides. Reflects your actual compliance posture. |

### How to Override

1. Open `NIST_Coverage_PowerBI.csv` in Excel or a text editor
2. Find the row(s) you want to override
3. Change `Compliant` from `0` to `1`
4. Add a justification in `ComplianceNote` (e.g., "Handled by third-party SIEM")
5. Save the CSV → Refresh in Power BI

The **Manual Overrides** card shows how many practices were marked compliant without KQL coverage.

## Updating Your Data

1. Run the validation query in Sentinel
2. Paste results into the HTML dashboard
3. Click **Export Power BI CSV** → save to this folder
4. Open Power BI → click **Refresh** — all visuals update automatically
5. Review and re-apply any manual overrides if needed

## Notes

- One row = one practice–table combination (denormalized for easy charting)
- `Compliant` defaults to the same value as `Covered` on export — only change it for overrides
- The `.pbip` format is fully editable JSON/TMDL (no binary .pbix needed)
- Schema versions: visual 2.0.0, report 3.2.0, page 2.1.0 (compatible with PBI Desktop 2.152+)
