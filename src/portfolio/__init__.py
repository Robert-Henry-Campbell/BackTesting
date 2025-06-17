# src/portfolio/__init__.py
"""
portfolio analysis package.
"""

from .core import (
    simulate_portfolio,
    identify_windows,
    calc_window_returns,
)

from .report import(
        boxplot_returns,
)

__all__ = [
    "simulate_portfolio",
    "identify_windows",
    "calc_window_returns",
]

__version__ = "0.1.0"
