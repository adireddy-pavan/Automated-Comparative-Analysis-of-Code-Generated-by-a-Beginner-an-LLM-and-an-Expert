#!/usr/bin/env python3
"""Make blinded stimulus files for FUTURE independent evaluation.

The packet is NOT a completed external validation. Keep the private key away
from raters. Do not distribute the labelled originals or the key to reviewers.
"""
import csv
import hashlib
import json
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'verification'/'independent_review_preparation'
SEED=20261016

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    public=OUT/'REVIEWER_PACKET'
    public.mkdir(exist_ok=True)
    metadata=[]
    key=[]
    randomizer=random.Random(SEED)
    for task in sorted((ROOT/'dataset/tasks').iterdir()):
        if not task.is_dir():continue
        m=json.loads((task/'meta.json').read_text(encoding='utf-8'))
        choices=['beginner','expert']
        randomizer.shuffle(choices)
        specs=public/task.name
        specs.mkdir(exist_ok=True)
        (specs/'SPECIFICATION.txt').write_text(m['description'].strip()+'\n',encoding='utf-8')
        for label,source in zip(('A','B'),choices):
            code=(task/'solutions'/f'{source}.py').read_bytes()
            (specs/f'candidate_{label}.py').write_bytes(code)
            data={'task_id':task.name,'candidate':label,'source':source,'sha256':hashlib.sha256(code).hexdigest()}
            key.append(data)
            metadata.append({'task_id':task.name,'candidate':label,'source_label':'WITHHELD',
                             'difficulty_rating_1_to_5':'','style_rating_1_to_5':'',
                             'correctness_confidence_1_to_5':'','feedback_notes':''})
    with (OUT/'PRIVATE_KEY_DO_NOT_SEND_TO_RATERS.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(key[0]));w.writeheader();w.writerows(key)
    with (public/'BLANK_RATING_FORM.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(metadata[0]));w.writeheader();w.writerows(metadata)
    (public/'READ_ME_FIRST.md').write_text('''# Future independent reviewer packet — BLIND TO SOURCE LABELS

No reviewer ratings have been collected. Do not pretend this packet is evidence of completed review. Before recruiting raters confirm any institutional ethics/consent requirements. Reviewers should not inspect the original repository, original class labels or private key before returning ratings.

Read the SPECIFICATION.txt in each task folder; then assess candidate_A.py and candidate_B.py in randomised source-label order. Supply the blank form with independent ratings and critical comments, and give the date and reviewer qualification (using an institution-approved identifier). An external reviewer should independently assess edge-case coverage and task difficulty, not assume the author-assigned tiers are correct. Ratings must be recorded before the private key is opened. The experimenter should preregister agreement and adjudication criteria in advance, document all exclusions and never edit submitted ratings.

This packet holds 60 constructed reference solutions, not code collected from actual novices or expert programmers. Evaluating the labels does not turn them into real participant output.
''',encoding='utf-8')
    print(f'Prepared {len(key)} unlabeled stimuli across 30 tasks; NO human review performed.')

if __name__=='__main__':main()
