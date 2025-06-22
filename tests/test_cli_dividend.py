import pandas as pd
import pandas.testing as pdt
from argparse import Namespace

from your_package.your_module import main


def naive_div(prices, dividends):
    v = [1.0]
    for i in range(len(prices) - 1):
        r = (prices[i + 1] - prices[i] + dividends[i + 1]) / prices[i]
        v.append(v[-1] * (1 + r))
    return v


def test_main_adds_dividend_portfolio(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "settle": [100.0, 110.0, 100.0],
            "div": [0.0, 1.0, 1.0],
        }
    )
    csv_path = tmp_path / "prices.csv"
    df.to_csv(csv_path, index=False)

    args = Namespace(
        csv=str(csv_path),
        window=1,
        leverage=[1.0],
        datecol="date",
        pricecol="settle",
        dividendcol="div",
        out=str(tmp_path),
        freq="day",
    )

    returns_df, ann_df, _ = main(args)

    prices0 = df["settle"].values
    divs0 = df["div"].values
    # expected dividend returns via naive simulation
    v_div = naive_div(prices0[:2], divs0[:2])
    ret0 = v_div[-1] / v_div[0] - 1.0
    v_div = naive_div(prices0[1:], divs0[1:])
    ret1 = v_div[-1] / v_div[0] - 1.0

    expected = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "1x_dividend": [ret0, ret1],
            "portfolio_1.0x": [0.1, -0.09090909090909094],
        }
    )

    pdt.assert_frame_equal(
        returns_df.sort_values("date").reset_index(drop=True),
        expected.sort_values("date").reset_index(drop=True),
    )

    # annualised check: same procedure using naive_div
    years = 1 / 252  # with freq "day" and window size 1 -> years = 1/252
    v_div = naive_div(prices0[:2], divs0[:2])
    ann0 = (v_div[-1] / v_div[0]) ** (1 / years) - 1.0
    v_div = naive_div(prices0[1:], divs0[1:])
    ann1 = (v_div[-1] / v_div[0]) ** (1 / years) - 1.0

    expected_ann = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "1x_dividend": [ann0, ann1],
            "portfolio_1.0x": ann_df["portfolio_1.0x"].tolist(),
        }
    )
    pdt.assert_frame_equal(
        ann_df.sort_values("date").reset_index(drop=True)[
            ["date", "1x_dividend", "portfolio_1.0x"]
        ],
        expected_ann.sort_values("date").reset_index(drop=True),
        check_dtype=False,
    )
