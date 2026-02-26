# CMMC Compliance AI Model — Project Status

## Project Overview

A suite of fine-tuned language models specialized in CMMC (Cybersecurity Maturity Model Certification) and cybersecurity compliance. Built on Qwen2.5 base models using QLoRA fine-tuning, covering CMMC 2.0, NIST SP 800-171/172/53, NIST CSF, HIPAA Security Rule, and DFARS clauses.

**Repository:** `cmmc-compliance-ai-model`
**Data Pipeline:** `cmmc-data-pipeline`
**Training Scripts:** `cmmc-finetune`
**HuggingFace:** `Nathan-Maine/cmmc-expert-*`

---

## V1.0 — Complete (February 11, 2026)

### Training Data (V1.0)

| Dataset | Train | Validation | Total |
|---------|-------|------------|-------|
| cmmc | 4,787 | 1,183 | 5,970 |
| nist_cybersecurity | 6,372 | 1,727 | 8,099 |
| hipaa_compliance | 961 | 250 | 1,211 |
| cmmc_balanced | 994 | 252 | 1,246 |
| cmmc_core | 320 | 60 | 380 |
| **Total** | **13,434** | **3,472** | **16,906** |

- ~3.3M tokens total
- Chat format: `{"messages": [system, user, assistant]}`
- 80/20 train/validation split
- Sources: Hand-curated from CMMC 2.0 documentation, NIST publications, HIPAA guidance

### Models Published

| Model | Base | Quant | Size | Eval Loss | HuggingFace |
|-------|------|-------|------|-----------|-------------|
| 7B | Qwen2.5-7B-Instruct | q5_k_m | 5.6 GB | 1.241 | Nathan-Maine/cmmc-expert-7b |
| 14B | Qwen2.5-14B-Instruct | q5_k_m | 10.4 GB | — | Nathan-Maine/cmmc-expert-14b |
| 32B | Qwen2.5-32B-Instruct | q4_k_m | 20.4 GB | — | Nathan-Maine/cmmc-expert-32b |
| 72B | Qwen2.5-72B-Instruct | q4_k_m | 44.2 GB | 1.004 | Nathan-Maine/cmmc-expert-72b |

- All models trained on RunPod A100 80GB instances
- QLoRA config: r=64, alpha=128, dropout=0.05, 4-bit NF4 quantization
- Training: 3 epochs, batch size 4, gradient accumulation 8, lr=2e-4, cosine scheduler
- 14B and 32B eval loss not captured (RunPod sessions destroyed before saving logs)
- 72B upload to HuggingFace completed February 13, 2026

### V1.0 Timeline

| Date | Milestone |
|------|-----------|
| Jan 2026 | Project started — data collection and curation |
| Feb 1, 2026 | Training data finalized (13,434 train examples) |
| Feb 5, 2026 | 7B model trained and published |
| Feb 7, 2026 | 14B model trained and published |
| Feb 9, 2026 | 32B model trained and published |
| Feb 11, 2026 | 72B model trained, README updated |
| Feb 13, 2026 | 72B GGUF uploaded to HuggingFace |

---

## V2.0 — Data Expansion (In Progress)

### Goal

Expand the training corpus with new authoritative sources via an automated scraping pipeline. Target: ~15,000+ combined training examples (v1.0 + v2.0 new data).

### Automated Data Pipeline

Built at `/home/inigo/Github Projects/cmmc-data-pipeline/`. Fully automated: scrape → relevance filter → convert → quality filter → MinHash LSH dedup → validate → version → merge.

**Pipeline Features:**
- 5 active data sources (see below)
- Rate-limited scraping with retry logic
- Relevance filtering (removes irrelevant regulatory sections)
- Quality filtering: min 200 chars, max 8,000 chars, table/alpha ratio checks
- MinHash LSH deduplication (128 perms, 0.8 Jaccard threshold, 5-gram shingles)
- Dedup against existing v1.0 training data
- Immutable versioned snapshots
- `--skip-scrape` mode to reprocess existing raw data

### V2.0 Data Sources

| Source | Raw Records | Description |
|--------|-------------|-------------|
| nist_csrc | 1,016 | NIST SP 800-53 Rev. 5 security controls (OSCAL JSON) |
| nist_sp800_171 | 97 | NIST SP 800-171 Rev. 3 CUI protection controls (OSCAL JSON) |
| nist_csf | 208 | NIST Cybersecurity Framework 2.0 categories/subcategories |
| dod_documents | 606 | DoD PDFs: CMMC assessment guides, scoping guides, policy |
| ecfr | 413 (75 after filter) | eCFR regulatory text: 32 CFR 170, 45 CFR 164, 48 CFR 252 |

**Dropped Sources:**
- **Federal Register** (2,098 docs → 73K chunks): Dropped from v2.0. FR is a publication venue, not a domain — the compliance knowledge it contains is already covered by the other 5 sources. FR data overwhelmed the pipeline (96.8% of v002) with regulatory history that added volume without proportional value.

### eCFR Relevance Filter

The eCFR scraper pulls all sections from 3 CFR titles, but not all are CMMC-relevant:

| CFR Reference | Records | Relevant | Notes |
|--------------|---------|----------|-------|
| 32 CFR 170 | 24 | All | CMMC program rule — always relevant |
| 45 CFR 164 | 41 | All | HIPAA Security Rule — always relevant |
| 48 CFR 252 (DFARS) | 348 | ~10 | Only cyber clauses kept (252.204-70xx, 252.239-7010) |

