import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from .core import (
    identify_windows,
    simulate_window,
    simulate_window_dividend,
    detect_bust,
    underlying_return,
)
from .report import boxplot_returns, summary_statistics
from .utils import name_run_output

FREQ_TO_PERIODS = {
    "day": 252,
    "month": 12,
    "year": 1,
}


def _format_label(value, freq):
    """Return ``value`` unchanged.

    This CLI previously attempted to parse dates and format them according
    to ``freq``. For full generality we now keep whatever objects appear in
    the date column so that arbitrary strings are supported.
    """

    return value


def main(args):
    data = pd.read_csv(args.csv)

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
    sharpe_tracker = {f"portfolio_{lev}x": [] for lev in args.leverage}
    if include_underlying:
        sharpe_tracker["underlying"] = []
    if dividend_column is not None:
        sharpe_tracker["1x_dividend"] = []

    for lev in args.leverage:
        for start_idx, end_idx in windows:
            prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]

            V_path = simulate_window(prices, leverage=lev)
            period_returns = np.diff(V_path) / V_path[:-1]

            if detect_bust(V_path):
                bust_counter[lev] += 1
                window_ret = 0.0
                window_ann = 0.0
                sharpe_tracker[f"portfolio_{lev}x"].append(0.0)
            else:
                window_ret = V_path[-1] / V_path[0] - 1.0
                years = (len(prices) - 1) / periods_per_year
                window_ann = (V_path[-1] / V_path[0]) ** (1 / years) - 1.0
                std = period_returns.std(ddof=1)
                if std == 0 or np.isnan(std):
                    sr = 0.0
                else:
                    sr = period_returns.mean() / std * np.sqrt(periods_per_year)
                sharpe_tracker[f"portfolio_{lev}x"].append(sr)

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
            window_prices = data.iloc[
                start_idx : end_idx + 1,
                data.columns.get_loc(args.pricecol),
            ]

            window_ret = window_prices.iat[-1] / window_prices.iat[0] - 1.0
            years = (len(window_prices) - 1) / periods_per_year
            window_ann = (window_prices.iat[-1] / window_prices.iat[0]) ** (1 / years) - 1.0

            period_returns = window_prices.pct_change().iloc[1:]
            std = period_returns.std(ddof=1)
            if std == 0 or np.isnan(std):
                sr = 0.0
            else:
                sr = period_returns.mean() / std * np.sqrt(periods_per_year)
            sharpe_tracker["underlying"].append(sr)

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

            period_returns = np.diff(V_path) / V_path[:-1]
            std = period_returns.std(ddof=1)
            if std == 0 or np.isnan(std):
                sr = 0.0
            else:
                sr = period_returns.mean() / std * np.sqrt(periods_per_year)
            sharpe_tracker["1x_dividend"].append(sr)

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

    stats_df = summary_statistics(
        returns_df=returns_df,
        annualised_df=annualised_returns_df,
        bust_df=summary_df,
        sharpe_dict=sharpe_tracker,
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
    stats_df.to_csv(
        name_run_output("summary_statistics", args.out, args.leverage, "csv"), index=False
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
    return returns_df, annualised_returns_df, summary_df, stats_df


__all__ = ["main"]
