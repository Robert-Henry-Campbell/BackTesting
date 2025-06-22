#!/usr/bin/env python
import argparse
import pandas as pd
from portfolio import simulate_portfolio, calc_window_returns, boxplot_returns, name_run_output, identify_windows, simulate_window
import matplotlib as plt
import os
from datetime import datetime


"""
def main(args):
    portfolio = pd.read_csv(args.csv)
    for lev in args.leverage:
        portfolio = simulate_portfolio(portfolio, leverage=lev)

    portfolio.to_csv(name_run_output('portfolio',args.out, args.leverage, 'csv'))


    returns = calc_window_returns(
        portfolio,
        window_size=args.window,
        date_column=args.datecol,
        portfolio_columns=[f"portfolio_{lev}x" for lev in args.leverage],
    )
    returns.to_csv(name_run_output('returns',args.out, args.leverage, "csv"))

    if args.plot:
        fig = boxplot_returns(
            returns,
            [f"portfolio_{lev}x_returns" for lev in args.leverage],
            showfliers=False
        )
        fig.show()
        fig.savefig(name_run_output('returns',args.out, args.leverage, "png"))
        log_fig = boxplot_returns(returns, 
                                  [f"portfolio_{lev}x_returns" for lev in args.leverage],
                                  log = True)

    pass
"""


def main(args):
    data = pd.read_csv(args.csv)
    data.sort_values(args.datecol, inplace=True)

    windows = identify_windows(data, window_size=args.window)

    cols = [args.datecol] + [f"portfolio_{lev}x_returns" for lev in args.leverage]
    returns_df = pd.DataFrame(columns=cols)
    annualised_returns_df = pd.DataFrame(columns=cols)

    bust_counter = {lev: 0 for lev in args.leverage}

    for lev in args.leverage:
        for start_idx, end_idx in windows:
            # slice prices for this window (inclusive of end_idx)
            #prices = data.loc[start_idx:end_idx, args.pricecol]
            prices = data.iloc[start_idx:end_idx, data.columns.get_loc(args.pricecol)]

            # run the recursion
            V_path = simulate_window(prices, leverage=lev)

            # detect bust
            if (V_path <= 0).any():
                bust_counter[lev] += 1
                window_ret  = 0.0
                window_ann  = 0.0
            else:
                window_ret = V_path[-1] / V_path[0] - 1.0
                years      = (len(prices) - 1) / 12       # 12-month year
                window_ann = (V_path[-1] / V_path[0]) ** (1/years) - 1.0

            # label row by first date in window
            win_label = data.loc[start_idx, args.datecol]

            # append (or update) rows
            for df, value in ((returns_df, window_ret),
                              (annualised_returns_df, window_ann)):
                if win_label not in df[args.datecol].values:
                    df.loc[len(df), args.datecol] = win_label
                df.loc[df[args.datecol] == win_label,
                       f"portfolio_{lev}x_returns"] = value

    # -------------------------------------------------------------- #
    # 4. summary: bust proportions                                   #
    # -------------------------------------------------------------- #
    total_windows = len(windows)
    summary_df = pd.DataFrame({
        'leverage'   : list(bust_counter.keys()),
        'bust_ratio' : [bust_counter[lev] / total_windows
                        for lev in bust_counter]
    })

    # -------------------------------------------------------------- #
    # 5. persist results                                             #
    # -------------------------------------------------------------- #
    returns_df.to_csv(name_run_output('returns', args.out,
                                      args.leverage, "csv"), index=False)
    annualised_returns_df.to_csv(name_run_output('ann_returns', args.out,
                                                 args.leverage, "csv"),
                                 index=False)
    summary_df.to_csv(name_run_output('bust_summary', args.out,
                                      args.leverage, "csv"), index=False)

    if args.plot:
        fig = boxplot_returns(
            returns_df= returns_df,
            portfolio_cols= [f"portfolio_{lev}x_returns" for lev in args.leverage],
            showfliers=False
        )
        fig.show()
        fig.savefig(name_run_output('returns',args.out, args.leverage, "png"))
        log_fig = boxplot_returns(returns_df, 
                                  [f"portfolio_{lev}x_returns" for lev in args.leverage],
                                  log = True)
        log_fig.savefig(name_run_output('returns_log',args.out, args.leverage, "png"))    


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
