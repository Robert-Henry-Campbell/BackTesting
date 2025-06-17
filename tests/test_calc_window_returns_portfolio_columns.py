import pandas as pd
from pandas.testing import assert_frame_equal

from portfolio.core import calc_window_returns


def test_calc_window_returns_various_portfolio_columns():
    df = pd.DataFrame(
        {
            "date": ["d1", "d2", "d3"],
            "port1": [1.0, 2.0, 4.0],
            "port2": [100.0, 50.0, 25.0],
        }
    )

    expected_dates = [["d1", "d2"], ["d2", "d3"]]

    # portfolio_columns=None -> only window_dates
    out_none = calc_window_returns(df, window_size=1, date_column="date", portfolio_columns=None)
    expected_none = pd.DataFrame({"window_dates": expected_dates})
    assert_frame_equal(out_none, expected_none, check_dtype=False)

    # single portfolio column
    out_one = calc_window_returns(df, window_size=1, date_column="date", portfolio_columns=["port1"])
    expected_one = pd.DataFrame({
        "window_dates": expected_dates,
        "port1_returns": [2.0, 2.0],
    })
    assert_frame_equal(out_one, expected_one, check_dtype=False)

    # two portfolio columns
    out_two = calc_window_returns(
        df,
        window_size=1,
        date_column="date",
        portfolio_columns=["port1", "port2"],
    )
    expected_two = pd.DataFrame({
        "window_dates": expected_dates,
        "port1_returns": [2.0, 2.0],
        "port2_returns": [0.5, 0.5],
    })
    assert_frame_equal(out_two, expected_two, check_dtype=False)

