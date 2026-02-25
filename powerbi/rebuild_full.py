"""
Rebuild the full Power BI project with:
  - 2 new columns: Compliant (int), ComplianceNote (text)
  - Slicers for Family, TableStatus, PracticeStatus
  - KPI cards: Technical Coverage + Compliance Score
  - Per-practice bar chart with status coloring
  - Detail table with all columns including Compliant
  - DAX measures for compliance score
"""

import json
import os
import shutil

BASE = r"C:\tools\nistframework\powerbi"
REPORT_DIR = os.path.join(BASE, "NISTCoverage.Report")
REPORT_DEF = os.path.join(REPORT_DIR, "definition")
MODEL_DIR = os.path.join(BASE, "NISTCoverage.SemanticModel")
MODEL_DEF = os.path.join(MODEL_DIR, "definition")
PAGE_ID = "pg_nist_coverage_01"
PAGE_DIR = os.path.join(REPORT_DEF, "pages", PAGE_ID)
VISUALS_DIR = os.path.join(PAGE_DIR, "visuals")
TABLE = "NIST_Coverage_PowerBI"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
CSV_PATH = os.path.join(BASE, "NIST_Coverage_PowerBI.csv")

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ═══ Wipe and rebuild ═══
for d in [REPORT_DIR, MODEL_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)
print("Cleaned old project dirs")

# ═══════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════
write_json(os.path.join(BASE, "NISTCoverage.pbip"), {
    "version": "1.0",
    "artifacts": [{"report": {"path": "NISTCoverage.Report"}, "semanticModel": {"path": "NISTCoverage.SemanticModel"}}]
})

