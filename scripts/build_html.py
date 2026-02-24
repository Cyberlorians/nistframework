#!/usr/bin/env python3
"""
build_html.py - Generate an interactive HTML reference page from practice YAMLs.
Output: output/index.html
"""
import os
import json
import yaml
import html as html_mod

PRACTICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "practices")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")


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
    """Generate the full HTML page."""
    # Embed practice data as JSON for client-side filtering
    data_json = json.dumps(practices, indent=None)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NIST 800-171 Rev.2 &mdash; Level 1 KQL Alignment</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #1c2333;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-dim: #1f6feb;
    --green: #3fb950;
    --orange: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
    --radius: 8px;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 0;
  }}
  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1a1f35 0%, #0d1117 100%);
    border-bottom: 1px solid var(--border);
    padding: 2rem 2rem 1.5rem;
  }}
  .header h1 {{
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }}
  .header h1 span {{ color: var(--accent); }}
  .header .subtitle {{
    color: var(--text-muted);
    font-size: 0.95rem;
  }}
  .stats {{
    display: flex;
    gap: 1.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
  }}
  .stat {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }}
  .stat strong {{
    color: var(--accent);
    font-size: 1.2rem;
    margin-right: 0.35rem;
  }}
  /* ── Filters ── */
  .filters {{
    display: flex;
    gap: 1rem;
    padding: 1rem 2rem;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    align-items: center;
  }}
  .filters label {{
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .filter-group {{
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }}
  select, input[type="text"] {{
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.45rem 0.75rem;
    font-size: 0.9rem;
    min-width: 180px;
    cursor: pointer;
  }}
  select:hover, input[type="text"]:hover {{
    border-color: var(--accent-dim);
  }}
  select:focus, input[type="text"]:focus {{
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(88,166,255,0.2);
  }}
  .clear-btn {{
    background: transparent;
    color: var(--text-muted);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.45rem 0.9rem;
    font-size: 0.85rem;
    cursor: pointer;
    align-self: flex-end;
  }}
  .clear-btn:hover {{ color: var(--accent); border-color: var(--accent-dim); }}
  /* ── Main ── */
  .main {{
    padding: 1.5rem 2rem 3rem;
    max-width: 1400px;
    margin: 0 auto;
  }}
  .results-count {{
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1rem;
  }}
  /* ── Practice Card ── */
  .practice {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 1rem;
    overflow: hidden;
  }}
  .practice-header {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
  }}
  .practice-header:hover {{
    background: var(--surface2);
  }}
  .practice-header .chevron {{
    color: var(--text-muted);
    font-size: 0.75rem;
    transition: transform 0.2s;
    flex-shrink: 0;
  }}
  .practice.open .chevron {{
    transform: rotate(90deg);
  }}
  .control-id {{
    font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
    font-weight: 700;
    font-size: 1rem;
    color: var(--accent);
    min-width: 4.5rem;
  }}
  .control-name {{
    font-weight: 600;
    font-size: 0.95rem;
    flex: 1;
  }}
  .family-pill {{
    font-size: 0.75rem;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    background: var(--accent-dim);
    color: #fff;
    white-space: nowrap;
  }}
  .nist53-pill {{
    font-size: 0.75rem;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    background: rgba(188,140,255,0.15);
    color: var(--purple);
    border: 1px solid rgba(188,140,255,0.3);
    white-space: nowrap;
  }}
  .count-pill {{
    font-size: 0.75rem;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    background: rgba(63,185,80,0.15);
    color: var(--green);
    border: 1px solid rgba(63,185,80,0.3);
    white-space: nowrap;
  }}
  /* ── Alignments ── */
  .practice-body {{
    display: none;
    border-top: 1px solid var(--border);
  }}
  .practice.open .practice-body {{
    display: block;
  }}
  .alignment {{
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
  }}
  .alignment:last-child {{
    border-bottom: none;
  }}
  .alignment-meta {{
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 0.75rem;
    align-items: center;
  }}
  .meta-tag {{
    font-size: 0.78rem;
    padding: 0.15rem 0.55rem;
    border-radius: 4px;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text-muted);
  }}
  .meta-tag strong {{
    color: var(--text);
    font-weight: 600;
  }}
  .meta-links {{
    display: flex;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }}
  .meta-links a {{
    font-size: 0.8rem;
    color: var(--accent);
    text-decoration: none;
  }}
  .meta-links a:hover {{ text-decoration: underline; }}
  /* ── KQL Block ── */
  .kql-wrapper {{
    position: relative;
    margin-top: 0.5rem;
  }}
  .kql-block {{
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
    font-size: 0.82rem;
    line-height: 1.5;
    overflow-x: auto;
    white-space: pre;
    color: var(--text);
    max-height: 400px;
    overflow-y: auto;
  }}
  .copy-btn {{
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: var(--surface);
    color: var(--text-muted);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.25rem 0.6rem;
    font-size: 0.75rem;
    cursor: pointer;
    z-index: 2;
  }}
  .copy-btn:hover {{
    color: var(--accent);
    border-color: var(--accent-dim);
  }}
  .copy-btn.copied {{
    color: var(--green);
    border-color: var(--green);
  }}
  /* ── KQL Syntax Highlighting ── */
  .kql-comment {{ color: #6a9955; }}
  .kql-keyword {{ color: #569cd6; font-weight: 600; }}
  .kql-function {{ color: #dcdcaa; }}
  .kql-string {{ color: #ce9178; }}
  .kql-number {{ color: #b5cea8; }}
  .kql-operator {{ color: #d4d4d4; }}
  /* ── Responsive ── */
  @media (max-width: 768px) {{
    .header {{ padding: 1.25rem 1rem; }}
    .filters {{ padding: 0.75rem 1rem; }}
    .main {{ padding: 1rem; }}
    .practice-header {{ flex-wrap: wrap; }}
    select, input[type="text"] {{ min-width: 140px; }}
  }}
  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
  ::-webkit-scrollbar-track {{ background: var(--bg); }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
</style>
</head>
<body>

<div class="header">
  <h1>NIST 800-171 Rev.2 <span>Level 1</span> KQL Alignment</h1>
  <p class="subtitle">Interactive reference — Microsoft Sentinel &amp; Defender KQL queries mapped to each NIST practice</p>
  <div class="stats">
    <div class="stat"><strong>{len(practices)}</strong> Practices</div>
    <div class="stat"><strong>{sum(len(p['alignments']) for p in practices)}</strong> KQL Queries</div>
    <div class="stat"><strong>{len(families)}</strong> Families</div>
    <div class="stat"><strong>{len(tables)}</strong> Tables</div>
  </div>
</div>

<div class="filters">
  <div class="filter-group">
    <label>Family</label>
    <select id="filterFamily">
      <option value="">All Families</option>
      {"".join(f'<option value="{html_mod.escape(f)}">{html_mod.escape(f)}</option>' for f in families)}
    </select>
  </div>
  <div class="filter-group">
    <label>Workload</label>
    <select id="filterWorkload">
      <option value="">All Workloads</option>
      {"".join(f'<option value="{html_mod.escape(w)}">{html_mod.escape(w)}</option>' for w in workloads)}
    </select>
  </div>
  <div class="filter-group">
    <label>Table</label>
    <select id="filterTable">
      <option value="">All Tables</option>
      {"".join(f'<option value="{html_mod.escape(t)}">{html_mod.escape(t)}</option>' for t in tables)}
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

<script>
const DATA = {data_json};

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
  // Single-pass tokenizer — avoids regex passes corrupting each other's span tags
  const lines = code.split('\\n');
  const result = [];

  for (const line of lines) {{
    // Check if this is a comment line (// ...)
    const trimmed = line.trimStart();
    if (trimmed.startsWith('//')) {{
      result.push('<span class="kql-comment">' + escHtml(line) + '</span>');
      continue;
    }}

    // Tokenize the line character by character
    let out = '';
    let i = 0;
    while (i < line.length) {{
      const ch = line[i];

      // Inline comment
      if (ch === '/' && line[i+1] === '/') {{
        out += '<span class="kql-comment">' + escHtml(line.slice(i)) + '</span>';
        break;
      }}

      // String literals
      if (ch === '"' || ch === "'") {{
        let j = i + 1;
        while (j < line.length && line[j] !== ch) {{
          if (line[j] === '\\\\') j++; // skip escaped char
          j++;
        }}
        j++; // include closing quote
        out += '<span class="kql-string">' + escHtml(line.slice(i, j)) + '</span>';
        i = j;
        continue;
      }}

      // Pipe operator
      if (ch === '|') {{
        out += '<span class="kql-operator">|</span>';
        i++;
        continue;
      }}

      // Word tokens (keywords, identifiers, function names)
      if (/[a-zA-Z_]/.test(ch)) {{
        let j = i + 1;
        while (j < line.length && /[a-zA-Z0-9_]/.test(line[j])) j++;
        const word = line.slice(i, j);
        // Check for function call: word followed by (
        let k = j;
        while (k < line.length && line[k] === ' ') k++;
        if (KQL_KEYWORDS.has(word.toLowerCase())) {{
          out += '<span class="kql-keyword">' + escHtml(word) + '</span>';
        }} else if (line[k] === '(') {{
          out += '<span class="kql-function">' + escHtml(word) + '</span>';
        }} else {{
          out += escHtml(word);
        }}
        i = j;
        continue;
      }}

      // Numbers
      if (/[0-9]/.test(ch)) {{
        let j = i + 1;
        while (j < line.length && /[0-9.]/.test(line[j])) j++;
        // Optional time suffix
        const suffix = line.slice(j).match(/^(ms|tick|[dhms])/);
        if (suffix) j += suffix[0].length;
        out += '<span class="kql-number">' + escHtml(line.slice(i, j)) + '</span>';
        i = j;
        continue;
      }}

      // Everything else (operators, whitespace, punctuation)
      out += escHtml(ch);
      i++;
    }}
    result.push(out);
  }}
  return result.join('\\n');
}}

function renderPractices(filter) {{
  const container = document.getElementById('practicesContainer');
  const family = document.getElementById('filterFamily').value;
  const workload = document.getElementById('filterWorkload').value;
  const table = document.getElementById('filterTable').value;
  const search = document.getElementById('filterSearch').value.toLowerCase();

  let html = '';
  let visiblePractices = 0;
  let visibleAlignments = 0;

  DATA.forEach((p, pi) => {{
    // Family filter
    if (family && p.family !== family) return;

    // Filter alignments by workload/table/search
    const filteredAlignments = p.alignments.filter(a => {{
      if (workload && a.workload !== workload) return false;
      if (table && a.table !== table) return false;
      if (search) {{
        const haystack = (p.control + ' ' + p.name + ' ' + p.family + ' ' +
          a.workload + ' ' + a.table + ' ' + a.kql + ' ' + (a.function || '') +
          ' ' + (a.category || '') + ' ' + (p.nist_800_53 || '')).toLowerCase();
        if (!haystack.includes(search)) return false;
      }}
      return true;
    }});

    if (filteredAlignments.length === 0) return;

    visiblePractices++;
    visibleAlignments += filteredAlignments.length;

    const nist53 = p.nist_800_53
      ? `<span class="nist53-pill">${{esc(p.nist_800_53)}}</span>` : '';

    html += `
      <div class="practice" data-idx="${{pi}}">
        <div class="practice-header" onclick="togglePractice(this)">
          <span class="chevron">&#9654;</span>
          <span class="control-id">${{esc(p.control)}}</span>
          <span class="control-name">${{esc(p.name)}}</span>
          <span class="family-pill">${{esc(p.family)}}</span>
          ${{nist53}}
          <span class="count-pill">${{filteredAlignments.length}} quer${{filteredAlignments.length === 1 ? 'y' : 'ies'}}</span>
        </div>
        <div class="practice-body">`;

    filteredAlignments.forEach((a, ai) => {{
      const uid = `kql_${{pi}}_${{ai}}`;
      const integrationLink = a.workload_integration
        ? `<a href="${{esc(a.workload_integration)}}" target="_blank">&#128279; Integration Docs</a>` : '';
      const eventLink = a.event_reference
        ? `<a href="${{esc(a.event_reference)}}" target="_blank">&#128203; Event Reference</a>` : '';

      html += `
          <div class="alignment">
            <div class="alignment-meta">
              ${{a.workload ? `<span class="meta-tag"><strong>Workload:</strong> ${{esc(a.workload)}}</span>` : ''}}
              <span class="meta-tag"><strong>Table:</strong> ${{esc(a.table)}}</span>
              ${{a.function ? `<span class="meta-tag"><strong>Function:</strong> ${{esc(a.function)}}</span>` : ''}}
              ${{a.category ? `<span class="meta-tag"><strong>Category:</strong> ${{esc(a.category)}}</span>` : ''}}
            </div>
            ${{(integrationLink || eventLink) ? `<div class="meta-links">${{integrationLink}}${{eventLink}}</div>` : ''}}
            <div class="kql-wrapper">
              <button class="copy-btn" onclick="copyKQL('${{uid}}', this)">Copy</button>
              <pre class="kql-block" id="${{uid}}">${{highlightKQL(a.kql)}}</pre>
            </div>
          </div>`;
    }});

    html += `
        </div>
      </div>`;
  }});

  container.innerHTML = html || '<p style="color:var(--text-muted);text-align:center;padding:3rem;">No results match your filters.</p>';
  document.getElementById('resultsCount').textContent =
    `Showing ${{visiblePractices}} practice${{visiblePractices !== 1 ? 's' : ''}} with ${{visibleAlignments}} KQL quer${{visibleAlignments !== 1 ? 'ies' : 'y'}}`;
}}

function esc(s) {{
  const d = document.createElement('div');
  d.textContent = s || '';
  return d.innerHTML;
}}

function togglePractice(el) {{
  el.parentElement.classList.toggle('open');
}}

function copyKQL(id, btn) {{
  const el = document.getElementById(id);
  const text = el.textContent || el.innerText;
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{
      btn.textContent = 'Copy';
      btn.classList.remove('copied');
    }}, 2000);
  }});
}}

function clearFilters() {{
  document.getElementById('filterFamily').value = '';
  document.getElementById('filterWorkload').value = '';
  document.getElementById('filterTable').value = '';
  document.getElementById('filterSearch').value = '';
  renderPractices();
}}

// Attach filter events
['filterFamily','filterWorkload','filterTable'].forEach(id => {{
  document.getElementById(id).addEventListener('change', renderPractices);
}});
document.getElementById('filterSearch').addEventListener('input', renderPractices);

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

    print(f"✅ Built {OUTPUT_FILE} — {len(practices)} practices, {sum(len(p['alignments']) for p in practices)} queries")


if __name__ == "__main__":
    main()
