#!/usr/bin/env python3
"""
build_querypack.py - Generate Sentinel Query Pack JSON from practice YAML files.
Output: output/NIST_800-171_QueryPack.json
"""
import os
import json
import yaml
import re

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "NIST_800-171_QueryPack.json")


def sanitize_id(text):
    """Create a safe ID from text."""
    return re.sub(r'[^a-zA-Z0-9_-]', '-', text).lower().strip('-')


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    queries = []

    for filename in sorted(os.listdir(PRACTICES_DIR)):
        if not filename.endswith(".yaml"):
            continue
        filepath = os.path.join(PRACTICES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        control = data.get("control", "")
        name = data.get("name", "")
        family = data.get("family", "")

        for i, alignment in enumerate(data.get("alignments", [])):
            product = alignment.get("product", "")
            workload = alignment.get("workload", "")
            table = alignment.get("table", "")
            kql = alignment.get("kql", "").strip()

            query_id = sanitize_id(f"nist-{control}-{table}-{workload}")
            display_name = f"NIST {control} - {workload} ({product})"
            description = f"{name} | {product} | {table}"

            queries.append({
                "id": query_id,
                "properties": {
                    "displayName": display_name,
                    "description": description,
                    "body": kql,
                    "related": {
                        "categories": [f"Security - NIST 800-171"],
                        "resourceTypes": [
                            "microsoft.operationalinsights/workspaces"
                        ],
                    },
                    "tags": {
                        "nist-control": [control],
                        "family": [family],
                        "product": [product],
                        "table": [table],
                    },
                },
            })

    output = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "resources": [
            {
                "type": "Microsoft.OperationalInsights/queryPacks",
                "apiVersion": "2019-09-01",
                "name": "NIST-800-171-QueryPack",
                "location": "[resourceGroup().location]",
                "properties": {
                    "displayName": "NIST 800-171 Alignment Queries",
                    "description": "Community-driven KQL queries mapped to NIST 800-171 Rev.2 controls for Microsoft security products.",
                },
            }
        ],
        "queries": queries,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Built {OUTPUT_FILE} with {len(queries)} queries.")


if __name__ == "__main__":
    main()