**Relevant DFARS clauses kept:**
- 252.204-7008 — Compliance with safeguarding CDI controls
- 252.204-7009 — Third-party cyber incident disclosure limits
- 252.204-7012 — Safeguarding CDI and Cyber Incident Reporting
- 252.204-7019 — Notice of NIST SP 800-171 DoD Assessment Requirements
- 252.204-7020 — NIST SP 800-171 DoD Assessment Requirements
- 252.204-7021 — Contractor Compliance with CMMC Level Requirements
- 252.204-7024 — Notice of CMMC Assessment and Scoping Requirements
- 252.204-7025 — Notice of CMMC Level Requirements
- 252.239-7009 — Representation of use of cloud computing
- 252.239-7010 — Cloud Computing Services

**Irrelevant DFARS clauses removed (338 records):** Buy American, trade agreements, intellectual property, small business, foreign contracting, and other non-cyber regulatory clauses.

### Pipeline Version History

| Version | Date | Records | Sources | Notes |
|---------|------|---------|---------|-------|
| v001 | Feb 12, 2026 | 803 | 3 (sp800_171, csf, dod) | First test run, only 3 sources |
| v002 | Feb 13, 2026 | 67,820 | 6 (all) | All sources — FR dominated at 96.8% |
| v003 | Feb 13, 2026 | 2,199 | 5 (no FR) | Dropped Federal Register |
| v004 | Feb 13, 2026 | 1,841 | 5 (no FR) | Relevance filter + max 8K length cap. Final v2.0 snapshot. |

### V2.0 Current Status

- [x] Pipeline infrastructure built and tested
- [x] All 5 sources scraped (raw data on disk)
- [x] Relevance filter for eCFR (removes 338 irrelevant DFARS records)
- [x] Max answer length cap (8,000 chars) to remove outliers
- [x] v004 pipeline run with filters — 1,841 unique records, validation PASSED
- [x] Merged v2.0 data with v1.0 training data (18,747 total examples)
- [x] Combined dataset analyzed
- [ ] Retrain models with expanded dataset

### V2.0 New Data Source Breakdown (v004: 1,841 records)

| Source | Records | % of v2.0 | Description |
|--------|---------|-----------|-------------|
| nist_csrc (SP 800-53) | 990 | 53.8% | Security and privacy controls |
| dod_documents | 566 | 30.7% | CMMC assessment guides, scoping, policy |
| nist_csf | 140 | 7.6% | Cybersecurity Framework 2.0 |
| nist_sp800_171 | 92 | 5.0% | CUI protection controls (Rev. 3) |
| ecfr | 53 | 2.9% | CMMC rule, HIPAA, cyber DFARS clauses |

### Combined Dataset (V1.0 + V2.0)

| Split | V1.0 | V2.0 New | Combined |
|-------|------|----------|----------|
| Train | 13,434 | 1,472 | **14,906** |
| Validation | 3,472 | 369 | **3,841** |
| **Total** | **16,906** | **1,841** | **18,747** |

**Answer Length Stats (combined train set):**
- Mean: 1,344 chars | Median: 1,494 chars
- P25: 760 | P75: 1,900 | P95: 2,018 | P99: 2,583
- Min: 100 | Max: 7,672
- 60.5% of records are 1,000-2,000 chars (well-formed paragraphs)

### V2.0 Architecture

```
cmmc-data-pipeline/
├── scrapers/           # Source-specific scrapers
│   ├── base.py         # Base class with rate limiting, retry, raw storage
│   ├── nist_csrc.py    # SP 800-53 Rev. 5 (OSCAL JSON)
│   ├── nist_sp800_171.py   # SP 800-171 Rev. 3 (OSCAL JSON)
│   ├── nist_csf.py     # CSF 2.0 (OSCAL JSON)
│   ├── dod_documents.py    # DoD PDFs (BeautifulSoup + PDF parsing)
│   ├── ecfr.py         # eCFR API (JSON)
│   └── federal_register.py # Federal Register API (dropped from v2.0)
├── processors/
│   ├── converter.py    # Raw → chat format conversion
│   ├── templates.py    # Question templates and system prompt
│   ├── quality_filter.py   # Length, table ratio, alpha ratio filters
│   ├── relevance_filter.py # Source-specific relevance filtering
│   └── dedup.py        # xxhash exact + MinHash LSH near-dedup
├── pipeline/
│   ├── runner.py       # Main orchestrator (7-step pipeline)
│   ├── versioning.py   # Immutable snapshot management
│   └── validator.py    # Format and quality validation
├── scripts/
│   ├── run_pipeline.py # CLI entry point
│   ├── merge.py        # Merge snapshot into training data
│   └── status.py       # Pipeline status report
├── data/
│   ├── raw/            # Scraped data by source and date
│   └── pipeline/versions/  # Immutable versioned snapshots
└── config.yaml         # All pipeline configuration
```

---

## Future Work

### V2.0 Completion
- Retrain all 4 model sizes with expanded dataset on RunPod A100 80GB
- Run evaluation benchmarks comparing v1.0 vs v2.0
- Publish updated models to HuggingFace

### V2.1+ Potential Sources
- FedRAMP authorization requirements
- CIS Controls (Center for Internet Security)
- ITAR compliance regulations
- ISO 27001/27002 mapping to CMMC
- NIST SP 800-172 enhanced security requirements

### Other Enhancements
- RAG integration for real-time compliance lookup
- Automated evaluation framework
- Model comparison dashboard
