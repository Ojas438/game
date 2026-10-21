#!/usr/bin/env bash
# Runs the whole project from start to finish.
set -e
cd "$(dirname "$0")"
python 01_get_data.py
python 02_make_labels.py
python 03_run_experiment.py
python 04_make_graphs.py
python 05_export_demo.py
if command -v node >/dev/null; then node check_demo.js; fi
