import pandas as pd
import pytest
from argparse import Namespace
from portfolio.cli import main


def test_dividend_portfolio_added(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "price": [100.0, 110.0, 105.0],
            "div": [0.0, 0.5, 0.5],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    args = Namespace(
        csv=str(csv),
        window=1,
        leverage=[1],
        datecol="date",
        pricecol="price",
        dividendcol="div",
        out=str(tmp_path),
        freq="day",
    )

    returns_df, _, _ = main(args)

    expected = [0.105, -0.04090909090909094]
    assert list(returns_df.columns) == ["date", "portfolio_1x", "1x_dividend"]
    assert returns_df["1x_dividend"].tolist() == pytest.approx(expected)
