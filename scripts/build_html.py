#!/usr/bin/env python3
"""
build_html.py - Generate an interactive HTML app from practice YAMLs.
Three tabs: Browse (reference), Validate (environment check), Contribute (CRUD form).
Output: output/index.html
"""
import os
import json
import yaml
import html as html_mod

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")
GITHUB_REPO = "Cyberlorians/nistframework"


def load_practices():
    """Load all practice YAMLs and return structured data."""
    practices = []
    families = set()
    tables = set()
    workloads = set()

    for filename in sorted(os.listdir(PRACTICES_DIR)):
        if not filename.endswith(".yaml") or filename.startswith("_"):
            continue
        filepath = os.path.join(PRACTICES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        family = data.get("family", "")
        families.add(family)

        alignments = []
        for a in data.get("alignments", []):
            table = a.get("table", "")
            workload = a.get("workload", "")
            if table:
                tables.add(table)
            if workload:
                workloads.add(workload)
            alignments.append({
                "workload": workload,
                "table": table,
                "function": a.get("function", ""),
                "category": a.get("category", ""),
                "workload_integration": a.get("workload_integration", ""),
                "event_reference": a.get("event_reference", ""),
                "kql": a.get("kql", "").strip(),
            })

        practices.append({
            "control": data.get("control", ""),
            "name": data.get("name", ""),
            "family": family,
            "nist_800_53": data.get("nist_800_53", ""),
            "alignments": alignments,
        })

    return practices, sorted(families), sorted(tables), sorted(workloads)


def build_html(practices, families, tables, workloads):
    data_json = json.dumps(practices, indent=None)
    all_tables_json = json.dumps(sorted(tables))
    all_families_json = json.dumps(sorted(families))
    all_workloads_json = json.dumps(sorted(workloads))

    family_options = "".join(
        f'<option value="{html_mod.escape(f)}">{html_mod.escape(f)}</option>'
        for f in families
    )
    workload_options = "".join(
        f'<option value="{html_mod.escape(w)}">{html_mod.escape(w)}</option>'
        for w in workloads
    )
    table_options = "".join(
        f'<option value="{html_mod.escape(t)}">{html_mod.escape(t)}</option>'
        for t in tables
    )
    total_queries = sum(len(p["alignments"]) for p in practices)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NIST 800-171 Rev.2 &mdash; Level 1 KQL Alignment</title>
<style>
:root {{
  --bg: #0d1117; --surface: #161b22; --surface2: #1c2333;
  --border: #30363d; --text: #e6edf3; --text-muted: #8b949e;
  --accent: #58a6ff; --accent-dim: #1f6feb; --green: #3fb950;
  --orange: #d29922; --red: #f85149; --purple: #bc8cff; --radius: 8px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6; }}

/* ── Header ── */
.header {{ background: linear-gradient(135deg, #1a1f35 0%, #0d1117 100%);
  border-bottom: 1px solid var(--border); padding: 1.5rem 2rem 0; }}
.header h1 {{ font-size: 1.6rem; font-weight: 700; }}
.header h1 span {{ color: var(--accent); }}
.header .subtitle {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem; }}
.stats {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }}
.stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 0.4rem 0.8rem; font-size: 0.82rem; }}
.stat strong {{ color: var(--accent); font-size: 1.1rem; margin-right: 0.3rem; }}

/* ── Tabs ── */
.tabs {{ display: flex; gap: 0; border-bottom: 2px solid var(--border); }}
.tab {{ padding: 0.65rem 1.5rem; cursor: pointer; color: var(--text-muted); font-size: 0.9rem;
  font-weight: 600; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.15s;
  user-select: none; }}
.tab:hover {{ color: var(--text); }}
.tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
.tab-panel {{ display: none; }}
.tab-panel.active {{ display: block; }}

/* ── Filters (Browse tab) ── */
.filters {{ display: flex; gap: 1rem; padding: 1rem 2rem; background: var(--surface);
  border-bottom: 1px solid var(--border); flex-wrap: wrap; align-items: center; }}
.filter-group {{ display: flex; flex-direction: column; gap: 0.25rem; }}
.filters label {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.05em; }}
select, input[type="text"], textarea {{ background: var(--bg); color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.45rem 0.75rem; font-size: 0.9rem; font-family: inherit; }}
select {{ min-width: 170px; cursor: pointer; }}
input[type="text"] {{ min-width: 170px; }}
textarea {{ min-width: 100%; resize: vertical; font-family: 'SF Mono','Cascadia Code','Consolas',monospace;
  font-size: 0.82rem; line-height: 1.5; }}
select:focus, input:focus, textarea:focus {{ outline: none; border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(88,166,255,0.2); }}
.clear-btn {{ background: transparent; color: var(--text-muted); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.45rem 0.9rem; font-size: 0.85rem; cursor: pointer; align-self: flex-end; }}
.clear-btn:hover {{ color: var(--accent); border-color: var(--accent-dim); }}

/* ── Main ── */
.main {{ padding: 1.5rem 2rem 3rem; max-width: 1400px; margin: 0 auto; }}
.results-count {{ color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem; }}

/* ── Practice Card ── */
.practice {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  margin-bottom: 0.75rem; overflow: hidden; }}
.practice-header {{ display: flex; align-items: center; gap: 0.75rem; padding: 0.85rem 1.25rem;
  cursor: pointer; user-select: none; transition: background 0.15s; }}
.practice-header:hover {{ background: var(--surface2); }}
.practice-header .chevron {{ color: var(--text-muted); font-size: 0.7rem; transition: transform 0.2s; flex-shrink: 0; }}
.practice.open .chevron {{ transform: rotate(90deg); }}
.control-id {{ font-family: 'SF Mono','Cascadia Code','Consolas',monospace; font-weight: 700;
  font-size: 0.95rem; color: var(--accent); min-width: 4.5rem; }}
