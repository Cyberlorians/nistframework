#!/usr/bin/env python3
"""
check_duplicates.py - Check for duplicate product+table combos within each practice.
"""
import os
import sys
import yaml

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")


def main():
    errors = []
    for filename in sorted(os.listdir(PRACTICES_DIR)):
        if not filename.endswith(".yaml"):
            continue
        filepath = os.path.join(PRACTICES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        seen = set()
        for i, alignment in enumerate(data.get("alignments", [])):
            key = (alignment.get("product"), alignment.get("workload"), alignment.get("table"))
            if key in seen:
                errors.append(f"{filename}: Duplicate alignment[{i}]: {key}")
            seen.add(key)

    if errors:
        print(f"❌ {len(errors)} duplicate(s) found:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("✅ No duplicates found.")


if __name__ == "__main__":
    main()
