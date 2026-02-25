# Power BI Template — NIST 800-171 Coverage Dashboard

## Quick Start

1. **Install Power BI Desktop** (free) from the [Microsoft Store](https://apps.microsoft.com/detail/9ntxr16hnw1t) or [powerbi.microsoft.com](https://powerbi.microsoft.com/desktop/)
2. **Export your CSV** from the NIST 800-171 dashboard → click **Export Power BI CSV** after analyzing your Sentinel environment
3. **Open the template** (`NIST_Coverage.pbit`) — Power BI will ask for the CSV path → point it to your exported file
4. Your dashboard is ready

## If No Template Exists Yet

You can build your own from the sample CSV:

1. Open Power BI Desktop → **Get Data** → **Text/CSV**
2. Select `NIST_Coverage_PowerBI_Sample.csv` from this folder → **Load**
3. Build your visuals using the pre-calculated columns (see schema below)
4. **File → Export → Power BI template (.pbit)** to save a reusable template
5. Commit the `.pbit` file back to this folder

## CSV Schema

| Column | Type | Description | Power BI Use |
|--------|------|-------------|--------------|
| `Control` | Text | NIST control ID (e.g., 3.1.1) | Row label, slicer |
| `ControlName` | Text | Plain-English control name | Tooltip, table column |
| `Family` | Text | NIST family (e.g., Access Control) | Slicer, legend, group axis |
| `TableName` | Text | Sentinel log table name | Detail rows |
| `TableStatus` | Text | Active / Configured / Not Found | Legend, color category |
| `StatusColor` | Text | Green / Orange / Red | Conditional formatting rules |
| `Covered` | Number | 1 = covered, 0 = gap | SUM for coverage counts |
| `PracticeStatus` | Text | Covered / No Coverage | Card visual, slicer |
| `FamilyCoveragePct` | Number | Per-family coverage % (0–100) | Gauge, bar chart |

## Suggested Visuals

| Visual Type | Fields |
|-------------|--------|
| **Donut chart** | Values = COUNT of `Control`, Legend = `PracticeStatus` |
| **Stacked bar** | Axis = `Family`, Values = COUNT of `TableName`, Legend = `TableStatus` |
| **Gauge** | Value = AVERAGE of `FamilyCoveragePct` |
| **Table** | Columns = `Control`, `ControlName`, `TableName`, `TableStatus` with conditional formatting on `StatusColor` |
| **Slicer** | Field = `Family` (dropdown) |
| **Card** | Value = SUM of `Covered` (shows total covered tables) |

## Updating Your Data

1. Run the validation query in Sentinel
2. Paste results into the NIST dashboard
3. Click **Export Power BI CSV**
4. In Power BI → **Home → Transform data → Source** → update the file path
5. Click **Close & Apply** — all visuals refresh automatically

## Notes

- The sample CSV uses realistic statuses to demonstrate all three states (Active, Configured, Not Found)
- One row = one practice–table combination (denormalized for easy charting)
- `FamilyCoveragePct` is pre-calculated so you don't need DAX measures for basic coverage views
- The `.pbit` template file is not tracked by git (add it manually after creating it)
