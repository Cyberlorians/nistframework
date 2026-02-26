# CMMC Compliance AI Model

**A locally-hosted, fine-tuned language model specialized in CMMC 2.0, NIST 800-171, NIST 800-53, HIPAA, DFARS, and cybersecurity compliance frameworks.**

> **Notice:** These models are provided for proof-of-concept and evaluation purposes only. Production-grade models are not publicly shared. For inquiries regarding production models or commercial licensing, please contact the maintainer: [Nathan Maine](mailto:nmaine@gmail.com).

Built to answer the question: *Can a small team deploy a domain-specific AI compliance advisor that runs entirely on-premises — no cloud, no API fees, no CUI exposure?*

**Yes. Four model sizes from 5 GB to 45 GB — from laptop to workstation to server.**

> **Current release:** Version 2.0 (February 2026) — All four models trained and published. Expanded training data (18,747 examples from 11 sources).
>
> **v1.0 models** remain available on HuggingFace for existing deployments

---

## Why This Exists

Organizations pursuing CMMC certification face a knowledge bottleneck. Compliance staff spend hours searching across NIST publications, CMMC assessment guides, and DFARS clauses to answer questions that a well-trained model can handle in seconds.

Commercial LLMs (GPT-4, Claude) are powerful but introduce data residency concerns for organizations handling CUI and ITAR-controlled information. These models run fully local — no data leaves the premises, no internet required, no per-token costs.

---

## Model Suite

All four models share the same compliance knowledge base and training data. The tiered approach allows organizations to deploy the model that best matches their available hardware.

| Model | Parameters | GGUF Size | Quantization | Eval Loss | Hardware Required |
|-------|-----------|-----------|--------------|-----------|-------------------|
| **cmmc-expert-7b** | 7.6B | 5.1 GB | q5_k_m | 1.142 | 8 GB VRAM (consumer GPU) |
| **cmmc-expert-14b** | 14.7B | 9.8 GB | q5_k_m | 1.144 | 12 GB VRAM |
| **cmmc-expert-32b** | 32.5B | 18.9 GB | q4_k_m | 1.073 | 24 GB VRAM or 32 GB RAM |
| **cmmc-expert-72b** | 72.7B | 45 GB | q4_k_m | **1.048** | 48 GB VRAM or 64 GB RAM |

**Base models**: [Qwen2.5 Instruct](https://huggingface.co/Qwen) — 7B, 14B, 32B, 72B. Models are fine-tuned for complete security domain coverage; behavioral guardrails and policy enforcement are handled at the [governed-llm-gateway](https://github.com/NathanMaine/governed-llm-gateway) layer. Base model migration to [Meta Llama 3.1/3.3](https://huggingface.co/meta-llama) in progress

**Method**: QLoRA fine-tuning — base model weights frozen in 4-bit, low-rank adapters trained on compliance data

**Runtime**: [Ollama](https://ollama.ai) (OpenAI-compatible API at `localhost:11434/v1`)

---

## Download

### Version 2.0 (Latest)

| Model | Hugging Face | Size | Status |
|-------|-------------|------|--------|
| **cmmc-expert-7b-v2.0** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-7b-v2.0) | 5.1 GB | Available |
| **cmmc-expert-14b-v2.0** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-14b-v2.0) | 9.8 GB | Available |
| **cmmc-expert-32b-v2.0** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-32b-v2.0) | 18.9 GB | Available |
| **cmmc-expert-72b-v2.0** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-72b-v2.0) | 45 GB | Available |

### Version 1.0 (Legacy)

