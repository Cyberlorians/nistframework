"""
Step 3: Relevance Filter
Scores and filters the NIST Cybersecurity dataset for CMMC/compliance relevance.
The NIST dataset is massive (424K) and covers all of cybersecurity. We need
only the portions relevant to CMMC, access control, CUI protection, etc.

Approach:
1. Score each example using weighted keyword matching
2. Keep top N most relevant examples
3. Sample to maintain source balance

Input: data/processed/02_quality_filtered.jsonl
Output: data/processed/03_relevance_filtered.jsonl
"""

import json
import re
import argparse
from pathlib import Path
from collections import defaultdict

# Weighted relevance keywords — higher weight = more relevant to CMMC
RELEVANCE_KEYWORDS = {
    # CMMC-specific (highest weight)
    'cmmc': 10, 'cybersecurity maturity model': 10,
    'cui': 8, 'controlled unclassified information': 8,
    'fci': 7, 'federal contract information': 7,
    'dfars': 7, '252.204-7012': 8,

    # NIST 800-171 (high weight — direct CMMC Level 2 mapping)
    '800-171': 9, 'nist sp 800-171': 9,
    '800-172': 7, 'nist sp 800-172': 7,

    # CMMC domains and key practices
    'access control': 6, 'audit and accountability': 6,
    'awareness and training': 5, 'configuration management': 5,
    'identification and authentication': 6, 'incident response': 5,
    'maintenance': 4, 'media protection': 5,
    'personnel security': 4, 'physical protection': 4,
    'risk assessment': 5, 'security assessment': 5,
    'system and communications protection': 5,
    'system and information integrity': 5,

    # Assessment and compliance terminology
    'assessment': 4, 'assessor': 5, 'c3pao': 7,
    'plan of action': 5, 'poa&m': 5, 'poam': 5,
    'system security plan': 5, 'ssp': 4,
    'body of evidence': 5, 'artifact': 3,

    # Related frameworks
    '800-53': 4, 'nist csf': 3,
    'fedramp': 4, 'itar': 5,
    'hipaa': 3, 'security rule': 3,

    # General compliance (lower weight)
    'compliance': 2, 'control': 2, 'safeguard': 2,
    'encryption': 3, 'multi-factor': 4, 'mfa': 4,
    'audit log': 3, 'privileged access': 4,
}


def score_relevance(text: str) -> float:
    """Score text for CMMC/compliance relevance using weighted keywords."""
    text_lower = text.lower()
    score = 0.0
    matched_terms = []

    for keyword, weight in RELEVANCE_KEYWORDS.items():
        count = len(re.findall(re.escape(keyword), text_lower))
        if count > 0:
            # Diminishing returns: first match worth full weight, subsequent worth less
            term_score = weight * (1 + 0.3 * min(count - 1, 3))
            score += term_score
            matched_terms.append(keyword)

    return score


def main():
    parser = argparse.ArgumentParser(description='Relevance filter for NIST data')
    parser.add_argument('--input', type=Path, default=Path('data/processed/02_quality_filtered.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('data/processed/03_relevance_filtered.jsonl'))
    parser.add_argument('--nist-keep', type=int, default=7000,
                       help='Max NIST examples to keep after relevance filtering')
    parser.add_argument('--min-score', type=float, default=5.0,
                       help='Minimum relevance score for NIST examples')
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Separate NIST from other sources (other sources pass through unfiltered)
    nist_examples = []
    other_examples = []

    with open(args.input, 'r') as f:
        for line in f:
            example = json.loads(line)
            if example.get('source') == 'nist_cybersecurity':
                # Score the full text (question + answer)
                full_text = ' '.join(
                    msg['content'] for msg in example['messages']
                    if msg['role'] in ('user', 'assistant')
                )
                score = score_relevance(full_text)
                example['_relevance_score'] = score
                nist_examples.append((score, line, example))
            else:
                other_examples.append(line)

    # Filter and sample NIST examples
    nist_relevant = [(s, l, e) for s, l, e in nist_examples if s >= args.min_score]
    nist_relevant.sort(key=lambda x: -x[0])  # Highest relevance first
    nist_kept = nist_relevant[:args.nist_keep]

    # Write output
    with open(args.output, 'w') as out:
        # Write non-NIST examples (pass through)
        for line in other_examples:
            out.write(line)

        # Write filtered NIST examples (remove temp score field)
        for score, line, example in nist_kept:
            del example['_relevance_score']
            out.write(json.dumps(example) + '\n')

    print(f"Relevance Filter Results:")
    print(f"  NIST input:     {len(nist_examples):,}")
    print(f"  NIST relevant:  {len(nist_relevant):,} (score >= {args.min_score})")
    print(f"  NIST kept:      {len(nist_kept):,} (top {args.nist_keep:,})")
    print(f"  NIST removed:   {len(nist_examples) - len(nist_kept):,}")
    print(f"  Other sources:  {len(other_examples):,} (passed through)")
    print(f"  Total output:   {len(other_examples) + len(nist_kept):,}")


if __name__ == '__main__':
    main()
