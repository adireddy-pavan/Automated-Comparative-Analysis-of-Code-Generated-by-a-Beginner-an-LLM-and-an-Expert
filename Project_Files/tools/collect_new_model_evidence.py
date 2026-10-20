#!/usr/bin/env python3
"""Optional NEW provider-attested run; NEVER overwrites original LLM files.

This is not a way to prove the historical model's identity. Requires explicit
--execute and an API key. Response ID and reported model are persisted verbatim.
Store key only in environment, not in reports or version control.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_ENDPOINT = 'https://api.anthropic.com/v1/messages'
_API_VERSION = '2023-06-01'


def prompt_for_task(task_id: str) -> str:
    """Use published task metadata but NO archived solution or test source."""
    task_dir = ROOT / 'dataset' / 'tasks' / task_id
    meta_path = task_dir / 'meta.json'
    if not meta_path.is_file():
        raise ValueError(f'Unknown task: {task_id}')
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    return (f"Implement one Python function named {meta['entry_point']} that meets this specification: "
            f"{meta['description']}\nUse only Python standard library. "
            "Return only executable Python source (no markdown fences or prose). "
            "No task tests, expected outputs or reference implementations are provided.")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def collect_new(task_id: str, model: str, samples: int, execute: bool = False) -> list[str]:
    """Return preview messages or collect genuinely new samples and receipts."""
    if samples < 1 or samples > 5:
        raise ValueError('Choose 1 to 5 independently requested samples')
    if not model.strip():
        raise ValueError('An explicit provider model ID is required')
    prompt = prompt_for_task(task_id)
    if not execute:
        return [f'DRY RUN ONLY: {samples} NEW API calls to {model!r} for {task_id}.', prompt]
    key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if not key:
        raise RuntimeError('ANTHROPIC_API_KEY is required with --execute; no files were written')
    # A new timestamped folder, kept separate from the 2026 archived evidence.
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = ROOT / 'prospective_model_runs' / f'{stamp}_{task_id}'
    if dest.exists():
        raise FileExistsError(dest)
    dest.mkdir(parents=True)
    message = {'model': model, 'max_tokens': 2048,
               'messages': [{'role': 'user', 'content': prompt}]}
    request_data = json.dumps(message, ensure_ascii=False).encode('utf-8')
    output=[]
    for i in range(1, samples+1):
        start = datetime.now(timezone.utc).isoformat()
        req = urllib.request.Request(_ENDPOINT, data=request_data,
            headers={'x-api-key':key, 'anthropic-version':_API_VERSION,
                     'content-type':'application/json'}, method='POST')
        t0 = time.monotonic()
        # Never serialize the request headers (which contain the API key).
        with urllib.request.urlopen(req, timeout=120) as resp:
            response_body = resp.read()
            response_status = resp.status
        completed = datetime.now(timezone.utc).isoformat()
        response = json.loads(response_body)
        code = ''.join(piece.get('text', '') for piece in response.get('content', [])
                       if piece.get('type') == 'text')
        if not code.strip():
            raise RuntimeError(f'Sample {i}: no text returned; inspect provider response')
        sample_dir = dest / f'sample_{i}'
        sample_dir.mkdir()
        (sample_dir / 'provider_response.json').write_bytes(response_body)
        (sample_dir / 'sample.py').write_text(code.rstrip()+'\n',encoding='utf-8')
        evidence = {
          'classification':'NEW provider API response, NOT proof of historical generation',
          'requested_model':model,'provider_reported_model':response.get('model'),
          'provider_response_id':response.get('id'),
          'received_utc':completed,'requested_utc':start,
          'round_trip_s':round(time.monotonic()-t0,3),
          'http_status':response_status,'provider_stop_reason':response.get('stop_reason'),
          'usage':response.get('usage'),
          'prompt_sha256':sha256(prompt.encode('utf-8')),
          'response_sha256':sha256(response_body),
          'source_sha256':sha256((code.rstrip()+'\n').encode('utf-8')),
          'task_id':task_id, 'sample':i, 'test_files_included_in_prompt':False,
          'authenticated_from':'API response record; provider identity still depends on trusted endpoint and credential',
        }
        (sample_dir / 'receipt.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
        output.append(f"NEW sample {i}: response={response.get('id','MISSING')} hash={evidence['source_sha256']}")
    (dest / 'prompt.txt').write_text(prompt+'\n',encoding='utf-8')
    return [f'NEW study data saved under {dest.relative_to(ROOT)}'] + output


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True)
    parser.add_argument('--model', required=True, help='Exact provider model ID, explicitly supplied by student')
    parser.add_argument('--samples',type=int,default=1)
    parser.add_argument('--execute',action='store_true',help='Make paid live API requests; absent by default')
    args=parser.parse_args()
    for line in collect_new(args.task,args.model,args.samples,args.execute):
        print(line)


if __name__=='__main__':main()
