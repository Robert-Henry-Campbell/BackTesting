import pandas as pd
import matplotlib.pyplot as plt

from .core import (
    identify_windows,
    simulate_window,
    simulate_window_dividend,
    detect_bust,
    underlying_return,
)
from .report import boxplot_returns
from .utils import name_run_output

FREQ_TO_PERIODS = {
    "day": 252,
    "month": 12,
    "year": 1,
}


def _format_label(value, freq):
    ts = pd.to_datetime(value)
    if freq == "year":
        return ts.strftime("%Y")
    if freq == "month":
        return ts.strftime("%Y-%m")
    return ts.strftime("%Y-%m-%d")


def main(args):
    data = pd.read_csv(args.csv)
    data.sort_values(args.datecol, inplace=True)
    data.reset_index(drop=True, inplace=True)

    periods_per_year = FREQ_TO_PERIODS.get(args.freq, 12)

    windows = identify_windows(data, window_size=args.window)

    dividend_column = getattr(args, "dividendcol", None)
    include_underlying = getattr(args, "underlying", False)

    start_col = f"start_{args.datecol}"
    end_col = f"end_{args.datecol}"
    cols = [start_col, end_col] + [f"portfolio_{lev}x" for lev in args.leverage]
    if include_underlying:
        cols.append("underlying")
    if dividend_column is not None:
        cols.append("1x_dividend")
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

            start_label = _format_label(data.iloc[start_idx][args.datecol], args.freq)
            end_label = _format_label(data.iloc[end_idx][args.datecol], args.freq)

            for df, value in (
                (returns_df, window_ret),
                (annualised_returns_df, window_ann),
            ):
                mask = (df[start_col] == start_label) & (df[end_col] == end_label)
                if not mask.any():
                    df.loc[len(df), [start_col, end_col]] = [start_label, end_label]
                    mask = (df[start_col] == start_label) & (df[end_col] == end_label)

                df.loc[mask, f"portfolio_{lev}x"] = value

    if include_underlying:
        for start_idx, end_idx in windows:
            prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]
            window_ret = underlying_return(prices)
            years = (len(prices) - 1) / periods_per_year
            window_ann = window_ret / years if years else 0.0

            start_label = _format_label(data.iloc[start_idx][args.datecol], args.freq)
            end_label = _format_label(data.iloc[end_idx][args.datecol], args.freq)

            for df, value in (
                (returns_df, window_ret),
                (annualised_returns_df, window_ann),
            ):
                mask = (df[start_col] == start_label) & (df[end_col] == end_label)
                if not mask.any():
                    df.loc[len(df), [start_col, end_col]] = [start_label, end_label]
                    mask = (df[start_col] == start_label) & (df[end_col] == end_label)

                df.loc[mask, "underlying"] = value

    if dividend_column is not None:
        for start_idx, end_idx in windows:
            prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]
            divs = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(dividend_column),
            ]
            V_path = simulate_window_dividend(prices, divs)
            window_ret = V_path[-1] / V_path[0] - 1.0
            years = (len(prices) - 1) / periods_per_year
            window_ann = (V_path[-1] / V_path[0]) ** (1 / years) - 1.0

            start_label = _format_label(data.iloc[start_idx][args.datecol], args.freq)
            end_label = _format_label(data.iloc[end_idx][args.datecol], args.freq)

            for df, value in (
                (returns_df, window_ret),
                (annualised_returns_df, window_ann),
            ):
                mask = (df[start_col] == start_label) & (df[end_col] == end_label)
                if not mask.any():
                    df.loc[len(df), [start_col, end_col]] = [start_label, end_label]
                    mask = (df[start_col] == start_label) & (df[end_col] == end_label)

                df.loc[mask, "1x_dividend"] = value

    value_cols = [f"portfolio_{lev}x" for lev in args.leverage]
    if include_underlying:
        value_cols.append("underlying")
    if dividend_column is not None:
        value_cols.append("1x_dividend")
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
        plot_cols = [f"portfolio_{lev}x" for lev in args.leverage]
        if include_underlying:
            plot_cols.append("underlying")
        if dividend_column is not None:
            plot_cols.append("1x_dividend")

        fig = boxplot_returns(
            returns_df=returns_df,
            portfolio_cols=plot_cols,
            showfliers=False,
        )
        fig.show()
        fig.savefig(name_run_output("returns", args.out, args.leverage, "png"))
        plt.close(fig)

        log_fig = boxplot_returns(returns_df, plot_cols, log=True)
        log_fig.savefig(name_run_output("returns_log", args.out, args.leverage, "png"))
        plt.close(log_fig)

        ann_fig = boxplot_returns(
            returns_df=annualised_returns_df,
            portfolio_cols=plot_cols,
            showfliers=False,
            label="annualized return",
        )
        ann_fig.savefig(
            name_run_output("returns_annualized", args.out, args.leverage, "png")
        )
        plt.close(ann_fig)
    return returns_df, annualised_returns_df, summary_df


__all__ = ["main"]
