#!/usr/bin/env python3
"""Audit stored code bytes and record what model provenance CANNOT be verified.

This is an archive/chain-of-custody check. SHA-256 proves byte identity only;
it cannot prove authorship, model/provider identity, sampling independence, or date.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'verification' / 'provenance_inventory.json'


def audit(root: Path = ROOT) -> dict:
    records = []
    errors = []
    seen = defaultdict(list)
    tasks = sorted(p for p in (root / 'dataset' / 'tasks').iterdir() if p.is_dir())
    for task in tasks:
        for source in ('beginner', 'llm', 'expert'):
            for sample in range(1, 6 if source == 'llm' else 2):
                rel = (Path('dataset/tasks') / task.name / 'solutions' / source / f'sample_{sample}.py'
                       if source == 'llm' else
                       Path('dataset/tasks') / task.name / 'solutions' / f'{source}.py')
                path = root / rel
                if not path.is_file():
                    errors.append(f'missing: {rel}')
                    continue
                data = path.read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                seen[(task.name, digest)].append(f'{source}:{sample}')
                records.append({'task': task.name, 'source_label': source,
                                'sample': sample, 'relative_path': rel.as_posix(),
                                'bytes': len(data), 'sha256': digest,
                                'provenance': ('author-reported model-labelled archive, NOT provider-authenticated'
                                               if source == 'llm' else
                                               'constructed style reference, NOT verified human-participant code')})
    duplicate_within_task = [
        {'task': task, 'sha256': digest, 'labels': labels}
        for (task, digest), labels in seen.items() if len(labels) > 1
    ]
    counts = dict(Counter(r['source_label'] for r in records))
    if counts != {'beginner': 30, 'llm': 150, 'expert': 30}:
        errors.append(f'Unexpected counts: {counts}')
    # No model API response receipts or subject-consent records accompany this archive.
    receipts_dir = root / 'dataset' / 'original_provider_receipts'
    original_receipts = sorted(str(p.relative_to(root)) for p in receipts_dir.rglob('*') if p.is_file()) if receipts_dir.exists() else []
    result = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'audit_type': 'Source-byte integrity inventory; NOT independent generation authentication',
        'status': 'pass' if not errors else 'fail',
        'record_count': len(records), 'counts': counts,
        'source_records': records,
        'identical_byte_files_within_task': duplicate_within_task,
        'original_provider_receipt_files_in_designated_folder': original_receipts,
        'claims_verified': ['existence, size, SHA-256 of archived Python source files'],
        'claims_not_verified': ['original model provider', 'claimed model identifier',
                                'claimed date of generation', 'independence of five model samples',
                                'unseen-test performance', 'actual human-programmer skill or authorship'],
        'remediation': ('Original dated provider API responses including response ID/model ID and matching source hashes '
                        'must come from the original author/provider. Fresh API calls would constitute a NEW experiment, '
                        'not retrospective authentication of this archive.'),
        'errors': errors,
    }
    return result


def main() -> int:
    result = audit()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'source_records'}, indent=2))
    return int(bool(result['errors']))


if __name__ == '__main__':
    sys.exit(main())
