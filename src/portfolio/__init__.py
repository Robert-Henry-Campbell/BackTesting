# src/portfolio/__init__.py
"""
portfolio analysis package.
"""

from .core import (
    simulate_portfolio,
    identify_windows,
    calc_window_returns,
    simulate_window,
    detect_bust,
    simulate_leveraged_series,
    window_return,
    annualise,
)

from .report import (
    boxplot_returns,
)

from .utils import to_native, name_run_output

__all__ = [
    "simulate_portfolio",
    "identify_windows",
    "calc_window_returns",
    "detect_bust",
]

__version__ = "0.1.0"
