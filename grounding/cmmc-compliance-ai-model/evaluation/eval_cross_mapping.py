"""
Cross-Framework Mapping Evaluation
Tests the model's ability to map controls across CMMC, NIST 800-53,
NIST 800-171, NIST CSF, and HIPAA.

This is the highest-value capability — organizations rarely have
single-framework obligations.

Usage:
    python evaluation/eval_cross_mapping.py --model cmmc-expert-7b
"""

import json
import time
import argparse
from pathlib import Path

import requests

OLLAMA_API = "http://localhost:11434/api/generate"

# Cross-framework mapping test cases
# Each test provides a source control and expects specific target mappings
MAPPING_TESTS = [
    {
        "source": "CMMC AC.L2-3.1.1",
        "question": "Map CMMC practice AC.L2-3.1.1 to equivalent controls in NIST 800-53 and HIPAA.",
        "expected_mappings": {
            "nist_800_53": ["AC-2", "AC-3"],
            "hipaa": ["164.312(a)(1)", "164.312(d)"],
        }
    },
    {
        "source": "CMMC AU.L2-3.3.1",
        "question": "What NIST 800-53 and HIPAA controls correspond to CMMC audit logging requirement AU.L2-3.3.1?",
        "expected_mappings": {
            "nist_800_53": ["AU-2", "AU-3", "AU-6"],
            "hipaa": ["164.312(b)"],
        }
    },
    {
        "source": "CMMC IA.L2-3.5.3",
        "question": "Map CMMC multi-factor authentication requirement IA.L2-3.5.3 to NIST 800-53 and HIPAA equivalents.",
        "expected_mappings": {
            "nist_800_53": ["IA-2", "IA-2(1)", "IA-2(2)"],
            "hipaa": ["164.312(d)"],
        }
    },
    {
        "source": "CMMC SC.L2-3.13.8",
        "question": "What NIST 800-53 controls map to CMMC encryption requirements under SC.L2-3.13.8?",
        "expected_mappings": {
            "nist_800_53": ["SC-8", "SC-8(1)", "SC-13"],
            "hipaa": ["164.312(a)(2)(iv)", "164.312(e)(2)(ii)"],
        }
    },
    {
        "source": "CMMC IR.L2-3.6.1",
        "question": "Map CMMC incident response planning IR.L2-3.6.1 to NIST 800-53 and NIST CSF equivalents.",
        "expected_mappings": {
            "nist_800_53": ["IR-1", "IR-4", "IR-5", "IR-8"],
            "nist_csf": ["RS.RP", "RS.CO", "DE.AE"],
        }
    },
]


def query_model(prompt: str, model: str) -> str:
    try:
        response = requests.post(OLLAMA_API, json={
            "model": model, "prompt": prompt, "stream": False
        }, timeout=60)
        return response.json().get('response', '')
    except Exception as e:
        return f"ERROR: {e}"


def check_mappings(response: str, expected: dict) -> dict:
    """Check if expected control mappings appear in the response."""
    response_upper = response.upper()
    results = {}

    for framework, controls in expected.items():
        found = []
        missing = []
        for control in controls:
            if control.upper() in response_upper:
                found.append(control)
            else:
                missing.append(control)
        results[framework] = {
            'found': found,
            'missing': missing,
            'accuracy': len(found) / len(controls) if controls else 0
        }

    return results


def main():
    parser = argparse.ArgumentParser(description='Evaluate cross-framework mapping')
    parser.add_argument('--model', type=str, default='cmmc-expert-7b')
    parser.add_argument('--output', type=Path, default=Path('evaluation/cross_mapping_results.json'))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    results = []

    for test in MAPPING_TESTS:
        print(f"\nSource: {test['source']}")
        start = time.time()
        response = query_model(test['question'], args.model)
        elapsed = time.time() - start

        mapping_results = check_mappings(response, test['expected_mappings'])

        overall_accuracy = sum(
            r['accuracy'] for r in mapping_results.values()
        ) / len(mapping_results) if mapping_results else 0

        results.append({
            'source_control': test['source'],
            'overall_accuracy': round(overall_accuracy, 3),
            'framework_results': mapping_results,
            'response_time_sec': round(elapsed, 2),
        })

        for fw, r in mapping_results.items():
            status = "\u2713" if r['accuracy'] >= 0.5 else "\u2717"
            print(f"  {status} {fw}: {r['accuracy']:.0%} -- found {r['found']}, missing {r['missing']}")

    avg_accuracy = sum(r['overall_accuracy'] for r in results) / len(results) if results else 0

    output = {
        'model': args.model,
        'average_mapping_accuracy': round(avg_accuracy, 3),
        'test_results': results,
    }

    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOverall cross-mapping accuracy: {avg_accuracy:.1%}")
    print(f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()
