#!/bin/bash
# Create GitHub Releases with GGUF model files attached.
#
# Usage:
#   ./publishing/github-releases/create_release.sh              # All models
#   ./publishing/github-releases/create_release.sh 7b           # Single model
#   ./publishing/github-releases/create_release.sh --dry-run    # Preview only
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - GGUF files at quantized/cmmc-expert-{size}.gguf
#   - Repository pushed to GitHub

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

VERSION="v1.0.0"
DRY_RUN=false
SELECTED_MODEL=""

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        7b|14b|32b|72b) SELECTED_MODEL="$arg" ;;
        *) echo "Usage: $0 [7b|14b|32b|72b] [--dry-run]"; exit 1 ;;
    esac
done

MODELS=("7b" "14b" "32b" "72b")
if [ -n "$SELECTED_MODEL" ]; then
    MODELS=("$SELECTED_MODEL")
fi

echo "============================================"
echo " CMMC Expert — GitHub Release Creator"
echo " Version: $VERSION"
echo "============================================"
echo ""

# Check prerequisites
if ! command -v gh &> /dev/null; then
    echo "ERROR: gh CLI not installed."
    echo "Install: brew install gh"
    exit 1
fi

# Verify we're in a git repo
if ! git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree &> /dev/null; then
    echo "ERROR: Not a git repository at $PROJECT_ROOT"
    exit 1
fi

# Create the tag if it doesn't exist
if ! git -C "$PROJECT_ROOT" tag -l "$VERSION" | grep -q "$VERSION"; then
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would create tag: $VERSION"
    else
        echo "Creating tag: $VERSION"
        git -C "$PROJECT_ROOT" tag -a "$VERSION" -m "Release $VERSION — CMMC Expert Model Suite (7B, 14B, 32B, 72B)"
        git -C "$PROJECT_ROOT" push origin "$VERSION"
    fi
fi

# Build release notes
RELEASE_NOTES=$(cat <<'NOTES'
## CMMC Expert Model Suite

Four fine-tuned language models for cybersecurity compliance — CMMC 2.0, NIST 800-171, NIST 800-53, HIPAA, and DFARS.

### Models

| Model | Parameters | GGUF Size | Quantization | Hardware |
|-------|-----------|-----------|--------------|----------|
| cmmc-expert-7b | 7.6B | 5.1 GB | q5_k_m | 8 GB VRAM |
| cmmc-expert-14b | 14.7B | ~10 GB | q5_k_m | 12 GB VRAM |
| cmmc-expert-32b | 32.5B | ~19 GB | q4_k_m | 24 GB VRAM |
| cmmc-expert-72b | 72.7B | ~42 GB | q4_k_m | 48 GB VRAM |

### Quick Start

```bash
# Install Ollama (https://ollama.ai)
# Download a GGUF file from this release
# Deploy locally:
./deployment/setup_ollama.sh 7b
ollama run cmmc-expert-7b "What is CMMC Level 2?"
```

### Also Available On

- **Hugging Face**: [Nathan-Maine/cmmc-expert-7b](https://huggingface.co/Nathan-Maine/cmmc-expert-7b) (and 14b, 32b, 72b)
- **Ollama Library**: `ollama pull Nathan-Maine/cmmc-expert-7b`

### What's Included

- GGUF model files (quantized, ready for Ollama)
- Full source code for the training pipeline, evaluation suite, and deployment config

### Base Model

Qwen2.5 Instruct — fine-tuned with QLoRA on 13,434 compliance examples across 8 frameworks.
NOTES
)

# Create the release
if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] Would create release $VERSION with notes:"
    echo "$RELEASE_NOTES"
    echo ""
else
    echo "Creating GitHub release $VERSION..."
    gh release create "$VERSION" \
        --repo "NathanMaine/cmmc-compliance-ai-model" \
        --title "CMMC Expert $VERSION — Model Suite (7B, 14B, 32B, 72B)" \
        --notes "$RELEASE_NOTES" \
        --draft
    echo "Draft release created."
fi

# Attach GGUF files
for size in "${MODELS[@]}"; do
    GGUF_FILE="$PROJECT_ROOT/quantized/cmmc-expert-$size.gguf"

    if [ ! -f "$GGUF_FILE" ]; then
        echo "  SKIP: cmmc-expert-$size.gguf (not found)"
        continue
    fi

    FILE_SIZE=$(du -h "$GGUF_FILE" | cut -f1)

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would attach: cmmc-expert-$size.gguf ($FILE_SIZE)"
    else
        echo "  Uploading: cmmc-expert-$size.gguf ($FILE_SIZE)..."
        gh release upload "$VERSION" "$GGUF_FILE" \
            --repo "NathanMaine/cmmc-compliance-ai-model" \
            --clobber
        echo "  Attached: cmmc-expert-$size.gguf"
    fi
done

echo ""
echo "============================================"
if [ "$DRY_RUN" = true ]; then
    echo " [DRY RUN] No changes made."
else
    echo " Release created (draft)."
    echo " Review and publish at:"
    echo "   https://github.com/NathanMaine/cmmc-compliance-ai-model/releases"
fi
echo "============================================"
