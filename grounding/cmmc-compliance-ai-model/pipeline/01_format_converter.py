"""
Step 1: Format Converter
Converts raw compliance data from various formats into standardized
chat-style instruction/response pairs for fine-tuning.

Input: Raw data files (JSON, JSONL, CSV, text)
Output: data/processed/01_formatted.jsonl

Each output example follows the chat format:
{
    "messages": [
        {"role": "system", "content": "You are a cybersecurity compliance expert..."},
        {"role": "user", "content": "<question>"},
        {"role": "assistant", "content": "<expert answer>"}
    ],
    "source": "<dataset_name>"
}
"""

import json
import csv
import argparse
from pathlib import Path
from typing import Generator

SYSTEM_PROMPT = (
    "You are a cybersecurity compliance expert specializing in CMMC 2.0, "
    "NIST SP 800-171, NIST SP 800-53, NIST CSF, and HIPAA Security Rule. "
    "Provide accurate, specific guidance with framework references. "
    "When referencing controls, cite the specific section numbers. "
    "Distinguish between CMMC levels and their requirements clearly."
)

# Source-specific parsers
# Each parser yields (question, answer) tuples from raw data

def parse_nist_cybersecurity(filepath: Path) -> Generator[tuple[str, str, str], None, None]:
    """Parse NIST Cybersecurity dataset (Hugging Face format).

    Original dataset contains embedding pairs. We extract the text
    content and restructure as Q&A pairs.
    """
    with open(filepath, 'r') as f:
        for line in f:
            record = json.loads(line)
            # Extract instruction and response from various field names
            question = record.get('instruction') or record.get('input') or record.get('question', '')
            answer = record.get('output') or record.get('response') or record.get('answer', '')
            if question and answer:
                yield question.strip(), answer.strip(), 'nist_cybersecurity'


def parse_cmmc_full(filepath: Path) -> Generator[tuple[str, str, str], None, None]:
    """Parse comprehensive CMMC Q&A dataset."""
    with open(filepath, 'r') as f:
        for line in f:
            record = json.loads(line)
            question = record.get('question', '')
            answer = record.get('answer', '')
            if question and answer:
                yield question.strip(), answer.strip(), 'cmmc_full'


def parse_cmmc_balanced(filepath: Path) -> Generator[tuple[str, str, str], None, None]:
    """Parse balanced CMMC dataset (equal representation across domains)."""
    with open(filepath, 'r') as f:
        data = json.load(f) if filepath.suffix == '.json' else [json.loads(l) for l in f]
        for record in data:
            question = record.get('instruction') or record.get('question', '')
            answer = record.get('output') or record.get('answer', '')
            if question and answer:
                yield question.strip(), answer.strip(), 'cmmc_balanced'


def parse_hipaa(filepath: Path) -> Generator[tuple[str, str, str], None, None]:
    """Parse HIPAA compliance Q&A pairs."""
    with open(filepath, 'r') as f:
        for line in f:
            record = json.loads(line)
            question = record.get('question') or record.get('instruction', '')
            answer = record.get('answer') or record.get('output', '')
            if question and answer:
                yield question.strip(), answer.strip(), 'hipaa'


def parse_cmmc_core(filepath: Path) -> Generator[tuple[str, str, str], None, None]:
    """Parse hand-curated CMMC core assessment questions."""
    with open(filepath, 'r') as f:
        for line in f:
            record = json.loads(line)
            question = record.get('question', '')
            answer = record.get('answer', '')
            if question and answer:
                yield question.strip(), answer.strip(), 'cmmc_core'


PARSERS = {
    'nist_cybersecurity': parse_nist_cybersecurity,
    'cmmc_full': parse_cmmc_full,
    'cmmc_balanced': parse_cmmc_balanced,
    'hipaa': parse_hipaa,
    'cmmc_core': parse_cmmc_core,
}


def format_as_chat(question: str, answer: str, source: str) -> dict:
    """Convert a Q&A pair into chat-style training format."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ],
        "source": source
    }


def main():
    parser = argparse.ArgumentParser(description='Convert raw data to chat format')
    parser.add_argument('--input-dir', type=Path, default=Path('data/raw'),
                       help='Directory containing raw source data files')
    parser.add_argument('--output', type=Path, default=Path('data/processed/01_formatted.jsonl'),
                       help='Output JSONL file path')
    parser.add_argument('--sources', nargs='+', choices=list(PARSERS.keys()),
                       default=list(PARSERS.keys()),
                       help='Which sources to process')
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    counts = {}
    total = 0

    with open(args.output, 'w') as out:
        for source_name in args.sources:
            source_files = list(args.input_dir.glob(f'{source_name}*'))
            if not source_files:
                print(f"  [SKIP] No files found for {source_name}")
                continue

            count = 0
            for filepath in source_files:
                parse_fn = PARSERS[source_name]
                for question, answer, src in parse_fn(filepath):
                    example = format_as_chat(question, answer, src)
                    out.write(json.dumps(example) + '\n')
                    count += 1

            counts[source_name] = count
            total += count
            print(f"  [{source_name}] {count:,} examples")

    print(f"\nTotal: {total:,} formatted examples -> {args.output}")
    print(f"\nSource distribution:")
    for src, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        pct = cnt / total * 100 if total > 0 else 0
        print(f"  {src}: {cnt:,} ({pct:.1f}%)")


if __name__ == '__main__':
    main()
