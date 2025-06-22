import pandas as pd
from typing import List, Optional
from .utils import to_native
import numpy as np


def simulate_leveraged_series(prices: pd.Series, leverage: float) -> pd.Series:
    """
    Daily rebalanced futures‑style leveraged P&L.
    Assumes `prices` is indexed chronologically.
    """
    value = np.ones_like(prices, dtype=float)  # start with 1.0 unit of capital
    for i in range(1, len(prices)):
        shares = value[i - 1] * leverage / prices.iat[i - 1]
        pnl = shares * (prices.iat[i] - prices.iat[i - 1])
        value[i] = value[i - 1] + pnl
    return pd.Series(value, index=prices.index, name=f"{leverage}x_equity")


def simulate_window(
    prices: pd.Series, leverage: float, init_value: float = 1.0
) -> np.ndarray:
    """
    prices : settlement prices from window start *through* window end
    returns: array of portfolio equity V_i (same length as prices)
    """
    V = np.empty(len(prices), dtype=float)
    V[0] = init_value

    for i in range(len(prices) - 1):
        P_i = prices.iloc[i]
        Q_i = leverage * V[i] / P_i  # position held during [i, i+1)
        V[i + 1] = V[i] + Q_i * (prices.iloc[i + 1] - P_i)

    return V


def simulate_window_with_dividends(
    prices: pd.Series, dividends: pd.Series, init_value: float = 1.0
) -> np.ndarray:
    """Simulate unleveraged equity with reinvested dividends.

    Parameters
    ----------
    prices : pd.Series
        Settlement prices from window start *through* window end.
    dividends : pd.Series
        Dividend amounts aligned with ``prices``. The value at index ``0`` is
        ignored because it corresponds to the starting point of the window.
    init_value : float, optional
        Starting portfolio value, by default ``1.0``.
    """

    V = np.empty(len(prices), dtype=float)
    V[0] = init_value

    for i in range(len(prices) - 1):
        P_i = prices.iloc[i]
        cash = prices.iloc[i + 1] - P_i + dividends.iloc[i + 1]
        V[i + 1] = V[i] * (1.0 + cash / P_i)

    return V


def detect_bust(equity_path: np.ndarray) -> bool:
    """Return ``True`` if ``equity_path`` hits zero or below.

    Examples
    --------
    >>> import numpy as np
    >>> detect_bust(np.array([1.0, 0.5, -0.1]))
    True
    >>> detect_bust(np.array([1.0, 1.2, 0.8]))
    False
    """
    return (np.asarray(equity_path) <= 0).any()


def identify_windows(df, window_size):
    """
    given a df, returns a list of lists of all possible sliding windows start/endpoints of a given window size.

    example
    ----
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...  'date': [1,2,3],
    ...    'portfolio1':[100,200,400],
    ...    'portfolio2':[100,50,25]
    ...    })
    >>> out = identify_windows(df,1)
    >>> out
    [[0, 1], [1, 2]]
    """
    windows = []
    for start in range(len(df) - window_size):
        end = start + window_size
        windows.append([start, end])
    return windows


def window_return(series: pd.Series, start: int, end: int) -> float:
    """
    Total proportional return on `series` from index `start` (inclusive) to `end` (exclusive).
    """
    return series.iat[end] / series.iat[start] - 1.0


def annualise(r: float, n_periods: int, periods_per_year: int) -> float:
    """Geometrically annualise ``r`` over ``n_periods``.

    Parameters
    ----------
    r : float
        Total return over the period.
    n_periods : int
        Number of observed periods used to generate ``r``.
    periods_per_year : int
        How many of those periods constitute one year.
    """

    return (1.0 + r) ** (periods_per_year / n_periods) - 1.0


def calc_window_returns(
    df, window_size, date_column, portfolio_columns: Optional[List[str]] = None
):
    """
    calculates portfolio return over all possible rolling windows of a given size

    ----
    example:
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...    'date': ['day1','day2','day3'],
    ...    'portfolio1':[100,200,2000],
    ...    'portfolio2':[100,50,5]
    ...    })
    >>> out = calc_window_returns(df,window_size=1, date_column = 'date', portfolio_columns=['portfolio1','portfolio2'])
    >>> out.equals(pd.DataFrame({
    ... 'window_dates':[['day1','day2'],['day2','day3']],
    ... 'portfolio1_returns':[2.0,10.0],
    ... 'portfolio2_returns':[0.5,0.1]
    ...  }))
    True
    """
    df = df.copy()
    if portfolio_columns is None:
        portfolio_columns = []
    windows = identify_windows(df, window_size=window_size)
    window_dates = []
    for date_idx, window in enumerate(windows):
        start_idx = window[0]
        end_idx = window[1]
        start_val = df.iloc[start_idx, df.columns.get_loc(date_column)]
        end_val = df.iloc[end_idx, df.columns.get_loc(date_column)]
        window_dates.append([to_native(start_val), to_native(end_val)])

    out = pd.DataFrame(
        {
            "window_dates": window_dates,
        }
    )

    # for each portfolio column, calculate the returns over the defined windows and add to the outdf
    for portfolio in portfolio_columns:
        # calculate the return for each window
        portfolio_returns = []  # captures return over the many possible windows
        for window in windows:
            start_idx = window[0]
            end_idx = window[1]
            # return is portfolio at end / portfolio at start
            window_return = (
                df.iloc[end_idx, df.columns.get_loc(portfolio)]
                / df.iloc[start_idx, df.columns.get_loc(portfolio)]
            )
            portfolio_returns.append(window_return)
        # add the returns to the out
        out[f"{portfolio}_returns"] = portfolio_returns
    # print(out)
    return out


def simulate_portfolio(df, leverage=1, dividend=False, rebalance_period=1):
    """DEPRECATED
    Simulate portfolio value given an S&P real-price column.

    Examples
    --------
    Basic two-row sanity check (10 % price rise → 10 % portfolio rise)

    >>> import pandas as pd, math
    >>> df = pd.DataFrame({'sp_real_price': [100, 110]})
    >>> test_leverage = 1
    >>> out = simulate_portfolio(df, leverage=test_leverage)
    >>> out[f'portfolio_{test_leverage}x'].tolist()
    [1.0, 1.1]

    """
    df = df.copy()

    df[f"portfolio_{leverage}x"] = 1.0
    portfolio_idx = df.columns.get_loc(f"portfolio_{leverage}x")

    last_rebalance = 0
    for i in range(1, len(df)):
        if i - last_rebalance == rebalance_period:
            if dividend:
                raise NotImplementedError("Dividend handling not built yet")

            base = df.iloc[last_rebalance, df.columns.get_loc("sp_real_price")]
            curr = df.iloc[i, df.columns.get_loc("sp_real_price")]

            df.iat[i, portfolio_idx] = (
                df.iat[last_rebalance, portfolio_idx] * (curr / base) ** leverage
            )
            last_rebalance = i
        else:  # carry forward
            df.iat[i, portfolio_idx] = df.iat[i - 1, portfolio_idx]

    return df


if __name__ == "__main__":
    import doctest

    doctest.testmod()
