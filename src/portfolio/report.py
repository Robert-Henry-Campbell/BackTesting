import pandas as pd
import matplotlib.pyplot as plt


def boxplot_returns(
    returns_df: pd.DataFrame, portfolio_cols, log=False, showfliers=True, label="Return"
):
    """
    Draw a box-and-whisker plot of window returns.

    Parameters
    ----------
    returns_df : DataFrame
    portfolio_cols : list[str]
    log : bool, optional
        If True, use a logarithmic scale for the y-axis.
    showfliers : bool, optional
        If False, outlier points will not be shown.
    """
    returns_df[portfolio_cols] = returns_df[portfolio_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    ax = returns_df[portfolio_cols].boxplot(showfliers=showfliers)
    ax.set_ylabel(label)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    if log:
        ax.set_yscale("log")
    fig = ax.get_figure()
    fig.tight_layout()
    return fig


def summary_statistics(
    returns_df: pd.DataFrame,
    annualised_df: pd.DataFrame,
    bust_df: pd.DataFrame,
    sharpe_dict: dict[str, list[float]],
) -> pd.DataFrame:
    """Aggregate window statistics for each portfolio column.

    Parameters
    ----------
    returns_df : DataFrame
        Table of total returns for each window.
    annualised_df : DataFrame
        Table of annualised returns (CAGR) for each window.
    bust_df : DataFrame
        Summary of bust proportions with columns ``leverage`` and ``bust_ratio``.
    sharpe_dict : dict[str, list[float]]
        Mapping of portfolio column name to a list of Sharpe ratios for each
        window.

    Returns
    -------
    DataFrame
        One row per portfolio column containing the metrics described in the
        specification.
    """

    start_col, end_col = returns_df.columns[:2]
    portfolio_cols = [c for c in returns_df.columns if c not in (start_col, end_col)]

    # map columns like ``portfolio_1x`` to bust ratios
    def _col_name(lev):
        text = str(lev)
        if text.endswith(".0"):
            text = text[:-2]
        return f"portfolio_{text}x"

    bust_map = {_col_name(row["leverage"]): row["bust_ratio"] for _, row in bust_df.iterrows()}

    stats = []
    for col in portfolio_cols:
        series_ret = pd.to_numeric(returns_df[col], errors="coerce")
        series_cagr = pd.to_numeric(annualised_df[col], errors="coerce")

        mean_ret = series_ret.mean()
        iqr_ret = series_ret.quantile(0.75) - series_ret.quantile(0.25)
        mean_cagr = series_cagr.mean()
        std_cagr = series_cagr.std()
        bust_ratio = bust_map.get(col, 0.0)

        sharpe_vals = sharpe_dict.get(col, [])
        avg_sharpe = float(pd.Series(sharpe_vals).mean()) if sharpe_vals else 0.0

        stats.append(
            {
                "portfolio": col,
                "mean_total_return": mean_ret,
                "iqr_total_return": iqr_ret,
                "mean_cagr": mean_cagr,
                "std_cagr": std_cagr,
                "bust_ratio": bust_ratio,
                "avg_sharpe": avg_sharpe,
                "min_total_return": series_ret.min(),
                "max_total_return": series_ret.max(),
            }
        )

    return pd.DataFrame(stats)


__all__ = ["boxplot_returns", "summary_statistics"]
