"""
Post-Training: Merge LoRA Adapters and Quantize to GGUF

1. Merges QLoRA adapters back into the base model (full precision)
2. Quantizes merged model to GGUF format for Ollama deployment
3. Validates output file size and basic inference

Usage:
    python training/merge_and_quantize.py --config training/config.yaml

Dependencies:
    pip install torch transformers peft llama-cpp-python
    Also requires: llama.cpp (for GGUF conversion)
"""

import yaml
import argparse
import subprocess
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def merge_adapter(config: dict, adapter_path: str):
    """Merge LoRA adapter weights into base model."""
    base_model = config['model']['base_model']
    merge_dir = config['merge']['output_dir']

    print(f"Loading base model: {base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    print(f"Loading adapter from: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)

    print("Merging adapter into base model...")
    model = model.merge_and_unload()

    print(f"Saving merged model to: {merge_dir}")
    Path(merge_dir).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(merge_dir)

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    tokenizer.save_pretrained(merge_dir)

    print("Merge complete.")
    return merge_dir


def quantize_to_gguf(config: dict, merged_dir: str):
    """Quantize merged model to GGUF format using llama.cpp."""
    quant_config = config['quantize']
    output_dir = Path(quant_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / quant_config['output_name']
    quant_method = quant_config['method']

    print(f"Quantizing to GGUF ({quant_method})...")

    # Step 1: Convert to GGUF (requires llama.cpp convert script)
    fp16_gguf = output_dir / "model-fp16.gguf"
    subprocess.run([
        "python", "llama.cpp/convert_hf_to_gguf.py",
        merged_dir,
        "--outfile", str(fp16_gguf),
        "--outtype", "f16",
    ], check=True)

    # Step 2: Quantize
    subprocess.run([
        "llama.cpp/llama-quantize",
        str(fp16_gguf),
        str(output_path),
        quant_method,
    ], check=True)

    # Clean up intermediate file
    fp16_gguf.unlink(missing_ok=True)

    size_gb = output_path.stat().st_size / (1024**3)
    print(f"Quantization complete: {output_path} ({size_gb:.1f} GB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Merge adapter and quantize model')
    parser.add_argument('--config', type=str, default='training/config.yaml')
    parser.add_argument('--adapter', type=str,
                       default='checkpoints/cmmc-expert-7b/final_adapter',
                       help='Path to trained adapter directory')
    parser.add_argument('--skip-merge', action='store_true',
                       help='Skip merge step (use existing merged model)')
    parser.add_argument('--skip-quantize', action='store_true',
                       help='Skip quantization step')
    args = parser.parse_args()

    config = load_config(args.config)

    if not args.skip_merge:
        merged_dir = merge_adapter(config, args.adapter)
    else:
        merged_dir = config['merge']['output_dir']
        print(f"Skipping merge, using: {merged_dir}")

    if not args.skip_quantize:
        output = quantize_to_gguf(config, merged_dir)
        print(f"\nReady for Ollama deployment: {output}")
        print(f"Next: ollama create cmmc-expert-7b -f deployment/Modelfile")

    print("\nDone.")


if __name__ == '__main__':
    main()