# ═══════════════════════════════════════════════
# SEMANTIC MODEL
# ═══════════════════════════════════════════════
write_json(os.path.join(MODEL_DIR, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": "NISTCoverage"},
    "config": {"version": "2.0", "logicalId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
})

write_json(os.path.join(MODEL_DIR, "definition.pbism"), {"version": "4.0", "settings": {}})

write_text(os.path.join(MODEL_DEF, "model.tmdl"), """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation PBI_QueryOrder = ["NIST_Coverage_PowerBI"]

annotation PBI_ProTooling = ["DevMode"]

ref table NIST_Coverage_PowerBI

ref cultureInfo en-US
""")

write_text(os.path.join(MODEL_DEF, "database.tmdl"), """database NISTCoverage

\tcompatibilityLevel: 1567
\tmodel Model
""")

write_text(os.path.join(MODEL_DEF, "relationships.tmdl"), "")

write_text(os.path.join(MODEL_DEF, "cultures", "en-US.tmdl"), """cultureInfo en-US

\tlinguisticMetadata =
\t\t{
\t\t  "Version": "1.0.0",
\t\t  "Language": "en-US"
\t\t}

""")

# ─── Table definition with 11 columns + DAX measures ───
csv_abs = CSV_PATH.replace("\\", "\\\\")
m_query_source = 'Csv.Document(File.Contents("' + csv_abs + '"),[Delimiter=",", Columns=11, Encoding=1252, QuoteStyle=QuoteStyle.None])'

def mk_col(name, dtype="string", fmt=None, summarize="none", tag=None):
    lines = [f"\tcolumn {name}", f"\t\tdataType: {dtype}"]
    if fmt:
        lines.append(f"\t\tformatString: {fmt}")
    if tag:
        lines.append(f"\t\tlineageTag: {tag}")
    lines.append(f"\t\tsummarizeBy: {summarize}")
    lines.append(f"\t\tsourceColumn: {name}")
    lines.append("")
    lines.append("\t\tannotation SummarizationSetBy = Automatic")
    return "\n".join(lines)

columns = [
    mk_col("Control", tag="38af12c0-050c-409e-aa12-46fc71c402c2"),
    mk_col("ControlName", tag="78348b56-9261-4aa7-a1db-2685bd492e0d"),
    mk_col("Family", tag="2e361855-ef60-4ad2-b43a-54ca28c8c139"),
    mk_col("TableName", tag="4b29a404-76aa-4295-a626-713fd33ddb9a"),
    mk_col("TableStatus", tag="e2ff452d-b786-4148-99cf-33371092beb2"),
    mk_col("StatusColor", tag="786024d8-7e8e-4d34-b1fb-9aab68287952"),
    mk_col("Covered", dtype="int64", fmt="0", summarize="sum", tag="44de1310-c536-4330-a6a5-9c1ea108b94d"),
    mk_col("PracticeStatus", tag="5b883b04-1433-4ba1-9ac6-2637eda69812"),
    mk_col("FamilyCoveragePct", dtype="int64", fmt="0", summarize="sum", tag="439c914e-44b5-4c78-a573-fe55389736d0"),
    mk_col("Compliant", dtype="int64", fmt="0", summarize="sum", tag="b1c2d3e4-f5a6-7890-bcde-fa1234567801"),
    mk_col("ComplianceNote", tag="c2d3e4f5-a6b7-8901-cdef-ab1234567802"),
]

# DAX measures
measures = """
\tmeasure 'Technical Coverage %' = DIVIDE(SUM(NIST_Coverage_PowerBI[Covered]), COUNTROWS(NIST_Coverage_PowerBI), 0) * 100
\t\tlineageTag: d1e2f3a4-b5c6-7890-1234-567890abcde1
\t\tformatString: 0.0

\tmeasure 'Compliance Score %' = DIVIDE(SUM(NIST_Coverage_PowerBI[Compliant]), COUNTROWS(NIST_Coverage_PowerBI), 0) * 100
\t\tlineageTag: d1e2f3a4-b5c6-7890-1234-567890abcde2
\t\tformatString: 0.0

\tmeasure 'Manual Overrides' = CALCULATE(COUNTROWS(NIST_Coverage_PowerBI), NIST_Coverage_PowerBI[Compliant] = 1, NIST_Coverage_PowerBI[Covered] = 0)
\t\tlineageTag: d1e2f3a4-b5c6-7890-1234-567890abcde3
\t\tformatString: 0
"""

tmdl = "table NIST_Coverage_PowerBI\n"
tmdl += "\tlineageTag: 8456f445-7abb-4810-a5f5-4045386aaa0c\n\n"
tmdl += "\n\n".join(columns)
tmdl += "\n"
tmdl += measures
tmdl += "\n\tpartition NIST_Coverage_PowerBI = m\n"
tmdl += "\t\tmode: import\n"
tmdl += "\t\tsource =\n"
tmdl += "\t\t\t\tlet\n"
tmdl += '\t\t\t\t    Source = ' + m_query_source + ',\n'
tmdl += '\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
tmdl += '\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Control", type text}, {"ControlName", type text}, {"Family", type text}, {"TableName", type text}, {"TableStatus", type text}, {"StatusColor", type text}, {"Covered", Int64.Type}, {"PracticeStatus", type text}, {"FamilyCoveragePct", Int64.Type}, {"Compliant", Int64.Type}, {"ComplianceNote", type text}})\n'
tmdl += "\t\t\t\tin\n"
tmdl += '\t\t\t\t    #"Changed Type"\n'
tmdl += "\n\tannotation PBI_ResultType = Table\n"

write_text(os.path.join(MODEL_DEF, "tables", "NIST_Coverage_PowerBI.tmdl"), tmdl)
print("✔ Semantic model (11 columns + 3 DAX measures)")

# ═══════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════
write_json(os.path.join(REPORT_DIR, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "Report", "displayName": "NISTCoverage"},
    "config": {"version": "2.0", "logicalId": "28bad5f8-b1cf-4778-afde-73c34a651924"}
})

write_json(os.path.join(REPORT_DIR, "definition.pbir"), {
    "version": "4.0",
    "datasetReference": {"byPath": {"path": "../NISTCoverage.SemanticModel"}, "byConnection": None}
})

write_json(os.path.join(REPORT_DEF, "report.json"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.2.0/schema.json",
    "themeCollection": {
        "baseTheme": {
            "name": "CY26SU02",
            "reportVersionAtImport": {"visual": "2.6.0", "report": "3.1.0", "page": "2.3.0"},
            "type": "SharedResources"
        }
    },
    "settings": {
        "useStylableVisualContainerHeader": True,
        "exportDataMode": "AllowSummarized",
        "useEnhancedTooltips": True,
        "useDefaultAggregateDisplayName": True
    },
    "resourcePackages": [{
        "name": "SharedResources",
        "type": "SharedResources",
        "items": [{"name": "CY26SU02", "path": "BaseThemes/CY26SU02.json", "type": "BaseTheme"}]
    }]
})

write_json(os.path.join(REPORT_DEF, "version.json"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
    "version": "2.0.0"
})

write_json(os.path.join(REPORT_DEF, "pages", "pages.json"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
    "pageOrder": [PAGE_ID],
    "activePageName": PAGE_ID
})

write_json(os.path.join(PAGE_DIR, "page.json"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
    "name": PAGE_ID,
    "displayName": "NIST 800-171 Coverage",
    "displayOption": "FitToPage",
    "height": 720,
    "width": 1280
})
print("✔ Report structure")