| Model | Hugging Face | Size |
|-------|-------------|------|
| **cmmc-expert-7b** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-7b) | 5.1 GB |
| **cmmc-expert-14b** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-14b) | ~10 GB |
| **cmmc-expert-32b** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-32b) | 18.5 GB |
| **cmmc-expert-72b** | [Download GGUF](https://huggingface.co/Nathan-Maine/cmmc-expert-72b) | 44.2 GB |

Quick start with Ollama:
```bash
# Download and run (pick your size)
ollama run Nathan-Maine/cmmc-expert-7b-v2.0

# Or use the OpenAI-compatible API
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Nathan-Maine/cmmc-expert-7b-v2.0",
    "messages": [{"role": "user", "content": "What are the access control requirements for CMMC Level 2?"}]
  }'
```

---

## Version 2.0 — Current Release

**Released:** February 2026

Version 2.0 significantly expands the training corpus with authoritative source material scraped directly from government APIs and official publications. An automated data pipeline handles scraping, conversion, quality filtering, deduplication, and versioning with full reproducibility.

### What's New in v2.0

- **40% more training data** — 18,747 total examples (up from 16,906 in v1.0)
- **6 new authoritative sources** — NIST SP 800-53 Rev. 5, NIST CSF 2.0, eCFR regulations, Federal Register, DoD PDFs, NIST SP 800-171 Rev. 3
- **Expanded LoRA coverage** — All 7 transformer modules targeted across all model sizes
- **Best eval loss: 1.048** — 72B flagship model achieves the lowest loss in the suite
- **Improved across the board** — 7B eval loss improved from 1.241 (v1.0) to 1.142 (v2.0)

The regulatory landscape changed substantially since the v1.0 training data was assembled. Version 2.0 addresses these gaps:

| Update | Date | Significance |
|--------|------|-------------|
| **NIST SP 800-171 Rev. 3** | May 2024 | Replaces Rev. 2. Consolidated from 110 to 97 controls. Adds 88 organization-defined parameters (ODPs) and 509 assessment objectives. This is the new CMMC Level 2 foundation |
| **NIST CSF 2.0** | Feb 2024 | Major revision adding the GOVERN function (6 functions total). 34 categories, 174 subcategories with implementation examples |
| **CMMC Final Rule** (32 CFR 170) | Dec 2024 | The actual regulation establishing the CMMC program. Effective rule text, not just guidance |
| **DFARS 252.204-7021** | Nov 2025 | Acquisition rule requiring CMMC certification in DoD contracts. Phase-in timeline and applicability |
| **NIST SP 800-172 Rev. 3** | 2025 (FPD) | Enhanced CUI requirements, final public draft. CMMC Level 3 delta |
| **DoD Assessment Guides** | 2025 | Official L2/L3 assessment procedures, scoping guides, ODP values document |

### Training Data

**14,906 training + 3,841 validation examples (~4.5M tokens)** assembled from 11 sources:

#### v1.0 Legacy Sources (13,434 examples)

| Source | Records | % | Coverage |
|--------|---------|---|----------|
| NIST Cybersecurity Publications | 6,372 | 33.9% | SP 800-171, 800-172, 800-53, 800-37, CSF, and related guidance |
| CMMC Primary | 4,787 | 25.5% | CMMC 2.0 requirements, controls, implementation guidance |
| CMMC Balanced | 994 | 5.3% | Proportional coverage across all CMMC domains |
| HIPAA Compliance | 961 | 5.1% | Security Rule requirements and technical safeguards |
| CMMC Core | 320 | 1.7% | High-priority practices and assessment-critical requirements |

#### v2.0 New Sources (1,841 examples via automated pipeline)

| Source | Scraper | Records | % | Method |
|--------|---------|---------|---|--------|
| **NIST SP 800-53 Rev. 5** | `nist_csrc` | 773 | 4.1% | OSCAL JSON catalog. Full control catalog including enhancements |
| **DoD Documents** | `dod_documents` | 519 | 2.8% | PDF extraction — Assessment Guide L2, Scoping Guides, ODP Values, SP 800-172 R3 |
| **Federal Register** | `federal_register` | 350 | 1.9% | Federal Register API — CMMC rulemakings, DFARS notices |
| **eCFR Regulations** | `ecfr` | 75 | 0.4% | eCFR API — 32 CFR 170 (CMMC), DFARS cyber clauses, 45 CFR 164 (HIPAA) |
| **NIST SP 800-171 Rev. 3** | `nist_sp800_171` | 63 | 0.3% | OSCAL JSON — 97 controls with assessment objectives and ODPs |
| **NIST CSF 2.0** | `nist_csf` | 61 | 0.3% | OSCAL JSON — 34 categories + subcategories with implementation examples |

### Automated Pipeline

The v2.0 data pipeline ([cmmc-data-pipeline](https://github.com/NathanMaine/cmmc-data-pipeline)) is fully automated and reproducible:

```
                Authoritative Sources
    ┌──────────────────────────────────────────┐
    │  NIST OSCAL (GitHub)    eCFR API         │
    │  DoD PDFs               Federal Register │
    └─────────────────┬────────────────────────┘
                      │
                      ▼
    ┌──────────────────────────────────────────┐
    │  Step 1: Scrape                          │
    │  Rate-limited, retry-enabled scrapers    │
    │  Raw JSON saved to data/raw/{source}/    │
    ├──────────────────────────────────────────┤
    │  Step 1b: Relevance Filter               │
    │  eCFR filtered to CMMC-relevant DFARS    │
    │  clauses only (252.204-70xx, 252.239)    │
    ├──────────────────────────────────────────┤
    │  Step 2: Convert                         │
    │  Source-specific templates generate       │
    │  chat-format instruction/response pairs  │
    ├──────────────────────────────────────────┤
    │  Step 3: Quality Filter                  │
    │  Min length, max length (8K), alpha ratio│
    ├──────────────────────────────────────────┤
    │  Step 4: Deduplicate                     │
    │  xxhash exact + MinHash LSH near-dedup   │
    │  (128 perms, Jaccard 0.8, 5-gram)        │
    ├──────────────────────────────────────────┤
    │  Step 5: Validate                        │
    │  Format checks, quality scoring, stats   │
    ├──────────────────────────────────────────┤
    │  Step 6: Version                         │
    │  Immutable snapshots with rollback       │
    ├──────────────────────────────────────────┤
    │  Step 7: Merge                           │
    │  Cross-version dedup against v1.0 data   │
    └──────────────────────────────────────────┘
```

The pipeline supports both full scrapes and incremental updates. Each run creates a versioned snapshot that can be inspected, diffed, or rolled back before merging into the training dataset.

### Pipeline Results (Final — v004)

| Step | Result |
|------|--------|
| Scraped | 4,438 raw records from 6 new sources |
| Relevance filtered | 4,100 kept (338 irrelevant DFARS clauses removed) |
| Converted | 2,193 chat-format training records |
| Quality filtered | 1,888 passed (305 rejected — too short or too long) |
| Deduplicated | 1,841 unique (47 near-duplicates removed) |
| Validated | **PASSED** — 0 format errors, avg answer length 1,322 chars |
| Merged with v1.0 | **18,747 total** (14,906 train + 3,841 validation) |

### Training Configuration

All models trained using QLoRA (Quantized Low-Rank Adaptation) — base weights frozen in 4-bit NF4, trainable adapter layers injected into all 7 transformer projection modules. Trained on NVIDIA A100-SXM4-80GB via RunPod.

| Parameter | 7B | 14B | 32B | 72B |
|-----------|-----|------|------|------|
| **GPU** | A100 80GB SXM | A100 80GB SXM | A100 80GB SXM | A100 80GB SXM |
| **LoRA rank** | 64 | 16 | 32 | 16 |
| **LoRA alpha** | 128 | 32 | 64 | 32 |
| **LoRA dropout** | 0.05 | 0.05 | 0.05 | 0.05 |
| **Target modules** | All 7 | All 7 | All 7 | All 7 |
| **Effective batch size** | 32 | 16 | 16 | 16 |
| **Learning rate** | 2e-4 | 1e-4 | 1e-4 | 5e-5 |
| **Epochs** | 3 | 3 | 3 | 3 |
| **Max sequence length** | 2048 | 2048 | 2048 | 2048 |
| **Precision** | bf16 | bf16 | bf16 | bf16 |
| **Optimizer** | AdamW 8-bit | AdamW 8-bit | AdamW 8-bit | AdamW 8-bit |
| **Packing** | Enabled | Enabled | Enabled | Enabled |
| **Training time** | ~3.1 hours | ~6.5 hours | ~9.6 hours | ~13.0 hours |
| **Final eval loss** | 1.142 | 1.144 | 1.073 | 1.048 |

The 72B model used [Unsloth](https://github.com/unslothai/unsloth) for memory-efficient 4-bit loading, enabling QLoRA fine-tuning on a single A100-80GB without multi-GPU setups.

### Evaluation Results

All models showed continuous improvement across training with no overfitting observed.

**Per-Model Training Metrics:**

| Metric | 7B | 14B | 32B | 72B |
|--------|------|------|------|------|
| **Final Eval Loss** | 1.142 | 1.144 | 1.073 | **1.048** |
| **Final Train Loss** | 1.030 | 1.009 | 1.005 | 0.966 |
| **Token Accuracy** | 76.5% | 77.7% | 77.9% | — |
| **Total Steps** | 282 | 561 | 561 | 564 |
| **Training Time** | 3.1h | 6.5h | 9.6h | 13.0h |
| **GGUF Size** | 5.1 GB | 9.8 GB | 18.9 GB | 45 GB |

The 72B model achieves the lowest eval loss in the suite (1.048), demonstrating that model scale continues to improve compliance reasoning quality even with the same training data.

**v1.0 vs v2.0 Comparison (7B):**

| Metric | v1.0 | v2.0 | Change |
|--------|------|------|--------|
| Training Examples | 13,434 | 14,906 | +11% |
| Eval Loss | 1.241 | 1.142 | -8% (improved) |
| LoRA Target Modules | 4 | 7 | +75% coverage |
| Data Sources | 5 | 11 | +6 new |

---

## Compliance Framework Coverage

### Full Coverage Map (v1.0 + v2.0 Combined)

| Framework | v1.0 | v2.0 Adds |
|-----------|------|-----------|
| **CMMC 2.0** (32 CFR Part 170) | Level 1–3 practices, assessment methodology | Actual regulatory text from eCFR, DoD assessment guide procedures, scoping guidance |
| **NIST SP 800-171** | Rev. 2 (110 requirements) | **Rev. 3** (97 controls with assessment objectives, methods, and 88 ODPs) |
| **NIST SP 800-172** | Original | **Rev. 3 Final Public Draft** (enhanced CUI requirements) |
| **NIST SP 800-53** | Rev. 5 (from NIST pubs dataset) | Rev. 5 full OSCAL catalog (1,016 controls + enhancements with structured statements and guidance) |
| **NIST CSF** | 1.1 (5 functions) | **2.0** (6 functions — adds GOVERN. 34 categories, 174 subcategories) |
| **HIPAA Security Rule** | Q&A training pairs | Full regulatory text from 45 CFR Part 164 (41 sections) |
| **DFARS Clauses** | 7012, 7019, 7020, 7021 guidance | Full regulatory text from 48 CFR Part 252 (348 sections) |
| **Federal Register** | — | CMMC rulemakings, DFARS proposed/final rules, CUI policy notices |
| **DoD Assessment Guides** | — | L2 Assessment Guide (332 chunks), L2/L3 Scoping Guides, ODP Values |

### DFARS and NIST Coverage Detail

The models understand the full chain from contract clause to technical implementation:

**DFARS 252.204-7012** — Safeguarding Covered Defense Information
- Adequate security requirements for CUI on contractor systems
- Cyber incident reporting obligations (72-hour timeline)
- Flow-down requirements to subcontractors
- Relationship to NIST SP 800-171 compliance

**DFARS 252.204-7019** — Notice of NIST SP 800-171 Assessment
- SPRS (Supplier Performance Risk System) scoring methodology
- Self-assessment requirements and documentation
- DoD Assessment Methodology (Basic, Medium, High)

**DFARS 252.204-7020** — NIST SP 800-171 DoD Assessment Requirements
- Government assessment access and cooperation requirements
- Relationship between SPRS scores and assessment levels

**DFARS 252.204-7021** — Cybersecurity Maturity Model Certification
- CMMC level requirements by contract type
- Phase-in timeline and applicability
- Relationship between CMMC levels and NIST SP 800-171/172

---

## Use Cases

| Application | How It Works |
|-------------|-------------|
| **SSP Generation** | Draft System Security Plan control descriptions with proper NIST/CMMC citations |
| **Gap Analysis** | Identify which controls are required for specific CMMC levels and contract requirements |
| **Assessment Prep** | Generate evidence checklists and assessment objective narratives |
| **Cross-Framework Mapping** | Map controls between CMMC, NIST 800-53, HIPAA, and other frameworks |
| **Policy Drafting** | Create initial policies and procedures aligned to specific CMMC practices |
| **DFARS Clause Analysis** | Identify applicable requirements from contract language (7012, 7019, 7020, 7021) |
| **Training & Education** | Always-available compliance reference — no waiting for SMEs |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     User Query                            │
│   "What access control requirements apply to              │
│    CMMC Level 2 for CUI handling?"                        │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              Ollama Runtime (Local)                        │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Foundation Model (frozen, 4-bit quantized)         │   │
│  │  + QLoRA Adapters (compliance-tuned)                │   │
│  │                                                     │   │
│  │  7B  — quick lookups, day-to-day queries            │   │
│  │  14B — detailed analysis, multi-control reasoning   │   │
│  │  32B — deep gap assessments, SSP drafting           │   │
│  │  72B — complex multi-framework analysis             │   │
│  └────────────────────────────────────────────────────┘   │
│  System prompt: Compliance expert across CMMC/NIST/HIPAA  │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              Structured Response                          │
│   - Framework-specific references (SP 800-171 §3.1)      │
│   - Implementation guidance                               │
│   - Assessment evidence requirements                      │
│   - Cross-framework mappings (CMMC ↔ 800-53 ↔ HIPAA)    │
│   - DFARS clause applicability                            │
└──────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **4 model sizes (7B–72B)** | Tiered deployment — laptop for quick lookups, workstation for deep analysis. Match the model to the hardware |
| **QLoRA (not full fine-tune)** | Trainable params are <0.1% of total. 50x less compute, comparable domain accuracy |
| **Security domain completeness** | Models are fine-tuned for complete security domain coverage, including vulnerability analysis, incident response scenarios, and access control failure modes required for professional SSP and POA&M generation. Behavioral guardrails and policy enforcement are handled at the governed-llm-gateway layer |
| **q5_k_m / q4_k_m quantization** | 5-bit for smaller models (accuracy-sensitive), 4-bit for larger (size-constrained). Compliance is fact-heavy — extra bit preserves control IDs |
| **Local-only deployment** | CUI/ITAR data cannot leave premises. Zero cloud dependency by design. Fully air-gappable |
| **Multi-framework training** | Organizations rarely have single-framework obligations. Cross-mapping across CMMC, NIST, HIPAA, and DFARS is the real value |
| **OSCAL-native scraping** | NIST's machine-readable OSCAL JSON provides structured control data far richer than PDF extraction |
| **Automated pipeline with versioning** | Reproducible data updates with immutable snapshots, rollback, and dedup against existing training data |

---

## Security and Privacy

This model suite was designed for environments where data sovereignty matters:

- **Fully air-gappable** — Runs entirely on local hardware after initial download. No internet required for inference
- **No telemetry** — No data is transmitted to any external service
- **No third-party API dependency** — No per-query costs, no rate limits, no data exposure to cloud providers
- **CUI-safe deployment** — Suitable for use in environments processing Controlled Unclassified Information, as no data leaves the local system boundary
- **Customizable** — Can be further fine-tuned with organization-specific policies, SSPs, and internal security documentation

---

## Hardware Requirements

### Inference (Running a Model)

| Model | GPU (VRAM) | CPU-Only (System RAM) | Storage |
|-------|-----------|----------------------|---------|
| **7B** | 8 GB | 16 GB | 10 GB |
| **14B** | 12 GB | 24 GB | 15 GB |
| **32B** | 24 GB | 32 GB | 25 GB |
| **72B** | 48 GB | 64 GB | 50 GB |

### Training (Reproducing from Scratch)

| Model | GPU Required | Approx. Time |
|-------|-------------|--------------|
| **7B** | 16 GB VRAM (e.g., RTX 5000 Ada) | ~3.1 hours |
| **14B** | 40+ GB VRAM (e.g., A100 40GB) | ~6.5 hours |
| **32B** | 80 GB VRAM (e.g., A100 80GB) | ~9.6 hours |
| **72B** | 80 GB VRAM (e.g., A100 80GB) | ~13.0 hours |

**OS**: Linux, macOS, Windows (WSL2)

---

## Repository Structure

```
cmmc-compliance-ai-model/
├── README.md                    # This file
├── docs/
│   ├── training-methodology.md  # Detailed QLoRA configuration and rationale
│   ├── data-pipeline.md         # Full pipeline documentation with filtering logic
│   └── evaluation-results.md    # Eval metrics, example outputs, failure modes
├── pipeline/
│   ├── 01_format_converter.py   # Raw → chat-style instruction pairs
│   ├── 02_quality_filter.py     # Length, artifact, and fragment removal
│   ├── 03_relevance_filter.py   # NIST relevance scoring and sampling
│   ├── 04_deduplication.py      # xxhash exact + MinHash LSH near-dedup
│   └── 05_train_val_split.py    # Stratified split with source balancing
├── training/
│   ├── train_qlora.py           # QLoRA training script
│   ├── config.yaml              # Hyperparameters and training config
│   └── merge_and_quantize.py    # Adapter merge + GGUF quantization
├── evaluation/
│   ├── eval_compliance.py       # Framework-specific accuracy testing
│   └── eval_cross_mapping.py    # Cross-framework mapping validation
├── deployment/
│   ├── Modelfile                # Ollama model configuration
│   └── setup_ollama.sh          # Local deployment script
└── publishing/
    ├── huggingface/             # Model cards + upload scripts
    ├── ollama/                  # Ollama Library submission guide
    └── github-releases/         # GitHub Release creation script
```

> **Note:** This repo contains the pipeline code, training configuration, and documentation. Pre-trained model weights (GGUF) are available on [Hugging Face](https://huggingface.co/Nathan-Maine). Training data and checkpoints are excluded from the repository.

---

## Roadmap

- [x] v1.0 — 7B model trained and published
- [x] v1.0 — 14B model trained and published
- [x] v1.0 — 32B model trained and published
- [x] v1.0 — 72B model trained and published
- [x] v2.0 — Automated scraping pipeline (6 new sources)
- [x] v2.0 — Expanded training data (18,747 examples from 11 sources)
- [x] v2.0 — 7B retrained and published on v2.0 data
- [x] v2.0 — 14B retrained and published on v2.0 data
- [x] v2.0 — 32B retrained and published on v2.0 data
- [x] v2.0 — 72B retrained and published on v2.0 data
- [ ] v4.0 — Base model migration from Qwen2.5 to Meta Llama 3.1/3.3 (US-origin, open weights)
- [ ] RAG integration — Live document retrieval for real-time regulatory updates
- [ ] Agent integration — Deploy as a compliance agent with tool use (document search, SSP generation, gap analysis automation)
- [ ] FedRAMP baselines, CIS Controls, and ITAR coverage

---

## Built With

- **Base Models**: [Qwen2.5 Instruct](https://huggingface.co/Qwen) — 7B, 14B, 32B, 72B (migration to [Meta Llama 3.1/3.3](https://huggingface.co/meta-llama) in progress)
- **Training**: [HuggingFace TRL](https://github.com/huggingface/trl) + [PEFT](https://github.com/huggingface/peft) + [bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes) — QLoRA fine-tuning
- **72B Training**: [Unsloth](https://github.com/unslothai/unsloth) — Memory-efficient model loading for 72B on single GPU
- **Quantization**: [llama.cpp](https://github.com/ggerganov/llama.cpp) — GGUF format (q4_k_m / q5_k_m)
- **Inference**: [Ollama](https://ollama.ai) — Local deployment with OpenAI-compatible API
- **Data Pipeline**: [cmmc-data-pipeline](https://github.com/NathanMaine/cmmc-data-pipeline) — Python + [datasketch](https://github.com/ekzhu/datasketch) + [xxhash](https://github.com/Cyan4973/xxHash) — Scraping, conversion, deduplication
- **Data Sources**: NIST OSCAL (GitHub), eCFR API, Federal Register API, DoD PDFs
- **Cloud Training Hardware**: NVIDIA A100 80GB SXM ([RunPod](https://www.runpod.io))

---

## Sources and References

All training data is derived from publicly available, authoritative government sources:

### CMMC Program

| Source | URL |
|--------|-----|
| CMMC Final Rule (32 CFR Part 170) | https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-D/part-170 |
| DoD CIO CMMC Portal | https://dodcio.defense.gov/cmmc/ |
| CMMC Level 2 Assessment Guide | https://dodcio.defense.gov/Portals/0/Documents/CMMC/AGLevel2.pdf |
| CMMC Level 2 Scoping Guide | https://dodcio.defense.gov/Portals/0/Documents/CMMC/ScopingGuideLevel2.pdf |
| CMMC Level 3 Scoping Guide | https://dodcio.defense.gov/Portals/0/Documents/CMMC/ScopingGuideLevel3.pdf |
| CMMC ODP Values Document | https://dodcio.defense.gov/Portals/0/Documents/CMMC/ODPValues.pdf |

### NIST Publications

| Source | URL |
|--------|-----|
| NIST SP 800-171 Rev. 3 | https://csrc.nist.gov/pubs/sp/800/171/r3/final |
| NIST SP 800-171 Rev. 3 OSCAL Catalog | https://github.com/usnistgov/oscal-content |
| NIST SP 800-172 Rev. 3 (Final Public Draft) | https://csrc.nist.gov/pubs/sp/800/172/r3/fpd |
| NIST SP 800-53 Rev. 5 | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final |
| NIST SP 800-53 Rev. 5 OSCAL Catalog | https://github.com/usnistgov/oscal-content |
| NIST SP 800-37 Rev. 2 (RMF) | https://csrc.nist.gov/pubs/sp/800/37/r2/final |
| NIST Cybersecurity Framework 2.0 | https://www.nist.gov/cyberframework |
| NIST CSF 2.0 OSCAL Catalog | https://github.com/usnistgov/oscal-content |

### Federal Regulations

| Source | URL |
|--------|-----|
| eCFR — 32 CFR Part 170 (CMMC) | https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-D/part-170 |
| eCFR — 48 CFR Part 252 (DFARS) | https://www.ecfr.gov/current/title-48/chapter-2/subchapter-H/part-252 |
| eCFR — 45 CFR Part 164 (HIPAA Security Rule) | https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164 |
| Federal Register (CMMC Rulemakings) | https://www.federalregister.gov/ |

### DFARS Clauses

| Clause | Title | Reference |
|--------|-------|-----------|
| DFARS 252.204-7012 | Safeguarding Covered Defense Information | https://www.ecfr.gov/current/title-48/section-252.204-7012 |
| DFARS 252.204-7019 | Notice of NIST SP 800-171 Assessment | https://www.ecfr.gov/current/title-48/section-252.204-7019 |
| DFARS 252.204-7020 | NIST SP 800-171 DoD Assessment Requirements | https://www.ecfr.gov/current/title-48/section-252.204-7020 |
| DFARS 252.204-7021 | Cybersecurity Maturity Model Certification | https://www.ecfr.gov/current/title-48/section-252.204-7021 |

### Data Formats

| Format | Description | Source |
|--------|-------------|--------|
| OSCAL JSON | Machine-readable security control catalogs (NIST's Open Security Controls Assessment Language) | https://pages.nist.gov/OSCAL/ |
| eCFR API | Electronic Code of Federal Regulations structured text | https://www.ecfr.gov/developers/documentation/api/v1 |
| Federal Register API | Government policy documents and rulemakings | https://www.federalregister.gov/developers/documentation/api/v1 |

---

## Limitations

- The model is trained on publicly available compliance framework documentation. It does not contain classified or controlled information.
- Responses should be treated as expert-informed guidance, not as legal or regulatory determinations. All compliance decisions should be validated by qualified assessors.
- The model's knowledge reflects the training data at time of creation. Regulatory updates published after the training cutoff should be incorporated through the automated pipeline or RAG.
- Performance on highly specialized or edge-case compliance scenarios may vary. The model performs best on well-documented framework requirements.

---

**Built by [Nathan Maine](https://nathanmaine.com)** — Solving compliance bottlenecks with purpose-built AI.
