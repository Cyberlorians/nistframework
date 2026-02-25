#!/usr/bin/env python3
"""
parse_cmmc.py - Parse cmmc_ref.md and generate cmmc_data.json
Extracts all CMMC 2.0 Level 1-3 practices with NIST, CISA, and DoD mappings.
"""
import re
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_FILE = os.path.join(ROOT_DIR, "cmmc_ref.md")
OUTPUT_FILE = os.path.join(ROOT_DIR, "cmmc_data.json")

# Family code → full name mapping
FAMILY_MAP = {
    "AC": "Access Control",
    "AT": "Awareness & Training",
    "AU": "Audit & Accountability",
    "CM": "Configuration Management",
    "IA": "Identification & Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PE": "Physical Protection",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "CA": "Security Assessment",
    "SC": "System & Communications Protection",
    "SI": "System & Information Integrity",
}


def parse_cmmc_ref(filepath):
    """Parse the CMMC reference markdown and extract all practices."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    practices = []

    # Pattern to match practice rows in markdown tables
    # Example: | **AC.L1-3.1.1** Limit system access to authorized users | 3.1.1 — ... | **Identity 1.1** — ... | **Identity 1.1** — ... |
    row_pattern = re.compile(
        r'\|\s*\*\*([A-Z]{2})\.L(\d)-([^\*]+)\*\*\s*([^|]*)\|'  # Practice ID + name
        r'\s*([^|]*)\|'   # NIST ref
        r'\s*([^|]*)\|'   # CISA ZTMM
        r'\s*([^|]*)\|',  # DoD ZT
        re.MULTILINE
    )

    for m in row_pattern.finditer(text):
        family_code = m.group(1).strip()
        level = int(m.group(2).strip())
        nist_num = m.group(3).strip()
        name = m.group(4).strip()
        nist_ref = m.group(5).strip()
        cisa_ztmm = m.group(6).strip()
        dod_zt = m.group(7).strip()

        # Build practice ID
        practice_id = f"{family_code}.L{level}-{nist_num}"

        # Clean up bold markers from CISA/DoD fields
        cisa_ztmm = re.sub(r'\*\*([^*]+)\*\*', r'\1', cisa_ztmm).strip()
        dod_zt = re.sub(r'\*\*([^*]+)\*\*', r'\1', dod_zt).strip()
        nist_ref = re.sub(r'\*\*([^*]+)\*\*', r'\1', nist_ref).strip()

        # Clean em-dash encoding issues
        for field in [name, nist_ref, cisa_ztmm, dod_zt]:
            field = field.replace('\u2014', '—').replace('\u2013', '–')

        # Extract just the NIST control number (e.g., "3.1.1" from "3.1.1 — ...")
        nist_control_match = re.match(r'([\d.]+)', nist_ref)
        nist_control = nist_control_match.group(1) if nist_control_match else nist_num

        # For L3, NIST ref starts with "172-"
        if level == 3:
            nist_control = nist_ref.split('—')[0].strip() if '—' in nist_ref else nist_ref.split('-')[0].strip()

        practices.append({
            "practice_id": practice_id,
            "name": name,
            "level": level,
            "family_code": family_code,
            "family": FAMILY_MAP.get(family_code, family_code),
            "nist_control": nist_control,
            "nist_ref": nist_ref,
            "cisa_ztmm": cisa_ztmm,
            "dod_zt": dod_zt,
        })

    return practices


def deduplicate(practices):
    """Remove duplicate practices (some appear twice in the ref doc)."""
    seen = set()
    unique = []
    for p in practices:
        if p["practice_id"] not in seen:
            seen.add(p["practice_id"])
            unique.append(p)
    return unique


def main():
    practices = parse_cmmc_ref(INPUT_FILE)
    practices = deduplicate(practices)

    # Sort by level, then family code, then practice ID
    practices.sort(key=lambda p: (p["level"], p["family_code"], p["practice_id"]))

    # Stats
    level_counts = {}
    family_codes = set()
    for p in practices:
        level_counts[p["level"]] = level_counts.get(p["level"], 0) + 1
        family_codes.add(p["family_code"])

    print(f"Parsed {len(practices)} CMMC practices:")
    for lvl in sorted(level_counts):
        print(f"  Level {lvl}: {level_counts[lvl]} practices")
    print(f"  Families: {', '.join(sorted(family_codes))}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(practices, f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
