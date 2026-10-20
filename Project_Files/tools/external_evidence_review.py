#!/usr/bin/env python3
"""Validate submitted external reviewer evidence without inventing assessments.

This is an integrity/consistency check, NOT authentication of reviewer identity,
independence, authorship, ethics clearance, or original human provenance.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'verification' / 'independent_review_preparation'
EXTERNAL = ROOT / 'verification' / 'external_results'
KEY = BASE / 'PRIVATE_KEY_DO_NOT_SEND_TO_RATERS.csv'
OUTPUT = ROOT / 'verification' / 'external_review_analysis.json'
FIELDS = ('difficulty_rating_1_to_5', 'style_rating_1_to_5', 'correctness_confidence_1_to_5')


def csvrows(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def expected_samples() -> dict[tuple[str, str], dict]:
    rows = csvrows(KEY)
    return {(r['task_id'], r['candidate']): r for r in rows}


def verify_packet(keys: dict) -> list[str]:
    errors = []
    for (task, candidate), row in keys.items():
        path = BASE / 'REVIEWER_PACKET' / task / f'candidate_{candidate}.py'
        if not path.exists():
            errors.append(f'Missing blinded candidate: {task}/{candidate}')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            errors.append(f'Blind candidate hash mismatch: {task}/{candidate}')
    return errors


def read_reviewer(number: int, expected: set[tuple[str, str]]) -> tuple[dict, dict]:
    directory = EXTERNAL / f'reviewer_{number:02d}'
    files = sorted(directory.glob('*.csv'))
    attestation = directory / 'REVIEWER_ATTESTATION.txt'
    result = {'reviewer': number, 'status': 'pending', 'rating_file': None,
              'rating_count': 0, 'problems': [], 'attestation_present': attestation.is_file()}
    if not files:
        result['problems'].append('No completed CSV received')
        return result, {}
    if len(files) != 1:
        result['problems'].append('Expected exactly one completed CSV per reviewer')
        return result, {}
    result['rating_file'] = str(files[0].relative_to(ROOT))
    data = {}
    for idx, r in enumerate(csvrows(files[0]), 2):
        try:
            pair = (r['task_id'].strip(), r['candidate'].strip())
            if pair not in expected or pair in data:
                raise ValueError('unrecognized or duplicate task/candidate')
            values = {field: int(r[field]) for field in FIELDS}
            if not all(1 <= val <= 5 for val in values.values()):
                raise ValueError('ratings must be integers between 1 and 5')
            label = r.get('perceived_level', '').strip().lower()
            if label not in {'beginner', 'expert', 'uncertain'}:
                raise ValueError('perceived_level must be beginner, expert or uncertain')
            # The source label in a received form MUST NOT disclose the key.
            if r.get('source_label', 'WITHHELD').strip().upper() != 'WITHHELD':
                raise ValueError('source_label must remain WITHHELD in the blinded file')
            data[pair] = {'values': values, 'perceived_level': label}
        except (ValueError, KeyError, TypeError) as exc:
            result['problems'].append(f'CSV line {idx}: {exc}')
    result['rating_count'] = len(data)
    if len(data) != len(expected):
        result['problems'].append(f'Expected {len(expected)} unique ratings, got {len(data)}')
    if not attestation.is_file():
        result['problems'].append('Missing completed reviewer attestation')
    else:
        fields = {}
        for line in attestation.read_text(encoding='utf-8').splitlines():
            key, colon, value = line.partition(':')
            if colon: fields[key.strip().lower()] = value.strip()
        for required in ('reviewer_identifier', 'review_date_utc', 'qualification', 'confirms_blind_to_key', 'confirms_independent_ratings', 'signature'):
            if not fields.get(required): result['problems'].append(f'Attestation field missing: {required}')
        for fld in ('reviewer_identifier','qualification','signature'):
            supplied = fields.get(fld,'')
            if supplied and (supplied.strip().lower() in ('todo','n/a','none','example','student','reviewer','your name')
                             or not any(ch.isalnum() for ch in supplied)):
                result['problems'].append(f'Attestation placeholder is not accepted: {fld}')
        if fields.get('review_date_utc'):
            try:
                date_text = fields['review_date_utc']
                parsed = datetime.fromisoformat(date_text.replace('Z','+00:00'))
                if parsed.tzinfo is None:
                    raise ValueError('UTC offset is required')
                if parsed.astimezone(timezone.utc) > datetime.now(timezone.utc):
                    raise ValueError('future review date')
            except ValueError as exc:
                result['problems'].append(f'Invalid review_date_utc: {exc}')
        for confirm in ('confirms_blind_to_key', 'confirms_independent_ratings'):
            if fields.get(confirm, '').lower() not in ('yes', 'true'):
                result['problems'].append(f'Attestation must explicitly confirm YES: {confirm}')
    result['status'] = 'received_format_valid' if not result['problems'] else 'incomplete_or_invalid'
    return result, data


def kappa(labels1: list[str], labels2: list[str]) -> float | None:
    """Unweighted agreement for a three-category reviewer classification."""
    if not labels1 or len(labels1) != len(labels2):
        return None
    n = len(labels1)
    observed = sum(a == b for a, b in zip(labels1, labels2)) / n
    a_count, b_count = Counter(labels1), Counter(labels2)
    expected = sum(a_count[x] * b_count[x] for x in ('beginner', 'expert', 'uncertain')) / (n*n)
    return (observed - expected) / (1 - expected) if expected < 1 else None


def main() -> int:
    keys = expected_samples()
    packet_errors = verify_packet(keys)
    expected = set(keys)
    result1, data1 = read_reviewer(1, expected)
    result2, data2 = read_reviewer(2, expected)
    report = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'classification': 'Review form audit only; reviewer independence not independently authenticated',
        'anonymous_packet_valid': not packet_errors,
        'packet_errors': packet_errors,
        'reviewers': [result1, result2],
        'paired_sample_count': 0,
        'raw_inter_rater_agreement': None,
        'cohens_kappa_unweighted': None,
        'per_reviewer_agreement_with_constructed_labels': {},
        'status': 'PENDING',
    }
    if result1['status'] == result2['status'] == 'received_format_valid' and not packet_errors:
        order = sorted(expected)
        classes1 = [data1[key]['perceived_level'] for key in order]
        classes2 = [data2[key]['perceived_level'] for key in order]
        report['paired_sample_count'] = len(order)
        report['raw_inter_rater_agreement'] = round(sum(a == b for a,b in zip(classes1,classes2)) / len(order), 5)
        val = kappa(classes1, classes2)
        report['cohens_kappa_unweighted'] = round(val, 5) if val is not None else None
        for n, data in ((1, data1), (2, data2)):
            determinate = [key for key in order if data[key]['perceived_level'] != 'uncertain']
            report['per_reviewer_agreement_with_constructed_labels'][f'reviewer_{n:02d}'] = {
                'classified_not_uncertain': len(determinate),
                'matches': sum(data[key]['perceived_level'] == keys[key]['source'] for key in determinate),
            }
        report['status'] = 'COMPLETED_FORMS_UNVERIFIED_INDEPENDENCE'
    report['limitations'] = [
        'Do not interpret constructed style labels as real human expert/novice author identities.',
        'Completion requires genuine independently submitted ratings and signed/datable attestations.',
        'This parser cannot establish institutional ethics approval or verify signatures and reviewer identity.',
        'A source key is opened only for post-submission comparisons, not distributed to reviewers.',
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 1 if packet_errors else 0  # missing external submissions is PENDING, not a test failure


if __name__ == '__main__':
    raise SystemExit(main())
