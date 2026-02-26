#!/usr/bin/env python3
"""
Upload CMMC Expert models to Hugging Face Hub.

Usage:
    # Upload all models
    python publishing/huggingface/upload_models.py

    # Upload a specific model
    python publishing/huggingface/upload_models.py --model 7b

    # Dry run (validate only, no upload)
    python publishing/huggingface/upload_models.py --dry-run

Prerequisites:
    pip install huggingface_hub
    huggingface-cli login
"""

import argparse
import sys
from pathlib import Path

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    print("ERROR: huggingface_hub not installed.")
    print("  pip install huggingface_hub")
    print("  huggingface-cli login")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HF_USERNAME = "Nathan-Maine"

MODELS = {
    "7b": {
        "repo_id": f"{HF_USERNAME}/cmmc-expert-7b",
        "gguf_file": "quantized/cmmc-expert-7b.gguf",
        "model_card": "publishing/huggingface/cmmc-expert-7b/README.md",
    },
    "14b": {
        "repo_id": f"{HF_USERNAME}/cmmc-expert-14b",
        "gguf_file": "quantized/cmmc-expert-14b.gguf",
        "model_card": "publishing/huggingface/cmmc-expert-14b/README.md",
    },
    "32b": {
        "repo_id": f"{HF_USERNAME}/cmmc-expert-32b",
        "gguf_file": "quantized/cmmc-expert-32b.gguf",
        "model_card": "publishing/huggingface/cmmc-expert-32b/README.md",
    },
    "72b": {
        "repo_id": f"{HF_USERNAME}/cmmc-expert-72b",
        "gguf_file": "quantized/cmmc-expert-72b.gguf",
        "model_card": "publishing/huggingface/cmmc-expert-72b/README.md",
    },
}


def upload_model(api: HfApi, size: str, dry_run: bool = False) -> bool:
    """Upload a single model to Hugging Face Hub."""
    config = MODELS[size]
    repo_id = config["repo_id"]
    gguf_path = PROJECT_ROOT / config["gguf_file"]
    card_path = PROJECT_ROOT / config["model_card"]

    print(f"\n{'=' * 60}")
    print(f"  Model: cmmc-expert-{size}")
    print(f"  Repo:  {repo_id}")
    print(f"  GGUF:  {gguf_path}")
    print(f"  Card:  {card_path}")
    print(f"{'=' * 60}")

    # Validate files exist
    if not gguf_path.exists():
        print(f"  WARNING: GGUF file not found at {gguf_path}")
        print(f"  Run the training pipeline first to generate the model.")
        return False

    if not card_path.exists():
        print(f"  ERROR: Model card not found at {card_path}")
        return False

    if dry_run:
        print(f"  [DRY RUN] Would upload {gguf_path.name} ({gguf_path.stat().st_size / 1e9:.1f} GB)")
        print(f"  [DRY RUN] Would upload README.md model card")
        return True

    # Create repo if it doesn't exist
    print(f"  Creating repo {repo_id}...")
    create_repo(repo_id, repo_type="model", exist_ok=True)

    # Upload model card
    print(f"  Uploading model card...")
    api.upload_file(
        path_or_fileobj=str(card_path),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
    )

    # Upload GGUF file
    file_size_gb = gguf_path.stat().st_size / 1e9
    print(f"  Uploading {gguf_path.name} ({file_size_gb:.1f} GB)...")
    print(f"  This may take a while for large models.")
    api.upload_file(
        path_or_fileobj=str(gguf_path),
        path_in_repo=gguf_path.name,
        repo_id=repo_id,
        repo_type="model",
    )

    # Upload Modelfile for Ollama users
    modelfile_path = PROJECT_ROOT / "deployment" / "Modelfile"
    if modelfile_path.exists():
        print(f"  Uploading Ollama Modelfile...")
        api.upload_file(
            path_or_fileobj=str(modelfile_path),
            path_in_repo="Modelfile",
            repo_id=repo_id,
            repo_type="model",
        )

    print(f"  Upload complete: https://huggingface.co/{repo_id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Upload CMMC Expert models to Hugging Face")
    parser.add_argument("--model", choices=["7b", "14b", "32b", "72b", "all"], default="all",
                        help="Which model to upload (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate files without uploading")
    args = parser.parse_args()

    api = HfApi()

    # Verify authentication
    if not args.dry_run:
        try:
            whoami = api.whoami()
            print(f"Authenticated as: {whoami['name']}")
        except Exception:
            print("ERROR: Not authenticated with Hugging Face.")
            print("  Run: huggingface-cli login")
            sys.exit(1)

    sizes = list(MODELS.keys()) if args.model == "all" else [args.model]
    results = {}

    for size in sizes:
        results[size] = upload_model(api, size, dry_run=args.dry_run)

    # Summary
    print(f"\n{'=' * 60}")
    print("  Upload Summary")
    print(f"{'=' * 60}")
    for size, success in results.items():
        status = "OK" if success else "SKIPPED (GGUF not found)"
        print(f"  cmmc-expert-{size}: {status}")

    if all(results.values()):
        print("\nAll models uploaded successfully!")
    else:
        print("\nSome models were skipped. Run the training pipeline to generate missing GGUF files.")


if __name__ == "__main__":
    main()
