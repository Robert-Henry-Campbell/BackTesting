#!/usr/bin/env python
import argparse
import pandas as pd
from portfolio import (
    simulate_portfolio,
    calc_window_returns,
    boxplot_returns,
    name_run_output,
    identify_windows,
    simulate_window,
    detect_bust,
)
import matplotlib.pyplot as plt
import os
from datetime import datetime


def main(args):
    data = pd.read_csv(args.csv)
    data.sort_values(args.datecol, inplace=True)

    windows = identify_windows(data, window_size=args.window)

    cols = [args.datecol] + [f"portfolio_{lev}x" for lev in args.leverage]
    returns_df = pd.DataFrame(columns=cols)
    annualised_returns_df = pd.DataFrame(columns=cols)

    bust_counter = {lev: 0 for lev in args.leverage}

    for lev in args.leverage:
        for start_idx, end_idx in windows:
            # slice prices for this window (inclusive of end_idx)
            # prices = data.loc[start_idx:end_idx, args.pricecol]
            prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]

            # run the recursion
            V_path = simulate_window(prices, leverage=lev)

            # detect bust
            if detect_bust(V_path):
                bust_counter[lev] += 1
                window_ret = 0.0
                window_ann = 0.0
            else:
                window_ret = V_path[-1] / V_path[0] - 1.0
                years = (len(prices) - 1) / 252
                window_ann = (V_path[-1] / V_path[0]) ** (1 / years) - 1.0

            # label row by first date in window
            win_label = data.loc[start_idx, args.datecol]

            # append (or update) rows
            for df, value in (
                (returns_df, window_ret),
                (annualised_returns_df, window_ann),
            ):
                if win_label not in df[args.datecol].values:
                    df.loc[len(df), args.datecol] = win_label

                df.loc[df[args.datecol] == win_label, f"portfolio_{lev}x"] = value

    # ensure date column retains datetime dtype
    returns_df[args.datecol] = pd.to_datetime(returns_df[args.datecol])
    annualised_returns_df[args.datecol] = pd.to_datetime(
        annualised_returns_df[args.datecol]
    )

    value_cols = [f"portfolio_{lev}x" for lev in args.leverage]
    returns_df[value_cols] = returns_df[value_cols].astype(float)
    annualised_returns_df[value_cols] = annualised_returns_df[value_cols].astype(float)

    # -------------------------------------------------------------- #
    # 4. summary: bust proportions                                   #
    # -------------------------------------------------------------- #
    total_windows = len(windows)
    summary_df = pd.DataFrame(
        {
            "leverage": list(bust_counter.keys()),
            "bust_ratio": [bust_counter[lev] / total_windows for lev in bust_counter],
        }
    )

    # -------------------------------------------------------------- #
    # 5. persist results                                             #
    # -------------------------------------------------------------- #
    returns_df.to_csv(
        name_run_output("returns", args.out, args.leverage, "csv"), index=False
    )
    annualised_returns_df.to_csv(
        name_run_output("ann_returns", args.out, args.leverage, "csv"), index=False
    )
    summary_df.to_csv(
        name_run_output("bust_summary", args.out, args.leverage, "csv"), index=False
    )

    if getattr(args, "plot", False):
        fig = boxplot_returns(
            returns_df=returns_df,
            portfolio_cols=[f"portfolio_{lev}x" for lev in args.leverage],
            showfliers=False,
        )
        fig.show()
        fig.savefig(name_run_output("returns", args.out, args.leverage, "png"))
        plt.close(fig)

        log_fig = boxplot_returns(
            returns_df, [f"portfolio_{lev}x" for lev in args.leverage], log=True
        )
        log_fig.savefig(name_run_output("returns_log", args.out, args.leverage, "png"))
        plt.close(log_fig)

        ann_fig = boxplot_returns(
            returns_df=annualised_returns_df,
            portfolio_cols=[f"portfolio_{lev}x" for lev in args.leverage],
            showfliers=False,
            label="annualized return",
        )
        ann_fig.savefig(
            name_run_output("returns_annualized", args.out, args.leverage, "png")
        )
        plt.close(ann_fig)
    return returns_df, annualised_returns_df, summary_df


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv", help="Path to price CSV")
    p.add_argument("--window", type=int, default=252)
    p.add_argument("--leverage", nargs="+", type=float, default=[1.0, 2.0])
    p.add_argument("--datecol", default="date")
    p.add_argument("--pricecol", default="sp_real_price")
    p.add_argument("--out", default="rolling_returns.csv")
    p.add_argument("--plot", action="store_true")
    main(p.parse_args())
