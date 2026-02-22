#!/usr/bin/env python3
"""
validate.py - Validate all practice YAML files against the expected schema.
Run by CI on every PR that touches practices/*.yaml.
"""
import sys
import os
import yaml
import argparse

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")

REQUIRED_TOP_KEYS = {"control", "name", "family", "alignments"}
REQUIRED_ALIGNMENT_KEYS = {"product", "workload", "table", "kql"}
VALID_FAMILIES = {
    "Access Control",
    "Awareness and Training",
    "Audit and Accountability",
    "Configuration Management",
    "Identification and Authentication",
    "Incident Response",
    "Maintenance",
    "Media Protection",
    "Personnel Security",
    "Physical Protection",
    "Risk Assessment",
    "Security Assessment",
    "System and Communications Protection",
    "System and Information Integrity",
}


def validate_file(filepath):
    errors = []
    filename = os.path.basename(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"{filename}: YAML parse error: {e}"]

    if not isinstance(data, dict):
        return [f"{filename}: Root must be a mapping"]

    # Check top-level keys
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    if missing:
        errors.append(f"{filename}: Missing top-level keys: {missing}")

    # Validate control matches filename
    expected_control = filename.replace(".yaml", "")
    if data.get("control") != expected_control:
        errors.append(f"{filename}: control '{data.get('control')}' does not match filename '{expected_control}'")

    # Validate family
    if data.get("family") and data["family"] not in VALID_FAMILIES:
        errors.append(f"{filename}: Unknown family '{data['family']}'")

    # Validate alignments
    alignments = data.get("alignments", [])
    if not isinstance(alignments, list) or len(alignments) == 0:
        errors.append(f"{filename}: 'alignments' must be a non-empty list")
    else:
        for i, alignment in enumerate(alignments):
            if not isinstance(alignment, dict):
                errors.append(f"{filename}: alignment[{i}] must be a mapping")
                continue
            missing_keys = REQUIRED_ALIGNMENT_KEYS - set(alignment.keys())
            if missing_keys:
                errors.append(f"{filename}: alignment[{i}] missing keys: {missing_keys}")
            # Validate KQL is not empty
            if alignment.get("kql") and not alignment["kql"].strip():
                errors.append(f"{filename}: alignment[{i}] has empty KQL")
            # Validate KQL has targeting
            kql = alignment.get("kql", "")
            if kql and "Part 0" not in kql:
                errors.append(f"{filename}: alignment[{i}] KQL missing 'Part 0: Analyst-Driven Targeting' section")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true", help="Output summary for GitHub Actions")
    args = parser.parse_args()

    all_errors = []
    file_count = 0

    for filename in sorted(os.listdir(PRACTICES_DIR)):
        if not filename.endswith(".yaml"):
            continue
        file_count += 1
        filepath = os.path.join(PRACTICES_DIR, filename)
        errors = validate_file(filepath)
        all_errors.extend(errors)

    if args.summary:
        print(f"Validated {file_count} practice files.")
        if all_errors:
            print(f"\n❌ {len(all_errors)} error(s) found:\n")
            for e in all_errors:
                print(f"- {e}")
        else:
            print(f"\n✅ All {file_count} files passed validation.")
        return

    if all_errors:
        print(f"❌ Validation failed with {len(all_errors)} error(s):\n")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"✅ All {file_count} practice files passed validation.")


if __name__ == "__main__":
    main()
