#!/usr/bin/env python
import argparse
import pandas as pd
from portfolio import simulate_portfolio, calc_window_returns, boxplot_returns

def main(args):
    df = pd.read_csv(args.csv)
    for lev in args.leverage:
        df = simulate_portfolio(df, leverage=lev)

    returns = calc_window_returns(
        df,
        window_size=args.window,
        date_column=args.datecol,
        portfolio_columns=[f"portfolio_{lev}x" for lev in args.leverage],
    )
    returns.to_csv(args.out, index=False)
    if args.plot:
        boxplot_returns(
            returns,
            [f"portfolio_{lev}x_returns" for lev in args.leverage],
        )
        plt.show()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv", help="Path to price CSV")
    p.add_argument("--window", type=int, default=252)
    p.add_argument("--leverage", nargs="+", type=float, default=[1.0, 2.0])
    p.add_argument("--datecol", default="date")
    p.add_argument("--out", default="rolling_returns.csv")
    p.add_argument("--plot", action="store_true")
    main(p.parse_args())
