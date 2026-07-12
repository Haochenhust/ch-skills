#!/usr/bin/env python3
"""Fetch market data from AKShare for stock training tasks.

Usage:
    python3 fetch_market_data.py --mode morning
    python3 fetch_market_data.py --mode evening [--stocks 000001,600519]
    python3 fetch_market_data.py --mode weekly
"""

import argparse
import json
import os
import sys
import warnings
from datetime import datetime, timedelta

# Suppress tqdm progress bars (AKShare uses them internally)
os.environ["TQDM_DISABLE"] = "1"

import akshare as ak
import pandas as pd

warnings.filterwarnings("ignore")

# Key indices
A_SHARE_INDICES = {
    "sh000001": "上证指数",
    "sh000300": "沪深300",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
}

US_INDICES = {
    ".DJI": "道琼斯",
    ".IXIC": "纳斯达克",
    ".INX": "标普500",
}

# Top industry sectors to track (同花顺)
KEY_SECTORS = [
    "半导体", "白酒", "电池", "光伏设备", "汽车整车",
    "医疗器械", "软件开发", "房地产", "银行", "证券",
    "消费电子", "军工装备", "钢铁", "煤炭开采加工", "电力",
]


def fetch_a_share_indices(days: int = 20) -> list[dict]:
    """Fetch A-share index daily data for the last N trading days."""
    results = []
    for symbol, name in A_SHARE_INDICES.items():
        try:
            df = ak.stock_zh_index_daily(symbol=symbol)
            df = df.tail(days)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest
            change_pct = (latest["close"] - prev["close"]) / prev["close"] * 100

            results.append({
                "name": name,
                "symbol": symbol,
                "close": round(float(latest["close"]), 2),
                "change_pct": round(change_pct, 2),
                "volume": int(latest["volume"]),
                "trend_5d": _calc_trend(df, 5),
                "trend_20d": _calc_trend(df, 20),
                "date": str(latest["date"]),
            })
        except Exception as e:
            results.append({"name": name, "symbol": symbol, "error": str(e)})
    return results


def fetch_us_indices(days: int = 5) -> list[dict]:
    """Fetch US stock index data."""
    results = []
    for symbol, name in US_INDICES.items():
        try:
            df = ak.index_us_stock_sina(symbol=symbol)
            df = df.tail(days)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest
            change_pct = (latest["close"] - prev["close"]) / prev["close"] * 100

            results.append({
                "name": name,
                "close": round(float(latest["close"]), 2),
                "change_pct": round(change_pct, 2),
                "date": str(latest["date"]),
            })
        except Exception as e:
            results.append({"name": name, "error": str(e)})
    return results


def fetch_sector_performance(days: int = 5) -> list[dict]:
    """Fetch industry sector performance from THS."""
    results = []
    for sector in KEY_SECTORS:
        try:
            end = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")
            df = ak.stock_board_industry_index_ths(
                symbol=sector, start_date=start, end_date=end
            )
            if df is None or df.empty:
                continue
            df = df.tail(days)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest
            change_pct = (latest["收盘价"] - prev["收盘价"]) / prev["收盘价"] * 100

            results.append({
                "name": sector,
                "close": round(float(latest["收盘价"]), 2),
                "change_pct": round(change_pct, 2),
                "volume": int(latest["成交量"]),
                "date": str(latest["日期"]),
            })
        except Exception:
            continue
    # Sort by change_pct descending
    results.sort(key=lambda x: x.get("change_pct", 0), reverse=True)
    return results


def fetch_limit_pool(date_str: str = None) -> dict:
    """Fetch limit-up pool data."""
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_em(date=date_str)
        return {
            "date": date_str,
            "count": len(df),
            "top_stocks": [
                {
                    "code": row["代码"],
                    "name": row["名称"],
                    "change_pct": round(float(row["涨跌幅"]), 2),
                    "industry": row.get("所属行业", ""),
                    "consecutive": int(row.get("连板数", 1)),
                }
                for _, row in df.head(10).iterrows()
            ],
        }
    except Exception as e:
        return {"date": date_str, "error": str(e)}


