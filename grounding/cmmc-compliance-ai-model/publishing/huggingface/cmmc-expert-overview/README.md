---
language:
- en
license: apache-2.0
tags:
- cmmc
- compliance
- cybersecurity
- nist-800-171
- nist-800-53
- hipaa
- dfars
- qlora
- qwen2.5
- gguf
- ollama
- air-gapped
- on-premises
---

# CMMC Expert — Cybersecurity Compliance AI Models

**A suite of fine-tuned language models specialized in CMMC 2.0, NIST 800-171, NIST 800-53, HIPAA, DFARS, and cybersecurity compliance frameworks. Built for on-premises, air-gapped deployment — no data leaves your network.**

Built to answer the question: *Can a small team deploy a domain-specific AI compliance advisor that runs entirely on-premises — no cloud, no API fees, no CUI exposure?*

**Yes. Four model sizes from 5 GB to 45 GB — from laptop to workstation to server.**

> **Current release:** Version 2.0 (February 2026) — All four models retrained on expanded dataset.
>
> **v3.0** (February 2026) — Experimental 7B testing alternative training methodology.

---

## Quick Start

```bash
# Install Ollama (if needed)
curl -fsSL https://ollama.ai/install.sh | sh

# Download and run (pick your size)
ollama run Nathan-Maine/cmmc-expert-7b-v2.0

# Ask a compliance question
>>> What access control requirements apply to CMMC Level 2 for CUI handling?

# Or use the OpenAI-compatible API
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Nathan-Maine/cmmc-expert-7b-v2.0",
    "messages": [{"role": "user", "content": "Map CMMC AC.L2-3.1.1 to its NIST 800-53 and HIPAA equivalents"}]
  }'
```

---

## Which Model Should I Use?

| Need | Model | GGUF Size | VRAM | Speed | Link |
|------|-------|-----------|------|-------|------|
| Quick lookups, day-to-day queries | **7B v2.0** | 5.1 GB | 6 GB | ~1-2s | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-7b-v2.0) |
| Detailed analysis, multi-control reasoning | **14B v2.0** | 9.8 GB | 12 GB | ~3-5s | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-14b-v2.0) |
| Deep gap assessments, SSP drafting | **32B v2.0** | 18.9 GB | 24 GB | ~30-60s | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-32b-v2.0) |
| Complex multi-framework synthesis | **72B v2.0** | 45 GB | 48 GB | ~2-4 min | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-72b-v2.0) |

**Start with the 7B** for most use cases. Move up to 14B or 32B when you need deeper reasoning across multiple frameworks or long-form document generation. The 72B is for the hardest problems — simultaneous analysis across all 8+ frameworks with full citation chains.

All models run on **CPU-only** as well (slower but no GPU required). Double the VRAM numbers for approximate RAM requirements.

---

## Why This Exists

Organizations pursuing CMMC certification face a knowledge bottleneck. Compliance staff spend hours searching across NIST publications, CMMC assessment guides, and DFARS clauses to answer questions that a well-trained model can handle in seconds.

Commercial LLMs (GPT-4, Claude) are powerful but introduce data residency concerns for organizations handling CUI and ITAR-controlled information. These models run fully local — **no data leaves the premises, no internet required, no per-token costs.**

### Security Domain Coverage

