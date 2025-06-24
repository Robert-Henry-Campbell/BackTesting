import pandas as pd
from portfolio.cli import _format_label


def test_format_label_is_identity():
    assert _format_label(pd.NaT, "day") is pd.NaT
    assert _format_label(None, "month") is None
    assert _format_label("not-a-date", "day") == "not-a-date"