.control-name {{ font-weight: 600; font-size: 0.92rem; flex: 1; }}
.pill {{ font-size: 0.72rem; padding: 0.15rem 0.55rem; border-radius: 999px; white-space: nowrap; }}
.pill-family {{ background: var(--accent-dim); color: #fff; }}
.pill-53 {{ background: rgba(188,140,255,0.15); color: var(--purple); border: 1px solid rgba(188,140,255,0.3); }}
.pill-count {{ background: rgba(63,185,80,0.15); color: var(--green); border: 1px solid rgba(63,185,80,0.3); }}

/* ── Alignment ── */
.practice-body {{ display: none; border-top: 1px solid var(--border); }}
.practice.open .practice-body {{ display: block; }}
.alignment {{ padding: 1rem 1.25rem; border-bottom: 1px solid var(--border); }}
.alignment:last-child {{ border-bottom: none; }}
.alignment-meta {{ display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.6rem; }}
.meta-tag {{ font-size: 0.76rem; padding: 0.12rem 0.5rem; border-radius: 4px;
  background: var(--surface2); border: 1px solid var(--border); color: var(--text-muted); }}
.meta-tag strong {{ color: var(--text); font-weight: 600; }}
.meta-links {{ display: flex; gap: 0.75rem; margin-bottom: 0.6rem; }}
.meta-links a {{ font-size: 0.78rem; color: var(--accent); text-decoration: none; }}
.meta-links a:hover {{ text-decoration: underline; }}

/* ── KQL ── */
.kql-wrapper {{ position: relative; margin-top: 0.4rem; }}
.kql-block {{ background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 0.85rem; font-family: 'SF Mono','Cascadia Code','Consolas',monospace;
  font-size: 0.8rem; line-height: 1.5; overflow-x: auto; white-space: pre; max-height: 380px; overflow-y: auto; }}
.copy-btn {{ position: absolute; top: 0.4rem; right: 0.4rem; background: var(--surface);
  color: var(--text-muted); border: 1px solid var(--border); border-radius: 4px;
  padding: 0.2rem 0.5rem; font-size: 0.72rem; cursor: pointer; z-index: 2; }}
.copy-btn:hover {{ color: var(--accent); border-color: var(--accent-dim); }}
.copy-btn.copied {{ color: var(--green); border-color: var(--green); }}
.kql-comment {{ color: #6a9955; }}
.kql-keyword {{ color: #569cd6; font-weight: 600; }}
.kql-function {{ color: #dcdcaa; }}
.kql-string {{ color: #ce9178; }}
.kql-number {{ color: #b5cea8; }}
.kql-operator {{ color: #d4d4d4; }}

/* ── Validate Tab ── */
.validate-section {{ max-width: 1000px; margin: 0 auto; }}
.validate-section h2 {{ font-size: 1.2rem; margin-bottom: 0.5rem; }}
.validate-section p {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }}
.validate-steps {{ display: flex; flex-direction: column; gap: 1.5rem; }}
.step {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1.25rem; }}
.step-num {{ display: inline-flex; align-items: center; justify-content: center; width: 1.8rem;
  height: 1.8rem; border-radius: 50%; background: var(--accent-dim); color: #fff;
  font-weight: 700; font-size: 0.85rem; margin-right: 0.6rem; }}
.step h3 {{ display: inline; font-size: 1rem; vertical-align: middle; }}
.step .desc {{ color: var(--text-muted); font-size: 0.88rem; margin: 0.5rem 0 0.75rem; }}
.validate-kql {{ background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 0.85rem; font-family: 'SF Mono','Cascadia Code','Consolas',monospace;
  font-size: 0.78rem; line-height: 1.5; overflow-x: auto; white-space: pre; max-height: 500px;
  overflow-y: auto; color: var(--text); }}
.btn {{ background: var(--accent-dim); color: #fff; border: none; border-radius: 6px;
  padding: 0.5rem 1.2rem; font-size: 0.88rem; font-weight: 600; cursor: pointer; }}
.btn:hover {{ background: var(--accent); }}
.btn-outline {{ background: transparent; color: var(--accent); border: 1px solid var(--accent-dim); }}
.btn-outline:hover {{ background: var(--accent-dim); color: #fff; }}
.btn-green {{ background: rgba(63,185,80,0.15); color: var(--green); border: 1px solid rgba(63,185,80,0.3); }}
.btn-green:hover {{ background: var(--green); color: #fff; }}
.btn-sm {{ padding: 0.35rem 0.8rem; font-size: 0.8rem; }}

/* ── Dashboard ── */
.dashboard {{ display: none; margin-top: 1.5rem; }}
.dashboard.visible {{ display: block; }}
.dash-grid {{ display: grid; grid-template-columns: 280px 1fr; gap: 1.25rem; margin-bottom: 1.5rem; }}
.score-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1.5rem; text-align: center; }}
.score-ring {{ position: relative; width: 160px; height: 160px; margin: 0 auto 1rem; }}
.score-ring svg {{ transform: rotate(-90deg); }}
.score-ring .ring-bg {{ fill: none; stroke: var(--border); stroke-width: 12; }}
.score-ring .ring-fg {{ fill: none; stroke-width: 12; stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease, stroke 0.3s; }}
.score-value {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  font-size: 2.2rem; font-weight: 800; }}
.score-label {{ color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem; }}
.score-meta {{ display: flex; justify-content: center; gap: 1.5rem; margin-top: 0.75rem; }}
.score-meta .sm {{ text-align: center; }}
.score-meta .sm-val {{ font-size: 1.1rem; font-weight: 700; }}
.score-meta .sm-lbl {{ font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; }}

.family-bars {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1.25rem; }}
.family-bars h3 {{ font-size: 0.95rem; margin-bottom: 0.75rem; }}
.fbar {{ margin-bottom: 0.75rem; }}
.fbar-label {{ display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem; }}
.fbar-track {{ background: var(--bg); border-radius: 4px; height: 18px; overflow: hidden;
  border: 1px solid var(--border); }}
.fbar-fill {{ height: 100%; border-radius: 3px; transition: width 0.6s ease; min-width: 2px; }}

.practice-table {{ width: 100%; border-collapse: collapse; background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }}
.practice-table th {{ background: var(--surface2); text-align: left; padding: 0.6rem 0.9rem;
  font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border); }}
.practice-table td {{ padding: 0.55rem 0.9rem; font-size: 0.85rem;
  border-bottom: 1px solid var(--border); }}
.practice-table tr:last-child td {{ border-bottom: none; }}
.status-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.4rem;
  vertical-align: middle; }}
.status-green {{ background: var(--green); }}
.status-yellow {{ background: var(--orange); }}
.status-red {{ background: var(--red); }}
.missing-list {{ margin-top: 0.5rem; }}
.missing-item {{ background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
  padding: 0.6rem 0.9rem; margin-bottom: 0.4rem; font-size: 0.85rem; display: flex;
  justify-content: space-between; align-items: center; }}
.missing-item .controls {{ color: var(--text-muted); font-size: 0.78rem; }}
.export-bar {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1.25rem; align-items: center; }}

/* ── Contribute Tab ── */
.contribute-section {{ max-width: 900px; margin: 0 auto; }}
.contribute-section h2 {{ font-size: 1.2rem; margin-bottom: 0.5rem; }}
.contribute-section p {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }}
.form-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }}
.form-group {{ display: flex; flex-direction: column; gap: 0.3rem; }}
.form-group.full {{ grid-column: 1 / -1; }}
.form-group label {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.04em; font-weight: 600; }}
.form-group .hint {{ font-size: 0.75rem; color: var(--text-muted); }}
.form-group input, .form-group select, .form-group textarea {{ width: 100%; }}
.yaml-preview {{ background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 1rem; font-family: 'SF Mono','Cascadia Code','Consolas',monospace;
  font-size: 0.78rem; line-height: 1.5; white-space: pre; overflow-x: auto;
  max-height: 400px; overflow-y: auto; color: var(--green); }}
.action-bar {{ display: flex; gap: 0.75rem; margin-top: 1rem; flex-wrap: wrap; }}
.or-divider {{ color: var(--text-muted); font-size: 0.85rem; align-self: center; }}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .header {{ padding: 1rem; }}
  .main {{ padding: 1rem; }}
  .form-grid {{ grid-template-columns: 1fr; }}
  .tab {{ padding: 0.5rem 0.8rem; font-size: 0.82rem; }}
}}
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
</style>
</head>
<body>

<!-- ════════════ HEADER ════════════ -->
<div class="header">
  <h1>NIST 800-171 Rev.2 <span>Level 1</span> KQL Alignment</h1>
  <p class="subtitle">Community-driven Microsoft Sentinel &amp; Defender KQL queries mapped to NIST 800-171</p>
  <div class="stats">
    <div class="stat"><strong>{len(practices)}</strong> Practices</div>
    <div class="stat"><strong>{total_queries}</strong> KQL Queries</div>
    <div class="stat"><strong>{len(families)}</strong> Families</div>
    <div class="stat"><strong>{len(tables)}</strong> Tables</div>
  </div>
  <div class="tabs">
    <div class="tab active" onclick="switchTab('browse')">Browse</div>
    <div class="tab" onclick="switchTab('validate')">Validate Environment</div>
    <div class="tab" onclick="switchTab('contribute')">Contribute</div>
  </div>
</div>

<!-- ════════════ BROWSE TAB ════════════ -->
<div class="tab-panel active" id="panel-browse">
  <div class="filters">
    <div class="filter-group">
      <label>Family</label>
      <select id="filterFamily">
        <option value="">All Families</option>
        {family_options}
      </select>
    </div>
    <div class="filter-group">
      <label>Workload</label>
      <select id="filterWorkload">
        <option value="">All Workloads</option>
        {workload_options}
      </select>
    </div>
    <div class="filter-group">
      <label>Table</label>
      <select id="filterTable">
        <option value="">All Tables</option>
        {table_options}
      </select>
    </div>
    <div class="filter-group">
      <label>Search</label>
      <input type="text" id="filterSearch" placeholder="Control ID, name, KQL&hellip;">
    </div>
    <button class="clear-btn" onclick="clearFilters()">Clear All</button>
  </div>
  <div class="main">
    <div class="results-count" id="resultsCount"></div>
    <div id="practicesContainer"></div>
  </div>
</div>

<!-- ════════════ VALIDATE TAB ════════════ -->
<div class="tab-panel" id="panel-validate">
  <div class="main validate-section">
    <h2>Validate Your Sentinel Environment</h2>
    <p>Four-step closed loop: generate the check query, run it in Sentinel, paste the results back here, and get a full coverage dashboard with Power BI export.</p>

    <div class="validate-steps">
      <div class="step">
        <span class="step-num">1</span>
        <h3>Copy the validation query</h3>
        <p class="desc">This query checks all {len(tables)} tables referenced by the framework. It reports each table as <strong style="color:var(--green)">Present</strong> or <strong style="color:var(--red)">Missing</strong> along with the NIST controls that depend on it.</p>
        <div class="kql-wrapper">
          <button class="copy-btn" onclick="copyValidationKQL(this)">Copy KQL</button>
          <pre class="validate-kql" id="validationKQL"></pre>
        </div>
      </div>

      <div class="step">
        <span class="step-num">2</span>
        <h3>Run in Sentinel &amp; export CSV</h3>
        <p class="desc">Open <strong>Microsoft Sentinel</strong> &rarr; <strong>Logs</strong> blade &rarr; paste the query &rarr; click <strong>Run</strong>.<br>
        Once results appear, click <strong>Export</strong> (top-right of results) &rarr; <strong>Export to CSV - All columns</strong>.</p>
      </div>

      <div class="step">
        <span class="step-num">3</span>
        <h3>Paste your results</h3>
        <p class="desc">Open the downloaded CSV in any text editor, select all, and paste it below. Or drag-and-drop the CSV file onto the box.</p>
        <textarea id="csvInput" rows="8" placeholder="Paste CSV contents here...&#10;&#10;TableName,Status,NistControls&#10;SigninLogs,Present,&quot;3.1.1, 3.1.2&quot;&#10;DeviceEvents,Missing,&quot;3.1.20&quot;&#10;..."></textarea>
        <div style="display:flex;gap:0.75rem;margin-top:0.75rem;align-items:center;">
          <button class="btn" onclick="analyzeCSV()">Analyze Coverage</button>
          <span style="color:var(--text-muted);font-size:0.82rem;" id="csvStatus"></span>
        </div>
      </div>

      <div class="step">
        <span class="step-num">4</span>
        <h3>Coverage Dashboard</h3>
        <p class="desc">Your environment coverage report, generated from the Sentinel results.</p>

        <div class="dashboard" id="dashboard">
          <div class="dash-grid">
            <div class="score-card">
              <div class="score-ring">
                <svg viewBox="0 0 160 160" width="160" height="160">
                  <circle class="ring-bg" cx="80" cy="80" r="70"/>
                  <circle class="ring-fg" id="ringFg" cx="80" cy="80" r="70"
                    stroke-dasharray="439.82" stroke-dashoffset="439.82"/>
                </svg>
                <div class="score-value" id="scoreValue">--</div>
              </div>
              <div class="score-label">Table Coverage</div>
              <div class="score-meta">
                <div class="sm"><div class="sm-val" id="smPresent" style="color:var(--green)">0</div><div class="sm-lbl">Present</div></div>
                <div class="sm"><div class="sm-val" id="smMissing" style="color:var(--red)">0</div><div class="sm-lbl">Missing</div></div>
                <div class="sm"><div class="sm-val" id="smTotal" style="color:var(--accent)">0</div><div class="sm-lbl">Total</div></div>
              </div>
            </div>

            <div class="family-bars">
              <h3>Coverage by NIST Family</h3>
              <div id="familyBars"></div>
            </div>
          </div>

          <h3 style="margin-bottom:0.75rem;">Practice-Level Status</h3>
          <div style="overflow-x:auto;">
            <table class="practice-table">
              <thead>
                <tr><th>Control</th><th>Name</th><th>Family</th><th>Status</th><th>Tables Present</th><th>Tables Missing</th></tr>
              </thead>
              <tbody id="practiceRows"></tbody>
            </table>
          </div>

          <div id="missingSection" style="margin-top:1.5rem;"></div>

          <div class="export-bar">
            <button class="btn btn-outline" onclick="exportPowerBI()">Export Power BI (M Query)</button>
            <button class="btn btn-outline" onclick="exportCoverageCSV()">Export Coverage CSV</button>
            <button class="btn btn-outline" onclick="printReport()">Print Report</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ════════════ CONTRIBUTE TAB ════════════ -->
<div class="tab-panel" id="panel-contribute">
  <div class="main contribute-section">
    <h2>Add a New KQL Alignment</h2>
    <p>Fill out the form below. When you're done, you can submit it as a GitHub Issue (no Git required) or copy the generated YAML to open a Pull Request.</p>

    <div class="form-grid">
      <div class="form-group">
        <label>NIST 800-171 Control *</label>
        <select id="cControl">
          <option value="">Select a control&hellip;</option>
        </select>
      </div>
      <div class="form-group">
        <label>Microsoft Product *</label>
        <input type="text" id="cProduct" placeholder="e.g., Entra ID">
      </div>
      <div class="form-group">
        <label>Workload *</label>
        <input type="text" id="cWorkload" placeholder="e.g., Entra">
      </div>
      <div class="form-group">
        <label>Table *</label>
        <input type="text" id="cTable" placeholder="e.g., SigninLogs">
      </div>
      <div class="form-group">
        <label>Function</label>
        <select id="cFunction">
          <option value="">Select&hellip;</option>
          <option>Identity</option>
          <option>Device</option>
          <option>Network</option>
          <option>Cloud</option>
          <option>Data</option>
        </select>
        <span class="hint">M-21-31 function category</span>
      </div>
      <div class="form-group">
        <label>Category</label>
        <input type="text" id="cCategory" placeholder="e.g., Identity & Credential Management">
      </div>
      <div class="form-group">
        <label>Workload Integration URL</label>
        <input type="text" id="cIntegration" placeholder="https://learn.microsoft.com/...">
      </div>
      <div class="form-group">
        <label>Event Reference URL</label>
        <input type="text" id="cEventRef" placeholder="https://learn.microsoft.com/...">
      </div>
      <div class="form-group full">
        <label>KQL Query *</label>
        <textarea id="cKQL" rows="18" placeholder="// Objective: What this query detects&#10;//&#10;// ----- Part 0: Analyst-Driven Targeting -----&#10;let TargetUsers = dynamic([]);&#10;//&#10;// ----- Part 1: Base Filter -----&#10;TableName&#10;| where TimeGenerated > ago(30d)&#10;// ..."></textarea>
      </div>
    </div>

    <h3 style="margin-bottom:0.5rem;">Generated YAML Preview</h3>
    <pre class="yaml-preview" id="yamlPreview">Fill in the form above to see the YAML output here...</pre>

    <div class="action-bar">
      <button class="btn" onclick="submitAsIssue()">Open as GitHub Issue</button>
      <span class="or-divider">or</span>
      <button class="btn btn-outline" onclick="copyYAML()">Copy YAML</button>
      <span class="or-divider">or</span>
      <button class="btn btn-green" onclick="openPREditor()">Edit on GitHub &rarr;</button>
    </div>
  </div>
</div>

<!-- ════════════ SCRIPTS ════════════ -->
<script>
const DATA = {data_json};
const ALL_TABLES = {all_tables_json};
const GITHUB_REPO = '{GITHUB_REPO}';

// ─── Tab switching ───
function switchTab(name) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`.tab-panel#panel-${{name}}`).classList.add('active');
  event.target.classList.add('active');
  if (name === 'validate') buildValidationKQL();
  if (name === 'contribute') populateControlDropdown();
}}

