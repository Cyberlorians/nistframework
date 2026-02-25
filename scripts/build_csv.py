#!/usr/bin/env python3
"""
build_csv.py - Combine all practice YAML files into a single master CSV.
Output: docs/NIST_800-171_Alignment.csv
"""
import os
import csv
import yaml

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "NIST_800-171_Alignment.csv")

CSV_HEADERS = [
    "NIST 800-171",
    "NIST 800-53",
    "Family",
    "Control Name",
    "Function",
    "Category",
    "Workload",
    "Table",
    "Workload Integration",
    "Event Reference",
    "KQL",
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = []

    for filename in sorted(os.listdir(PRACTICES_DIR)):
        if not filename.endswith(".yaml") or filename.startswith("_"):
            continue
        filepath = os.path.join(PRACTICES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        control = data.get("control", "")
        name = data.get("name", "")
        family = data.get("family", "")
        nist_53 = data.get("nist_800_53", "")

        for alignment in data.get("alignments", []):
            rows.append({
                "NIST 800-171": control,
                "NIST 800-53": nist_53,
                "Control Name": name,
                "Family": family,
                "Function": alignment.get("function", ""),
                "Category": alignment.get("category", ""),
                "Workload": alignment.get("workload", ""),
                "Table": alignment.get("table", ""),
                "Workload Integration": alignment.get("workload_integration", ""),
                "Event Reference": alignment.get("event_reference", ""),
                "KQL": alignment.get("kql", "").strip(),
            })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    practice_count = len([f for f in os.listdir(PRACTICES_DIR) if f.endswith(".yaml") and not f.startswith("_")])
    print(f"✅ Built {OUTPUT_FILE} with {len(rows)} rows from {practice_count} practice files.")


if __name__ == "__main__":
    main()
