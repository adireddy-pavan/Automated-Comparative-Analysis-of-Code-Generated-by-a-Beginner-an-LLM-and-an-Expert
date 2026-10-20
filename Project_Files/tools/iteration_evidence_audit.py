#!/usr/bin/env python3
"""Inventory real Git revision metadata; never invent historical development events."""
from __future__ import annotations
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification' / 'iteration_evidence_audit.json'


def git(*args):
    p = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True,
                       timeout=30, check=False)
    return p.stdout.strip() if p.returncode == 0 else None


def main():
    log = git('log', '--all', '--format=%H%x1f%aI%x1f%an%x1f%ae%x1f%s%x1e')
    commits = []
    if log:
        for record in log.split('\x1e'):
            parts = record.strip().split('\x1f')
            if len(parts) != 5:
                continue
            sha, date, author, email, subject = parts
            # This is classification by declared author metadata only, NOT identity authentication.
            audit_authored = 'review' in (author + ' ' + email).lower() or 'assistant' in (author + ' ' + subject).lower()
            paths_raw = git('diff-tree','--no-commit-id','--name-only','-r','--root',sha) or ''
            paths = [p for p in paths_raw.splitlines() if p.strip()]
            commits.append({'sha':sha, 'recorded_author_date':date, 'recorded_author':author,
                            'subject':subject, 'review_period_or_ai_assisted':audit_authored,
                            'changed_file_count':len(paths), 'changed_files':paths[:100],
                            'file_list_truncated':len(paths)>100})
    report = {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'commit_count':len(commits), 'commits':commits,
        'source_git_available':log is not None,
        'verified_original_student_development_history':False,
        'note':'Changed-file lists are genuine Git diff inventories; links from an issue to a retest still require contemporaneous records.',
        'supervision_evidence_folder':str(ROOT / 'verification/external_results/development_history'),
        'external_history_evidence_files':[str(p.relative_to(ROOT)) for p in sorted(
            (ROOT / 'verification/external_results/development_history').glob('*'))
            if p.is_file() and p.name != 'NOT_YET_COMPLETED.txt'],
        'limitations':[
            'Git author strings and dates are stored metadata, not independently authenticated origin.',
            'Review-period commits are genuine review-history evidence but do not reconstruct the original development period.',
            'Source-code diffs and dated before/after retest logs must support each claimed iteration.',
            'Never backdate, rewrite, squash, or manufacture historical commits.',
        ],
    }
    OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Found {len(commits)} Git commits. Original student development history NOT authenticated.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
