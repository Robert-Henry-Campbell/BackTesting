import pandas as pd
import pandas.testing as pdt
from argparse import Namespace

from portfolio.cli import main
from test_main_integration import naive_sim


def test_dividend_portfolio_added(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "price": [100.0, 110.0, 100.0],
            "div": [0.0, 1.0, 1.0],
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

    prices = df["price"].tolist()
    divs = df["div"].tolist()
    path = naive_sim(prices, 1.0)
    exp_port = [path[1] / path[0] - 1.0, path[2] / path[1] - 1.0]
    div_returns = [
        (prices[1] - prices[0] + divs[1]) / prices[0],
        (prices[2] - prices[1] + divs[2]) / prices[1],
    ]
    expected = pd.DataFrame(
        {
            "date": df["date"].iloc[:2].tolist(),
            "portfolio_1x": exp_port,
            "1x_dividend": div_returns,
        }
    )

    pdt.assert_frame_equal(
        returns_df.sort_values("date").reset_index(drop=True),
        expected.sort_values("date").reset_index(drop=True),
    )
    assert "1x_dividend" in returns_df.columns
