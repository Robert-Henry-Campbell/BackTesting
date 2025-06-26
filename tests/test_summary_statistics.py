import pandas as pd
import pandas.testing as pdt

from portfolio.report import summary_statistics


def test_summary_statistics_basic():
    returns_df = pd.DataFrame({
        "start": ["s1", "s2"],
        "end": ["e1", "e2"],
        "portfolio_1x": [0.1, 0.2],
        "portfolio_2x": [0.2, 0.4],
    })
    annual_df = pd.DataFrame({
        "start": ["s1", "s2"],
        "end": ["e1", "e2"],
        "portfolio_1x": [0.1, 0.2],
        "portfolio_2x": [0.2, 0.4],
    })
    bust_df = pd.DataFrame({"leverage": [1, 2], "bust_ratio": [0.0, 0.5]})
    sharpe = {"portfolio_1x": [1.0, 2.0], "portfolio_2x": [2.0, 3.0]}

    out = summary_statistics(returns_df, annual_df, bust_df, sharpe)

    expected = pd.DataFrame({
        "portfolio": ["portfolio_1x", "portfolio_2x"],
        "mean_total_return": [0.15, 0.3],
        "iqr_total_return": [0.05, 0.1],
        "mean_cagr": [0.15, 0.3],
        "std_cagr": [0.070710678, 0.141421356],
        "bust_ratio": [0.0, 0.5],
        "avg_sharpe": [1.5, 2.5],
        "min_total_return": [0.1, 0.2],
        "max_total_return": [0.2, 0.4],
    })

    pdt.assert_frame_equal(out.round(6), expected.round(6))
