# NIST 800-171 Framework - Session Notes
# Last Updated: 2026-02-22
# Purpose: Continuity notes for agent handoff if session is lost.

## PROJECT OVERVIEW

This project maps NIST 800-171 Rev.2 controls to Microsoft Security products with
KQL queries for GRC compliance and DFIR investigation. The architecture is:

1. GitHub Repo (source of truth) - community CRUD via PRs
2. CI/CD (GitHub Actions) - validates YAML, builds CSV + Query Pack JSON
3. Sentinel MCP - validate queries, deploy, check coverage (NOT YET CONNECTED)
4. Security Copilot - natural language compliance investigation (FUTURE)

No workbook needed. Query Packs + Watchlist + MCP replaces it.

## WHAT'S BUILT

### Repo Location: C:\tools\nistframework

### Practice Files (practices/*.yaml) - ALL 17 L1 CONTROLS COMPLETE
- 3.1.1  - Limit system access to authorized users (12 alignments)
- 3.1.2  - Limit system access to authorized functions (9 alignments)
- 3.1.20 - Verify and control external connections (8 alignments)
- 3.1.22 - Control public information (7 alignments)
- 3.5.1  - Identify system users (7 alignments)
- 3.5.2  - Authenticate identities (8 alignments)
- 3.8.3  - Sanitize or destroy media before disposal (5 alignments)
- 3.8.4  - Mark media with CUI markings (5 alignments)
- 3.10.1 - Limit physical access (3 alignments)
- 3.10.3 - Escort and monitor visitors (4 alignments)
- 3.10.4 - Maintain audit logs of physical access (5 alignments)
- 3.10.5 - Control and manage physical access devices (6 alignments)
- 3.13.1 - Monitor and protect communications at boundaries (8 alignments)
- 3.13.5 - Implement subnetworks for public components (4 alignments)
- 3.14.1 - Identify, report, and correct system flaws (7 alignments)
- 3.14.2 - Provide protection from malicious code (11 alignments)
- 3.14.5 - Perform scans and real-time protection (7 alignments)

### CI/CD (/.github/workflows/)
- validate.yml  - Runs on PR, validates YAML schema + checks duplicates
- build.yml     - Runs on merge to main, builds CSV + Query Pack JSON

### Scripts (/scripts/)
- validate.py        - Schema validation for practice YAML files
- check_duplicates.py - Detects duplicate product+workload+table combos
- build_csv.py       - Combines all YAML → output/NIST_800-171_Alignment.csv
- build_querypack.py - Combines all YAML → output/NIST_800-171_QueryPack.json

### Docs
- README.md       - Full project overview, coverage, KQL convention, integration
- CONTRIBUTING.md - How to contribute, YAML format, naming conventions, rules

### Issue Templates (/.github/ISSUE_TEMPLATE/)
- suggest-alignment.md - For non-git users to propose new mappings
- fix-kql.md            - For reporting KQL bugs/improvements

## KQL CONVENTION (CRITICAL - MAINTAIN THIS)

Every KQL query MUST follow this pattern:
- Part 0: Analyst-Driven Targeting (let TargetX = dynamic(["*"]))
  - Wildcard ["*"] for GRC (full-scope compliance audit)
  - Specific values for DFIR (scoped investigation)
- Part 1: Base Filter (table + time range + target filtering)
- Part 2: Enrichment (extend, parse_json, summarize - optional)
- Final Output: project + sort + take 50

## WHAT'S NEXT

### Immediate
1. Run build_csv.py and build_querypack.py to generate output artifacts
2. git init → push to GitHub (Cyberlorians org)
3. Enable branch protection on main (require PR + approval)
4. Connect Sentinel MCP server to VS Code

### After Push
5. Sentinel MCP: validate all KQL against live workspace
6. Sentinel MCP: identify coverage gaps (tables that don't exist)
7. Deploy Query Pack to Sentinel workspace
8. Upload CSV as Sentinel Watchlist

### Future
9. Level 2 expansion (110 NIST 800-171 controls) - USE MCP TO SCALE
10. Level 3 expansion (35 NIST 800-172 controls)
11. Security Copilot promptbook for compliance investigations
12. Analytics Rule templates for detection-worthy queries

## SENTINEL MCP SETUP

The user needs to add the Sentinel MCP server to VS Code settings.
Required config (mcp section in settings.json or .vscode/mcp.json):

```json
{
  "mcpServers": {
    "sentinel": {
      "command": "...",
      "args": ["..."],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "...",
        "AZURE_RESOURCE_GROUP": "...",
        "AZURE_WORKSPACE_NAME": "...",
        "AZURE_WORKSPACE_ID": "..."
      }
    }
  }
}
```

Exact command depends on the MCP server implementation being used.

## KEY DECISIONS MADE
- No workbook: Query Packs + Watchlist + MCP replaces it
- No CMMC column: NIST 800-171 is the universal language
- No CISA/DoD ZTMM: stripped to focus on Microsoft alignment
- YAML per practice (not one big CSV): granular PRs, clean diffs, schema validation
- Every KQL has targeting: supports both GRC and DFIR use cases
- CI rebuilds output on merge: contributors never touch CSV directly
- Issue templates for non-git users: lowers the barrier to contribute

## PREVIOUS FILES (can be cleaned up)
- C:\tools\CMMC_L1_NIST171.csv - Original CSV with CMMC column (superseded)
- C:\tools\NIST_800-171_L1.csv - Cleaned CSV without CMMC column (superseded)
