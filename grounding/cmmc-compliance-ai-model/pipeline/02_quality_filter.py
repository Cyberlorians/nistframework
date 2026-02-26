"""
Step 2: Quality Filter
Removes low-quality entries that would degrade fine-tuning:
- Too short (<100 chars in answer)
- Table-heavy fragments (>30% pipe characters)
- OCR artifacts (high ratio of non-ASCII or garbled Unicode)
- Echo responses (answer just restates question)

Input: data/processed/01_formatted.jsonl
Output: data/processed/02_quality_filtered.jsonl
"""

import json
import re
import argparse
from pathlib import Path
from difflib import SequenceMatcher

MIN_ANSWER_LENGTH = 100
MAX_TABLE_RATIO = 0.30        # Max ratio of '|' chars to total chars
MAX_GARBLED_RATIO = 0.10      # Max ratio of non-printable/garbled chars
MIN_QUESTION_LENGTH = 20
ECHO_SIMILARITY_THRESHOLD = 0.7  # If Q&A are >70% similar, likely echo


def is_too_short(answer: str) -> bool:
    """Filter entries where the answer is too short to be useful."""
    return len(answer.strip()) < MIN_ANSWER_LENGTH


def is_table_heavy(text: str) -> bool:
    """Filter entries that are mostly tabular data (pipes, dashes)."""
    if not text:
        return False
    table_chars = text.count('|') + text.count('+') + text.count('\u2500')
    return table_chars / len(text) > MAX_TABLE_RATIO


def has_ocr_artifacts(text: str) -> bool:
    """Filter entries with OCR/encoding artifacts."""
    if not text:
        return False
    # Count non-printable and garbled characters
    garbled = sum(1 for c in text if ord(c) > 127 and not c.isalpha())
    garbled += len(re.findall(r'[\xc3\xb0\xc5\xb8\x00-\x08\x0b\x0c\x0e-\x1f]', text))
    return garbled / len(text) > MAX_GARBLED_RATIO


def is_echo_response(question: str, answer: str) -> bool:
    """Filter entries where the answer just restates the question."""
    ratio = SequenceMatcher(None, question.lower(), answer.lower()[:len(question)*2]).ratio()
    return ratio > ECHO_SIMILARITY_THRESHOLD


def quality_check(example: dict) -> tuple[bool, str]:
    """Run all quality checks. Returns (passes, reason_if_failed)."""
    messages = example.get('messages', [])

    question = ''
    answer = ''
    for msg in messages:
        if msg['role'] == 'user':
            question = msg['content']
        elif msg['role'] == 'assistant':
            answer = msg['content']

    if len(question.strip()) < MIN_QUESTION_LENGTH:
        return False, 'question_too_short'

    if is_too_short(answer):
        return False, 'answer_too_short'

    if is_table_heavy(answer):
        return False, 'table_heavy'

    if has_ocr_artifacts(question) or has_ocr_artifacts(answer):
        return False, 'ocr_artifacts'

    if is_echo_response(question, answer):
        return False, 'echo_response'

    return True, 'passed'


def main():
    parser = argparse.ArgumentParser(description='Quality filter training data')
    parser.add_argument('--input', type=Path, default=Path('data/processed/01_formatted.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('data/processed/02_quality_filtered.jsonl'))
    parser.add_argument('--report', type=Path, default=Path('data/processed/02_quality_report.json'))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    stats = {'total': 0, 'passed': 0, 'failed': {}}

    with open(args.input, 'r') as inp, open(args.output, 'w') as out:
        for line in inp:
            stats['total'] += 1
            example = json.loads(line)
            passes, reason = quality_check(example)

            if passes:
                out.write(line)
                stats['passed'] += 1
            else:
                stats['failed'][reason] = stats['failed'].get(reason, 0) + 1

    stats['removed'] = stats['total'] - stats['passed']
    stats['removal_rate'] = f"{stats['removed'] / stats['total'] * 100:.1f}%"

    with open(args.report, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"Quality Filter Results:")
    print(f"  Input:   {stats['total']:,}")
    print(f"  Passed:  {stats['passed']:,}")
    print(f"  Removed: {stats['removed']:,} ({stats['removal_rate']})")
    print(f"\n  Removal breakdown:")
    for reason, count in sorted(stats['failed'].items(), key=lambda x: -x[1]):
        print(f"    {reason}: {count:,}")


if __name__ == '__main__':
    main()