Models are fine-tuned for complete security domain coverage, including vulnerability analysis, incident response scenarios, and access control failure modes required for professional SSP and POA&M generation. Security assessments require analyzing threats, testing controls, and documenting attack scenarios. Behavioral guardrails and policy enforcement are handled at the [governed-llm-gateway](https://github.com/NathanMaine/governed-llm-gateway) layer.

---

## Compliance Framework Coverage

Trained across **eight overlapping frameworks** to support cross-framework mapping — because organizations rarely have single-framework obligations:

| Framework | Coverage |
|-----------|----------|
| **CMMC 2.0** (32 CFR Part 170) | All three levels — L1, L2, L3 practices, assessment methodology, actual regulatory text |
| **NIST SP 800-171 Rev. 2 & 3** | Rev. 2 (110 requirements) + Rev. 3 (97 controls with assessment objectives and 88 ODPs) |
| **NIST SP 800-172 Rev. 3** | Enhanced CUI requirements for critical programs (Final Public Draft) |
| **NIST SP 800-53 Rev. 5** | Full OSCAL catalog — 1,016 controls + enhancements with structured statements |
| **NIST CSF 2.0** | 6 functions (adds GOVERN), 34 categories, 174 subcategories |
| **NIST SP 800-37** | Risk Management Framework (RMF) steps and authorization process |
| **HIPAA Security Rule** | Administrative, physical, and technical safeguards + full 45 CFR 164 text |
| **DFARS Clauses** | 252.204-7012, 7019, 7020, 7021 — full regulatory text and analysis |

The models understand the **full compliance chain**: from DFARS contract clauses → CMMC level requirements → NIST 800-171 controls → NIST 800-53 mappings → implementation evidence. They can trace a requirement from a contract clause all the way down to the specific technical control and assessment objective.

---

## Use Cases

| Application | Description |
|-------------|-------------|
| **SSP Generation** | Draft System Security Plan control descriptions with proper NIST/CMMC citations |
| **Gap Analysis** | Identify which controls are required for specific CMMC levels and contract requirements |
| **Cross-Framework Mapping** | Map controls between CMMC ↔ NIST 800-53 ↔ HIPAA ↔ DFARS with rationale |
| **Assessment Prep** | Generate evidence checklists and assessment objective narratives |
| **Policy Drafting** | Create policies and procedures aligned to specific CMMC practices |
| **DFARS Clause Analysis** | Trace requirements from contract clauses through CMMC to technical controls |
| **Training & Education** | Always-available compliance reference for teams — no waiting for SMEs |
| **RMF Integration** | Map compliance activities to Risk Management Framework steps |

---

## Version History

### How We Got Here

The project started in January 2026 with a simple hypothesis: QLoRA fine-tuning on curated compliance data could produce a useful domain-specific model at a fraction of the cost of commercial alternatives. Three versions later, we've validated that hypothesis and learned a lot about what works (and what doesn't) for knowledge-dense compliance domains.

### v1.0 — The Foundation (February 2026)

**Goal:** Prove that fine-tuning works for compliance.

- **Training data:** 16,906 examples from 5 hand-curated sources (~3.3M tokens)
- **Method:** QLoRA with LoRA rank 64, 4-bit NF4 quantization, 3 epochs
- **Models:** 4 sizes (7B, 14B, 32B, 72B) trained on RunPod A100 80GB
- **Framework:** Unsloth + HuggingFace TRL + PEFT
- **Result:** 7B eval loss 1.241, 72B eval loss 1.004

v1.0 proved the concept. The models could accurately cite specific CMMC practices, map controls across frameworks, and generate structured compliance documents. Even the 7B model was useful for day-to-day compliance queries.

