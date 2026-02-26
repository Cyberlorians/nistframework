# Publishing Guide

How to distribute the CMMC Expert models across all three channels.

## Channels

| Channel | Audience | Command |
|---------|----------|---------|
| **Hugging Face** | ML practitioners, researchers | Browse/download from HF Hub |
| **Ollama Library** | Practitioners, quickest path | `ollama pull Nathan-Maine/cmmc-expert-7b` |
| **GitHub Releases** | Developers, offline installs | Download GGUF from Releases page |

## Prerequisites

1. **Model files generated** — Run the full training pipeline to produce GGUF files at `quantized/cmmc-expert-{7b,14b,32b,72b}.gguf`
2. **Hugging Face account** — [huggingface.co](https://huggingface.co), run `huggingface-cli login`
3. **Ollama account** — [ollama.com](https://ollama.com), run `ollama login`
4. **GitHub CLI** — `brew install gh`, run `gh auth login`

## Step 1: Hugging Face

```bash
# Install the HF client
pip install huggingface_hub

# Authenticate
huggingface-cli login

# Upload all models (or use --model 7b for a single model)
python publishing/huggingface/upload_models.py

# Dry run first to verify
python publishing/huggingface/upload_models.py --dry-run
```

Each model gets its own HF repo with a detailed model card:
- `Nathan-Maine/cmmc-expert-7b`
- `Nathan-Maine/cmmc-expert-14b`
- `Nathan-Maine/cmmc-expert-32b`
- `Nathan-Maine/cmmc-expert-72b`

## Step 2: Ollama Library

```bash
# Create and push each model
./deployment/setup_ollama.sh 7b
ollama push Nathan-Maine/cmmc-expert-7b

./deployment/setup_ollama.sh 14b
ollama push Nathan-Maine/cmmc-expert-14b

./deployment/setup_ollama.sh 32b
ollama push Nathan-Maine/cmmc-expert-32b

./deployment/setup_ollama.sh 72b
ollama push Nathan-Maine/cmmc-expert-72b
```

See [ollama/README.md](ollama/README.md) for details.

## Step 3: GitHub Releases

```bash
# Preview what will be created
./publishing/github-releases/create_release.sh --dry-run

# Create the release (draft mode — review before publishing)
./publishing/github-releases/create_release.sh
```

This creates a draft GitHub Release with GGUF files attached. Review at the Releases page, then publish.

See [github-releases/create_release.sh](github-releases/create_release.sh) for options.

## Step 4: Update README

After publishing, update the main README.md to add download links:

```markdown
## Download

| Model | Hugging Face | Ollama | GitHub Release |
|-------|-------------|--------|----------------|
| 7B | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-7b) | `ollama pull Nathan-Maine/cmmc-expert-7b` | [GGUF](https://github.com/NathanMaine/cmmc-compliance-ai-model/releases) |
| 14B | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-14b) | `ollama pull Nathan-Maine/cmmc-expert-14b` | [GGUF](https://github.com/NathanMaine/cmmc-compliance-ai-model/releases) |
| 32B | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-32b) | `ollama pull Nathan-Maine/cmmc-expert-32b` | [GGUF](https://github.com/NathanMaine/cmmc-compliance-ai-model/releases) |
| 72B | [Download](https://huggingface.co/Nathan-Maine/cmmc-expert-72b) | `ollama pull Nathan-Maine/cmmc-expert-72b` | [GGUF](https://github.com/NathanMaine/cmmc-compliance-ai-model/releases) |
```

## Licensing

All four models are released under **Apache 2.0**, matching the Qwen2.5 base model license.