# ─── Visual helpers ───
def col(prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": TABLE}}, "Property": prop}}

def agg(prop, func):
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": TABLE}}, "Property": prop}}, "Function": func}}

def measure(name):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": TABLE}}, "Property": name}}

def add_visual(name, data):
    vdir = os.path.join(VISUALS_DIR, name)
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "visual.json"), "w") as f:
        json.dump(data, f, indent=2)

# ═══════════════════════════════════════════════
# VISUALS — Layout 1280x720
# ═══════════════════════════════════════════════
#
#  ┌──────────────────────────────────────────────────────────────┐
#  │ TITLE                                                 y=8   │
#  ├──────┬──────┬──────┬──────┬──────┬───────────────────────────┤
#  │TECH% │COMP% │OVERR │ACT   │CFG   │ SLICERS: Family, Status  │ y=48
#  ├──────┴──────┴──────┴──────┴──────┴───────────────────────────┤
#  │ STACKED BAR: Per-Practice (Control), bars by TableStatus     │ y=155
#  ├──────────────────────────────────────────────────────────────┤
#  │ DETAIL TABLE: all columns                                    │ y=415
#  └──────────────────────────────────────────────────────────────┘

# ── 1. Title ──
add_visual("v01_title", {
    "$schema": SCHEMA, "name": "v01_title",
    "position": {"x": 20, "y": 8, "z": 0, "width": 1240, "height": 38},
    "visual": {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "NIST 800-171 Rev.2 Level 1  —  Sentinel Coverage & Compliance Dashboard", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16px", "color": "#1a1a2e"}}]}]}}]}
    }
})

# ── 2. Card: Technical Coverage % ──
add_visual("v02_techpct", {
    "$schema": SCHEMA, "name": "v02_techpct",
    "position": {"x": 20, "y": 48, "z": 1, "width": 155, "height": 100},
    "visual": {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [{"field": measure("Technical Coverage %"), "queryRef": f"[Technical Coverage %]", "active": True}]}}},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Technical %'"}}}}}]}
    }
})

# ── 3. Card: Compliance Score % ──
add_visual("v03_comppct", {
    "$schema": SCHEMA, "name": "v03_comppct",
    "position": {"x": 185, "y": 48, "z": 2, "width": 155, "height": 100},
    "visual": {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [{"field": measure("Compliance Score %"), "queryRef": f"[Compliance Score %]", "active": True}]}}},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Compliance %'"}}}}}]}
    }
})

# ── 4. Card: Manual Overrides count ──
add_visual("v04_overrides", {
    "$schema": SCHEMA, "name": "v04_overrides",
    "position": {"x": 350, "y": 48, "z": 3, "width": 130, "height": 100},
    "visual": {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [{"field": measure("Manual Overrides"), "queryRef": f"[Manual Overrides]", "active": True}]}}},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Overrides'"}}}}}]}
    }
})

# ── 5. Card: Active tables ──
add_visual("v05_active", {
    "$schema": SCHEMA, "name": "v05_active",
    "position": {"x": 490, "y": 48, "z": 4, "width": 120, "height": 100},
    "visual": {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [{"field": agg("TableName", 5), "queryRef": f"CountNonNull({TABLE}.TableName)", "active": True}]}}},
        "filters": [{"name": "f_act", "type": "Categorical", "expression": col("TableStatus"), "filter": {"whereItems": [{"condition": {"Comparison": {"ComparisonKind": 0, "Left": col("TableStatus"), "Right": {"Literal": {"Value": "'Active'"}}}}}]}}],
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Active'"}}}}}]}
    }
})

# ── 6. Card: Configured tables ──
add_visual("v06_configured", {
    "$schema": SCHEMA, "name": "v06_configured",
    "position": {"x": 620, "y": 48, "z": 5, "width": 120, "height": 100},
    "visual": {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [{"field": agg("TableName", 5), "queryRef": f"CountNonNull({TABLE}.TableName)", "active": True}]}}},
        "filters": [{"name": "f_cfg", "type": "Categorical", "expression": col("TableStatus"), "filter": {"whereItems": [{"condition": {"Comparison": {"ComparisonKind": 0, "Left": col("TableStatus"), "Right": {"Literal": {"Value": "'Configured'"}}}}}]}}],
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Configured'"}}}}}]}
    }
})

# ── 7. Slicer: Family ──
add_visual("v07_family", {
    "$schema": SCHEMA, "name": "v07_family",
    "position": {"x": 770, "y": 48, "z": 6, "width": 240, "height": 100},
    "visual": {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [{"field": col("Family"), "queryRef": f"{TABLE}.Family", "active": True}]}}},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Family'"}}}}}]}
    }
})