def fetch_northbound(days: int = 5) -> list[dict]:
    """Fetch northbound (HSGT) capital flow."""
    try:
        df = ak.stock_hsgt_hist_em(symbol="沪股通")
        df = df.tail(days)
        results = []
        for _, row in df.iterrows():
            results.append({
                "date": str(row["日期"]),
                "index": round(float(row["上证指数"]), 2) if pd.notna(row["上证指数"]) else None,
                "index_change": round(float(row["上证指数-涨跌幅"]), 2) if pd.notna(row["上证指数-涨跌幅"]) else None,
                "top_stock": row.get("领涨股", ""),
                "top_stock_change": round(float(row["领涨股-涨跌幅"]), 2) if pd.notna(row.get("领涨股-涨跌幅")) else None,
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def fetch_stock_daily(codes: list[str], days: int = 5) -> list[dict]:
    """Fetch daily data for specific stocks."""
    results = []
    for code in codes:
        try:
            # AKShare uses format like "000001" for stock_zh_a_hist
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=(datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq",
            )
            if df is None or df.empty:
                continue
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest

            results.append({
                "code": code,
                "name": str(latest.get("股票代码", code)),
                "close": round(float(latest["收盘"]), 2),
                "change_pct": round(float(latest["涨跌幅"]), 2),
                "volume": int(latest["成交量"]),
                "turnover": round(float(latest.get("换手率", 0)), 2),
                "date": str(latest["日期"]),
            })
        except Exception as e:
            results.append({"code": code, "error": str(e)})
    return results


def _calc_trend(df: pd.DataFrame, days: int) -> str:
    """Calculate trend direction over N days."""
    if len(df) < days:
        return "insufficient_data"
    subset = df.tail(days)
    start_close = float(subset.iloc[0]["close"])
    end_close = float(subset.iloc[-1]["close"])
    change = (end_close - start_close) / start_close * 100
    if change > 1:
        return f"上涨 {round(change, 2)}%"
    elif change < -1:
        return f"下跌 {round(change, 2)}%"
    else:
        return f"震荡 {round(change, 2)}%"


def morning_report() -> dict:
    """Generate morning prediction data package."""
    return {
        "mode": "morning",
        "timestamp": datetime.now().isoformat(),
        "us_indices": fetch_us_indices(days=5),
        "a_share_indices": fetch_a_share_indices(days=20),
        "sectors": fetch_sector_performance(days=5),
        "limit_pool": fetch_limit_pool(),
        "northbound": fetch_northbound(days=5),
    }


def evening_report(stock_codes: list[str] = None) -> dict:
    """Generate evening review data package."""
    data = {
        "mode": "evening",
        "timestamp": datetime.now().isoformat(),
        "a_share_indices": fetch_a_share_indices(days=5),
        "sectors": fetch_sector_performance(days=5),
        "limit_pool": fetch_limit_pool(),
        "northbound": fetch_northbound(days=5),
    }
    if stock_codes:
        data["tracked_stocks"] = fetch_stock_daily(stock_codes, days=5)
    return data


def weekly_report() -> dict:
    """Generate weekly review data package."""
    return {
        "mode": "weekly",
        "timestamp": datetime.now().isoformat(),
        "us_indices": fetch_us_indices(days=10),
        "a_share_indices": fetch_a_share_indices(days=20),
        "sectors": fetch_sector_performance(days=10),
        "northbound": fetch_northbound(days=10),
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch market data for stock training")
    parser.add_argument(
        "--mode",
        choices=["morning", "evening", "weekly"],
        required=True,
        help="Data fetch mode",
    )
    parser.add_argument(
        "--stocks",
        type=str,
        default=None,
        help="Comma-separated stock codes for evening mode (e.g., 000001,600519)",
    )
    args = parser.parse_args()

    if args.mode == "morning":
        result = morning_report()
    elif args.mode == "evening":
        codes = args.stocks.split(",") if args.stocks else None
        result = evening_report(stock_codes=codes)
    elif args.mode == "weekly":
        result = weekly_report()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
