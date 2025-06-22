"""Tests mirroring the doctest examples in :mod:`portfolio.core`."""

import pandas as pd
from portfolio import simulate_portfolio, calc_window_returns


def test_simulate_portfolio_doctest_example():
    df = pd.DataFrame({"sp_real_price": [100, 110]})
    test_leverage = 1
    out = simulate_portfolio(df, leverage=test_leverage)
    assert out[f"portfolio_{test_leverage}x"].tolist() == [1.0, 1.1]


def test_calc_window_returns_doctest_example():
    df = pd.DataFrame(
        {
            "date": ["day1", "day2", "day3"],
            "portfolio1": [100, 200, 2000],
            "portfolio2": [100, 50, 5],
        }
    )
    out = calc_window_returns(
        df,
        window_size=1,
        date_column="date",
        portfolio_columns=["portfolio1", "portfolio2"],
    )
    expected = pd.DataFrame(
        {
            "window_dates": [["day1", "day2"], ["day2", "day3"]],
            "portfolio1_returns": [2.0, 10.0],
            "portfolio2_returns": [0.5, 0.1],
        }
    )
    assert out.equals(expected)
