# NIST 800-171 Alignment Framework

Open-source mapping of **NIST 800-171 Rev.2 Level 1** controls to **Microsoft Sentinel** tables and **KQL queries** you can run today.

> **[Open the Dashboard →](https://cyberlorians.github.io/nistframework/)**

---

## What You Get

An interactive dashboard that maps every NIST 800-171 Level 1 control to the KQL queries that prove you meet it. No installs, no licenses, no setup — just open the link above.

### Use the Dashboard

1. **Open** [cyberlorians.github.io/nistframework](https://cyberlorians.github.io/nistframework/)
2. **Browse** — controls are grouped by compliance family (Access Control, ID & Auth, etc.)
3. **Filter** — narrow by Microsoft product, Sentinel table, or family
4. **Search** — find any control, table, or keyword instantly
5. **Copy KQL** — click the copy button on any query and paste it straight into Microsoft Sentinel
6. **Run it** — the query runs against your Sentinel workspace and returns compliance evidence

That's it. Every query follows a consistent structure so you know exactly what you're running and why.

### What's Covered

| Family | Controls | Count |
|--------|----------|-------|
| Access Control | 3.1.1, 3.1.2, 3.1.20, 3.1.22 | 4 |
| Identification & Authentication | 3.5.1, 3.5.2 | 2 |
| Media Protection | 3.8.3, 3.8.4 | 2 |
| Physical Protection | 3.10.1, 3.10.3, 3.10.4, 3.10.5 | 4 |
| System & Communications Protection | 3.13.1, 3.13.5 | 2 |
| System & Information Integrity | 3.14.1, 3.14.2, 3.14.5 | 3 |

**17 controls** · **119 KQL queries** · **11 Microsoft products** · **56+ Sentinel tables**

---

## Contribute

This is a community project. Every mapping lives in a simple YAML file — if you can write KQL, you can contribute.

### Add or improve a mapping

1. **Fork** this repo
2. **Open** `practices/_template.yaml` — this is your starting point
3. **Copy** it to a new file named after the control (e.g. `practices/3.1.1.yaml`)
4. **Fill in** the control name, family, and your KQL queries
5. **Open a Pull Request** — automated validation checks your YAML immediately
6. Once merged, **CI rebuilds the dashboard** and your queries go live

> You only edit YAML. The dashboard rebuilds itself automatically.

The dashboard also has a built-in **YAML Generator** tab — fill in a form and it produces the YAML for you. Copy it into a file and submit your PR.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide and KQL conventions.

---

## How It Works

```
practices/*.yaml       ← Contributors edit these
       │
    CI runs on merge
       │
       ▼
  validate.py          ← Checks YAML schema (must pass)
  build_html.py        ← Rebuilds the dashboard
       │
       ▼
  GitHub Pages         → cyberlorians.github.io/nistframework
```

Every practice YAML file contains:
- The NIST control ID and name
- The compliance family
- One or more KQL queries, each with its Sentinel table and Microsoft product

CI validates the YAML, rebuilds the HTML, and deploys to GitHub Pages. No manual steps.

## Roadmap

- [x] Level 1 — 17 controls, 119 KQL queries
- [x] Interactive dashboard on GitHub Pages
- [ ] Level 2 — 110 controls
- [ ] Level 3 — 35 NIST 800-172 controls
- [ ] ATO validation workbook for Sentinel
- [ ] Security Copilot promptbook

## License

MIT