| Model | Eval Loss | Train Loss | GGUF | Training Time |
|-------|-----------|------------|------|---------------|
| [cmmc-expert-7b](https://huggingface.co/Nathan-Maine/cmmc-expert-7b) | 1.241 | 1.030 | 5.1 GB (q5_k_m) | ~3.1h |
| [cmmc-expert-14b](https://huggingface.co/Nathan-Maine/cmmc-expert-14b) | — | — | ~10 GB (q5_k_m) | ~6h |
| [cmmc-expert-32b](https://huggingface.co/Nathan-Maine/cmmc-expert-32b) | — | — | ~19 GB (q4_k_m) | ~14h |
| [cmmc-expert-72b](https://huggingface.co/Nathan-Maine/cmmc-expert-72b) | 1.004 | — | ~42 GB (q4_k_m) | ~32h |

### v2.0 — Data Expansion (February 2026) ⭐ Recommended

**Goal:** Expand coverage with authoritative source material via automated pipeline.

The compliance landscape evolved significantly: NIST SP 800-171 Rev. 3 replaced Rev. 2, NIST CSF 2.0 added the GOVERN function, the CMMC Final Rule (32 CFR 170) was published, and new DFARS clauses took effect. v2.0 addresses all of these.

**Key improvements over v1.0:**
- **+40% training data** — 18,747 examples from 11 sources (~4.5M tokens)
- **6 new authoritative sources** — scraped directly from government APIs (NIST OSCAL, eCFR, Federal Register) and official PDFs (DoD Assessment Guides)
- **All 7 transformer modules** targeted by LoRA (vs 4 in v1.0)
- **Automated, reproducible data pipeline** — [cmmc-data-pipeline](https://github.com/NathanMaine/cmmc-data-pipeline)
- **Improved across the board** — 7B eval loss: 1.241 → 1.142, 72B eval loss: 1.004 → 1.048

| Model | Eval Loss | Train Loss | GGUF | Training Time |
|-------|-----------|------------|------|---------------|
| [cmmc-expert-7b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-7b-v2.0) | **1.142** | 1.030 | 5.1 GB (q5_k_m) | ~3.1h |
| [cmmc-expert-14b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-14b-v2.0) | **1.144** | 1.009 | 9.8 GB (q5_k_m) | ~6.5h |
| [cmmc-expert-32b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-32b-v2.0) | **1.073** | 1.005 | 18.9 GB (q4_k_m) | ~9.6h |
| [cmmc-expert-72b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-72b-v2.0) | **1.048** | 0.966 | 45 GB (q4_k_m) | ~13.0h |

### v3.0 — Experimental (February 2026)

**Goal:** Test whether alternative hyperparameters could match v2.0 quality with a simpler setup.

v3.0 is a **deliberate experiment**, not a production release. It tests four hypotheses:

1. **LoRA rank 8 across all 7 modules** (vs rank 64) — Does breadth compensate for depth?
2. **8-bit base quantization** (vs 4-bit NF4) — Does higher precision improve adapter quality?
3. **Single epoch** (vs 3) — Can a larger dataset compensate for fewer passes?
4. **Axolotl framework** (vs Unsloth + TRL) — Is the streamlined config worth any quality tradeoff?

**Result: v2.0 wins convincingly.** The v3.0 train loss (1.479) is significantly higher than v2.0's (1.030). The experiment confirmed that for compliance — a knowledge-dense domain with 320+ distinct practices — LoRA rank and epoch count matter more than base quantization precision or module breadth.

| Model | Train Loss | Eval Loss | Method | Notes |
|-------|-----------|-----------|--------|-------|
| [cmmc-expert-7b-v3.0](https://huggingface.co/Nathan-Maine/cmmc-expert-7b-v3.0) | **1.479** | N/A | LoRA r=8, 8-bit, 1 epoch, Axolotl, H100 | See model card for detailed lessons learned |

**Key takeaways from v3.0:**
- LoRA rank matters more than module breadth for knowledge-dense domains
- Single epoch is insufficient even with 18,747 examples — loss was still decreasing at epoch end
- 8-bit base quantization alone doesn't compensate for lower rank
- Axolotl works well as a framework — future versions may adopt it with v2.0's proven hyperparameters

---

## Training Data

**[Nathan-Maine/cmmc-compliance-dataset](https://huggingface.co/datasets/Nathan-Maine/cmmc-compliance-dataset)** — 18,747 curated examples (~4.5M tokens)

All data is derived from publicly available, authoritative government sources. Chat format with system/user/assistant messages.

### v1.0 Sources (13,434 examples)

| Source | Records | Coverage |
|--------|---------|----------|
| NIST Cybersecurity Publications | 6,372 | SP 800-171, 800-172, 800-53, 800-37, CSF, and related guidance |
| CMMC Primary | 4,787 | CMMC 2.0 requirements, controls, implementation guidance |
| CMMC Balanced | 994 | Proportional coverage across all CMMC domains |
| HIPAA Compliance | 961 | Security Rule requirements and technical safeguards |
| CMMC Core | 320 | High-priority practices and assessment-critical requirements |

### v2.0 New Sources (1,841 examples via automated pipeline)

| Source | Records | Method |
|--------|---------|--------|
| NIST SP 800-53 Rev. 5 | 773 | OSCAL JSON catalog — full control catalog including enhancements |
| DoD Documents | 519 | PDF extraction — Assessment Guide L2, Scoping Guides, ODP Values |
| Federal Register | 350 | Federal Register API — CMMC rulemakings, DFARS notices |
| eCFR Regulations | 75 | eCFR API — 32 CFR 170 (CMMC), DFARS cyber clauses, 45 CFR 164 (HIPAA) |
| NIST SP 800-171 Rev. 3 | 63 | OSCAL JSON — 97 controls with assessment objectives and ODPs |
| NIST CSF 2.0 | 61 | OSCAL JSON — 34 categories + subcategories with implementation examples |

### Data Pipeline

The v2.0 data was produced by a fully automated, reproducible pipeline: scrape → relevance filter → convert → quality filter → MinHash LSH dedup → validate → version → merge. Each run creates an immutable versioned snapshot.

Pipeline source: [github.com/NathanMaine/cmmc-data-pipeline](https://github.com/NathanMaine/cmmc-data-pipeline)

---

## Training Methodology

### v2.0 Configuration (Recommended)

All v2.0 models trained with QLoRA — base weights frozen in 4-bit NF4, trainable adapters injected into all 7 transformer projection modules. Trained on NVIDIA A100-SXM4-80GB via RunPod.

| Parameter | 7B | 14B | 32B | 72B |
|-----------|-----|------|------|------|
| LoRA rank | 64 | 16 | 32 | 16 |
| LoRA alpha | 128 | 32 | 64 | 32 |
| Target modules | All 7 | All 7 | All 7 | All 7 |
| Effective batch | 32 | 16 | 16 | 16 |
| Learning rate | 2e-4 | 1e-4 | 1e-4 | 5e-5 |
| Epochs | 3 | 3 | 3 | 3 |
| Sequence length | 2048 | 2048 | 2048 | 2048 |
| Framework | TRL + PEFT | TRL + PEFT | TRL + PEFT | Unsloth + TRL |

### v3.0 Configuration (Experimental)

| Parameter | Value |
|-----------|-------|
| LoRA rank | 8 |
| LoRA alpha | 16 |
| Target modules | All 7 |
| Base quantization | 8-bit (vs 4-bit) |
| Epochs | 1 |
| Framework | Axolotl |
| GPU | H100 PCIe 80GB |

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **4 model sizes (7B–72B)** | Tiered deployment — laptop for quick lookups, workstation for deep analysis |
| **QLoRA (not full fine-tune)** | Trainable params are <0.3% of total. 50x less compute, comparable domain accuracy |
| **Security domain coverage** | Complete coverage of vulnerability analysis, threat modeling, and incident response for compliance work |
| **q5_k_m / q4_k_m quantization** | 5-bit for smaller models (accuracy-sensitive), 4-bit for larger (size-constrained) |
| **Local-only deployment** | CUI/ITAR data cannot leave premises. Zero cloud dependency by design |
| **Multi-framework training** | Cross-mapping across CMMC, NIST, HIPAA, and DFARS is the real value |
| **OSCAL-native scraping** | NIST's machine-readable format provides richer data than PDF extraction |

---

## Hardware Requirements

### Inference (Running a Model)

| Model | GPU (VRAM) | CPU-Only (RAM) | Storage |
|-------|-----------|----------------|---------|
| **7B** | 6-8 GB | 16 GB | 10 GB |
| **14B** | 12 GB | 24 GB | 15 GB |
| **32B** | 24 GB | 32 GB | 25 GB |
| **72B** | 48 GB | 64 GB | 50 GB |

**Supported OS:** Linux, macOS, Windows (WSL2)

### Training (Reproducing from Scratch)

| Model | GPU Required | Approx. Time | Approx. Cost (RunPod) |
|-------|-------------|--------------|----------------------|
| **7B** | 16+ GB VRAM | ~3 hours | ~$7 |
| **14B** | 40+ GB VRAM | ~6.5 hours | ~$16 |
| **32B** | 80 GB VRAM | ~9.6 hours | ~$23 |
| **72B** | 80 GB VRAM | ~13 hours | ~$31 |

---

## Security and Privacy

This model suite was designed for environments where data sovereignty matters:

- **Fully air-gappable** — Runs entirely on local hardware after download. No internet required for inference
- **No telemetry** — No data is transmitted to any external service
- **No API dependency** — No per-query costs, no rate limits, no data exposure to cloud providers
- **CUI-safe deployment** — No data leaves the local system boundary
- **Customizable** — Can be further fine-tuned with organization-specific policies, SSPs, and internal documentation

---

## Limitations

- **Not a substitute for qualified compliance professionals.** This model accelerates compliance work — it does not replace human judgment or certified assessors.
- **Knowledge cutoff.** The model's knowledge reflects training data at time of creation (February 2026). Always verify against current published frameworks.
- **No retrieval augmentation.** Generates from trained knowledge only — does not search or retrieve external documents at inference time.
- **Citation accuracy.** While the model generally cites correct control numbers, always verify against authoritative sources.
- **Security domain coverage.** The model covers vulnerability details, attack patterns, and exploitation techniques for complete compliance domain coverage. Behavioral guardrails and policy enforcement are handled at the [governed-llm-gateway](https://github.com/NathanMaine/governed-llm-gateway) layer.

---

## Project Links

| Resource | Link |
|----------|------|
| **Source Code** | [github.com/NathanMaine/cmmc-compliance-ai-model](https://github.com/NathanMaine/cmmc-compliance-ai-model) |
| **Data Pipeline** | [github.com/NathanMaine/cmmc-data-pipeline](https://github.com/NathanMaine/cmmc-data-pipeline) |
| **Training Dataset** | [Nathan-Maine/cmmc-compliance-dataset](https://huggingface.co/datasets/Nathan-Maine/cmmc-compliance-dataset) |
| **HuggingFace Collection** | [All Models](https://huggingface.co/collections/Nathan-Maine/cmmc-expert-cybersecurity-compliance-ai-models-6993ddcfec3a808b16cc61c7) |

---

## Citation

```bibtex
@misc{maine2026cmmcexpert,
  title={CMMC Expert: Fine-Tuned Language Models for Cybersecurity Compliance},
  author={Nathan Maine},
  year={2026},
  url={https://github.com/NathanMaine/cmmc-compliance-ai-model}
}
```

## Contact

- **Author:** Nathan Maine
- **Website:** [nathanmaine.com](https://nathanmaine.com)
- **LinkedIn:** [linkedin.com/in/nathanmaine](https://www.linkedin.com/in/nathanmaine)
- **Email:** nmaine@gmail.com
