import pandas as pd
import pandas.testing as pdt
from argparse import Namespace

from portfolio.cli import main
from test_main_integration import naive_sim


def test_underlying_portfolio_added(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "price": [100.0, 110.0, 100.0],
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
        out=str(tmp_path),
        freq="day",
        underlying=True,
    )

    returns_df, _, _ = main(args)
    start_col = f"start_{args.datecol}"
    end_col = f"end_{args.datecol}"

    prices = df["price"].tolist()
    path = naive_sim(prices, 1.0)
    exp_port = [path[1] / path[0] - 1.0, path[2] / path[1] - 1.0]
    underlying_returns = [prices[1] - prices[0], prices[2] - prices[1]]
    expected = pd.DataFrame(
        {
            start_col: df["date"].iloc[:2].dt.strftime("%Y-%m-%d").tolist(),
            end_col: df["date"].iloc[1:3].dt.strftime("%Y-%m-%d").tolist(),
            "portfolio_1x": exp_port,
            "underlying": underlying_returns,
        }
    )

    pdt.assert_frame_equal(
        returns_df.sort_values(start_col).reset_index(drop=True),
        expected.sort_values(start_col).reset_index(drop=True),
    )
    assert "underlying" in returns_df.columns