# ── 8. Slicer: TableStatus ──
add_visual("v08_status", {
    "$schema": SCHEMA, "name": "v08_status",
    "position": {"x": 1020, "y": 48, "z": 7, "width": 240, "height": 100},
    "visual": {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [{"field": col("TableStatus"), "queryRef": f"{TABLE}.TableStatus", "active": True}]}}},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Status'"}}}}}]}
    }
})

# ── 9. Stacked Bar: Per-Practice Table Breakdown ──
add_visual("v09_practices", {
    "$schema": SCHEMA, "name": "v09_practices",
    "position": {"x": 20, "y": 155, "z": 8, "width": 1240, "height": 255},
    "visual": {
        "visualType": "clusteredBarChart",
        "query": {"queryState": {
            "Category": {"projections": [{"field": col("Control"), "queryRef": f"{TABLE}.Control", "active": True}]},
            "Y": {"projections": [{"field": agg("TableName", 5), "queryRef": f"CountNonNull({TABLE}.TableName)", "active": True}]},
            "Series": {"projections": [{"field": col("TableStatus"), "queryRef": f"{TABLE}.TableStatus", "active": True}]}
        }},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Tables per Practice (by status)'"}}}}}]}
    }
})

# ── 10. Detail Table ──
detail_cols = ["Control", "ControlName", "TableName", "TableStatus", "Covered", "Compliant", "ComplianceNote"]
add_visual("v10_detail", {
    "$schema": SCHEMA, "name": "v10_detail",
    "position": {"x": 20, "y": 415, "z": 9, "width": 1240, "height": 292},
    "visual": {
        "visualType": "tableEx",
        "query": {"queryState": {"Values": {"projections": [
            {"field": col(c), "queryRef": f"{TABLE}.{c}", "active": True} for c in detail_cols
        ]}}},
        "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Coverage Detail — Edit Compliant & ComplianceNote columns in CSV to override'"}}}}}]}
    }
})

# ═══════════════════════════════════════════════
# VALIDATE
# ═══════════════════════════════════════════════
print("\n── Validation ──")
errors = 0

# Check all JSON files
for root, dirs, files in os.walk(BASE):
    for fn in files:
        if fn.endswith((".json", ".pbir", ".pbism", ".pbip")):
            fp = os.path.join(root, fn)
            try:
                with open(fp) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print(f"  ✘ JSON ERROR: {os.path.relpath(fp, BASE)}: {e}")
                errors += 1

# Check TMDL
table_file = os.path.join(MODEL_DEF, "tables", "NIST_Coverage_PowerBI.tmdl")
with open(table_file) as f:
    content = f.read()
if "dataType: dateTime" in content:
    print("  ✘ Control is still dateTime!"); errors += 1
if "LocalDateTable" in content:
    print("  ✘ Date table ref found!"); errors += 1
if "measure 'Technical Coverage %'" in content:
    print("  ✔ DAX measures present")
else:
    print("  ✘ DAX measures missing!"); errors += 1

# Check columns
expected_cols = ["Control", "ControlName", "Family", "TableName", "TableStatus", "StatusColor", "Covered", "PracticeStatus", "FamilyCoveragePct", "Compliant", "ComplianceNote"]
for ec in expected_cols:
    if f"column {ec}" not in content and f"sourceColumn: {ec}" not in content:
        print(f"  ✘ Column {ec} missing in TMDL!"); errors += 1

# Check visual count
visuals = [d for d in os.listdir(VISUALS_DIR) if os.path.isdir(os.path.join(VISUALS_DIR, d))]
print(f"  ✔ {len(visuals)} visuals: {sorted(visuals)}")

# Check CSV
import csv as csv_mod
with open(CSV_PATH) as f:
    reader = csv_mod.reader(f)
    header = next(reader)
    rows = list(reader)
if header == expected_cols:
    print(f"  ✔ CSV: {len(rows)} rows, 11 columns match")
else:
    print(f"  ✘ CSV header mismatch: {header}"); errors += 1

# Schema check
for root, dirs, files in os.walk(VISUALS_DIR):
    for fn in files:
        if fn == "visual.json":
            with open(os.path.join(root, fn)) as f:
                vj = json.load(f)
            s = vj.get("$schema", "")
            if "2.0.0" not in s:
                print(f"  ✘ Wrong schema in {root}: {s}"); errors += 1

if errors:
    print(f"\n✘ {errors} error(s)!")
else:
    print("\n✔ All validation passed!")
