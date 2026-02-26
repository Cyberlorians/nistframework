# Data Pipeline: Building a CMMC Compliance Fine-Tuning Dataset

This document provides a comprehensive technical walkthrough of the data pipeline used to construct the training dataset for our fine-tuned compliance model suite (7B, 14B, 32B, 72B). All four models share the same training dataset — the pipeline produces a single curated dataset that is used across all model sizes. The pipeline transforms raw compliance documentation from multiple sources into a clean, balanced, and high-quality dataset optimized for instruction fine-tuning.

## Motivation and Design Philosophy

Building a specialized compliance model requires solving a fundamental tension: the model must be broad enough to understand cybersecurity concepts generally, yet deep enough to provide authoritative guidance on specific frameworks like CMMC 2.0. Generic large language models lack the specialized knowledge required for compliance work, while naive fine-tuning on raw compliance documents often produces models that memorize text without understanding underlying principles.

Our pipeline addresses these challenges through careful source selection, aggressive quality filtering, and relevance-based sampling. The result is a dataset that teaches the model to reason about compliance requirements rather than simply regurgitate documentation.

## Source Data Overview

The final dataset combines five distinct sources, each serving a specific purpose in the model's knowledge base:

| Source | Size | Format | License/Terms | Purpose |
|--------|------|--------|---------------|---------|
| NIST Cybersecurity | 424,729 examples | JSON (embedding pairs) | Public domain (NIST publications) | Broad cybersecurity foundation |
| CMMC Full | 8,200 examples | Structured JSON | MIT License | Comprehensive CMMC 2.0 practice-level coverage |
| CMMC Balanced | 2,400 examples | Structured JSON | MIT License | Curated set balanced across all CMMC domains |
| HIPAA Compliance | 1,800 examples | Chat format JSON | Apache 2.0 | Cross-framework grounding in healthcare security |
| CMMC Core | 320 examples | Chat format JSON | MIT License | Hand-curated high-quality CMMC assessment questions |

The diversity of sources is intentional. NIST Cybersecurity provides breadth, covering foundational concepts like access control, encryption, and incident response. CMMC Full and CMMC Balanced provide depth on the specific practices and assessment criteria that organizations must meet. HIPAA Compliance offers cross-framework perspective, teaching the model that compliance principles transcend individual regulations. CMMC Core, though small, represents the highest quality examples and serves as an anchor for assessment-oriented reasoning.

## Step 1: Format Conversion

The raw data arrived in heterogeneous formats reflecting their origins. NIST Cybersecurity came as embedding pairs (text chunks paired with vector embeddings), CMMC datasets arrived as structured JSON with separate question and answer fields, and HIPAA data was already in conversational format but with inconsistent system prompts.

