import pandas as pd
import pytest

from portfolio import simulate_portfolio


PRICE_DATA = [100, 110, 120]


@pytest.mark.parametrize("leverage", [0.5, 1, 2, 3, -1])
def test_simulate_portfolio_various_leverage(leverage):
    df = pd.DataFrame({"sp_real_price": PRICE_DATA})
    out = simulate_portfolio(df, leverage=leverage)
    portfolio_col = f"portfolio_{leverage}x"

    expected = [1.0]
    for i in range(1, len(PRICE_DATA)):
        curr = PRICE_DATA[i]
        base = PRICE_DATA[i - 1]
        expected.append(expected[-1] * (curr / base) ** leverage)

    assert out[portfolio_col].tolist() == pytest.approx(expected)
