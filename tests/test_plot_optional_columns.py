import pandas as pd
import matplotlib.pyplot as plt
from argparse import Namespace

from portfolio.cli import main


def test_plot_includes_optional_cols(tmp_path, monkeypatch):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "price": [100.0, 101.0, 102.0],
            "div": [0.0, 1.0, 1.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    called_cols = []

    def dummy_boxplot_returns(*args, **kwargs):
        if args:
            # first positional is returns_df, second is portfolio_cols
            portfolio_cols = args[1]
        else:
            portfolio_cols = kwargs.get("portfolio_cols")
        called_cols.append(portfolio_cols)
        return plt.figure()

    monkeypatch.setattr("portfolio.cli.boxplot_returns", dummy_boxplot_returns)
    monkeypatch.setattr(
        "portfolio.cli.name_run_output",
        lambda name, out, lev, ftype: str(tmp_path / f"{name}.{ftype}"),
    )

    args = Namespace(
        csv=str(csv),
        window=1,
        leverage=[1.0],
        datecol="date",
        pricecol="price",
        dividendcol="div",
        underlying=True,
        out=str(tmp_path),
        freq="day",
        plot=True,
    )

    main(args)

    expected = ["portfolio_1.0x", "underlying", "1x_dividend"]
    assert all(cols == expected for cols in called_cols)
