"""
Step 5: Train/Validation Split
Creates stratified 80/20 split maintaining source distribution.

Input: data/processed/04_deduplicated.jsonl
Output: data/final/train.jsonl, data/final/val.jsonl
"""

import json
import random
import argparse
from pathlib import Path
from collections import defaultdict

SPLIT_RATIO = 0.8
RANDOM_SEED = 42


def main():
    parser = argparse.ArgumentParser(description='Create stratified train/val split')
    parser.add_argument('--input', type=Path, default=Path('data/processed/04_deduplicated.jsonl'))
    parser.add_argument('--output-dir', type=Path, default=Path('data/final'))
    parser.add_argument('--split', type=float, default=SPLIT_RATIO)
    parser.add_argument('--seed', type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)

    # Group examples by source for stratified split
    by_source = defaultdict(list)
    with open(args.input, 'r') as f:
        for line in f:
            example = json.loads(line)
            source = example.get('source', 'unknown')
            by_source[source].append(line)

    train_lines = []
    val_lines = []

    print("Stratified split by source:")
    for source, lines in sorted(by_source.items()):
        random.shuffle(lines)
        split_idx = int(len(lines) * args.split)
        train = lines[:split_idx]
        val = lines[split_idx:]
        train_lines.extend(train)
        val_lines.extend(val)
        print(f"  {source}: {len(train):,} train / {len(val):,} val ({len(lines):,} total)")

    # Shuffle final datasets
    random.shuffle(train_lines)
    random.shuffle(val_lines)

    # Write output files
    train_path = args.output_dir / 'train.jsonl'
    val_path = args.output_dir / 'val.jsonl'

    with open(train_path, 'w') as f:
        for line in train_lines:
            f.write(line)

    with open(val_path, 'w') as f:
        for line in val_lines:
            f.write(line)

    print(f"\nFinal split:")
    print(f"  Train: {len(train_lines):,} -> {train_path}")
    print(f"  Val:   {len(val_lines):,} -> {val_path}")
    print(f"  Ratio: {len(train_lines)/(len(train_lines)+len(val_lines))*100:.1f}% / "
          f"{len(val_lines)/(len(train_lines)+len(val_lines))*100:.1f}%")


if __name__ == '__main__':
    main()
