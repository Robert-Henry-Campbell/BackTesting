#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest

