import pandas as pd
from typing import List, Optional
import doctest


def simulate_portfolio(df, leverage=1, dividend=False, rebalance_period=1):
    """
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

    df[f'portfolio_{leverage}x'] = 1.0
    portfolio_idx = df.columns.get_loc(f'portfolio_{leverage}x')

    last_rebalance = 0
    for i in range(1, len(df)):
        if i - last_rebalance == rebalance_period:
            if dividend:
                raise NotImplementedError("Dividend handling not built yet")

            base = df.iloc[last_rebalance, df.columns.get_loc('sp_real_price')]
            curr = df.iloc[i,            df.columns.get_loc('sp_real_price')]

            df.iat[i, portfolio_idx] = (
                df.iat[last_rebalance, portfolio_idx] *
                (curr / base) ** leverage
            )
            last_rebalance = i
        else:  # carry forward
            df.iat[i, portfolio_idx] = df.iat[i-1, portfolio_idx]

    return df

doctest.run_docstring_examples(simulate_portfolio, globals())



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
        windows.append([start,end])
    return windows


doctest.run_docstring_examples(identify_windows, globals())


def calc_window_returns(df, window_size, date_column, portfolio_columns: Optional[List[str]] = None ):
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
        window_dates.append([df.iloc[start_idx, df.columns.get_loc(date_column)],
                             df.iloc[end_idx, df.columns.get_loc(date_column)]])
    
    out = pd.DataFrame({
        'window_dates': window_dates,
        })

    #for each portfolio column, calculate the returns over the defined windows and add to the outdf
    for portfolio in portfolio_columns:
        #calculate the return for each window
        portfolio_returns = [] #captures return over the many possible windows
        for window in windows:
            start_idx = window[0]
            end_idx = window[1]
            #return is portfolio at end / portfolio at start
            window_return = df.iloc[end_idx, df.columns.get_loc(portfolio)] / df.iloc[start_idx, df.columns.get_loc(portfolio)]
            portfolio_returns.append(window_return)
        #add the returns to the out
        out[f'{portfolio}_returns'] = portfolio_returns
    #print(out)
    return out




doctest.run_docstring_examples(calc_window_returns, globals())