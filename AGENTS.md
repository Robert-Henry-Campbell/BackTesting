# agents.md — Automation Guide for Codex & CI Runners

> **Project:** portfolio-project
> **Language:** Python ≥ 3.9  (uses `pyproject.toml`, `src/` layout)
> **Primary CLI:** `python main.py`

---

## 1 · Dependency Installation

```bash
# 1 Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate            # Windows: .\.venv\Scripts\Activate

# 2 Editable install — pulls runtime deps from pyproject.toml
pip install -e .

# 3 Install test tooling
pip install pytest
```

> 💡 *Common failure*: skipping step 2 leads to `ImportError: No module named 'pandas'` during tests.

---

## 2 · Project Entry Points

| Task                    | Command                                                            |
| ----------------------- | ------------------------------------------------------------------ |
| Run pipeline CLI        | `python main.py <csv_path> [--window N] [--leverage ...] [--plot]` |
| Execute unit + doctests | `pytest -q`                                                        |
| Lint (optional)         | `ruff src/ tests/`                                                 |
| Format                  | `black src/ tests/`                                                |

---

## 3 · Expected Directory Structure

```text
portfolio_project/
│
├─ src/portfolio/          ← import package
│   ├─ __init__.py
│   ├─ core.py             ← simulate_portfolio, identify_windows, calc_window_returns
│   └─ plots.py            ← plotting utilities (matplotlib)
│
├─ tests/                  ← pytest files (discoverable via test_*.py)
│   └─ test_smoke.py
│
├─ main.py                 ← CLI entry point
├─ pyproject.toml          ← build & dependency metadata (PEP 621)
├─ README.md
└─ .gitignore
```

---

## 4 · Testing Contract

* Doctests live in `src/portfolio/core.py`.
* Pytest must discover every file matching `test_*.py` under `tests/`.
* A passing suite means:

  * `pytest` exits with status 0
  * Smoke test returns the expected DataFrame
  * No `ImportError` for `pandas`, `numpy`, or `matplotlib`.

---

## 5 · CI‑Friendly One‑Liner

```bash
python -m venv .venv && \
source .venv/bin/activate && \
pip install -e . && \
pip install pytest && \
pytest -q
```

---

## 6 · Known Caveats

* **Spaces in paths** — wrap test paths in quotes:
  `pytest -q "tests/test_smoke.py"`
* **Headless CI** — set a non‑GUI backend for matplotlib:
  `export MPLBACKEND=Agg`

---

## 7 · Future Work (optional for agent)

1. Add `pre-commit` hooks (Black, Ruff, pytest).
2. Provide a GitHub Actions workflow (`python -m build`, `pytest`).
3. Extend the CLI with `--savefig <png>` and logging levels.

---

*End of file.*
