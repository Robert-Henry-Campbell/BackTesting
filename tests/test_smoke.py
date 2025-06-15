"""
Smoke-test for the full pipeline.

We feed a tiny three-row price series, run it through every public function,
and assert that the outputs match the values printed during the manual run:

    Raw prices:                 1 → 2 → 1
    portfolio_1x path:          1.0 → 2.0 → 1.0
    windows (size 1):           [[0,1], [1,2]]
    window returns:             2.0 , 0.5
"""

import pandas as pd
from pandas.testing import assert_frame_equal

from portfolio.core import (
    simulate_portfolio,
    identify_windows,
    calc_window_returns,
)




def test_smoke_price_1_2_1_window_size_1():
    # ------------------------------------------------------------------
    # 1  Synthetic price data
    # ------------------------------------------------------------------
    df = pd.DataFrame(
        {
            "date": ["day1", "day2", "day3"],
            "sp_real_price": [1, 2, 1],
        }
    )

    # ------------------------------------------------------------------
    # 2  Simulate a 1× portfolio (rebalance every row)
    #     Expected portfolio_1x column: 1.0, 2.0, 1.0
    # ------------------------------------------------------------------
    df = simulate_portfolio(df, leverage=1)
    assert df["portfolio_1x"].tolist() == [1.0, 2.0, 1.0]

    # ------------------------------------------------------------------
    # 3  Sliding windows of length 1
    #     Our implementation returns inclusive-exclusive pairs:
    #     [[0,1], [1,2]]
    # ------------------------------------------------------------------
    windows = identify_windows(df, 1)
    assert windows == [[0, 1], [1, 2]]

    # ------------------------------------------------------------------
    # 4  Rolling-window returns
    #     • window 0-1: 2 / 1  = 2.0
    #     • window 1-2: 1 / 2  = 0.5
    # ------------------------------------------------------------------
    out = calc_window_returns(
        df,
        window_size=1,
        date_column="date",
        portfolio_columns=["portfolio_1x"],
    )

    expected = pd.DataFrame(
        {
            "window_dates": [["day1", "day2"], ["day2", "day3"]],
            "portfolio_1x_returns": [2.0, 0.5],
        }
    )

    assert_frame_equal(out, expected, check_dtype=False)
