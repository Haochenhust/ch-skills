#!/usr/bin/env python3
"""Check if a given date is a trading day on the Shanghai Stock Exchange."""

import argparse
import json
import os
import sys
from datetime import datetime, date

import akshare as ak
import pandas as pd

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".trading_calendar_cache.json")


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(data: dict) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def get_trading_days() -> set[str]:
    """Fetch trading calendar from AKShare and cache it."""
    cache = load_cache()
    cache_year = cache.get("year")
    current_year = date.today().year

    if cache_year == current_year and "dates" in cache:
        return set(cache["dates"])

    df = ak.tool_trade_date_hist_sina()
    # Filter to current year and next year
    dates = set()
    for _, row in df.iterrows():
        d = row["trade_date"]
        if isinstance(d, pd.Timestamp):
            d = d.date()
        if isinstance(d, date):
            if d.year in (current_year, current_year + 1):
                dates.add(d.strftime("%Y%m%d"))

    save_cache({"year": current_year, "dates": sorted(dates)})
    return dates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date to check in YYYYMMDD format (default: today)",
    )
    args = parser.parse_args()

    if args.date:
        check_date = args.date
    else:
        check_date = datetime.now().strftime("%Y%m%d")

    trading_days = get_trading_days()
    is_trading = check_date in trading_days

    result = {
        "date": check_date,
        "is_trading_day": is_trading,
    }

    print(json.dumps(result, ensure_ascii=False))
    return 0 if is_trading else 1


if __name__ == "__main__":
    sys.exit(main())
