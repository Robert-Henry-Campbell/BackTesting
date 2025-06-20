import pandas as pd
from portfolio import calc_window_returns


def test_calc_window_returns_custom_date_column():
    df = pd.DataFrame(
        {
            "timestamp": ["t1", "t2", "t3"],
            "portfolio1": [100, 200, 300],
        }
    )

    out = calc_window_returns(
        df,
        window_size=1,
        date_column="timestamp",
        portfolio_columns=["portfolio1"],
    )

    expected_dates = [["t1", "t2"], ["t2", "t3"]]
    assert out["window_dates"].tolist() == expected_dates

