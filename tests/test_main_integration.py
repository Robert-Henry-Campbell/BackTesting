# test_main_integration.py
import pandas as pd
import numpy as np
import pandas.testing as pdt
import matplotlib.pyplot as plt
import pytest
from argparse import Namespace
from pathlib import Path

# import the main you want to test
# import the CLI entry point under test
from portfolio.cli import main


# ---------- helper: independent leverage simulation ---------------- #
def naive_sim(prices, leverage, V0=1.0):
    V = [V0]
    for i in range(len(prices) - 1):
        Q_i = leverage * V[i] / prices[i]
        V.append(V[i] + Q_i * (prices[i + 1] - prices[i]))
    return np.array(V)


FREQ_TO_PERIODS = {"day": 252, "month": 12, "year": 1}


def build_expected_frames(df_prices, window_size, leverage, datecol, pricecol, freq):
    """Return returns_df, annual_df, summary_df calculated independently."""
    # 1. windows
    windows = [[i, i + window_size] for i in range(len(df_prices) - window_size)]

    # 2. returns containers
    returns_rows = []
    ann_rows = []
    busts = 0

    for start, end in windows:
        window_prices = df_prices.iloc[start : end + 1][pricecol]
        V_path = naive_sim(window_prices.values, leverage)
        busted = (V_path <= 0).any()
        if busted:
            busts += 1
            window_ret = 0.0
            window_ann = 0.0
        else:
            window_ret = V_path[-1] / V_path[0] - 1.0
            periods_per_year = FREQ_TO_PERIODS[freq]
            years = (len(window_prices) - 1) / periods_per_year
            window_ann = (V_path[-1] / V_path[0]) ** (1 / years) - 1.0

        win_label = df_prices.iloc[start][datecol]
        returns_rows.append({datecol: win_label, f"portfolio_{leverage}x": window_ret})
        ann_rows.append({datecol: win_label, f"portfolio_{leverage}x": window_ann})

    returns_df = pd.DataFrame(returns_rows)
    annual_df = pd.DataFrame(ann_rows)
    summary_df = pd.DataFrame(
        {"leverage": [leverage], "bust_ratio": [busts / len(windows)]}
    )
    # ensure identical column order
    ordered_cols = [datecol, f"portfolio_{leverage}x"]
    returns_df = returns_df[ordered_cols]
    annual_df = annual_df[ordered_cols]

    return returns_df, annual_df, summary_df


# ------------------------------ test -------------------------------- #
def test_main_integration(tmp_path: Path):
    # 1. create a small price CSV
    csv_path = tmp_path / "prices.csv"
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "settle": [100.0, 110.0, 100.0],
        }
    )
    df.to_csv(csv_path, index=False)

    # 2. build args object similar to CLI Namespace
    args = Namespace(
        csv=str(csv_path),
        window=1,
        leverage=[1.5],
        datecol="date",
        pricecol="settle",
        out=str(tmp_path),  # required by name_run_output but unused here
        freq="day",
    )

    # 3. call main (must return the three data frames)
    returns_df, ann_df, summary_df = main(args)

    # 4. compute expected frames independently
    exp_ret, exp_ann, exp_sum = build_expected_frames(
        df, window_size=1, leverage=1.5, datecol="date", pricecol="settle", freq="day"
    )

    # 5. assert equality (order-insensitive on index)
    pdt.assert_frame_equal(
        returns_df.sort_values("date").reset_index(drop=True),
        exp_ret.sort_values("date").reset_index(drop=True),
    )
    pdt.assert_frame_equal(
        ann_df.sort_values("date").reset_index(drop=True),
        exp_ann.sort_values("date").reset_index(drop=True),
    )
    pdt.assert_frame_equal(
        summary_df.reset_index(drop=True), exp_sum.reset_index(drop=True)
    )


def test_multiple_leverage_columns(tmp_path: Path):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=4, freq="D"),
            "price": [100.0, 105.0, 103.0, 106.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    args = Namespace(
        csv=str(csv),
        window=2,
        leverage=[1.0, 2.0, 3.0],
        datecol="date",
        pricecol="price",
        out=str(tmp_path),
        freq="day",
    )

    returns_df, ann_df, _ = main(args)

    expected_cols = ["date"] + [f"portfolio_{lev}x" for lev in args.leverage]
    assert list(returns_df.columns) == expected_cols
    assert list(ann_df.columns) == expected_cols
    assert not returns_df.isna().any().any()
    assert not ann_df.isna().any().any()


def test_unsorted_input_sorted_output(tmp_path: Path):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"]),
            "price": [120.0, 100.0, 110.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    args = Namespace(
        csv=str(csv),
        window=1,
        leverage=[1.0],
        datecol="date",
        pricecol="price",
        out=str(tmp_path),
        freq="day",
    )

    returns_df, ann_df, _ = main(args)

    sorted_df = df.sort_values("date").reset_index(drop=True)
    exp_ret, exp_ann, _ = build_expected_frames(
        sorted_df, 1, 1.0, "date", "price", "day"
    )
    pdt.assert_frame_equal(
        returns_df.sort_values("date").reset_index(drop=True),
        exp_ret.sort_values("date").reset_index(drop=True),
    )
    pdt.assert_frame_equal(
        ann_df.sort_values("date").reset_index(drop=True),
        exp_ann.sort_values("date").reset_index(drop=True),
    )


def test_plot_option_creates_files(tmp_path: Path, monkeypatch):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "price": [100.0, 101.0, 102.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    figs = []

    def dummy_boxplot_returns(*args, **kwargs):
        fig = plt.figure()
        figs.append(fig)
        return fig

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
        out=str(tmp_path),
        freq="day",
        plot=True,
    )

    main(args)

    assert len(figs) == 3
    for fname in ["returns.png", "returns_log.png", "returns_annualized.png"]:
        assert (tmp_path / fname).exists()


def test_bust_detection(tmp_path: Path):
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "price": [100.0, 90.0, 90.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    args = Namespace(
        csv=str(csv),
        window=1,
        leverage=[10.0],
        datecol="date",
        pricecol="price",
        out=str(tmp_path),
        freq="day",
    )

    returns_df, _, summary_df = main(args)

    assert returns_df.iloc[0, 1] == 0.0
    assert summary_df.loc[0, "bust_ratio"] == 0.5


def test_date_column_override(tmp_path: Path):
    df = pd.DataFrame(
        {
            "ts": ["2024-01", "2024-02", "2024-03"],
            "price": [100.0, 110.0, 120.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    args = Namespace(
        csv=str(csv),
        window=1,
        leverage=[1.0],
        datecol="ts",
        pricecol="price",
        out=str(tmp_path),
        freq="month",
    )

    returns_df, _, _ = main(args)

    assert list(returns_df.columns)[0] == "ts"
    assert returns_df["ts"].tolist() == ["2024-01", "2024-02"]


def test_missing_price_column(tmp_path: Path):
    df = pd.DataFrame(
        {
            "date": ["d1", "d2"],
            "price": [1.0, 2.0],
        }
    )
    csv = tmp_path / "prices.csv"
    df.to_csv(csv, index=False)

    args = Namespace(
        csv=str(csv),
        window=1,
        leverage=[1.0],
        datecol="date",
        pricecol="missing",  # does not exist
        out=str(tmp_path),
        freq="day",
    )

    with pytest.raises(KeyError):
        main(args)
