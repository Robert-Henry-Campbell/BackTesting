from portfolio.core import (
    simulate_portfolio,
    identify_windows,
    calc_window_returns,
)

import pandas as pd
df = pd.DataFrame({
        'date': ['day1','day2','day3'],
        "sp_real_price": [1, 2, 1],
    })

print("Raw")
print(df)

# simulate 1× leverage
df = simulate_portfolio(df, leverage=1)
print("\nAfter simulate_portfolio 1×")
print(df)

# windows of length 1
windows = identify_windows(df, 1)
print("\nWindows:", windows)

# returns
returns = calc_window_returns(
    df,
    window_size=1,
    date_column="date",
    portfolio_columns=["portfolio_1x"],
)
print("\nReturns")
print(returns)
