
# Portfolio-Project 📈

Simulate leveraged S&P real-price portfolios, slice them into rolling windows, and
analyse cumulative returns—ready for research, dashboards, or quant pipelines.

---

## Features
| Function | Purpose |
|----------|---------|
| `simulate_portfolio` | Apply arbitrary leverage, optional dividend logic, and periodic rebalancing to an `sp_real_price` column. |
| `identify_windows`   | Generate inclusive-exclusive index pairs for every sliding window of length *N*. |
| `calc_window_returns`| Compute cumulative returns for each window across one or many portfolio columns. |
| *(CLI)* `main.py`    | One-shot command-line runner: read CSV → simulate → window → export CSV / plot. |

---

## Quick start

```bash
# 1  Clone
git clone https://github.com/<your-org>/portfolio-project.git
cd portfolio-project

# 2  Create & activate a virtual env  (PowerShell shown; adjust for your shell)
python -m venv .venv
.\.venv\Scripts\Activate

# 3  Install package + runtime deps (editable)
pip install -e .

# 4  Run doctests & unit tests
pip install pytest
pytest -q

# 5  Run the CLI on your own CSV
python main.py data/sp500_real.csv --window 252 --leverage 1 2 --plot




portfolio_project/
│
├─ src/
│  └─ portfolio/              ← import package  (namespace: portfolio.*)
│     ├─ __init__.py
│     ├─ core.py              ← simulate_portfolio, identify_windows, calc_window_returns
│     └─ plots.py             ← boxplot_returns & any future visualisation
│
├─ tests/
│  ├─ test_unit.py            ← fast unit tests (pytest)
│  └─ test_pipeline.py        ← integration “full run”
│
├─ data/                      ← raw CSVs (never committed if large)
│
├─ main.py                    ← CLI / entry point
│
├─ pyproject.toml             ← build & tooling metadata (PEP 621)
├─ requirements.txt           ← pinned runtime deps (if not using Poetry)
├─ README.md
└─ .gitignore
