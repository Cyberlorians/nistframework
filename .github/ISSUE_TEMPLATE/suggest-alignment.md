---
name: Suggest Alignment
about: Propose a new product/table/KQL mapping for a NIST control
title: "[Alignment] NIST {control} - {table}"
labels: ["enhancement", "community-contribution"]
assignees: ''
---

## NIST Control

**Control Number:** (e.g., 3.14.2)
**Control Name:** (e.g., Provide protection from malicious code)

## Proposed Alignment

**Microsoft Product:** (e.g., Microsoft Defender for Endpoint)
**Workload:** (e.g., MDE)
**Table:** (e.g., DeviceEvents)
**Function:** (e.g., Device — optional)
**Category:** (e.g., Host-Based Detection — optional)

## Documentation Links (optional)

**Workload Integration:** (URL to Microsoft Learn integration guide)
**Event Reference:** (URL to table/event schema docs)

## KQL Query

```kql
// Objective: What this query detects
//
// ----- Part 0: Analyst-Driven Targeting (Optional) -----
let TargetDevices = dynamic([]);
//
// ----- Part 1: Base Filter -----
TableName
| where TimeGenerated > ago(30d)
//
// ----- Part 2: Parse -----
| extend ...
//
// ----- Part 3: Enrich -----
| extend ...
//
// ----- Part 4: Apply Dynamic Filters -----
| where (array_length(TargetDevices) == 0 or DeviceName in (TargetDevices))
//
// ----- Part 5: Final Output -----
| distinct ...
| sort by TimeGenerated desc
| take 50
```

## Why This Alignment?

Explain why this product/table is relevant to this NIST control.

## Testing

- [ ] I tested this query in a Sentinel workspace or MDE Advanced Hunting
- [ ] Query returns results
- [ ] Dynamic targeting works (empty array = all, populated = scoped)
