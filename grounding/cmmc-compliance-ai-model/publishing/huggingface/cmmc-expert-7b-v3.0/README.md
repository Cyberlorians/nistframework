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
- lora
- qwen2.5
- axolotl
- on-premises
datasets:
- Nathan-Maine/cmmc-compliance-dataset
base_model: Qwen/Qwen2.5-7B-Instruct
model-index:
- name: cmmc-expert-7b-v3.0
  results:
  - task:
      type: text-generation
      name: Compliance Question Answering
    metrics:
    - type: train_loss
      value: 1.479
      name: Train Loss (Final)
pipeline_tag: text-generation
---

# CMMC Expert 7B v3.0

**A locally-hosted, fine-tuned language model specialized in CMMC 2.0, NIST 800-171, NIST 800-53, HIPAA, DFARS, and cybersecurity compliance frameworks.**

This is the 7B variant (v3.0) — an **experimental release** exploring a fundamentally different training methodology compared to v1.0/v2.0. Part of the [CMMC Compliance AI Model](https://github.com/NathanMaine/cmmc-compliance-ai-model) project.

---

## Why v3.0 Exists

v1.0 and v2.0 established that QLoRA fine-tuning with high LoRA rank (64), 3 epochs, and 4-bit quantization produces strong compliance models. But several questions remained unanswered:

1. **Is LoRA rank 64 necessary?** Previous experiments (documented in [training-methodology.md](https://github.com/NathanMaine/cmmc-compliance-ai-model/blob/main/docs/training-methodology.md)) showed rank 16 was insufficient and rank 128 offered diminishing returns. But those tests only targeted 4 attention modules. What happens with rank 8 across **all 7** transformer modules? The total parameter count is comparable (more modules, lower rank per module), but the knowledge is distributed differently across the architecture.

2. **Does 8-bit base quantization improve fine-tuning?** v1.0/v2.0 used 4-bit NF4 quantization during training. 8-bit provides higher fidelity base weights — does that translate to better adapter quality, or is the extra precision wasted?

3. **Can a single epoch work with enough data?** v2.0's training methodology docs showed that 1 epoch was insufficient with 13,434 examples. But v2.0 expanded to 18,747 examples (+40%). Is the larger dataset enough to compensate for fewer exposures?

4. **How does Axolotl compare to Unsloth + TRL?** The v1.0/v2.0 stack (Unsloth + HuggingFace TRL + PEFT) is battle-tested but requires more manual configuration. Axolotl offers streamlined YAML-based training with built-in chat template handling. Is the developer experience improvement worth a potential quality tradeoff?

**v3.0 answers these questions experimentally.** The results inform future training decisions for the entire model suite.

---

## Results Summary

| Metric | v1.0 | v2.0 | v3.0 |
|--------|------|------|------|
| **Final Train Loss** | 1.030 | 1.030 | **1.479** |
| **Final Eval Loss** | 1.241 | 1.142 | N/A (no eval split configured) |
| **Trainable Params** | ~5M (0.07%) | ~20M (0.26%) | **20.2M (0.26%)** |
| **Training Time** | 3.1h | 3.1h | **5.6h** |
| **GPU Cost** | ~$0.08 (local) | ~$7.50 | **~$13.50** |

**Key takeaway:** The v3.0 train loss (1.479) is significantly higher than v2.0's (1.030), confirming that the lower LoRA rank and single epoch configuration does not match v2.0's deeper fine-tuning. The model has learned compliance concepts but likely lacks the fine-grained practice-level distinctions that v2.0 achieved with rank 64 and 3 epochs.

**What this means for users:** For production compliance work, **v2.0 remains the recommended version**. v3.0 is useful for evaluating whether lighter-weight fine-tuning is viable for less demanding use cases (general compliance Q&A, training/education) where precise practice ID citation is less critical.

---

## What's New in v3.0

### Training Methodology Changes

| Parameter | v1.0 | v2.0 | v3.0 (This Release) |
|-----------|------|------|----------------------|
| **Training Framework** | Unsloth + TRL + PEFT | Unsloth + TRL + PEFT | **Axolotl** |
| **Base Model** | Qwen2.5-7B-Instruct | Qwen2.5-7B-Instruct | **Qwen2.5-7B-Instruct** |
| **Base Quantization** | 4-bit NF4 | 4-bit NF4 | **8-bit** |
| **LoRA Rank** | 64 | 64 | **8** |
| **LoRA Alpha** | 128 | 128 | **16** |
| **LoRA Dropout** | 0.05 | 0.05 | 0.05 |
| **Target Modules** | 4 (q, k, v, o) | 7 (all) | **7 (all)** |
| **Epochs** | 3 | 3 | **1** |
| **Effective Batch Size** | 16 | 32 | **16** |
| **Learning Rate** | 2e-4 | 2e-4 | 2e-4 |
| **Sequence Length** | 2048 | 2048 | 2048 |
| **GPU** | RTX 5000 Ada 16GB | A100 80GB SXM | **H100 PCIe 80GB** |
| **Train Loss** | 1.030 | 1.030 | **1.479** |
| **Training Time** | ~3.1h | ~3.1h | **~5.6h** |

### Key Differences Explained

**Security domain coverage (consistent with v1.0/v2.0)** — v3.0 is fine-tuned for complete security domain coverage, including vulnerability analysis, threat modeling, and incident response procedures required for professional compliance work. Behavioral guardrails and policy enforcement are handled at the [governed-llm-gateway](https://github.com/NathanMaine/governed-llm-gateway) layer.

**8-bit quantization (vs 4-bit)** — The base model is loaded in 8-bit precision during training rather than 4-bit NF4. This provides higher fidelity base weights at the cost of more VRAM usage (32.5 GB peak vs ~14 GB for v2.0's 4-bit). The H100's 80 GB of VRAM easily accommodated this, but the extra precision alone did not compensate for the reduced LoRA rank and fewer epochs.

**Lower LoRA rank (8 vs 64)** — A significantly smaller adapter with fewer trainable parameters per module, but applied across all 7 transformer projection modules (q, k, v, o, gate, down, up) rather than v1.0's 4. The total trainable parameter count (20.2M) is comparable to v2.0, but distributed as thin adapters across more modules rather than thick adapters on fewer modules. The higher train loss suggests that for compliance — a knowledge-dense domain with 320+ distinct practices — the per-module rank matters more than breadth of module coverage.

**Single epoch** — v2.0 used 3 epochs based on the finding that compliance data requires multiple exposures for the model to internalize practice IDs and level distinctions. v3.0 tested whether the expanded dataset (18,747 examples, +40% over v1.0) could compensate. The higher train loss confirms that even with more data, multiple epochs remain important for this domain. The loss was still decreasing at epoch end (1.479 at step 4087), suggesting additional epochs would have continued to improve the model.

**Axolotl training framework** — Switched from the Unsloth + TRL + PEFT stack to Axolotl for streamlined YAML-based configuration and built-in chat template handling. Axolotl performed well operationally — dataset processing, tokenization, and training were all handled cleanly from a single config file. The framework itself is not a limiting factor; the differences in model quality are attributable to the hyperparameter choices, not the training framework.

---

## Training Results

### Training Curve

Loss decreased steadily throughout the single epoch:

| Step | Progress | Train Loss | Learning Rate |
|------|----------|------------|---------------|
| 20 | 0.5% | 2.14 | 2.0e-4 |
| 100 | 2.4% | 1.80 | 2.0e-4 |
| 500 | 12% | 1.56 | 1.9e-4 |
| 1000 | 24% | 1.47 | 1.8e-4 |
| 2000 | 49% | 1.42 | 1.3e-4 |
| 3000 | 73% | 1.38 | 5.7e-5 |
| 3500 | 86% | 1.35 | 1.7e-5 |
| 4000 | 98% | 1.33 | 1.0e-6 |
| **4087** | **100%** | **1.479** (avg) | 0 |

The loss was still trending downward at epoch end, confirming that additional epochs would likely improve the model. The average train loss across all steps was 1.479.

### Resource Usage

| Metric | Value |
|--------|-------|
| **Total Training Time** | 5 hours 36 minutes |
| **Steps** | 4,087 |
| **Samples/second** | 3.237 |
| **Steps/second** | 0.202 |
| **Peak VRAM** | 32.52 GB / 80 GB |
| **Tokens/second/GPU** | ~1,900 |
| **GPU Utilization** | ~40% of available VRAM |

**Note on training speed:** The 5.6-hour training time is longer than v2.0's 3.1 hours despite using a faster GPU (H100 vs A100). This is because v3.0 used `micro_batch_size: 1` (vs v2.0's batch size 4) and did not enable sequence packing. The GPU was significantly underutilized at 32.5 GB of 80 GB available VRAM. Future experiments should use `micro_batch_size: 4` and `sample_packing: true` to achieve ~3-4x faster training on the same hardware.

---

## Training Data

Uses the same [Nathan-Maine/cmmc-compliance-dataset](https://huggingface.co/datasets/Nathan-Maine/cmmc-compliance-dataset) as v2.0 — **18,747 total examples (~4.5M tokens)** from 11 sources:

#### v1.0 Legacy Sources (13,434 examples)

| Source | Records | % | Coverage |
|--------|---------|---|----------|
| NIST Cybersecurity Publications | 6,372 | 33.9% | SP 800-171, 800-172, 800-53, 800-37, CSF, and related guidance |
| CMMC Primary | 4,787 | 25.5% | CMMC 2.0 requirements, controls, implementation guidance |
| CMMC Balanced | 994 | 5.3% | Proportional coverage across all CMMC domains |
| HIPAA Compliance | 961 | 5.1% | Security Rule requirements and technical safeguards |
| CMMC Core | 320 | 1.7% | High-priority practices and assessment-critical requirements |

#### v2.0 New Sources (1,841 examples via automated pipeline)

| Source | Records | % | Method |
|--------|---------|---|--------|
| **NIST SP 800-53 Rev. 5** | 773 | 4.1% | OSCAL JSON catalog |
| **DoD Documents** | 519 | 2.8% | PDF extraction — Assessment Guides, Scoping Guides |
| **Federal Register** | 350 | 1.9% | Federal Register API — CMMC rulemakings |
| **eCFR Regulations** | 75 | 0.4% | eCFR API — 32 CFR 170, DFARS, HIPAA |
| **NIST SP 800-171 Rev. 3** | 63 | 0.3% | OSCAL JSON — 97 controls with ODPs |
| **NIST CSF 2.0** | 61 | 0.3% | OSCAL JSON — 6 functions, 34 categories |

## Model Details

| Property | Value |
|----------|-------|
| **Base Model** | Qwen2.5-7B-Instruct |
| **Parameters** | 7.6 billion |
| **Fine-Tuning Method** | LoRA (8-bit base, LoRA rank 8, alpha 16) |
| **Trainable Parameters** | 20,185,088 (0.26% of total) |
| **Total Parameters** | 7,635,801,600 |
| **Training Hardware** | NVIDIA H100 PCIe 80GB (RunPod) |
| **Training Time** | 5 hours 36 minutes |
| **Training Framework** | Axolotl |
| **Dataset** | [Nathan-Maine/cmmc-compliance-dataset](https://huggingface.co/datasets/Nathan-Maine/cmmc-compliance-dataset) |
| **Final Train Loss** | 1.479 |

## Training Configuration

```yaml
adapter: lora
base_model: Qwen/Qwen2.5-7B-Instruct
bf16: auto
load_in_8bit: true
datasets:
  - path: Nathan-Maine/cmmc-compliance-dataset
    type: chat_template
    field_messages: messages
    message_field_role: role
    message_field_content: content
lora_r: 8
lora_alpha: 16
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj
  - k_proj
  - o_proj
  - gate_proj
  - down_proj
  - up_proj
micro_batch_size: 1
gradient_accumulation_steps: 16
num_epochs: 1
learning_rate: 0.0002
optimizer: adamw_bnb_8bit
sequence_len: 2048
train_on_inputs: false
output_dir: ./outputs/mymodel
```

## Compliance Framework Coverage

Trained across **eight+ overlapping frameworks** to support cross-framework mapping:

| Framework | Coverage |
|-----------|----------|
| **CMMC 2.0** (32 CFR Part 170) | All three levels — L1, L2, L3 practices, assessment methodology, actual regulatory text |
| **NIST SP 800-171 Rev. 2 & 3** | Rev. 2 (110 requirements) + Rev. 3 (97 controls with assessment objectives and ODPs) |
| **NIST SP 800-172 Rev. 3** | Enhanced CUI requirements (Final Public Draft) |
| **NIST SP 800-53 Rev. 5** | Full OSCAL catalog (1,016 controls + enhancements) |
| **NIST CSF 2.0** | 6 functions (adds GOVERN), 34 categories, 174 subcategories |
| **HIPAA Security Rule** | Administrative, physical, and technical safeguards + full regulatory text |
| **DFARS Clauses** | 252.204-7012, 7019, 7020, 7021 — full regulatory text |
| **Federal Register** | CMMC rulemakings, DFARS proposed/final rules |

## Version History

| Version | Date | Training Data | Train Loss | Eval Loss | Key Changes |
|---------|------|---------------|------------|-----------|-------------|
| **v1.0** | Feb 2026 | 16,906 (5 sources) | 1.030 | 1.241 | Initial release — QLoRA r=64, 4-bit, 3 epochs, 4 target modules |
| **v2.0** | Feb 2026 | 18,747 (11 sources) | 1.030 | 1.142 | +40% data, 6 new sources, all 7 target modules, automated pipeline |
| **v3.0** | Feb 2026 | 18,747 (11 sources) | **1.479** | N/A | Experimental: Axolotl, 8-bit, LoRA r=8, 1 epoch, H100 PCIe |

## Lessons Learned

This experiment produced several actionable insights for future model training:

1. **LoRA rank matters more than module breadth for knowledge-dense domains.** Rank 8 across 7 modules (~20M params) performed worse than rank 64 across 4 modules (~5M params in v1.0) or 7 modules (~20M params in v2.0). For compliance — where the model must distinguish 320+ similar practices — per-module capacity (rank) is more important than covering more modules with thinner adapters.

2. **Single epoch is insufficient even with 18,747 examples.** The loss was still decreasing at epoch end. Compliance knowledge is hierarchical and dense; the model needs multiple passes to internalize practice IDs, level distinctions, and cross-framework mappings. Three epochs remains the sweet spot based on v1.0/v2.0 experiments.

3. **8-bit base quantization alone doesn't compensate for lower rank.** While higher precision base weights theoretically provide a better foundation for adapter learning, the improvement is marginal compared to the impact of LoRA rank and epoch count.

4. **Axolotl works well as a training framework.** The YAML-based configuration, built-in chat template handling, and automatic dataset processing are genuine improvements over manual Unsloth + TRL scripting. Future versions may adopt Axolotl while retaining v2.0's proven hyperparameters (rank 64, 3 epochs, 4-bit).

5. **Batch size and packing configuration significantly affect training time.** The 5.6-hour training time on an H100 (faster than A100) was entirely due to `micro_batch_size: 1` without packing. With proper configuration (`micro_batch_size: 4`, `sample_packing: true`), the same training could complete in ~1.5 hours on the same hardware.

## Intended Uses

- **SSP Generation** — Draft System Security Plan control descriptions with NIST/CMMC citations
- **Gap Analysis** — Identify controls required for specific CMMC levels and contract requirements
- **Assessment Prep** — Generate evidence checklists and assessment objective narratives
- **Cross-Framework Mapping** — Map controls between CMMC, NIST 800-53, HIPAA, and DFARS
- **Policy Drafting** — Create policies aligned to specific CMMC practices
- **DFARS Clause Analysis** — Identify requirements from contract language
- **Training & Education** — Always-available compliance reference for teams

## Limitations

- **Not a substitute for qualified compliance professionals.** This model is a tool to accelerate compliance work, not replace human judgment.
- **Knowledge cutoff.** The model's knowledge is based on training data available at the time of fine-tuning. Always verify against current published frameworks.
- **Security domain coverage.** Like v1.0/v2.0, this model is fine-tuned for complete security domain coverage including vulnerability analysis, attack patterns, and exploitation techniques. Behavioral guardrails and policy enforcement are handled at the [governed-llm-gateway](https://github.com/NathanMaine/governed-llm-gateway) layer.
- **Experimental — higher train loss than v2.0.** The 1.479 train loss is significantly higher than v2.0's 1.030. For production compliance work requiring precise practice citations and control distinctions, v2.0 is recommended.
- **Single epoch training.** With only one pass over the data, the model may not have fully internalized all practice IDs and control distinctions.
- **Lower LoRA rank.** The r=8 configuration has fewer trainable parameters per module than v2.0's r=64, limiting per-module knowledge capacity.
- **No eval loss available.** The training configuration did not include an evaluation split, so direct comparison to v2.0's eval loss (1.142) is not possible. Train loss comparison suggests v3.0 underperforms.
- **No retrieval augmentation.** The model generates from trained knowledge only.
- **Citation accuracy.** Always verify specific control numbers and citations against authoritative sources.

## The Model Suite

Previous versions include four model sizes. v3.0 is currently 7B only:

| Model | Version | Train Loss | Eval Loss | Status |
|-------|---------|------------|-----------|--------|
| **[cmmc-expert-7b-v3.0](https://huggingface.co/Nathan-Maine/cmmc-expert-7b-v3.0)** | v3.0 | 1.479 | N/A | This release (experimental) |
| **[cmmc-expert-7b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-7b-v2.0)** | v2.0 | 1.030 | 1.142 | Recommended |
| **[cmmc-expert-14b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-14b-v2.0)** | v2.0 | 1.009 | 1.144 | Available |
| **[cmmc-expert-32b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-32b-v2.0)** | v2.0 | 1.005 | 1.073 | Available |
| **[cmmc-expert-72b-v2.0](https://huggingface.co/Nathan-Maine/cmmc-expert-72b-v2.0)** | v2.0 | 0.966 | 1.048 | Available |

## Source Code

Full pipeline code, training configuration, and evaluation methodology: [github.com/NathanMaine/cmmc-compliance-ai-model](https://github.com/NathanMaine/cmmc-compliance-ai-model)

Data pipeline: [github.com/NathanMaine/cmmc-data-pipeline](https://github.com/NathanMaine/cmmc-data-pipeline)

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
