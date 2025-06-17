import pandas as pd
from pandas.testing import assert_frame_equal

from portfolio import calc_window_returns


def test_calc_window_returns_multiple_window_sizes():
    df = pd.DataFrame({
        'date': ['day1', 'day2', 'day3'],
        'portfolio1': [100, 200, 400],
    })

    # window size 1
    out1 = calc_window_returns(
        df,
        window_size=1,
        date_column='date',
        portfolio_columns=['portfolio1'],
    )
    expected1 = pd.DataFrame({
        'window_dates': [['day1', 'day2'], ['day2', 'day3']],
        'portfolio1_returns': [2.0, 2.0],
    })
    assert_frame_equal(out1, expected1, check_dtype=False)

    # window size 2
    out2 = calc_window_returns(
        df,
        window_size=2,
        date_column='date',
        portfolio_columns=['portfolio1'],
    )
    expected2 = pd.DataFrame({
        'window_dates': [['day1', 'day3']],
        'portfolio1_returns': [4.0],
    })
    assert_frame_equal(out2, expected2, check_dtype=False)

