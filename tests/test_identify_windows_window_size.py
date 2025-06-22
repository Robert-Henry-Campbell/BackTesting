import pandas as pd
from portfolio.core import identify_windows


def test_identify_windows_various_sizes():
    df = pd.DataFrame({"x": [0, 0, 0, 0]})

    assert identify_windows(df, 1) == [[0, 1], [1, 2], [2, 3]]
    assert identify_windows(df, 2) == [[0, 2], [1, 3]]
    assert identify_windows(df, 3) == [[0, 3]]
