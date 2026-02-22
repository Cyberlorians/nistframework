---
name: Suggest Alignment
about: Propose a new product/table/KQL mapping for a NIST control
title: "[Alignment] NIST {control} - {product}"
labels: ["enhancement", "community-contribution"]
assignees: ''
---

## NIST Control

**Control Number:** (e.g., 3.14.2)
**Control Name:** (e.g., Provide protection from malicious code)

## Proposed Alignment

**Microsoft Product:** (e.g., Microsoft Defender for Endpoint)
**Workload:** (e.g., AV Detections)
**Table:** (e.g., DeviceEvents)

## KQL Query

```kql
// Paste your KQL here — must include Part 0 targeting
// Part 0: Analyst-Driven Targeting
let TargetUsers = dynamic(["*"]);
let LookbackDays = 30;
// Part 1: Base Filter
// ...
```

## Why This Alignment?

Explain why this product/table is relevant to this NIST control.

## Testing

- [ ] I tested this query against a live Sentinel workspace
- [ ] Query returns results
- [ ] Targeting variables work (both wildcard and specific values)
