import pandas as pd
import pytest
import matplotlib as plt

from portfolio import boxplot_returns


def test_boxplot_returns_object():
    df = pd.DataFrame({'bunk_col':[1,2,3],
                       'port_col_10':[9,10,11],
                       'port_col_20': [19,20,21]})
    out = boxplot_returns(returns_df = df, portfolio_cols= list(df.columns)[1:3])
    assert type(out) == plt.figure.Figure

