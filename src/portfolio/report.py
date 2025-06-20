import pandas as pd
import matplotlib.pyplot as plt

def boxplot_returns(returns_df: pd.DataFrame, portfolio_cols):
    """
    Draw a box-and-whisker plot of window returns.

    Parameters
    ----------
    returns_df : DataFrame
    portfolio_cols : list[str]
    """
    ax = returns_df[portfolio_cols].boxplot()
    ax.set_ylabel("Total Return")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Tilt x labels
    fig = ax.get_figure()
    return fig