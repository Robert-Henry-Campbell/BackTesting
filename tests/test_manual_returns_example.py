import pandas as pd
import pandas.testing as pdt
from argparse import Namespace

from portfolio.cli import main


def test_manual_returns_single_window(tmp_path):
    # create example CSV
    df = pd.DataFrame(
        {
            "date": ["2025-01", "2025-02", "2025-03", "2025-04"],
            "sp_real_price": [100.0, 104.0, 97.76, 86.0288],
        }
    )
    csv_path = tmp_path / "prices.csv"
    df.to_csv(csv_path, index=False)

    args = Namespace(
        csv=str(csv_path),
        window=len(df) - 1,  # single window covering all rows
        leverage=[1, 2, 10],
        datecol="date",
        pricecol="sp_real_price",
        out=str(tmp_path),
        freq="month",
    )

    returns_df, _, summary_df = main(args)
    start_col = f"start_{args.datecol}"
    end_col = f"end_{args.datecol}"

    expected = pd.DataFrame(
        {
            start_col: ["2025-01"],
            end_col: ["2025-04"],
            "portfolio_1x": [-0.139712],
            "portfolio_2x": [-0.277696],
            "portfolio_10x": [0.0],
        }
    )

    pdt.assert_frame_equal(returns_df.reset_index(drop=True), expected)

    expected_summary = pd.DataFrame(
        {
            "leverage": [1, 2, 10],
            "bust_ratio": [0.0, 0.0, 1.0],
        }
    )

    pdt.assert_frame_equal(
        summary_df.sort_values("leverage").reset_index(drop=True),
        expected_summary,
    )
