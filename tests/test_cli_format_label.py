import pandas as pd
from portfolio.cli import _format_label


def test_format_label_handles_invalid_dates():
    assert pd.isna(_format_label(pd.NaT, "day"))
    assert pd.isna(_format_label(None, "month"))
    assert pd.isna(_format_label("not-a-date", "day"))
