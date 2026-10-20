#!/usr/bin/env bash
# Genuine local verification. This script STOPS on failures.
# Execute only trusted coursework solutions; temp processes are NOT a sandbox.
set -Eeuo pipefail
STAMP="$(date -u +%Y%m%d_%H%M%S)"
mkdir -p verification
LOG="verification/full_verification_${STAMP}.log"
STATUS="verification/full_verification_${STAMP}.status"
exec > >(tee "$LOG") 2>&1
onexit() {
  local code=$?
  if [ "$code" -eq 0 ]; then
    printf 'PASS (all required stages) %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > "$STATUS"
    echo "PASS: all stages completed. $LOG"
  else
    printf 'FAIL (exit %s; not a completed verification) %s\n' "$code" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > "$STATUS"
    echo "FAILED: exit $code. See $LOG. Do NOT claim full reproducibility."
  fi
}
trap onexit EXIT

echo "UTC start: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "Python host: $(python3 --version)"
echo 'Before running, preserve the archived ZIP: this pipeline regenerates outputs and evidence.'
VENV_DIR="${VENV_DIR:-.venv_verify}"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r requirements.txt
"$VENV_DIR/bin/python" -m pip freeze > "verification/installed_packages_${STAMP}.txt"
"$VENV_DIR/bin/python" -m pip check
"$VENV_DIR/bin/python" tools/audit_repro_evidence.py
"$VENV_DIR/bin/python" -m pytest tests/ -q
"$VENV_DIR/bin/python" -m pylint --fail-under=10.0 src/ run_analysis.py config.py
"$VENV_DIR/bin/python" -m bandit -q -c pyproject.toml -r src/ run_analysis.py config.py
"$VENV_DIR/bin/python" run_analysis.py
"$VENV_DIR/bin/python" - <<'PY'
from pathlib import Path
import csv
with Path('outputs/metrics.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==210, f'Expected 210 rows, got {len(rows)}'
for required in ('outputs/stats.json','report/report.md','report/report.docx','report/dashboard.html'):
    assert Path(required).is_file(), f'Missing generated output: {required}'
print('Output checks PASSED: 210 metric rows and required generated artefacts')
PY
printf 'UTC end: %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