We standardized everything to the chat-style format expected by modern instruction-tuned models:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a cybersecurity compliance expert specializing in CMMC 2.0, NIST 800-171, and related frameworks. Provide accurate, detailed, and actionable guidance."
    },
    {
      "role": "user",
      "content": "What are the technical requirements for multi-factor authentication under CMMC Level 2?"
    },
    {
      "role": "assistant",
      "content": "CMMC Level 2 requires multi-factor authentication (MFA) for both local and network access to privileged accounts and for network access to non-privileged accounts..."
    }
  ]
}
```

This format decision is critical. Qwen2.5-Instruct, our base model, was trained using conversational fine-tuning with this exact message structure. By matching the training format, we ensure optimal transfer learning. The model already understands the semantics of system/user/assistant roles and can focus on learning compliance content rather than relearning conversation structure.

The system prompt standardization is equally important. Raw datasets used varying instructions: "You are a helpful assistant," "Answer the following question," or no system prompt at all. We unified on a compliance-specific system prompt that primes the model for authoritative, detailed responses in the compliance domain. This consistent framing across all examples reinforces the model's specialization.

For the NIST Cybersecurity dataset, format conversion required extracting meaningful question-answer pairs from text chunks originally designed for embedding generation. We applied heuristic parsing to identify question-like sentences (those ending with "?", containing interrogatives like "what," "how," "why") and paired them with surrounding context as answers. This process is lossy but necessary to transform document chunks into instruction data.

## Step 2: Quality Filtering

Raw compliance documentation contains substantial noise: OCR artifacts from scanned PDFs, table fragments that render as garbled text, truncated sentences from improper document parsing, and entries that provide no meaningful information.

Our quality filter applied four criteria:

### Minimum Length Threshold

We removed entries shorter than 100 characters in the assistant response. Compliance questions demand thorough answers. A response like "Yes" or "See NIST 800-171 3.1.1" provides no training signal. The model must learn to explain requirements, not just reference them. In practice, meaningful compliance explanations rarely fit in less than a paragraph.

This filter removed approximately 3% of raw entries, primarily from the NIST dataset where some embedding pairs consisted of sentence fragments.

### Table Fragment Removal

Compliance documents are filled with tables: control matrices, requirement mappings, scoring rubrics. These tables render poorly as plain text, appearing as disconnected columns of words with implicit relationships lost. Worse, when fine-tuning data contains malformed tables, the model learns to generate similarly malformed output.

We identified table fragments through pattern matching: consecutive lines with fewer than 5 words, high frequency of pipe characters or multiple consecutive spaces (table delimiters), and lines consisting primarily of dashes or equals signs (table borders). Any example where more than 30% of lines matched these patterns was removed.

This aggressive filtering eliminated 5% of entries but dramatically improved output quality. In early experiments without this filter, the model would occasionally generate table-like structures mid-response, breaking conversational flow.

### OCR Artifact Removal

Many compliance PDFs undergo scanning and OCR, introducing unicode errors, broken ligatures (fi becomes ), and phantom characters. We filtered entries containing more than 2% non-ASCII characters (excluding common unicode quotes and dashes), as well as entries with repeated unusual character sequences like "�" or broken word fragments like "man ager" or "compli ance."

This removed 2% of entries, concentrated in older NIST publications.

### Question-Restating Filter

A surprising number of raw entries consisted of the question simply restated as the answer. For example:

```
Q: What is the purpose of CMMC certification?
A: The purpose of CMMC certification is CMMC certification.
```

These circular entries appear when document parsing misidentifies section headers or when embedding pairs are constructed from headings rather than body text. We filtered any entry where the answer had more than 70% token overlap with the question (excluding common words).

This removed 2% of entries and prevented the model from learning to generate tautological responses.

### Combined Impact

Quality filtering reduced the raw dataset from 437,449 examples to 384,872 examples, a 12% reduction. This is acceptable loss for the substantial improvement in data cleanliness. The filter is conservative by design: we prefer to discard borderline cases rather than risk training on noise.

## Step 3: Relevance Filtering

The NIST Cybersecurity dataset presents a unique challenge. At 424,729 examples, it comprises 97% of the raw data by volume. It covers the entire cybersecurity domain: penetration testing, malware analysis, cryptographic primitives, cloud security, IoT security, and countless other topics. While this breadth is valuable, most of it is irrelevant to CMMC compliance.

If we included the full NIST dataset, the fine-tuned model would become a general cybersecurity chatbot that happens to know some CMMC, rather than a CMMC specialist with broad cybersecurity grounding. The solution is relevance-based filtering.

### Relevance Scoring Methodology

We developed a keyword-based relevance scoring system weighted toward CMMC-specific concepts:

**High-weight terms (3 points each):**
- CMMC, CUI, FCI, NIST 800-171, controlled unclassified information, federal contract information, defense industrial base, DIB

**Medium-weight terms (2 points each):**
- Access control, audit logging, identification and authentication, incident response, media protection, personnel security, physical protection, risk assessment, security assessment, system and communications protection

**Low-weight terms (1 point each):**
- Authorization, authentication, configuration management, cryptography, information flow, security training, security engineering, system monitoring

Each example received a score based on term frequency in both question and answer, with scoring capped per term (maximum 3 occurrences counted) to prevent keyword stuffing from dominating. We then sorted the NIST dataset by score and kept the top 72,000 examples, representing the most compliance-relevant 17% of the NIST data.

### Sampling Strategy

Even after relevance filtering, 72,000 NIST examples would overwhelm the other sources. We needed NIST to provide foundation without dominating the model's knowledge distribution. Through experimentation, we found that 7,000 NIST examples (sampled from the top 72K) provided optimal balance. This 10:1 reduction is aggressive but necessary.

Sampling was stratified by relevance score quartile to maintain representation across relevance levels. We wanted the model to see both highly specific CMMC-adjacent NIST content and more general cybersecurity concepts that provide supporting knowledge.

This step is the most impactful transformation in the entire pipeline. It converts a general cybersecurity dataset into targeted compliance training data. Without relevance filtering, preliminary models showed weak CMMC specialization, often providing generic security advice rather than framework-specific guidance. With filtering, the model learned to ground responses in CMMC requirements while still demonstrating broad security knowledge.

## Step 4: Deduplication

Compliance documentation is inherently repetitive. The same access control requirements appear in NIST 800-171, CMMC 2.0 practice documentation, NIST Cybersecurity Framework mappings, and CMMC assessment guides. This redundancy serves a purpose in documentation (reinforcement, multiple perspectives) but is harmful in training data.

When a model sees near-identical examples repeatedly, it memorizes specific phrasings rather than learning underlying concepts. This leads to brittle performance: the model excels at reciting memorized text but struggles with novel questions or reframed requirements. Deduplication is essential for generalization.

### Phase 1: Exact Deduplication

We first removed byte-identical duplicates using xxhash, a fast non-cryptographic hash function. For each example, we computed a hash of the concatenated user message and assistant message (excluding the system prompt, which is identical across all examples). Examples with identical hashes were deduplicated, keeping only the first occurrence.

This fast pass removed 4% of the dataset, primarily exact copies that appeared when multiple CMMC datasets sourced from the same root documentation.

### Phase 2: Near-Deduplication

Exact deduplication misses paraphrased duplicates: entries that convey identical information with minor wording variations. For example:

```
Example A: "CMMC Level 2 requires multi-factor authentication for privileged account access."
Example B: "Multi-factor authentication is required for privileged accounts under CMMC Level 2."
```

These are semantically identical but have different hashes. To catch these cases, we implemented MinHash LSH (Locality-Sensitive Hashing), a probabilistic algorithm for near-duplicate detection.

MinHash represents each example as a set of character n-grams (n=3), computes multiple hash signatures, and uses locality-sensitive hashing to efficiently find examples with high Jaccard similarity. We set the similarity threshold at 0.8, meaning examples sharing 80% or more of their n-grams were considered duplicates.

This phase removed an additional 4% of the dataset. The Jaccard threshold of 0.8 is conservative; we experimented with 0.7 and 0.9. At 0.7, we removed too many examples that were similar but not truly duplicative (e.g., different CMMC levels with analogous requirements). At 0.9, we missed many paraphrased duplicates. The 0.8 threshold provided the best balance.

### Deduplication Impact

Combined, deduplication removed 8% of the dataset after quality filtering, reducing the corpus from 384,872 examples to approximately 354,000 examples. The impact on model performance is subtle but measurable. In ablation testing, models trained without deduplication showed 3% lower validation accuracy on held-out paraphrased questions, suggesting memorization rather than true understanding.

Deduplication also reduced training time by 8% and lowered the risk of overfitting, allowing us to train for more epochs without degradation in validation loss.

## Step 5: Validation Split

The final step is splitting the cleaned dataset into training and validation sets. We performed an 80/20 stratified split, maintaining proportional representation of each source dataset.

### Stratification Strategy

Stratification is critical when combining multiple sources of varying quality and focus. Without stratification, random splitting could produce a validation set over-representing small sources (like CMMC Core) or under-representing large sources (like NIST Cybersecurity). This would make validation metrics unreliable: good performance might reflect easy questions from a small source rather than true model capability.

We stratified by source dataset as the primary key, ensuring that the training and validation sets both contain approximately:
- 47.4% NIST Cybersecurity examples
- 35.6% CMMC Full examples
- 10.2% CMMC Balanced examples
- 5.1% HIPAA Compliance examples
- 1.7% CMMC Core examples

This proportional representation ensures validation metrics accurately reflect model performance across the knowledge distribution.

### Final Dataset Statistics

After all pipeline steps, the final dataset contains:

- **Training set:** 13,434 examples
- **Validation set:** 3,472 examples
- **Total:** 16,906 examples

The validation set is never seen during training. It serves exclusively for monitoring evaluation loss and preventing overfitting. We checkpoint the model whenever validation loss reaches a new minimum, ensuring the final model represents the best generalization point rather than the end of training.

### Split Verification

We verified the split quality by computing summary statistics for both sets:

- Average question length: 78 tokens (train), 77 tokens (validation)
- Average answer length: 312 tokens (train), 309 tokens (validation)
- Source distribution: χ² test p-value = 0.89 (no significant difference)

These metrics confirm that the split maintains distributional similarity between training and validation sets.

## Data Quality Observations

Building this dataset required deep familiarity with both the AI/ML engineering challenges of fine-tuning and the substantive domain of compliance frameworks. Several observations emerged from the process:

### Quality vs. Quantity Trade-offs

CMMC Core, with only 320 examples, is by far the highest quality source. Each entry is hand-curated, answers are detailed and accurate, and questions reflect real-world assessment scenarios. Yet it represents less than 2% of the final dataset. In contrast, NIST Cybersecurity contributes 47.4% of the final dataset but required aggressive filtering to achieve acceptable quality.

This quality-quantity trade-off is fundamental to fine-tuning. High-quality data provides strong learning signal but insufficient coverage. Large-scale data provides coverage but diluted signal. The optimal dataset blends both: a small core of exceptional examples to establish quality standards, surrounded by a larger corpus of good-enough examples to provide breadth.

### The Criticality of Relevance Filtering

Relevance filtering is the single most important pipeline step. Without it, the NIST dataset would contribute generic cybersecurity knowledge that drowns out CMMC specialization. With it, the model learns to contextualize broad security concepts within compliance frameworks.

This lesson generalizes: when fine-tuning for domain specialization, source data must be aggressively filtered for relevance. It is better to have 7,000 highly relevant examples than 400,000 loosely related ones.

### Cross-Framework Learning

Including HIPAA Compliance data initially seemed tangential, but it proved valuable. HIPAA and CMMC address different regulatory contexts (healthcare vs. defense) but share fundamental concepts: access control, audit trails, encryption, incident response. By training on both, the model learns that compliance principles transcend specific frameworks. This improves transfer learning: the model can reason about compliance requirements it hasn't seen by analogy to similar requirements in other frameworks.

The training data also covers DFARS clause requirements (252.204-7012, 7019, 7020, 7021) and NIST SP 800-37 (Risk Management Framework), providing the full chain from contract-level obligations through framework requirements to technical controls. This end-to-end coverage is critical for practitioners who must trace compliance requirements from their contract language through to specific technical implementations.

This insight suggests that future iterations should include additional frameworks (SOC 2, ISO 27001, GDPR) to further strengthen cross-framework reasoning.

### The 47.4% NIST / 35.6% CMMC Split

The final source distribution reflects careful balancing. NIST provides breadth: foundational cybersecurity knowledge that prevents the model from becoming a narrow CMMC lookup table. CMMC Full and CMMC Balanced provide depth: detailed practice-level guidance, assessment criteria, and framework-specific terminology.

The 47/36 split emerged from empirical testing. At 60/40 (more NIST), the model performed well on general security questions but poorly on CMMC-specific assessments. At 30/70 (more CMMC), the model excelled on CMMC but struggled with questions requiring broader security context. The 47/36 split occupies a sweet spot: strong CMMC specialization with robust security foundations.

## Conclusion

Building a high-quality fine-tuning dataset is an exercise in disciplined curation. Raw data is abundant but noisy. The pipeline's purpose is to extract signal from noise through systematic transformation: standardizing formats, filtering aggressively, balancing sources, and eliminating redundancy.

The resulting 16,906-example dataset is small by pre-training standards but substantial for fine-tuning. It represents approximately 5.3 million tokens of high-quality compliance instruction data. When paired with the Qwen2.5 Instruct model family (7B, 14B, 32B, 72B), this dataset produces specialized compliance models that balance breadth and depth, demonstrating both strong CMMC knowledge and robust cybersecurity reasoning across all model sizes.

The pipeline is reproducible and extensible. As new compliance frameworks emerge or existing frameworks evolve, the pipeline can ingest additional sources and rebalance the mixture. The modular design (format conversion, quality filtering, relevance filtering, deduplication, splitting) allows each step to be tuned independently based on source characteristics and performance requirements.

This is not merely a data processing pipeline. It is a knowledge distillation process that transforms scattered compliance documentation into structured learning material optimized for language model fine-tuning. The care invested in data preparation directly determines model quality. A model is only as good as its training data, and building that data requires equal parts engineering rigor and domain expertise.
