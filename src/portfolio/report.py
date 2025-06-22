import pandas as pd
import matplotlib.pyplot as plt


def boxplot_returns(returns_df: pd.DataFrame, portfolio_cols, log=False, showfliers=True):
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
    returns_df[portfolio_cols] = returns_df[portfolio_cols].apply(pd.to_numeric, errors='coerce')

    ax = returns_df[portfolio_cols].boxplot(showfliers=showfliers)
    ax.set_ylabel("Total Return")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    if log:
        ax.set_yscale("log")
    fig = ax.get_figure()
    fig.tight_layout() 
    return fig