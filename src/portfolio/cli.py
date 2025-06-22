import pandas as pd
import matplotlib.pyplot as plt

from .core import (
    identify_windows,
    simulate_window,
    detect_bust,
    simulate_window_with_dividends,
)
from .report import boxplot_returns
from .utils import name_run_output

FREQ_TO_PERIODS = {
    "day": 252,
    "month": 12,
    "year": 1,
}


def main(args):
    data = pd.read_csv(args.csv)
    data.sort_values(args.datecol, inplace=True)

    periods_per_year = FREQ_TO_PERIODS.get(args.freq, 12)

    windows = identify_windows(data, window_size=args.window)

    has_dividend = getattr(args, "dividendcol", None) is not None

    cols = [args.datecol]
    if has_dividend:
        cols.append("1x_dividend")
    cols += [f"portfolio_{lev}x" for lev in args.leverage]
    returns_df = pd.DataFrame(columns=cols)
    annualised_returns_df = pd.DataFrame(columns=cols)

    bust_counter = {lev: 0 for lev in args.leverage}

    for lev in args.leverage:
        for start_idx, end_idx in windows:
            prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]

            V_path = simulate_window(prices, leverage=lev)

            if detect_bust(V_path):
                bust_counter[lev] += 1
                window_ret = 0.0
                window_ann = 0.0
            else:
                window_ret = V_path[-1] / V_path[0] - 1.0
                years = (len(prices) - 1) / periods_per_year
                window_ann = (V_path[-1] / V_path[0]) ** (1 / years) - 1.0

            win_label = data.loc[start_idx, args.datecol]

            for df, value in (
                (returns_df, window_ret),
                (annualised_returns_df, window_ann),
            ):
                if win_label not in df[args.datecol].values:
                    df.loc[len(df), args.datecol] = win_label

                df.loc[df[args.datecol] == win_label, f"portfolio_{lev}x"] = value

    if has_dividend:
        for start_idx, end_idx in windows:
            prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]
            divs = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.dividendcol),
            ].copy()
            divs.iloc[0] = 0.0

            V_path = simulate_window_with_dividends(prices, divs)
            window_ret = V_path[-1] / V_path[0] - 1.0
            years = (len(prices) - 1) / periods_per_year
            window_ann = (V_path[-1] / V_path[0]) ** (1 / years) - 1.0

            win_label = data.loc[start_idx, args.datecol]

            for df, value in (
                (returns_df, window_ret),
                (annualised_returns_df, window_ann),
            ):
                if win_label not in df[args.datecol].values:
                    df.loc[len(df), args.datecol] = win_label

                df.loc[df[args.datecol] == win_label, "1x_dividend"] = value

    returns_df[args.datecol] = pd.to_datetime(returns_df[args.datecol])
    annualised_returns_df[args.datecol] = pd.to_datetime(
        annualised_returns_df[args.datecol]
    )

    value_cols = [f"portfolio_{lev}x" for lev in args.leverage]
    if has_dividend:
        value_cols = ["1x_dividend"] + value_cols
    returns_df[value_cols] = returns_df[value_cols].astype(float)
    annualised_returns_df[value_cols] = annualised_returns_df[value_cols].astype(float)

    total_windows = len(windows)
    summary_df = pd.DataFrame(
        {
            "leverage": list(bust_counter.keys()),
            "bust_ratio": [bust_counter[lev] / total_windows for lev in bust_counter],
        }
    )

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


__all__ = ["main"]
