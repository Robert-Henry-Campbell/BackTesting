#!/usr/bin/env python
import argparse

from portfolio.cli import main

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv", help="Path to price CSV")
    p.add_argument("--window", type=int, default=252, help='# periods in total investment window') 
    p.add_argument("--leverage", nargs="+", type=float, default=[1.0, 2.0])
    p.add_argument("--datecol", default="date")
    p.add_argument("--pricecol", default="sp_real_price")
    p.add_argument("--dividendcol", default=None)
    p.add_argument("--underlying", action="store_true")
    p.add_argument("--freq", choices=["day", "month", "year"], default="month")
    p.add_argument("--out", default="data/outputs/")
    p.add_argument("--plot", action="store_true")
    main(p.parse_args())
