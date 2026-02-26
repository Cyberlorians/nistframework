"""
Step 4: Deduplication
Removes duplicate and near-duplicate entries using two methods:
1. Exact dedup via xxhash — catches byte-identical entries
2. Near-dedup via MinHash LSH — catches paraphrased duplicates (Jaccard threshold 0.8)

Compliance documents are inherently repetitive — the same control appears in
NIST 800-171, CMMC assessment guide, and multiple training sources. Without
dedup, the model memorizes specific phrasings rather than learning concepts.

Input: data/processed/03_relevance_filtered.jsonl
Output: data/processed/04_deduplicated.jsonl

Dependencies: pip install xxhash datasketch
"""

import json
import argparse
from pathlib import Path
from typing import Set

import xxhash
from datasketch import MinHash, MinHashLSH

NUM_PERM = 128          # MinHash permutations (higher = more accurate, slower)
LSH_THRESHOLD = 0.8     # Jaccard similarity threshold for near-dedup
SHINGLE_SIZE = 5        # Word n-gram size for MinHash


def text_to_shingles(text: str, k: int = SHINGLE_SIZE) -> Set[str]:
    """Convert text to word-level k-shingles."""
    words = text.lower().split()
    if len(words) < k:
        return {' '.join(words)}
    return {' '.join(words[i:i+k]) for i in range(len(words) - k + 1)}


def create_minhash(shingles: Set[str]) -> MinHash:
    """Create MinHash signature from shingles."""
    mh = MinHash(num_perm=NUM_PERM)
    for shingle in shingles:
        mh.update(shingle.encode('utf-8'))
    return mh


def extract_text(example: dict) -> str:
    """Extract combined question + answer text for dedup comparison."""
    return ' '.join(
        msg['content'] for msg in example.get('messages', [])
        if msg['role'] in ('user', 'assistant')
    )


def main():
    parser = argparse.ArgumentParser(description='Deduplicate training data')
    parser.add_argument('--input', type=Path, default=Path('data/processed/03_relevance_filtered.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('data/processed/04_deduplicated.jsonl'))
    parser.add_argument('--threshold', type=float, default=LSH_THRESHOLD)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    print("Phase 1: Exact dedup via xxhash...")
    seen_hashes: Set[str] = set()
    exact_dupes = 0
    unique_examples = []

    with open(args.input, 'r') as f:
        for line in f:
            example = json.loads(line)
            text = extract_text(example)
            h = xxhash.xxh64(text.encode('utf-8')).hexdigest()

            if h in seen_hashes:
                exact_dupes += 1
            else:
                seen_hashes.add(h)
                unique_examples.append((text, line))

    print(f"  Exact duplicates removed: {exact_dupes:,}")
    print(f"  Unique after exact dedup: {len(unique_examples):,}")

    print("\nPhase 2: Near-dedup via MinHash LSH...")
    lsh = MinHashLSH(threshold=args.threshold, num_perm=NUM_PERM)
    near_dupes = 0
    kept = []

    for idx, (text, line) in enumerate(unique_examples):
        shingles = text_to_shingles(text)
        mh = create_minhash(shingles)

        # Check if similar document already exists
        result = lsh.query(mh)
        if result:
            near_dupes += 1
        else:
            lsh.insert(f"doc_{idx}", mh)
            kept.append(line)

        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx + 1:,}/{len(unique_examples):,}...")

    # Write deduplicated output
    with open(args.output, 'w') as out:
        for line in kept:
            out.write(line)

    total_removed = exact_dupes + near_dupes
    original_count = exact_dupes + len(unique_examples)

    print(f"\nDeduplication Results:")
    print(f"  Input:          {original_count:,}")
    print(f"  Exact dupes:    {exact_dupes:,}")
    print(f"  Near dupes:     {near_dupes:,}")
    print(f"  Total removed:  {total_removed:,} ({total_removed/original_count*100:.1f}%)")
    print(f"  Final output:   {len(kept):,} -> {args.output}")


if __name__ == '__main__':
    main()
