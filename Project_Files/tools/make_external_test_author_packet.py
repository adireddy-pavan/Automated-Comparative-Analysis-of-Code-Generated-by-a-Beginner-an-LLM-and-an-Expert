#!/usr/bin/env python3
"""Make metadata-only materials for a genuinely external test author.

The author must create and freeze hidden cases WITHOUT access to source files,
existing tests, archive metrics, or supplementary results.
"""
import csv,json,zipfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'verification'/'external_test_author_packet.zip'
rows=[]
for task in sorted((ROOT/'dataset/tasks').iterdir()):
    if task.is_dir():
        m=json.loads((task/'meta.json').read_text(encoding='utf-8'))
        rows.append({'task_id':task.name,'entry_point':m['entry_point'],'claimed_tier':m['difficulty'],'specification':m['description'],'reviewer_clarification':'','test_case_id':'','inputs_json':'','expected_json':'','design_rationale':''})
out=io.StringIO()
writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('TASK_SPECIFICATIONS_ONLY.csv',out.getvalue())
    z.writestr('READ_FIRST.txt', '''PROSPECTIVE EXTERNAL TEST-DESIGN PACKET (NOT VALIDATION RESULTS)\n\nThis packet deliberately excludes ALL candidate code and previous testing files. The external author should write and freeze new deterministic tests from the specifications only. Confirm whether any specification is ambiguous BEFORE running solutions. Independently log authorship, test timestamps, hashes, and code/test access history. Do not inspect prior solutions or results until cases are frozen. Have an additional second reviewer adjudicate oracle correctness where practical. Institutional permissions may be needed before recruiting participants.\n\nAfter receipt, save the approved cases as a new version and evaluate original LLM-labelled archives as a POST-GENERATION, EXTERNALLY AUTHORED test of the archived solutions, not a prospective sampling experiment (original generation has already occurred). Truly prospective generation requires new model calls AFTER tests are frozen but WITHOUT access to them.\n''')
print('Created spec-only 30-task external-author packet (no tests or results fabricated).')
