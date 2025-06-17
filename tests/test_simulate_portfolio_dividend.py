import pandas as pd
import pytest

from portfolio import simulate_portfolio


def test_simulate_portfolio_raises_for_dividend_true():
    df = pd.DataFrame({'sp_real_price': [100, 110]})
    with pytest.raises(NotImplementedError):
        simulate_portfolio(df, leverage=1, dividend=True)


def test_simulate_portfolio_no_dividend_runs():
    df = pd.DataFrame({'sp_real_price': [100, 110]})
    out = simulate_portfolio(df, leverage=1, dividend=False)
    assert out['portfolio_1x'].tolist() == [1.0, 1.1]
