"""
Compliance Evaluation Suite
Tests the fine-tuned model against framework-specific accuracy benchmarks.

Evaluates 5 categories:
1. CMMC Level Identification — Can the model correctly identify which CMMC level a practice belongs to?
2. Control Reference Accuracy — Does the model cite correct NIST SP 800-171 section numbers?
3. Cross-Framework Mapping — Can the model map controls across CMMC/NIST 800-53/HIPAA?
4. Implementation Guidance Quality — Does the model provide actionable, specific guidance?
5. Assessment Evidence Specificity — Does the model name specific artifacts assessors expect?

Usage:
    python evaluation/eval_compliance.py --model cmmc-expert-7b

Dependencies:
    pip install requests  (for Ollama API)
"""

import json
import time
import argparse
from pathlib import Path

import requests

OLLAMA_API = "http://localhost:11434/api/generate"

# Evaluation questions with expected elements in answers
EVAL_QUESTIONS = {
    "cmmc_level_identification": [
        {
            "question": "What CMMC level requires multi-factor authentication for all users accessing CUI?",
            "expected_elements": ["level 2", "800-171", "3.5.3", "identification and authentication"],
            "category": "cmmc_level"
        },
        {
            "question": "At which CMMC level must organizations implement security awareness training?",
            "expected_elements": ["level 2", "awareness and training", "at.2", "800-171"],
            "category": "cmmc_level"
        },
        {
            "question": "Is vulnerability scanning required at CMMC Level 1?",
            "expected_elements": ["no", "level 2", "level 3", "not required at level 1"],
            "category": "cmmc_level"
        },
        {
            "question": "What access control requirements exist at CMMC Level 1 versus Level 2?",
            "expected_elements": ["level 1", "level 2", "fci", "cui", "access control"],
            "category": "cmmc_level"
        },
        {
            "question": "Which CMMC level first requires incident response planning?",
            "expected_elements": ["level 2", "incident response", "ir.", "800-171"],
            "category": "cmmc_level"
        },
    ],
    "control_reference_accuracy": [
        {
            "question": "What is the NIST SP 800-171 requirement for limiting system access to authorized users?",
            "expected_elements": ["3.1.1", "access control", "authorized users", "transactions", "functions"],
            "category": "control_ref"
        },
        {
            "question": "Cite the specific NIST 800-171 control for audit log review.",
            "expected_elements": ["3.3", "audit", "review", "accountability"],
            "category": "control_ref"
        },
        {
            "question": "What NIST 800-171 section covers encryption of CUI at rest?",
            "expected_elements": ["3.13", "cryptographic", "protection", "system and communications"],
            "category": "control_ref"
        },
    ],
    "cross_framework_mapping": [
        {
            "question": "How does CMMC Level 2 AC.L2-3.1.1 map to NIST 800-53 controls?",
            "expected_elements": ["ac-2", "ac-3", "ac-17", "800-53", "access control"],
            "category": "cross_map"
        },
        {
            "question": "What HIPAA Security Rule requirements overlap with CMMC access controls?",
            "expected_elements": ["164.312", "access control", "unique user", "encryption"],
            "category": "cross_map"
        },
    ],
    "implementation_guidance": [
        {
            "question": "How should a small defense contractor implement multi-factor authentication to meet CMMC Level 2?",
            "expected_elements": ["mfa", "phishing-resistant", "authenticator", "privileged", "non-privileged"],
            "category": "implementation"
        },
        {
            "question": "What specific steps should an organization take to implement audit logging for CMMC compliance?",
            "expected_elements": ["audit events", "log", "review", "retention", "protection", "centralized"],
            "category": "implementation"
        },
    ],
    "assessment_evidence": [
        {
            "question": "What artifacts should I prepare for a CMMC Level 2 assessment of access control practices?",
            "expected_elements": ["ssp", "policy", "procedure", "access control list", "acl", "evidence", "screenshot"],
            "category": "evidence"
        },
        {
            "question": "What documentation does a C3PAO assessor expect for incident response capability?",
            "expected_elements": ["incident response plan", "irp", "test", "exercise", "contact", "reporting"],
            "category": "evidence"
        },
    ],
}


def query_model(prompt: str, model: str = "cmmc-expert-7b") -> str:
    """Query the Ollama model and return the response text."""
    try:
        response = requests.post(OLLAMA_API, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        }, timeout=60)
        return response.json().get('response', '')
    except Exception as e:
        return f"ERROR: {e}"


def evaluate_response(response: str, expected: list[str]) -> tuple[float, list[str]]:
    """Score response against expected elements. Returns (score, matched_elements)."""
    response_lower = response.lower()
    matched = [elem for elem in expected if elem.lower() in response_lower]
    score = len(matched) / len(expected) if expected else 0.0
    return score, matched


def main():
    parser = argparse.ArgumentParser(description='Evaluate compliance model accuracy')
    parser.add_argument('--model', type=str, default='cmmc-expert-7b')
    parser.add_argument('--output', type=Path, default=Path('evaluation/results.json'))
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    results = {
        'model': args.model,
        'categories': {},
        'overall_score': 0.0,
    }

    all_scores = []

    for category, questions in EVAL_QUESTIONS.items():
        category_scores = []
        category_results = []

        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"{'='*60}")

        for q in questions:
            start = time.time()
            response = query_model(q['question'], args.model)
            elapsed = time.time() - start

            score, matched = evaluate_response(response, q['expected_elements'])
            category_scores.append(score)
            all_scores.append(score)

            result = {
                'question': q['question'],
                'score': score,
                'matched_elements': matched,
                'expected_elements': q['expected_elements'],
                'response_time_sec': round(elapsed, 2),
            }
            if args.verbose:
                result['response'] = response
            category_results.append(result)

            status = "\u2713" if score >= 0.6 else "\u2717"
            print(f"  {status} {score:.0%} | {q['question'][:60]}...")
            print(f"    Matched: {matched}")

        avg = sum(category_scores) / len(category_scores) if category_scores else 0
        results['categories'][category] = {
            'average_score': round(avg, 3),
            'questions': category_results,
        }
        print(f"  Category average: {avg:.1%}")

    results['overall_score'] = round(
        sum(all_scores) / len(all_scores) if all_scores else 0, 3
    )

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"OVERALL SCORE: {results['overall_score']:.1%}")
    print(f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()
