# Tharun Project — convenience targets.
# Windows users without `make` can run the equivalent commands shown in README.md.

PY ?= .venv/bin/python
PIP ?= .venv/bin/pip

.PHONY: setup run figures report dashboard webapp screenshots test clean help

help:
	@echo "Targets:"
	@echo "  make setup       - create .venv and install requirements"
	@echo "  make run         - run the full analysis pipeline (python run_analysis.py)"
	@echo "  make figures     - regenerate figures only"
	@echo "  make report      - regenerate the report only (uses existing outputs/)"
	@echo "  make dashboard   - build the self-contained web dashboard (report/dashboard.html)"
	@echo "  make webapp      - build + serve the dashboard live at http://localhost:8000"
	@echo "  make screenshots - capture GUI + code screenshots into screenshots/ (needs Chromium)"
	@echo "  make test        - run the framework unit tests (must pass)"
	@echo "  make clean       - remove generated outputs/figures/report/evidence + caches"

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PY) run_analysis.py

figures:
	$(PY) -c "import config; from src import utils, statistics_engine, visualize, metrics, dataset_loader, correctness; import pandas as pd; df=pd.read_csv(config.METRICS_CSV); blob=utils.read_json(config.STATS_JSON); visualize.make_all_figures(df, blob)"

report:
	$(PY) -c "from src import report; report.build_report()"

dashboard:
	$(PY) -m src.webapp build

webapp:
	$(PY) -m src.webapp serve

screenshots:
	$(PY) tools/capture_screenshots.py
	$(PY) tools/capture_terminal.py

test:
	$(PY) -m pytest tests/ -v

clean:
	rm -rf outputs/* figures/* report/* evidence/*
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
	@echo "Cleaned generated artifacts (dataset and source code are untouched)."
