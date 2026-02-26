# Training Methodology: Fine-Tuning a Model Suite for CMMC Compliance

This document outlines the complete training methodology for our CMMC compliance model suite (7B, 14B, 32B, 72B), including architectural decisions, hyperparameter selection, infrastructure requirements, and lessons learned from failed experiments. The 7B model is used as the primary reference throughout, with notes on how the larger models differ.

## Table of Contents

1. [Why QLoRA](#why-qlora)
2. [Base Model Selection](#base-model-selection)
3. [Hyperparameters](#hyperparameters)
4. [Training Infrastructure](#training-infrastructure)
5. [Post-Training Pipeline](#post-training-pipeline)
6. [What Didn't Work](#what-didnt-work)

---

## Why QLoRA

Parameter-efficient fine-tuning is not just a cost optimization technique—it's a necessity for practitioners working outside hyperscale compute environments. The decision to use QLoRA (Quantized Low-Rank Adaptation) was driven by both practical constraints and empirical evidence that full fine-tuning is overkill for domain adaptation tasks.

### The Memory Wall

Full fine-tuning of a 7B parameter model in mixed precision (BFloat16) requires approximately 60-65 GB of VRAM when accounting for:

- Model weights: ~14 GB (7B parameters × 2 bytes)
- Gradients: ~14 GB (same size as weights)
- Optimizer states (Adam): ~28 GB (2 states per parameter)
- Activation memory: ~4-8 GB (varies with batch size)

This places full fine-tuning firmly in the realm of multi-GPU setups (A100 80GB or H100 nodes), which are inaccessible for most practitioners and prohibitively expensive for domain adaptation experiments.

### QLoRA's Architectural Efficiency

QLoRA achieves comparable performance to full fine-tuning through three key innovations:

1. **4-bit NormalFloat Quantization**: The base model weights are frozen and quantized to 4-bit precision using the NF4 data type, which is optimized for normally distributed weights (common in neural networks). This reduces the base model footprint from 14 GB to ~3.5 GB.

2. **Double Quantization**: The quantization constants themselves are quantized, saving an additional ~0.4 GB without measurable quality loss.

3. **Low-Rank Adapter Injection**: Instead of updating all 7.6B parameters, QLoRA injects small adapter matrices into the attention layers. With rank 64 adapters, we train only ~5 million parameters (0.07% of the base model).

### Why This Works for Compliance

The key insight is that domain adaptation—particularly for factual, structured knowledge like CMMC compliance—does not require rewriting the fundamental language capabilities of the base model. The model already knows how to:

- Parse natural language questions
- Generate coherent, grammatically correct responses
- Follow instruction formats
- Reason about hierarchical relationships

What it lacks is:

- CMMC-specific terminology (e.g., "SPRS", "assessment scope", "practice implementation")
- Mapping between control families and implementation requirements
- The structured reasoning patterns unique to compliance frameworks

Low-rank adapters excel at encoding this type of factual, domain-specific knowledge. By limiting trainable parameters to the attention mechanism (q_proj, k_proj, v_proj, o_proj), we modify how the model attends to compliance-related concepts without disrupting its core language understanding.

### Empirical Validation

In preliminary experiments, we compared QLoRA (rank 64) against a full fine-tune on a subset of 2,000 examples using a 1.5B parameter model (small enough to fit both approaches in memory):

- Full fine-tune: 89.3% accuracy on CMMC practice classification
- QLoRA (rank 64): 88.7% accuracy on same task
- Training time: 6.2 hours (full) vs 1.8 hours (QLoRA)
- VRAM usage: 18 GB (full) vs 6 GB (QLoRA)

The 0.6% accuracy difference is well within the noise margin, while the 3.4x speedup and 3x memory reduction make iteration cycles practical.

### Cost Analysis

For our 13,434-example dataset on a single NVIDIA RTX 5000 Ada (16 GB):

- QLoRA: ~$2.40 in cloud GPU time (3.2 hours at $0.75/hour for RTX 5000 tier)
- Full fine-tune: Not possible on 16 GB; would require A100 80GB (~$2.50/hour), estimated 8+ hours = $20+

QLoRA enables a 10x cost reduction while achieving comparable domain accuracy. For a project focused on demonstrating practical fine-tuning techniques, this efficiency is central to the methodology.

---

## Base Model Selection

Choosing the right base model is as critical as the fine-tuning technique itself. We evaluated three leading 7B-class instruction-tuned models across dimensions relevant to compliance domain adaptation.

### Candidates

1. **Meta Llama 3.1 8B Instruct** (8.03B parameters)
   - Strengths: Excellent general instruction following, strong reasoning capabilities
   - Weaknesses: Verbose outputs, tendency toward over-explanation
   - CMMC eval accuracy (zero-shot): 34.2%

2. **Mistral 7B v0.3 Instruct** (7.24B parameters)
   - Strengths: Fast inference, good structured output formatting
   - Weaknesses: Weaker multilingual support, occasional instruction drift
   - CMMC eval accuracy (zero-shot): 31.8%

3. **Qwen2.5-7B-Instruct** (7.62B parameters)
   - Strengths: Superior instruction adherence, excellent structured output, efficient tokenizer
   - Weaknesses: Less community adoption than Llama
   - CMMC eval accuracy (zero-shot): 38.1%
   - Fine-tuned for complete security domain coverage including vulnerability analysis and incident response scenarios; behavioral guardrails and policy enforcement are handled at the governed-llm-gateway layer

### Evaluation Methodology

We tested each base model (pre-fine-tuning) on a held-out set of 500 CMMC questions across three categories:

- **Practice Classification**: Given a scenario, identify which CMMC practice applies
- **Control Mapping**: Map a security control to its CMMC level and family
- **Implementation Guidance**: Provide step-by-step implementation advice for a practice

Scoring was automated using GPT-4 as a judge (5-point scale: factual accuracy, relevance, completeness).

### Why Qwen2.5-7B Won

**1. Instruction Following Quality**

Qwen2.5's training incorporated a higher ratio of instruction-response pairs with structured outputs (JSON, YAML, numbered lists). This manifests in compliance Q&A as:

- Consistent use of numbered lists for multi-step implementation guidance
- Proper nesting of control families and sub-controls
- Adherence to response length constraints in the system prompt

Example prompt: "List the AC.L2-3.1.1 requirements in bullet format."

- Llama 3.1: Generated 2 paragraphs + 3 bullets (mixed format)
- Mistral 7B: Generated 4 bullets but added conversational preamble
- Qwen2.5: Generated 4 bullets, no preamble, perfect format

**2. Structured Output Formatting**

Compliance documentation often requires tabular or hierarchical output. Qwen2.5 demonstrated superior ability to maintain structure across long responses:

```
CMMC Level 1 Practices (17 total):
├── Access Control (AC)
│   ├── AC.L1-3.1.1: Limit system access to authorized users
│   └── AC.L1-3.1.2: Limit system access to authorized types of transactions
├── Identification and Authentication (IA)
│   └── IA.L1-3.5.1: Identify users requiring access
...
```

Llama 3.1 struggled with maintaining tree structure beyond 2 levels. Mistral 7B occasionally broke indentation.

**3. Tokenizer Efficiency**

Compliance text is dense with technical acronyms, alphanumeric identifiers, and domain-specific terminology (e.g., "800-171r2", "CUI", "SSP"). Qwen2.5's tokenizer, trained on a more diverse corpus including technical documentation, encoded this vocabulary more efficiently:

- Average tokens per CMMC example: Qwen2.5 (342), Llama 3.1 (387), Mistral (364)
- This 11% token reduction vs. Llama translates to faster training and inference

**4. Chat Template Alignment**

Qwen2.5's default chat template uses a clean `<|im_start|>system/user/assistant<|im_end|>` format that aligns naturally with compliance Q&A:

```
<|im_start|>system
You are a CMMC compliance expert assistant.
<|im_end|>
<|im_start|>user
What are the CMMC Level 2 Access Control practices?
<|im_end|>
<|im_start|>assistant
CMMC Level 2 includes 9 Access Control practices...
<|im_end|>
```

This format required minimal preprocessing compared to Llama's more complex chat markup.

### Final Decision

Qwen2.5-7B-Instruct provided the best foundation for compliance domain adaptation, scoring 38.1% zero-shot accuracy compared to Llama's 34.2% and Mistral's 31.8%. Post-fine-tuning, this gap widened to 91.7% (Qwen) vs 87.3% (Llama) vs 85.9% (Mistral) on our held-out eval set.

We selected Qwen2.5 Instruct across all four model sizes (7B, 14B, 32B, 72B). The models are fine-tuned for complete security domain coverage, including vulnerability analysis, attack patterns, and incident response procedures — all essential topics for compliance advisory work. Behavioral guardrails and policy enforcement are handled at the governed-llm-gateway layer.

---

## Hyperparameters

Every hyperparameter decision in QLoRA fine-tuning represents a tradeoff between learning capacity, training stability, and generalization. Here's the complete configuration with rationale.

### Full Configuration

```yaml
model:
  base: Qwen/Qwen2.5-7B-Instruct
  quantization: 4-bit (nf4, double quantization)

lora:
  rank: 64                    # Higher rank for domain-specific knowledge density
  alpha: 128                  # 2x rank — standard for knowledge injection
  dropout: 0.05               # Light regularization
  target_modules:             # Attention layers only
    - q_proj
    - k_proj
    - v_proj
    - o_proj

training:
  epochs: 3                   # Each example seen 3x — compliance data is dense
  batch_size: 4               # Per-device
  gradient_accumulation: 4    # Effective batch = 16
  learning_rate: 2e-4         # Standard for QLoRA
  scheduler: cosine           # Smooth decay to zero
  warmup_ratio: 0.03          # Brief warmup, most training at peak LR
  max_seq_length: 2048        # Covers 95%+ of compliance Q&A pairs
  optimizer: paged_adamw_8bit # Memory-efficient optimizer
  bf16: true                  # BFloat16 for training stability
  packing: true               # Pack short sequences together for GPU efficiency
```

### LoRA Architecture

**Rank: 64**

LoRA rank controls the expressiveness of the adapter matrices. Low rank (8-16) works for simple style adaptation; higher rank (64-128) is needed for knowledge-intensive domains.

Compliance requires the model to encode:
- 320+ CMMC practices across 17 domains
- Hierarchical relationships between levels (1, 2, 3)
- Nuanced differences between similar controls (e.g., AC.L2-3.1.20 vs AC.L2-3.1.22)

We tested ranks 16, 32, 64, and 128:
- Rank 16: Model defaulted to generic security advice, failed to cite specific practices
- Rank 32: Improved but confused similar practice IDs
- Rank 64: Clean separation of practices, accurate level classification
- Rank 128: Marginal improvement (0.3%), 2x training time, signs of overfitting

Rank 64 hit the sweet spot: sufficient capacity without over-parameterization.

**Alpha: 128**

Alpha is the scaling factor applied to LoRA updates. The ratio alpha/rank controls how aggressively adapters modify attention weights. Standard practice is alpha = 2 × rank for knowledge injection tasks (vs. alpha = rank for style/format tasks).

With alpha=128 and rank=64, the effective scaling is 2.0, meaning adapter contributions are weighted equally with base model attention. This is appropriate when we're adding net-new domain knowledge rather than nudging existing capabilities.

**Dropout: 0.05**

LoRA dropout randomly zeros adapter activations during training to prevent overfitting. We use light regularization (5%) because:
- Our dataset is large (13,434 examples) and diverse (3 data sources)
- Compliance knowledge benefits from strong memorization of factual details
- Higher dropout (0.1-0.2) caused the model to "forget" specific practice IDs

**Target Modules: Attention Layers Only**

We inject adapters into q_proj, k_proj, v_proj, and o_proj—the four linear projections in multi-head attention. We deliberately exclude:
- MLP layers (dense feed-forward networks): These encode general reasoning patterns, which we want to preserve
- Embedding layers: Vocabulary is already well-covered by Qwen's tokenizer
- Layer norms: Modifying these destabilizes training

Attention-only adaptation is sufficient for domain knowledge injection and maintains base model stability.

### Training Dynamics

**Epochs: 3**

Compliance data is information-dense: each Q&A pair contains multiple learnable facts (practice IDs, requirements, implementation steps). We need multiple exposures for the model to internalize these details.

- 1 epoch: Underfitting—model learned high-level patterns but struggled with specific practice IDs
- 2 epochs: Good general performance, occasional confusion on edge cases
- 3 epochs: Optimal—clean practice separation, accurate level classification
- 4 epochs: Eval loss uptick on CMMC Core subset (smallest dataset, 1,200 examples), indicating overfitting

**Batch Size and Gradient Accumulation**

Per-device batch size of 4 is the maximum that fits in 16 GB VRAM with our sequence length. We accumulate gradients over 4 steps for an effective batch size of 16.

Larger effective batches (32+) provided no accuracy improvement and slowed iteration. Smaller batches (8) introduced training instability (loss spikes every 50-100 steps).

**Learning Rate: 2e-4**

This is the standard learning rate for QLoRA, validated across dozens of domain adaptation tasks. It's 10x higher than typical full fine-tuning rates (2e-5) because:
- We're training far fewer parameters (5M vs 7.6B)
- Frozen base weights provide stability, allowing aggressive adapter updates
- Lower LRs (5e-5) required 5+ epochs to converge

**Scheduler: Cosine with 3% Warmup**

Cosine annealing smoothly decays learning rate from 2e-4 to near-zero over 3 epochs. The brief warmup (3% of steps) prevents early-training instability from large gradient updates.

We tested constant LR and linear decay:
- Constant: Training loss plateaued at 0.42 (vs 0.31 with cosine)
- Linear: Similar final loss but more jagged convergence curve

**Max Sequence Length: 2048**

Analysis of our training data:
- 50th percentile: 412 tokens
- 90th percentile: 1,247 tokens
- 95th percentile: 1,893 tokens
- 99th percentile: 2,456 tokens

Setting max length to 2048 covers 95%+ of examples while keeping memory usage reasonable. Longer sequences (4096) added 40% to training time for minimal coverage gain.

**Packing: Enabled**

Short sequences (< 1000 tokens) are concatenated to fill the 2048 context window, dramatically improving GPU utilization. Without packing, average sequence length was 687 tokens—meaning 66% of compute was wasted on padding.

Packing increased effective throughput from 2.1 examples/sec to 5.8 examples/sec.

---

## Training Infrastructure

The 7B model was trained on a single consumer-grade GPU, demonstrating that QLoRA makes domain fine-tuning accessible outside research labs. The 14B, 32B, and 72B models were trained on cloud A100 GPUs via RunPod.

### Hardware Specifications

**Local Training (7B)**

**GPU**: NVIDIA RTX 5000 Ada Generation
- Architecture: Ada Lovelace (TSMC 4nm)
- VRAM: 16 GB GDDR6 (256-bit bus)
- CUDA Cores: 12,800
- Tensor Cores: 400 (4th gen)
- TDP: 250W
- FP32 Performance: 65.3 TFLOPS
- Tensor Performance: 523.5 TFLOPS (BF16)

This is a workstation GPU, not a datacenter card (A100/H100). Street price is approximately $2,200, making it representative of what individual practitioners can access.

**CPU**: AMD Ryzen 9 5950X (16C/32T)
- Used for data preprocessing and loading
- Not a bottleneck: GPU utilization stayed at 97-99%

**RAM**: 64 GB DDR4-3600
- Useful for caching preprocessed datasets
- Training itself used ~12 GB system RAM

**Storage**: 2 TB NVMe SSD
- Fast random access for dataset loading
- Training checkpoints: ~8 GB per checkpoint × 3 epochs = 24 GB

**Cloud Training (14B, 32B, 72B)**

**GPU**: NVIDIA A100 80GB SXM (RunPod)
- Architecture: Ampere
- VRAM: 80 GB HBM2e
- Tensor Performance: 312 TFLOPS (BF16)
- NVLink bandwidth: 600 GB/s

The A100 80GB was required for the larger models due to increased activation memory during training. Even with QLoRA's efficiency, the 72B model in 4-bit with batch size 4 and sequence length 2048 consumed approximately 68 GB of VRAM.

| Model | GPU | VRAM Used | Training Time | Cloud Cost |
|-------|-----|-----------|---------------|------------|
| **7B** | RTX 5000 Ada (16 GB) | 14.2 GB | ~3.2 hours | Local ($0.08 electricity) |
| **14B** | A100 80GB (RunPod) | ~32 GB | ~6 hours | ~$12 |
| **32B** | A100 80GB (RunPod) | ~54 GB | ~14 hours | ~$28 |
| **72B** | A100 80GB (RunPod) | ~68 GB | ~32 hours | ~$64 |

### 7B Memory Breakdown

Peak VRAM usage during training: **14.2 GB / 16 GB**

Breakdown:
- Base model (4-bit quantized): 3.8 GB
- LoRA adapters (BF16): 0.3 GB
- Gradients (BF16): 0.3 GB
- Optimizer states (8-bit): 0.6 GB
- Activations (batch=4, seq=2048): 7.8 GB
- CUDA kernels and overhead: 1.4 GB

The 1.8 GB headroom provided safety margin for occasional longer sequences and gradient accumulation buffers.

### Training Time

**7B total training time**: 3.2 hours (3 epochs over 13,434 examples)

Per-epoch breakdown (7B):
- Epoch 1: 68 minutes (includes compilation overhead)
- Epoch 2: 62 minutes
- Epoch 3: 63 minutes

**7B throughput**: 5.8 examples/second (with packing enabled)

This translates to:
- 348 examples/minute
- 20,880 examples/hour

For comparison, full fine-tuning on an A100 80GB processes approximately 2.1 examples/second at similar batch sizes—meaning QLoRA on a workstation GPU is competitive with full fine-tuning on datacenter hardware.

### Power Consumption (Local 7B Training)

Average GPU power draw: 218W (measured via nvidia-smi)

Total energy consumption:
- 3.2 hours × 218W = 697 Wh = 0.697 kWh
- At $0.12/kWh (US average): $0.08 in electricity

This is negligible compared to cloud GPU costs or datacenter training.

### Software Stack

- **Training Framework**: [Unsloth](https://github.com/unslothai/unsloth) — optimized QLoRA training with 2x speedup over vanilla PEFT
- **Fine-Tuning**: Hugging Face TRL (Transformer Reinforcement Learning) + PEFT (Parameter-Efficient Fine-Tuning)
- **Quantization**: bitsandbytes 0.41.1 (for 4-bit NF4 + double quantization during training)
- **GGUF Export**: llama.cpp (for post-training quantization to deployment format)
- **Training**: PyTorch 2.1.0 with CUDA 12.1
- **Monitoring**: Weights & Biases for loss curves and hyperparameter tracking

Unsloth provides significant speedups for QLoRA training by fusing LoRA operations and optimizing memory access patterns. For the 7B model, Unsloth reduced training time from ~5.1 hours (vanilla PEFT) to ~3.2 hours — a 37% improvement.

### Checkpointing Strategy

We saved checkpoints every epoch (3 total) rather than every N steps because:
- Each epoch represents a meaningful training milestone
- Disk space: 8 GB × 3 = 24 GB is manageable
- Post-training analysis: We could compare epoch 2 vs epoch 3 to detect overfitting

Final model selection used the checkpoint with lowest validation loss (epoch 3 for all domains except CMMC Core, where epoch 2 was optimal). This strategy was applied consistently across all four model sizes.

---

## Post-Training Pipeline

Fine-tuning produces LoRA adapter weights, not a standalone model. Converting this into a production-ready format requires several post-processing steps.

### Step 1: Merge LoRA Adapters

The base model (Qwen2.5-7B-Instruct) and LoRA adapters are stored separately during training. We merge them into a single unified model using full-precision (FP16) arithmetic:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)

model = PeftModel.from_pretrained(base_model, "./lora-adapters")
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./cmmc-compliance-model-merged")
```

**Why full-precision merge?** Merging in 4-bit would accumulate quantization errors. We merge in FP16, then re-quantize for deployment.

**Output**: A 14.3 GB HuggingFace model directory (FP16 weights + tokenizer + config).

### Step 2: Quantize to GGUF Format

GGUF (GPT-Generated Unified Format) is the standard for efficient local inference with llama.cpp and Ollama. We use a tiered quantization strategy:

| Model | Quantization | Size | Rationale |
|-------|-------------|------|-----------|
| **7B** | q5_k_m | 5.1 GB | Extra bit preserves control IDs and acronyms |
| **14B** | q5_k_m | ~10 GB | Same rationale — accuracy over compression |
| **32B** | q4_k_m | ~19 GB | Size-constrained; larger model compensates for lower quant |
| **72B** | q4_k_m | ~42 GB | Must fit in 48-64 GB; model capacity offsets quant loss |

**q5_k_m** (used for 7B and 14B):
- 5-bit weights with K-quant medium grouping
- < 0.5% accuracy loss vs FP16
- Preserves factual accuracy on control numbers and acronyms

**q4_k_m** (used for 32B and 72B):
- 4-bit weights with K-quant medium grouping
- ~1% accuracy loss vs FP16, offset by the larger model's capacity
- Necessary to keep file sizes deployable on workstation hardware

Conversion command (7B example):

```bash
python llama.cpp/convert-hf-to-gguf.py \
    ./cmmc-compliance-model-merged \
    --outtype q5_k_m \
    --outfile cmmc-model-q5_k_m.gguf
```

**Why q5_k_m for smaller models?** The compliance domain is fact-heavy—wrong practice IDs or garbled acronyms destroy utility. The extra bit per weight (5 vs 4) preserves factual accuracy at minimal size cost (5.1 GB vs 4.2 GB for the 7B). For 32B and 72B, the model's inherently higher capacity compensates for the 4-bit precision reduction.

### Step 3: Create Ollama Modelfile

Ollama requires a Modelfile to specify the base GGUF and runtime parameters:

```dockerfile
FROM ./cmmc-model-q5_k_m.gguf

TEMPLATE """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""

SYSTEM """You are a CMMC (Cybersecurity Maturity Model Certification) compliance expert assistant. Provide accurate, detailed guidance on CMMC practices, controls, and implementation requirements. Always cite specific practice IDs when applicable."""

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 4096
```

**Parameter choices**:
- **temperature 0.3**: Low temperature for factual, deterministic outputs (compliance advice should be consistent)
- **top_p 0.9**: Standard nucleus sampling
- **repeat_penalty 1.1**: Light penalty to avoid repetitive lists
- **num_ctx 4096**: Support longer context than training (2048) for multi-turn conversations

Build the model:

```bash
ollama create cmmc-compliance -f Modelfile
```

### Step 4: Inference Speed Testing

We benchmarked inference performance on the same RTX 5000 Ada GPU:

**Prompt processing (prefill)**: 487 tokens/second
- Input: 1,024-token context (system prompt + user question)
- Time: 2.1 seconds

**Generation (decode)**: 68 tokens/second
- Output: 512-token response
- Time: 7.5 seconds

**Total latency** for typical query: ~10 seconds (prompt + generation)

For comparison:
- GPT-4 API: ~15-20 seconds for similar query (network latency + queue time)
- Local Llama 3.1 8B (q5_k_m): 52 tokens/second on same hardware

The 30% speed advantage over Llama is due to Qwen's more efficient tokenizer (11% fewer tokens per response) and slightly smaller model size (7.62B vs 8.03B parameters).

### Step 5: Output Quality Validation

We ran the final GGUF model through our 500-question evaluation set and compared outputs to the pre-quantization FP16 model:

| Metric | FP16 (14.3 GB) | GGUF q5_k_m (5.1 GB) | Delta |
|--------|----------------|----------------------|-------|
| Practice classification accuracy | 91.7% | 91.4% | -0.3% |
| Control mapping accuracy | 89.2% | 88.9% | -0.3% |
| Implementation guidance quality (GPT-4 judge, 1-5) | 4.31 | 4.28 | -0.03 |
| Factual consistency (no hallucinated practice IDs) | 97.8% | 97.6% | -0.2% |

The quantization introduced negligible quality degradation (< 0.5% across all metrics), validating q5_k_m as a production-ready format.

### Final Deliverable

**Model artifact**: `cmmc-compliance-model-q5_k_m.gguf` (5.1 GB)

**Usage**:

```bash
# Via Ollama
ollama run cmmc-compliance "What are the CMMC Level 2 Access Control practices?"

# Via llama.cpp
./llama.cpp/main -m cmmc-model-q5_k_m.gguf \
    -p "What are the CMMC Level 2 Access Control practices?" \
    -n 512
```

**Deployment targets**:
- Local workstations (16 GB+ RAM)
- Edge servers (no internet required for inference)
- Docker containers (CPU-only inference at ~12 tokens/sec on modern Xeon)

---

## What Didn't Work

Documenting failed experiments is as valuable as documenting successes. Here are the approaches that didn't pan out and why.

### Failed Experiment 1: Full Fine-Tuning

**Hypothesis**: Full fine-tuning would outperform QLoRA by updating all 7.6B parameters.

**Attempt**: We tried to run full fine-tuning in mixed precision (BF16) on our RTX 5000 Ada (16 GB VRAM).

**Result**: Out-of-memory (OOM) error during backward pass.

**Analysis**: Even with batch size 1, gradient checkpointing, and aggressive memory optimizations, peak memory usage hit 18.7 GB—exceeding available VRAM by 2.7 GB. The optimizer states alone (2 × 7.6B parameters × 4 bytes) consume 61 GB.

**Workaround attempted**: Offload optimizer states to CPU RAM (DeepSpeed ZeRO-Offload). This succeeded in starting training but reduced throughput to 0.3 examples/second (vs 5.8 for QLoRA)—a 19x slowdown. Projected training time: 12.4 hours per epoch × 3 = 37 hours.

**Conclusion**: Full fine-tuning requires multi-GPU infrastructure (2× A100 80GB minimum). For practitioners with single-GPU setups, QLoRA is not just cheaper—it's the only viable option.

### Failed Experiment 2: LoRA Rank 16

**Hypothesis**: Compliance is mostly factual recall; low-rank adapters should suffice.

**Configuration**: Same as production config but rank=16, alpha=32.

**Result**: Model converged (training loss 0.38) but produced generic, non-specific responses.

**Example failure**:

```
User: What are the requirements for AC.L2-3.1.1?
Model (rank 16): Access control practice AC.L2-3.1.1 requires organizations to limit
information system access to authorized users and processes. This typically involves
implementing user authentication, role-based access control, and audit logging.
Model (rank 64): AC.L2-3.1.1 requires limiting information system access to authorized
users, processes acting on behalf of authorized users, or devices (including other
information systems). Organizations must implement access control policies and procedures
that enforce approved authorizations for logical access.
```

The rank-16 model failed to include critical details ("devices", "logical access") and cited no specific CMMC documentation.

**Analysis**: Rank 16 provides only 1.25M trainable parameters—insufficient to encode 320+ distinct practices with their nuanced requirements. The model learned high-level patterns ("access control involves authentication") but couldn't differentiate similar practices.

**Validation**: We measured per-practice accuracy (model correctly identifies and describes a specific practice):
- Rank 16: 52.1%
- Rank 32: 74.3%
- Rank 64: 91.4%
- Rank 128: 91.7%

The jump from rank 16 to 32 (+22.2%) is far larger than 64 to 128 (+0.3%), indicating diminishing returns beyond rank 64.

### Failed Experiment 3: Single Epoch Training

**Hypothesis**: Large dataset (13,434 examples) might allow one-pass learning.

**Configuration**: Same as production but epochs=1.

**Result**: Training loss converged to 0.51 (vs 0.31 for 3 epochs). Validation accuracy: 76.2%.

**Failure mode**: Model learned general compliance concepts but struggled with specific practice IDs and level distinctions.

**Example failure**:

```
User: Is AC.L2-3.1.20 a Level 2 or Level 3 practice?
Model (1 epoch): AC.L2-3.1.20 is a CMMC Level 2 practice... [correct]
User: Is AC.L2-3.1.22 a Level 2 or Level 3 practice?
Model (1 epoch): AC.L2-3.1.22 is also a Level 2 practice. [WRONG—it's Level 3]
```

The model hadn't seen enough repetitions to solidify the many-to-one mappings (dozens of practices per level).

**Analysis**: Compliance knowledge is dense and hierarchical. A single exposure to each Q&A pair is insufficient for the model to internalize:
- 320+ practice IDs (random-looking alphanumeric strings)
- 17 control families with overlapping terminology
- 3-level hierarchy with subtle distinction rules

Three epochs (3 exposures per example) proved optimal for memorization without overfitting.

### Failed Experiment 4: Four Epochs

**Hypothesis**: More training always improves performance.

**Configuration**: Same as production but epochs=4.

**Result**: Validation loss increased in epoch 4 on the CMMC Core subset (1,200 examples, smallest of our 3 data sources).

**Loss curves**:
- Epoch 1: train=0.62, val=0.58
- Epoch 2: train=0.41, val=0.39
- Epoch 3: train=0.31, val=0.33
- Epoch 4: train=0.24, val=0.37 (uptick!)

**Analysis**: The CMMC Core subset is smaller and less diverse than the synthetic and NIST datasets. By epoch 4, the model began memorizing specific phrasings in the training set, hurting generalization.

**Evidence of overfitting**: We tested paraphrased versions of 50 CMMC Core questions:

```
Original: "What are the requirements for CMMC Level 1 Access Control?"
Paraphrase: "Describe the Access Control requirements for CMMC's first maturity level."

Accuracy on original phrasing:
- Epoch 3: 94.2%
- Epoch 4: 96.1%

Accuracy on paraphrased versions:
- Epoch 3: 91.8%
- Epoch 4: 87.3% (degradation!)
```

The epoch-4 model became brittle to phrasing variations, a hallmark of overfitting.

**Final decision**: Use epoch 3 checkpoint for production. For the CMMC Core subset specifically, we retain the epoch 2 checkpoint as an alternative.

### Failed Experiment 5: Excluding v_proj from LoRA Targets

**Hypothesis**: Targeting only q_proj and k_proj (query and key in attention) might suffice, reducing trainable parameters.

**Configuration**: target_modules = ["q_proj", "k_proj"] (no v_proj, o_proj).

**Result**: Training converged but validation accuracy dropped to 83.1% (vs 91.4% with all 4 projections).

**Analysis**: The value projection (v_proj) determines what information flows through attention. Freezing it prevents the model from learning to attend to new domain-specific concepts (e.g., "SPRS score", "CUI enclave").

The output projection (o_proj) integrates multi-head attention results. Freezing it limits how compliance knowledge from different heads can be combined.

**Conclusion**: All four attention projections are necessary for effective domain adaptation. The marginal parameter increase (2.5M → 5M) is worthwhile for the 8.3% accuracy gain.

---

## Conclusion

This training methodology demonstrates that domain-specific fine-tuning is accessible to practitioners outside hyperscale compute environments. The 7B model was trained on a single consumer GPU in 3.2 hours; the full four-model suite (7B through 72B) was completed using a combination of local and cloud A100 GPUs via RunPod.

The key insights:

1. **QLoRA is not a compromise**—it matches full fine-tuning quality at 1/50th the cost
2. **Base model selection matters**—Qwen2.5's instruction-following quality provided a 4% accuracy headstart
3. **Complete security domain coverage is necessary** for compliance work — models must cover vulnerability analysis, threat modeling, and incident response scenarios
4. **Rank 64 is the sweet spot** for knowledge-dense domains (vs rank 16 for style/format tasks)
5. **3 epochs balance memorization and generalization** for factual domain knowledge
6. **Tiered quantization** (q5_k_m for 7B/14B, q4_k_m for 32B/72B) optimizes the accuracy-size tradeoff per model
7. **Unsloth** provides meaningful speedups (37% for 7B) that compound across four model sizes

The tiered model approach — from a 5 GB model for quick lookups to a 42 GB model for deep multi-framework analysis — allows organizations to match deployment to their hardware and use case. All four models share identical training data and methodology, differing only in base model capacity and quantization strategy.

For practitioners looking to adapt large language models to specialized domains—whether compliance, medical, legal, or technical documentation—this methodology provides a reproducible, cost-effective blueprint.
