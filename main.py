#!/usr/bin/env python
import argparse
import pandas as pd
from portfolio import simulate_portfolio, calc_window_returns, boxplot_returns, name_run_output
import matplotlib as plt
import os
from datetime import datetime

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
        )
        fig.show()
        fig.savefig(name_run_output('returns',args.out, args.leverage, "png"))
    pass

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv", help="Path to price CSV")
    p.add_argument("--window", type=int, default=252)
    p.add_argument("--leverage", nargs="+", type=float, default=[1.0, 2.0])
    p.add_argument("--datecol", default="date")
    p.add_argument("--out", default="rolling_returns.csv")
    p.add_argument("--plot", action="store_true")
    main(p.parse_args())
