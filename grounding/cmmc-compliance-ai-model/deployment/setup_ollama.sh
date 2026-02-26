#!/bin/bash
# Setup script for CMMC Compliance AI Model on Ollama
# Deploys the quantized model for local inference
#
# Usage:
#   ./deployment/setup_ollama.sh              # Default: 7b model
#   ./deployment/setup_ollama.sh 7b           # Explicit 7b
#   ./deployment/setup_ollama.sh 14b          # 14b model
#   ./deployment/setup_ollama.sh 32b          # 32b model
#   ./deployment/setup_ollama.sh 72b          # 72b model
#
# Prerequisites:
#   - Ollama installed (https://ollama.ai)
#   - Quantized model file at ./quantized/cmmc-expert-{size}.gguf
#   - Sufficient VRAM/RAM for the selected model size:
#       7b:  8 GB VRAM  | 14b: 12 GB VRAM
#       32b: 24 GB VRAM | 72b: 48 GB VRAM

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Model size selection (default: 7b)
MODEL_SIZE="${1:-7b}"

case "$MODEL_SIZE" in
    7b|14b|32b|72b)
        MODEL_NAME="cmmc-expert-$MODEL_SIZE"
        ;;
    *)
        echo "ERROR: Invalid model size '$MODEL_SIZE'"
        echo "Valid options: 7b, 14b, 32b, 72b"
        exit 1
        ;;
esac

MODEL_FILE="$PROJECT_ROOT/quantized/$MODEL_NAME.gguf"
MODELFILE="$SCRIPT_DIR/Modelfile"

echo "============================================"
echo " CMMC Compliance AI Model -- Ollama Setup"
echo " Model: $MODEL_NAME"
echo "============================================"
echo ""

# Check prerequisites
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama is not installed."
    echo "Install from: https://ollama.ai"
    exit 1
fi

if [ ! -f "$MODEL_FILE" ]; then
    echo "ERROR: Model file not found at $MODEL_FILE"
    echo ""
    echo "To generate the model file, run the training pipeline:"
    echo "  1. python pipeline/01_format_converter.py"
    echo "  2. python pipeline/02_quality_filter.py"
    echo "  3. python pipeline/03_relevance_filter.py"
    echo "  4. python pipeline/04_deduplication.py"
    echo "  5. python pipeline/05_train_val_split.py"
    echo "  6. python training/train_qlora.py"
    echo "  7. python training/merge_and_quantize.py"
    echo ""
    echo "Available model files:"
    ls -lh "$PROJECT_ROOT/quantized/"*.gguf 2>/dev/null || echo "  (none found)"
    exit 1
fi

if [ ! -f "$MODELFILE" ]; then
    echo "ERROR: Modelfile not found at $MODELFILE"
    exit 1
fi

# Create a temporary Modelfile with the correct FROM path for the selected model
TEMP_MODELFILE=$(mktemp)
sed "s|FROM ./quantized/cmmc-expert-7b.gguf|FROM ./quantized/$MODEL_NAME.gguf|" "$MODELFILE" > "$TEMP_MODELFILE"

# Check if model already exists
if ollama list | grep -q "$MODEL_NAME"; then
    echo "Model '$MODEL_NAME' already exists in Ollama."
    read -p "Overwrite? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        rm -f "$TEMP_MODELFILE"
        exit 0
    fi
    echo "Removing existing model..."
    ollama rm "$MODEL_NAME"
fi

# Create model in Ollama
echo "Creating model '$MODEL_NAME' in Ollama..."
echo "  Model file: $MODEL_FILE"
echo "  Config: $MODELFILE"
echo ""

cd "$PROJECT_ROOT"
ollama create "$MODEL_NAME" -f "$TEMP_MODELFILE"
rm -f "$TEMP_MODELFILE"

echo ""
echo "============================================"
echo " Setup Complete!"
echo "============================================"
echo ""
echo "Test the model:"
echo "  ollama run $MODEL_NAME \"What access controls are required for CMMC Level 2?\""
echo ""
echo "Or use the API:"
echo "  curl http://localhost:11434/api/generate -d '{"
echo "    \"model\": \"$MODEL_NAME\","
echo "    \"prompt\": \"What are the key differences between CMMC Level 1 and Level 2?\","
echo "    \"stream\": false"
echo "  }'"
echo ""
echo "Model details:"
ollama show "$MODEL_NAME" --modelfile 2>/dev/null || echo "  (run 'ollama show $MODEL_NAME' to see details)"
