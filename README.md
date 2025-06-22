
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

# 2  Set up the Python environment
bash scripts/setup_env.sh

# 3  Run doctests & unit tests
pytest -q

# 4  Run the CLI on your own CSV
python main.py data/sp500_real.csv --window 252 --leverage 1 2 --freq month --plot
```

## Command-Line Interface (CLI) Usage

You can run the main analysis script via:

```bash
python main.py <csv_path> [options]

#example run:
python main.py data/processed/data_for_futures.csv --window 240 --leverage 0.5 0.75 1.0 1.25 1.5 1.75 2.0 2.25 2.50 2.75 3.0 --out data/outputs/
```

### Required Positional Argument

- `<csv_path>`  
  Path to the input CSV file containing at least a `sp_real_price` column and a `date` column.  
  Example: `data/sp500_real.csv`

### Optional Arguments

- `--window <int>`  
  Size of the rolling window (in rows = months).  
  **Default:** `252`

- `--leverage <float float ...>`  
  One or more leverage levels to simulate.  
  Example: `--leverage 1.0 2.0 3.0`  
  **Default:** `1.0 2.0`

- `--datecol <str>`
  Name of the column to use for date labels.
  **Default:** `"date"`

- `--freq {day,month,year}`
  Frequency of the input data. Determines how annualised returns are calculated.
  **Default:** `month`


- `--out <filename>`  
  Output path for the CSV containing rolling returns.  
  **Default:** `rolling_returns.csv` (written to current directory)

- `--plot`  
  If included, generates a boxplot of returns for each portfolio and displays it using `matplotlib.pyplot.show()`.

### Example Usage

```bash
python main.py data/sp500_real.csv --window 252 --leverage 1.0 2.0 3.0 --freq month --plot --out results/returns.csv
```

## Project Layout

```
portfolio_project/
│
├─ data/
│  ├─ raw/
│  │  └─ shiller_longrun_market_data.xls       ← unmodified original data
│  ├─ outputs/
│  └─ processed/
│     └─ data_for_futures.csv                  ← cleaned data used in analysis
│
├─ notebooks/
│  ├─ backtesting_0.1.ipynb
│  ├─ backtesting_0.2.ipynb
│  ├─ backtesting_0.3.py
│  ├─ dataset_cleanup.ipynb
│  └─ smoke_run_0.1.py                         ← manual tests / sandboxing
│
├─ notes/
│  └─ futures modelling notes.gdoc             ← reference notes
│
├─ src/
│  └─ portfolio/                               ← importable package
│     ├─ __init__.py
│     ├─ core.py                               ← simulate_portfolio, identify_windows, calc_window_returns
│     ├─ plots.py                              ← boxplot_returns and visualisation utilities
│     └─ report.py                             ← boxplot_returns and visualisation utilities
│
├─ tests/
│  ├─ test_smoke.py                            ← integration test matching the manual run
│  ├─ blank.txt                                ← placeholder / temp
│  └─ __pycache__/                             ← ignored bytecode cache
│
├─ main.py                                     ← CLI entry point
├─ pyproject.toml                              ← packaging & dependency metadata (PEP 621)
├─ dev-requirements.txt                        ← test/lint tooling (pytest, ruff, black, etc.)
├─ LICENSE
├─ .gitignore
└─ README.md
```


## testing

if your directory contains spaces, bash and powershell will mangle test discovery. you must manually point to the test directory using:
```bash
pytest -q tests/test_smoke.py
```
