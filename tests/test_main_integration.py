# test_main_integration.py
import pandas as pd
import numpy as np
import pandas.testing as pdt
from argparse import Namespace
from pathlib import Path

# import the main you want to test
from your_package.your_module import main


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