// ─── KQL syntax highlighter (single-pass tokenizer) ───
const KQL_KEYWORDS = new Set([
  'let','where','extend','project','summarize','join','union','take','limit',
  'top','sort','order','by','on','in','has','contains','startswith','endswith',
  'matches','regex','between','ago','now','datetime','timespan','bin','count',
  'dcount','sum','avg','min','max','make_list','make_set','mv_expand',
  'parse_json','tostring','toint','tolong','todouble','tobool','todatetime',
  'iff','iif','case','not','and','or','distinct','render','as','asc','desc',
  'isfuzzy','true','false','dynamic','array_length','strlen','strcat',
  'parse','evaluate','datatable','print','getschema','toscalar','set',
  'materialize','range','invoke','external','with','pack','bag_unpack',
  'mv-apply','mv-expand','arg_max','arg_min','percentile','stdev','variance',
  'format_datetime','format_timespan','extract','replace','split','trim',
  'tolower','toupper','indexof','substring','isempty','isnotempty','isnull',
  'isnotnull','coalesce','ingestion_time','column_ifexists'
]);

function escHtml(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function highlightKQL(code) {{
  const lines = code.split('\\n');
  const result = [];
  for (const line of lines) {{
    const trimmed = line.trimStart();
    if (trimmed.startsWith('//')) {{ result.push('<span class="kql-comment">' + escHtml(line) + '</span>'); continue; }}
    let out = ''; let i = 0;
    while (i < line.length) {{
      const ch = line[i];
      if (ch === '/' && line[i+1] === '/') {{ out += '<span class="kql-comment">' + escHtml(line.slice(i)) + '</span>'; break; }}
      if (ch === '"' || ch === "'") {{
        let j = i+1; while (j < line.length && line[j] !== ch) {{ if (line[j]==='\\\\') j++; j++; }} j++;
        out += '<span class="kql-string">' + escHtml(line.slice(i,j)) + '</span>'; i=j; continue;
      }}
      if (ch === '|') {{ out += '<span class="kql-operator">|</span>'; i++; continue; }}
      if (/[a-zA-Z_]/.test(ch)) {{
        let j=i+1; while (j<line.length && /[a-zA-Z0-9_]/.test(line[j])) j++;
        const word = line.slice(i,j); let k=j; while(k<line.length && line[k]===' ') k++;
        if (KQL_KEYWORDS.has(word.toLowerCase())) out += '<span class="kql-keyword">' + escHtml(word) + '</span>';
        else if (line[k]==='(') out += '<span class="kql-function">' + escHtml(word) + '</span>';
        else out += escHtml(word);
        i=j; continue;
      }}
      if (/[0-9]/.test(ch)) {{
        let j=i+1; while(j<line.length && /[0-9.]/.test(line[j])) j++;
        const sfx = line.slice(j).match(/^(ms|tick|[dhms])/); if(sfx) j+=sfx[0].length;
        out += '<span class="kql-number">' + escHtml(line.slice(i,j)) + '</span>'; i=j; continue;
      }}
      out += escHtml(ch); i++;
    }}
    result.push(out);
  }}
  return result.join('\\n');
}}

function esc(s) {{ const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }}

// ─── Browse Tab ───
function renderPractices() {{
  const container = document.getElementById('practicesContainer');
  const family = document.getElementById('filterFamily').value;
  const workload = document.getElementById('filterWorkload').value;
  const table = document.getElementById('filterTable').value;
  const search = document.getElementById('filterSearch').value.toLowerCase();
  let html = '', visP = 0, visA = 0;
  DATA.forEach((p, pi) => {{
    if (family && p.family !== family) return;
    const fa = p.alignments.filter(a => {{
      if (workload && a.workload !== workload) return false;
      if (table && a.table !== table) return false;
      if (search) {{
        const h = (p.control+' '+p.name+' '+p.family+' '+a.workload+' '+a.table+' '+a.kql+' '+(a.function||'')+' '+(a.category||'')+' '+(p.nist_800_53||'')).toLowerCase();
        if (!h.includes(search)) return false;
      }}
      return true;
    }});
    if (!fa.length) return;
    visP++; visA += fa.length;
    const n53 = p.nist_800_53 ? `<span class="pill pill-53">${{esc(p.nist_800_53)}}</span>` : '';
    html += `<div class="practice" data-idx="${{pi}}">
      <div class="practice-header" onclick="togglePractice(this)">
        <span class="chevron">&#9654;</span>
        <span class="control-id">${{esc(p.control)}}</span>
        <span class="control-name">${{esc(p.name)}}</span>
        <span class="pill pill-family">${{esc(p.family)}}</span>
        ${{n53}}
        <span class="pill pill-count">${{fa.length}} quer${{fa.length===1?'y':'ies'}}</span>
      </div><div class="practice-body">`;
    fa.forEach((a, ai) => {{
      const uid = `kql_${{pi}}_${{ai}}`;
      const iLink = a.workload_integration ? `<a href="${{esc(a.workload_integration)}}" target="_blank">&#128279; Integration</a>` : '';
      const eLink = a.event_reference ? `<a href="${{esc(a.event_reference)}}" target="_blank">&#128203; Reference</a>` : '';
      html += `<div class="alignment">
        <div class="alignment-meta">
          ${{a.workload ? `<span class="meta-tag"><strong>Workload:</strong> ${{esc(a.workload)}}</span>` : ''}}
          <span class="meta-tag"><strong>Table:</strong> ${{esc(a.table)}}</span>
          ${{a.function ? `<span class="meta-tag"><strong>Function:</strong> ${{esc(a.function)}}</span>` : ''}}
          ${{a.category ? `<span class="meta-tag"><strong>Category:</strong> ${{esc(a.category)}}</span>` : ''}}
        </div>
        ${{(iLink||eLink) ? `<div class="meta-links">${{iLink}}${{eLink}}</div>` : ''}}
        <div class="kql-wrapper">
          <button class="copy-btn" onclick="copyEl('${{uid}}',this)">Copy</button>
          <pre class="kql-block" id="${{uid}}">${{highlightKQL(a.kql)}}</pre>
        </div>
      </div>`;
    }});
    html += `</div></div>`;
  }});
  container.innerHTML = html || '<p style="color:var(--text-muted);text-align:center;padding:3rem;">No results match your filters.</p>';
  document.getElementById('resultsCount').textContent = `Showing ${{visP}} practice${{visP!==1?'s':''}} with ${{visA}} KQL quer${{visA!==1?'ies':'y'}}`;
}}

function togglePractice(el) {{ el.parentElement.classList.toggle('open'); }}
function clearFilters() {{
  ['filterFamily','filterWorkload','filterTable','filterSearch'].forEach(id => document.getElementById(id).value = '');
  renderPractices();
}}

function copyEl(id, btn) {{
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = 'Copied!'; btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

// ─── Validate Tab ───
function buildValidationKQL() {{
  const tableMap = {{}};
  DATA.forEach(p => {{
    p.alignments.forEach(a => {{
      if (!tableMap[a.table]) tableMap[a.table] = new Set();
      tableMap[a.table].add(p.control);
    }});
  }});
  const tbl = Object.keys(tableMap).sort();
  let kql = '// NIST 800-171 Environment Validation Query\\n';
  kql += '// Checks all ' + tbl.length + ' tables required by the alignment framework\\n';
  kql += '// Paste into Sentinel Logs blade > Run > Export to CSV\\n//\\n';
  kql += 'let ValidationResults = datatable(TableName:string, NistControls:string) [\\n';
  tbl.forEach((t, i) => {{
    const controls = Array.from(tableMap[t]).sort().join(', ');
    kql += '    "' + t + '", "' + controls + '"' + (i < tbl.length-1 ? ',' : '') + '\\n';
  }});
  kql += '];\\n';
  kql += '// Check each table for data in last 30 days\\n';
  kql += 'union isfuzzy=true\\n';
  tbl.forEach((t, i) => {{
    const controls = Array.from(tableMap[t]).sort().join(', ');
    kql += '    (' + t + '\\n';
    kql += '     | where TimeGenerated > ago(30d)\\n';
    kql += '     | take 1\\n';
    kql += '     | project TableName="' + t + '", Status="Present", NistControls="' + controls + '")' + (i < tbl.length-1 ? ',' : '') + '\\n';
  }});
  kql += '| union (\\n';
  kql += '    ValidationResults\\n';
  kql += '    | where TableName !in (\\n';
  kql += '        union isfuzzy=true\\n';
  tbl.forEach((t, i) => {{
    kql += '            (' + t + ' | take 1 | project v="' + t + '")' + (i < tbl.length-1 ? ',' : '') + '\\n';
  }});
  kql += '        | distinct v\\n';
  kql += '    )\\n';
  kql += '    | project TableName, Status="Missing", NistControls\\n';
  kql += ')\\n';
  kql += '| sort by Status asc, TableName asc';
  document.getElementById('validationKQL').textContent = kql;
}}

function copyValidationKQL(btn) {{
  navigator.clipboard.writeText(document.getElementById('validationKQL').textContent).then(() => {{
    btn.textContent = 'Copied!'; btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy KQL'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

// ─── CSV Analysis ───
function parseCSV(raw) {{
  const lines = raw.trim().split(/\\r?\\n/);
  if (lines.length < 2) return [];
  // Parse header
  const hdr = parseCSVLine(lines[0]).map(h => h.trim().replace(/^\\uFEFF/, ''));
  const iName = hdr.findIndex(h => /tablename/i.test(h));
  const iStatus = hdr.findIndex(h => /status/i.test(h));
  const iControls = hdr.findIndex(h => /nistcontrols|controls/i.test(h));
  if (iName < 0 || iStatus < 0) return [];
  const rows = [];
  for (let i = 1; i < lines.length; i++) {{
    if (!lines[i].trim()) continue;
    const cols = parseCSVLine(lines[i]);
    rows.push({{
      table: (cols[iName]||'').trim(),
      status: (cols[iStatus]||'').trim(),
      controls: iControls >= 0 ? (cols[iControls]||'').trim() : ''
    }});
  }}
  return rows;
}}

function parseCSVLine(line) {{
  const cols = []; let cur = ''; let inQ = false;
  for (let i = 0; i < line.length; i++) {{
    const ch = line[i];
    if (inQ) {{
      if (ch === '"' && line[i+1] === '"') {{ cur += '"'; i++; }}
      else if (ch === '"') inQ = false;
      else cur += ch;
    }} else {{
      if (ch === '"') inQ = true;
      else if (ch === ',') {{ cols.push(cur); cur = ''; }}
      else cur += ch;
    }}
  }}
  cols.push(cur);
  return cols;
}}

function analyzeCSV() {{
  const raw = document.getElementById('csvInput').value;
  const rows = parseCSV(raw);
  const statusEl = document.getElementById('csvStatus');
  if (!rows.length) {{
    statusEl.textContent = 'Could not parse CSV. Ensure it has TableName and Status columns.';
    statusEl.style.color = 'var(--red)';
    return;
  }}
  statusEl.textContent = 'Parsed ' + rows.length + ' rows.';
  statusEl.style.color = 'var(--green)';
  renderDashboard(rows);
}}

function renderDashboard(rows) {{
  const dash = document.getElementById('dashboard');
  dash.classList.add('visible');

  // Build lookup: table → status
  const tableStatus = {{}};
  rows.forEach(r => {{ tableStatus[r.table] = r.status.toLowerCase() === 'present'; }});

  // Also map ALL expected tables from DATA (in case Sentinel didn't return some)
  const expectedTables = new Set();
  DATA.forEach(p => p.alignments.forEach(a => expectedTables.add(a.table)));

  const present = rows.filter(r => r.status.toLowerCase() === 'present').length;
  const missing = rows.filter(r => r.status.toLowerCase() !== 'present').length;
  const total = rows.length;
  const pct = total > 0 ? Math.round((present / total) * 100) : 0;

  // Score ring
  const circ = 2 * Math.PI * 70; // ~439.82
  const offset = circ - (circ * pct / 100);
  const ring = document.getElementById('ringFg');
  ring.style.strokeDashoffset = offset;
  ring.style.stroke = pct >= 80 ? 'var(--green)' : pct >= 50 ? 'var(--orange)' : 'var(--red)';
  document.getElementById('scoreValue').textContent = pct + '%';
  document.getElementById('scoreValue').style.color = pct >= 80 ? 'var(--green)' : pct >= 50 ? 'var(--orange)' : 'var(--red)';
  document.getElementById('smPresent').textContent = present;
  document.getElementById('smMissing').textContent = missing;
  document.getElementById('smTotal').textContent = total;

  // Family bars
  const familyStats = {{}};
  DATA.forEach(p => {{
    const fam = p.family;
    if (!familyStats[fam]) familyStats[fam] = {{ present: new Set(), missing: new Set(), total: new Set() }};
    p.alignments.forEach(a => {{
      familyStats[fam].total.add(a.table);
      if (tableStatus[a.table] === true) familyStats[fam].present.add(a.table);
      else if (tableStatus[a.table] === false) familyStats[fam].missing.add(a.table);
      else familyStats[fam].missing.add(a.table); // unknown = missing
    }});
  }});

  let barsHtml = '';
  Object.keys(familyStats).sort().forEach(f => {{
    const s = familyStats[f];
    const fp = s.present.size;
    const ft = s.total.size;
    const fpct = ft > 0 ? Math.round((fp / ft) * 100) : 0;
    const color = fpct >= 80 ? 'var(--green)' : fpct >= 50 ? 'var(--orange)' : 'var(--red)';
    barsHtml += '<div class="fbar">';
    barsHtml += '<div class="fbar-label"><span>' + esc(f) + '</span><span style="font-weight:600;color:' + color + '">' + fp + '/' + ft + ' (' + fpct + '%)</span></div>';
    barsHtml += '<div class="fbar-track"><div class="fbar-fill" style="width:' + fpct + '%;background:' + color + '"></div></div>';
    barsHtml += '</div>';
  }});
  document.getElementById('familyBars').innerHTML = barsHtml;

  // Practice-level table
  let trows = '';
  DATA.forEach(p => {{
    const pTables = p.alignments.map(a => a.table);
    const unique = [...new Set(pTables)];
    const pres = unique.filter(t => tableStatus[t] === true);
    const miss = unique.filter(t => tableStatus[t] !== true);
    let dot, label;
    if (miss.length === 0) {{ dot = 'status-green'; label = 'Full Coverage'; }}
    else if (pres.length > 0) {{ dot = 'status-yellow'; label = 'Partial'; }}
    else {{ dot = 'status-red'; label = 'No Coverage'; }}
    trows += '<tr>';
    trows += '<td style="font-family:monospace;color:var(--accent);font-weight:600">' + esc(p.control) + '</td>';
    trows += '<td>' + esc(p.name) + '</td>';
    trows += '<td>' + esc(p.family) + '</td>';
    trows += '<td><span class="status-dot ' + dot + '"></span>' + label + '</td>';
    trows += '<td style="color:var(--green)">' + pres.join(', ') + '</td>';
    trows += '<td style="color:var(--red)">' + (miss.length ? miss.join(', ') : '—') + '</td>';
    trows += '</tr>';
  }});
  document.getElementById('practiceRows').innerHTML = trows;

  // Missing tables section
  const missingTables = rows.filter(r => r.status.toLowerCase() !== 'present');
  let missHtml = '';
  if (missingTables.length) {{
    missHtml += '<h3 style="margin-bottom:0.5rem;color:var(--red)">Missing Tables (' + missingTables.length + ')</h3>';
    missHtml += '<p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:0.75rem;">These tables need data connectors or integrations enabled to achieve full coverage.</p>';
    missHtml += '<div class="missing-list">';
    missingTables.sort((a,b) => a.table.localeCompare(b.table)).forEach(r => {{
      missHtml += '<div class="missing-item"><span style="font-family:monospace;font-weight:600;color:var(--red)">' + esc(r.table) + '</span><span class="controls">Used by: ' + esc(r.controls) + '</span></div>';
    }});
    missHtml += '</div>';
  }}
  document.getElementById('missingSection').innerHTML = missHtml;

  // Store for export
  window._coverageData = {{ rows, tableStatus, familyStats, pct, present, missing, total }};
}}

// ─── Exports ───
function exportPowerBI() {{
  if (!window._coverageData) {{ alert('Analyze your CSV first.'); return; }}
  const d = window._coverageData;
  let mquery = 'let\\n';
  mquery += '    Source = Table.FromRows(\\n';
  mquery += '        {{\\n';
  d.rows.forEach((r, i) => {{
    mquery += '            {{\"' + r.table + '\", \"' + r.status + '\", \"' + r.controls.replace(/"/g, '""') + '\"}}' + (i < d.rows.length-1 ? ',' : '') + '\\n';
  }});
  mquery += '        }},\\n';
  mquery += '        type table [TableName = Text.Type, Status = Text.Type, NistControls = Text.Type]\\n';
  mquery += '    ),\\n';
  mquery += '    StatusColor = Table.AddColumn(Source, \"StatusColor\", each if [Status] = \"Present\" then \"Green\" else \"Red\"),\\n';
  mquery += '    Coverage = Table.AddColumn(StatusColor, \"CoverageValue\", each if [Status] = \"Present\" then 1 else 0)\\n';
  mquery += 'in\\n';
  mquery += '    Coverage';

  const blob = new Blob([mquery], {{type: 'text/plain'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'NIST_Coverage_PowerBI.m';
  a.click();
  URL.revokeObjectURL(a.href);
}}

function exportCoverageCSV() {{
  if (!window._coverageData) {{ alert('Analyze your CSV first.'); return; }}
  let csv = 'Control,Name,Family,Status,TablesPresent,TablesMissing\\n';
  DATA.forEach(p => {{
    const ts = window._coverageData.tableStatus;
    const unique = [...new Set(p.alignments.map(a => a.table))];
    const pres = unique.filter(t => ts[t] === true).join('; ');
    const miss = unique.filter(t => ts[t] !== true).join('; ');
    const status = miss ? (pres ? 'Partial' : 'No Coverage') : 'Full Coverage';
    csv += '"' + p.control + '","' + p.name + '","' + p.family + '","' + status + '","' + pres + '","' + miss + '"\\n';
  }});
  const blob = new Blob([csv], {{type: 'text/csv'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'NIST_Coverage_Report.csv';
  a.click();
  URL.revokeObjectURL(a.href);
}}

function printReport() {{
  if (!window._coverageData) {{ alert('Analyze your CSV first.'); return; }}
  const d = window._coverageData;
  let html = '<html><head><title>NIST 800-171 Coverage Report</title>';
  html += '<style>body{{font-family:Segoe UI,sans-serif;padding:2rem;max-width:1000px;margin:0 auto}}';
  html += 'table{{width:100%;border-collapse:collapse;margin:1rem 0}}th,td{{border:1px solid #ccc;padding:0.5rem;text-align:left;font-size:0.85rem}}';
  html += 'th{{background:#f0f0f0}}h1{{font-size:1.4rem}}h2{{font-size:1.1rem;margin-top:1.5rem}}';
  html += '.green{{color:#2da44e}}.red{{color:#cf222e}}.yellow{{color:#bf8700}}</style></head><body>';
  html += '<h1>NIST 800-171 Rev.2 Level 1 - Environment Coverage Report</h1>';
  html += '<p>Generated: ' + new Date().toISOString().slice(0,10) + '</p>';
  html += '<h2>Summary: ' + d.pct + '% Table Coverage (' + d.present + '/' + d.total + ')</h2>';
  html += '<table><tr><th>Control</th><th>Name</th><th>Family</th><th>Status</th><th>Present</th><th>Missing</th></tr>';
  DATA.forEach(p => {{
    const unique = [...new Set(p.alignments.map(a => a.table))];
    const pres = unique.filter(t => d.tableStatus[t] === true);
    const miss = unique.filter(t => d.tableStatus[t] !== true);
    const cls = miss.length === 0 ? 'green' : pres.length > 0 ? 'yellow' : 'red';
    const label = miss.length === 0 ? 'Full' : pres.length > 0 ? 'Partial' : 'None';
    html += '<tr><td>' + p.control + '</td><td>' + p.name + '</td><td>' + p.family + '</td>';
    html += '<td class="' + cls + '">' + label + '</td><td>' + pres.join(', ') + '</td><td class="red">' + miss.join(', ') + '</td></tr>';
  }});
  html += '</table></body></html>';
  const w = window.open('', '_blank');
  w.document.write(html);
  w.document.close();
  w.print();
}}

// ─── Contribute Tab ───
let controlDropdownPopulated = false;

function populateControlDropdown() {{
  if (controlDropdownPopulated) return;
  const sel = document.getElementById('cControl');
  DATA.forEach(p => {{
    const opt = document.createElement('option');
    opt.value = p.control;
    opt.textContent = p.control + ' — ' + p.name;
    sel.appendChild(opt);
  }});
  controlDropdownPopulated = true;
}}

function generateYAML() {{
  const control = document.getElementById('cControl').value;
  const product = document.getElementById('cProduct').value.trim();
  const workload = document.getElementById('cWorkload').value.trim();
  const table = document.getElementById('cTable').value.trim();
  const func = document.getElementById('cFunction').value;
  const category = document.getElementById('cCategory').value.trim();
  const integration = document.getElementById('cIntegration').value.trim();
  const eventRef = document.getElementById('cEventRef').value.trim();
  const kql = document.getElementById('cKQL').value;

  if (!control || !product || !workload || !table || !kql.trim()) {{
    return 'Fill in all required fields (*) to generate YAML...';
  }}

  // Find practice info
  const practice = DATA.find(p => p.control === control);
  let yaml = '';
  yaml += '  # New alignment added via web form\\n';
  yaml += '  - product: "' + product + '"\\n';
  if (func) yaml += '    function: "' + func + '"\\n';
  if (category) yaml += '    category: "' + category + '"\\n';
  yaml += '    workload: "' + workload + '"\\n';
  yaml += '    table: "' + table + '"\\n';
  if (integration) yaml += '    workload_integration: "' + integration + '"\\n';
  if (eventRef) yaml += '    event_reference: "' + eventRef + '"\\n';
  yaml += '    kql: |\\n';
  kql.split('\\n').forEach(line => {{
    yaml += '      ' + line + '\\n';
  }});

  return yaml;
}}

function updateYAMLPreview() {{
  document.getElementById('yamlPreview').textContent = generateYAML();
}}

function submitAsIssue() {{
  const control = document.getElementById('cControl').value;
  const product = document.getElementById('cProduct').value.trim();
  const table = document.getElementById('cTable').value.trim();
  const kql = document.getElementById('cKQL').value;
  const workload = document.getElementById('cWorkload').value.trim();
  const func = document.getElementById('cFunction').value;
  const category = document.getElementById('cCategory').value.trim();

  if (!control || !product || !table || !kql.trim()) {{
    alert('Please fill in all required fields (Control, Product, Workload, Table, KQL)');
    return;
  }}

  const title = encodeURIComponent(`[Alignment] NIST ${{control}} - ${{table}}`);
  const practice = DATA.find(p => p.control === control);
  const practiceName = practice ? practice.name : '';

  let body = `## NIST Control\\n\\n`;
  body += `**Control Number:** ${{control}}\\n`;
  body += `**Control Name:** ${{practiceName}}\\n\\n`;
  body += `## Proposed Alignment\\n\\n`;
  body += `**Microsoft Product:** ${{product}}\\n`;
  body += `**Workload:** ${{workload}}\\n`;
  body += `**Table:** ${{table}}\\n`;
  if (func) body += `**Function:** ${{func}}\\n`;
  if (category) body += `**Category:** ${{category}}\\n`;
  const tick = String.fromCharCode(96);
  body += '\\n## KQL Query\\n\\n' + tick+tick+tick + 'kql\\n' + kql + '\\n' + tick+tick+tick + '\\n\\n';
  body += '## Generated YAML\\n\\n' + tick+tick+tick + 'yaml\\n' + generateYAML() + '\\n' + tick+tick+tick + '\\n';

  const url = `https://github.com/${{GITHUB_REPO}}/issues/new?title=${{title}}&body=${{encodeURIComponent(body)}}&labels=enhancement,community-contribution`;
  window.open(url, '_blank');
}}

function copyYAML() {{
  const yaml = generateYAML();
  navigator.clipboard.writeText(yaml).then(() => {{
    alert('YAML copied to clipboard! Open a PR on GitHub and paste this into the practice file.');
  }});
}}

function openPREditor() {{
  const control = document.getElementById('cControl').value;
  if (!control) {{ alert('Please select a control first.'); return; }}
  const url = `https://github.com/${{GITHUB_REPO}}/edit/main/practices/${{control}}.yaml`;
  window.open(url, '_blank');
}}

// ─── Event bindings ───
['filterFamily','filterWorkload','filterTable'].forEach(id =>
  document.getElementById(id).addEventListener('change', renderPractices));
document.getElementById('filterSearch').addEventListener('input', renderPractices);

// Update YAML preview on any form change
['cControl','cProduct','cWorkload','cTable','cFunction','cCategory','cIntegration','cEventRef','cKQL'].forEach(id =>
  document.getElementById(id).addEventListener('input', updateYAMLPreview));
['cControl','cFunction'].forEach(id =>
  document.getElementById(id).addEventListener('change', updateYAMLPreview));

// CSV drag-and-drop
const csvBox = document.getElementById('csvInput');
csvBox.addEventListener('dragover', e => {{ e.preventDefault(); csvBox.style.borderColor = 'var(--accent)'; }});
csvBox.addEventListener('dragleave', () => {{ csvBox.style.borderColor = 'var(--border)'; }});
csvBox.addEventListener('drop', e => {{
  e.preventDefault(); csvBox.style.borderColor = 'var(--border)';
  const file = e.dataTransfer.files[0];
  if (file) {{
    const reader = new FileReader();
    reader.onload = ev => {{ csvBox.value = ev.target.result; analyzeCSV(); }};
    reader.readAsText(file);
  }}
}});

// Initial render
renderPractices();
</script>
</body>
</html>"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    practices, families, tables, workloads = load_practices()
    page = build_html(practices, families, tables, workloads)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"Built {OUTPUT_FILE} - {len(practices)} practices, "
          f"{sum(len(p['alignments']) for p in practices)} queries")


if __name__ == "__main__":
    main()
