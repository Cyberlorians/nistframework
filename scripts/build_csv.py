#!/usr/bin/env python3
"""
build_csv.py - Combine all practice YAML files into a single master CSV.
Output: output/NIST_800-171_Alignment.csv
"""
import os
import csv
import yaml

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "NIST_800-171_Alignment.csv")

CSV_HEADERS = [
    "NIST 800-171",
    "Control Name",
    "Family",
    "Microsoft Product",
    "Workload",
    "Table",
    "KQL",
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = []

    for filename in sorted(os.listdir(PRACTICES_DIR)):
        if not filename.endswith(".yaml"):
            continue
        filepath = os.path.join(PRACTICES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        control = data.get("control", "")
        name = data.get("name", "")
        family = data.get("family", "")

        for alignment in data.get("alignments", []):
            rows.append({
                "NIST 800-171": control,
                "Control Name": name,
                "Family": family,
                "Microsoft Product": alignment.get("product", ""),
                "Workload": alignment.get("workload", ""),
                "Table": alignment.get("table", ""),
                "KQL": alignment.get("kql", "").strip(),
            })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Built {OUTPUT_FILE} with {len(rows)} rows from {len(os.listdir(PRACTICES_DIR))} practice files.")


if __name__ == "__main__":
    main()
