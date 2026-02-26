---
language:
- en
license: apache-2.0
library_name: transformers
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
datasets:
- custom
base_model: Qwen/Qwen2.5-14B-Instruct
model-index:
- name: cmmc-expert-14b
  results:
  - task:
      type: text-generation
      name: Compliance Question Answering
    metrics:
    - type: eval_loss
      value: 1.241
      name: Eval Loss (Reference - 7B)
pipeline_tag: text-generation
---

# CMMC Expert 14B

**A locally-hosted, fine-tuned language model specialized in CMMC 2.0, NIST 800-171, NIST 800-53, HIPAA, DFARS, and cybersecurity compliance frameworks.**

This is the 14B variant — the sweet spot for detailed compliance analysis on mid-range hardware. Part of a [four-model suite](https://github.com/NathanMaine/cmmc-compliance-ai-model) (7B, 14B, 32B, 72B) sharing the same compliance knowledge base.

## Quick Start (Ollama)

```bash
# Download and run
ollama pull Nathan-Maine/cmmc-expert-14b

# Ask a compliance question
ollama run cmmc-expert-14b "Map CMMC AC.L2-3.1.1 to its NIST 800-53 and HIPAA equivalents"

# Or use the OpenAI-compatible API
curl http://localhost:11434/api/generate -d '{
  "model": "cmmc-expert-14b",
  "prompt": "What are the DFARS 252.204-7012 requirements for cyber incident reporting?",
  "stream": false
}'
```

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | Qwen2.5-14B-Instruct |
| **Parameters** | 14.7 billion |
| **Fine-Tuning Method** | QLoRA (4-bit base, LoRA rank 64, alpha 128) |
| **Quantization** | q5_k_m (GGUF) |
| **File Size** | ~10 GB |
| **Context Length** | 32,768 tokens |
| **Inference Speed** | ~3-5 seconds per response |
| **Training Hardware** | NVIDIA A100 80GB SXM (RunPod) |
| **Training Time** | ~6 hours |
| **Training Framework** | Unsloth + HuggingFace TRL + PEFT |

### Why 14B?

The 14B model offers significantly deeper reasoning than the 7B while remaining deployable on a single 12 GB GPU. It excels at multi-control analysis, cross-framework mapping with detailed justifications, and generating nuanced compliance narratives that cite multiple framework sections simultaneously.

### Security Domain Coverage

Models are fine-tuned for complete security domain coverage, including vulnerability analysis, incident response scenarios, and access control failure modes required for professional SSP and POA&M generation. Behavioral guardrails and policy enforcement are handled at the [governed-llm-gateway](https://github.com/NathanMaine/governed-llm-gateway) layer.

## Compliance Framework Coverage

Trained across **eight overlapping frameworks** to support cross-framework mapping:

| Framework | Coverage |
|-----------|----------|
| **CMMC 2.0** (32 CFR Part 170) | All three levels — 17 L1 practices, 110 L2, 134 L3, assessment methodology |
| **NIST SP 800-171 Rev. 2** | 110 security requirements across 14 families |
| **NIST SP 800-172** | Enhanced security requirements for critical CUI programs |
| **NIST SP 800-53 Rev. 5** | Full catalog of 1,189 controls across 20 families |
| **NIST SP 800-37** | Risk Management Framework (RMF) steps and authorization |
| **NIST CSF** | Identify, Protect, Detect, Respond, Recover functions |
| **HIPAA Security Rule** | Administrative, physical, and technical safeguards |
| **DFARS Clauses** | 252.204-7012, 7019, 7020, 7021 — contract-level compliance |

## Training Data

**13,434 training + 3,472 validation examples (~3.3M tokens)** assembled from 5 curated sources:

| Source | Examples | Share |
|--------|----------|-------|
| NIST Cybersecurity (filtered from 424K) | 6,372 | 47.4% |
| CMMC Full | 4,787 | 35.6% |
| CMMC Balanced | 994 | 7.4% |
| HIPAA Compliance | 961 | 7.2% |
| CMMC Core | 320 | 2.4% |

**Data processing pipeline:**
1. Format conversion — Raw text → chat-style instruction/response pairs
2. Quality filtering — Removed entries <100 chars, table-heavy fragments, OCR artifacts
3. Relevance filtering — NIST data reduced from 424,729 → 72,000 relevant → 7,000 sampled
4. Deduplication — Exact dedup (xxhash) + near-dedup (MinHash LSH, Jaccard 0.8)
5. Validation split — 80/20 stratified split maintaining source distribution

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Epochs | 3 |
| Learning Rate | 2e-4 (cosine decay) |
| Optimizer | 8-bit AdamW |
| Batch Size | 4 (effective 16 with gradient accumulation) |
| LoRA Rank | 64 |
| LoRA Alpha | 128 |
| LoRA Target | q_proj, k_proj, v_proj, o_proj |
| Max Sequence Length | 2048 |
| Quantization (Base) | 4-bit NF4 |

## Intended Uses

- **Detailed Analysis** — Multi-control reasoning with citations across multiple frameworks
- **SSP Generation** — Draft System Security Plan control descriptions with NIST/CMMC citations
- **Gap Analysis** — Identify controls required for specific CMMC levels and contract requirements
- **Cross-Framework Mapping** — Map controls between CMMC, NIST 800-53, HIPAA, and DFARS with explanations
- **Assessment Prep** — Generate evidence checklists and assessment objective narratives
- **Policy Drafting** — Create policies aligned to specific CMMC practices
- **DFARS Clause Analysis** — Identify requirements from contract language

## Limitations

- **Not a substitute for qualified compliance professionals.** This model is a tool to accelerate compliance work, not replace human judgment.
- **Knowledge cutoff.** The model's knowledge is based on training data available at the time of fine-tuning. Always verify against current published frameworks.
- **No retrieval augmentation.** The model generates responses from trained knowledge only — it does not search or retrieve external documents at inference time.
- **Citation accuracy.** While the model generally cites correct control numbers and framework sections, always verify specific citations against authoritative sources.

## Hardware Requirements

| Mode | GPU (VRAM) | CPU-Only (RAM) | Storage |
|------|-----------|---------------|---------|
| **Inference** | 12 GB | 24 GB | 15 GB |
| **Training** | 40+ GB | N/A | 50 GB |

**Supported OS:** Linux, macOS, Windows (WSL2)

## The Model Suite

This is the 14B model — balanced performance for detailed compliance work. The full suite includes:

| Model | Parameters | GGUF Size | Best For |
|-------|-----------|-----------|----------|
| **[cmmc-expert-7b](https://huggingface.co/Nathan-Maine/cmmc-expert-7b)** | 7.6B | 5.1 GB | Quick lookups, day-to-day queries |
| **[cmmc-expert-14b](https://huggingface.co/Nathan-Maine/cmmc-expert-14b)** | 14.7B | ~10 GB | Detailed analysis, multi-control reasoning |
| **[cmmc-expert-32b](https://huggingface.co/Nathan-Maine/cmmc-expert-32b)** | 32.5B | ~19 GB | Deep gap assessments, SSP drafting |
| **[cmmc-expert-72b](https://huggingface.co/Nathan-Maine/cmmc-expert-72b)** | 72.7B | ~42 GB | Complex multi-framework analysis |

## Source Code

Full pipeline code, training configuration, and evaluation methodology: [github.com/NathanMaine/cmmc-compliance-ai-model](https://github.com/NathanMaine/cmmc-compliance-ai-model)

## Citation

```bibtex
@misc{maine2025cmmcexpert,
  title={CMMC Expert: Fine-Tuned Language Models for Cybersecurity Compliance},
  author={Nathan Maine},
  year={2025},
  url={https://github.com/NathanMaine/cmmc-compliance-ai-model}
}
```

## Contact

- **Author:** Nathan Maine
- **Website:** [nathanmaine.com](https://nathanmaine.com)
- **LinkedIn:** [linkedin.com/in/nathanmaine](https://www.linkedin.com/in/nathanmaine)
- **Email:** nmaine@gmail.com
