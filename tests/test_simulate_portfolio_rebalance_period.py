import pandas as pd
import pytest

from portfolio import simulate_portfolio


def manual_portfolio(prices, leverage, rebalance_period):
    path = [1.0]
    last_rebalance = 0
    for i in range(1, len(prices)):
        if i - last_rebalance == rebalance_period:
            base = prices[last_rebalance]
            curr = prices[i]
            path.append(path[last_rebalance] * ((curr / base) ** leverage))
            last_rebalance = i
        else:
            path.append(path[i - 1])
    return path


@pytest.mark.parametrize("period", [1, 2, 10])
def test_simulate_portfolio_rebalance_period(period):
    prices = [100, 110, 120, 130]
    df = pd.DataFrame({"sp_real_price": prices})
    out = simulate_portfolio(df, leverage=2, rebalance_period=period)
    expected = manual_portfolio(prices, leverage=2, rebalance_period=period)
    assert out["portfolio_2x"].tolist() == expected
