#!/usr/bin/env python3
"""Fetch financial data from AKShare for investment research.

Usage:
    python3 fetch_financial_data.py --mode stock --symbols 002463,300724
    python3 fetch_financial_data.py --mode etf [--filter keyword]
    python3 fetch_financial_data.py --mode valuation --symbols 002463
"""

import os
# AKShare calls domestic Chinese APIs (eastmoney, sina) — proxy causes connection failures
# no_proxy='*' overrides both env vars and macOS system proxy
for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
    os.environ.pop(key, None)
os.environ["no_proxy"] = "*"

import argparse
import json
import sys
import warnings
from datetime import datetime, timedelta

os.environ["TQDM_DISABLE"] = "1"

import akshare as ak
import pandas as pd

warnings.filterwarnings("ignore")


def fetch_stock_financials(symbol: str) -> dict:
    """Fetch comprehensive financial data for a single stock."""
    result = {"code": symbol}

    # 1. Financial abstract (revenue, profit across quarters)
    try:
        df = ak.stock_financial_abstract(symbol=symbol)
        if df is not None and not df.empty:
            # Get latest available periods
            period_cols = [c for c in df.columns if c not in ["选项", "指标"]]
            latest_periods = period_cols[:4]  # Last 4 reporting periods

            financials = {}
            for _, row in df.iterrows():
                indicator = row["指标"]
                values = {}
                for period in latest_periods:
                    val = row[period]
                    if pd.notna(val):
                        try:
                            values[period] = float(val)
                        except (ValueError, TypeError):
                            values[period] = str(val)
                if values:
                    financials[indicator] = values

            # Extract key metrics
            key_metrics = {}
            metric_names = [
                "归母净利润", "营业总收入", "毛利率", "净利率",
                "净资产收益率", "每股收益", "每股净资产",
                "资产负债率", "经营现金流/营业收入"
            ]
            for name in metric_names:
                if name in financials:
                    key_metrics[name] = financials[name]

            result["financial_abstract"] = {
                "periods": latest_periods,
                "key_metrics": key_metrics,
            }

            # Calculate YoY growth rates
            if "归母净利润" in financials and len(latest_periods) >= 2:
                latest = latest_periods[0]
                # Find same period last year
                latest_year = int(latest[:4])
                latest_suffix = latest[4:]
                yoy_period = f"{latest_year - 1}{latest_suffix}"
                if yoy_period in financials.get("归母净利润", {}):
                    curr = financials["归母净利润"][latest]
                    prev = financials["归母净利润"][yoy_period]
                    if prev and prev != 0:
                        growth = (curr - prev) / abs(prev) * 100
                        result["profit_yoy_growth"] = round(growth, 2)

            if "营业总收入" in financials and len(latest_periods) >= 2:
                latest = latest_periods[0]
                latest_year = int(latest[:4])
                latest_suffix = latest[4:]
                yoy_period = f"{latest_year - 1}{latest_suffix}"
                if yoy_period in financials.get("营业总收入", {}):
                    curr = financials["营业总收入"][latest]
                    prev = financials["营业总收入"][yoy_period]
                    if prev and prev != 0:
                        growth = (curr - prev) / abs(prev) * 100
                        result["revenue_yoy_growth"] = round(growth, 2)

    except Exception as e:
        result["financial_abstract_error"] = str(e)

    # 2. Financial analysis indicators (ratios)
    try:
        df = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=str(datetime.now().year - 1))
        if df is not None and not df.empty:
            latest = df.iloc[0]
            ratios = {}
            ratio_fields = {
                "销售毛利率(%)": "gross_margin",
                "销售净利率(%)": "net_margin",
                "净资产收益率(%)": "roe",
                "总资产净利润率(%)": "roa",
                "资产负债率(%)": "debt_ratio",
                "流动比率": "current_ratio",
                "速动比率": "quick_ratio",
                "总资产周转率(次)": "asset_turnover",
                "存货周转率(次)": "inventory_turnover",
                "营业利润率(%)": "operating_margin",
            }
            for cn_name, en_name in ratio_fields.items():
                if cn_name in latest.index and pd.notna(latest[cn_name]):
                    try:
                        ratios[en_name] = round(float(latest[cn_name]), 2)
                    except (ValueError, TypeError):
                        pass
            ratios["report_date"] = str(latest.get("日期", ""))
            result["financial_ratios"] = ratios
    except Exception as e:
        result["financial_ratios_error"] = str(e)

    # 3. Current price and basic valuation
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=(datetime.now() - timedelta(days=10)).strftime("%Y%m%d"),
            end_date=datetime.now().strftime("%Y%m%d"),
            adjust="qfq",
        )
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            result["price"] = {
                "close": round(float(latest["收盘"]), 2),
                "change_pct": round(float(latest["涨跌幅"]), 2),
                "volume": int(latest["成交量"]),
                "turnover": round(float(latest.get("换手率", 0)), 2),
                "date": str(latest["日期"]),
            }

            # Simple PE calculation if we have profit data
            if "financial_abstract" in result:
                metrics = result["financial_abstract"].get("key_metrics", {})
                eps_data = metrics.get("每股收益", {})
                if eps_data:
                    # Get latest annual EPS (TTM approximation)
                    annual_periods = [p for p in eps_data.keys() if p.endswith("1231")]
                    if annual_periods:
                        latest_annual_eps = eps_data[annual_periods[0]]
                        if latest_annual_eps and float(latest_annual_eps) > 0:
                            pe = round(float(latest["收盘"]) / float(latest_annual_eps), 2)
                            result["valuation"] = {"pe_ttm_approx": pe}

                nav_data = metrics.get("每股净资产", {})
                if nav_data:
                    latest_nav = list(nav_data.values())[0]
                    if latest_nav and float(latest_nav) > 0:
                        pb = round(float(latest["收盘"]) / float(latest_nav), 2)
                        if "valuation" not in result:
                            result["valuation"] = {}
                        result["valuation"]["pb"] = pb

    except Exception as e:
        result["price_error"] = str(e)

    return result


def fetch_etf_list(keyword: str = None) -> dict:
    """Fetch ETF list with optional keyword filter."""
    try:
        df = ak.fund_etf_category_sina(symbol="ETF基金")
        if df is None or df.empty:
            return {"error": "No ETF data returned"}

        # Clean up
        records = []
        for _, row in df.iterrows():
            record = {
                "code": str(row["代码"]),
                "name": str(row["名称"]),
                "price": float(row["最新价"]) if pd.notna(row["最新价"]) else None,
                "change_pct": float(row["涨跌幅"]) if pd.notna(row["涨跌幅"]) else None,
                "volume": int(row["成交量"]) if pd.notna(row["成交量"]) else 0,
                "amount": float(row["成交额"]) if pd.notna(row["成交额"]) else 0,
            }
            records.append(record)

        # Apply keyword filter
        if keyword:
            records = [r for r in records if keyword.lower() in r["name"].lower()
                      or keyword.lower() in r["code"].lower()]

        # Sort by volume descending (most active first)
        records.sort(key=lambda x: x.get("volume", 0) or 0, reverse=True)

        return {
            "total": len(records),
            "etfs": records[:50],  # Top 50 by volume
            "filter": keyword,
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_cross_border_etfs() -> dict:
    """Fetch cross-border ETFs (QDII, Hong Kong, US tracking)."""
    all_etfs = fetch_etf_list()
    if "error" in all_etfs:
        return all_etfs

    keywords = ["纳指", "纳斯达克", "标普", "美国", "恒生", "港股", "中概",
                "日经", "德国", "法国", "越南", "印度", "东南亚", "亚太",
                "黄金", "原油", "豆粕", "有色", "QDII"]
    cross_border = []
    for etf in all_etfs.get("etfs", []):
        for kw in keywords:
            if kw in etf["name"]:
                etf["category"] = kw
                cross_border.append(etf)
                break

    # Deduplicate
    seen = set()
    unique = []
    for etf in cross_border:
        if etf["code"] not in seen:
            seen.add(etf["code"])
            unique.append(etf)

    return {
        "total": len(unique),
        "etfs": unique,
        "type": "cross_border",
    }


def fetch_sector_etfs() -> dict:
    """Fetch sector/industry theme ETFs."""
    all_etfs = fetch_etf_list()
    if "error" in all_etfs:
        return all_etfs

    keywords = ["半导体", "芯片", "AI", "人工智能", "机器人", "算力", "光模块",
                "新能源", "电池", "光伏", "风电", "汽车",
                "医药", "医疗", "创新药", "生物",
                "军工", "国防", "航天",
                "证券", "银行", "保险", "金融",
                "消费", "白酒", "食品",
                "地产", "建材",
                "通信", "5G", "计算机", "软件",
                "红利", "价值", "成长", "科创"]
    sector = []
    for etf in all_etfs.get("etfs", []):
        for kw in keywords:
            if kw in etf["name"]:
                etf["theme"] = kw
                sector.append(etf)
                break

    seen = set()
    unique = []
    for etf in sector:
        if etf["code"] not in seen:
            seen.add(etf["code"])
            unique.append(etf)

    return {
        "total": len(unique),
        "etfs": unique,
        "type": "sector_theme",
    }


def fetch_etf_daily(symbol: str, start_date: str = None, end_date: str = None, adjust: str = "qfq") -> dict:
    """Fetch ETF daily OHLCV data. Tries eastmoney first, falls back to sina.

    Args:
        symbol: ETF code, e.g. '510300', '159967'
        start_date: Start date in YYYYMMDD format. Defaults to 60 days ago.
        end_date: End date in YYYYMMDD format. Defaults to today.
        adjust: Price adjustment - 'qfq' (forward), 'hfq' (backward), '' (none). Default 'qfq'.
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")

    # Try eastmoney first (has more fields: amplitude, change_pct, turnover)
    source = "eastmoney"
    try:
        df = ak.fund_etf_hist_em(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
        if df is not None and not df.empty:
            records = []
            for _, row in df.iterrows():
                records.append({
                    "date": str(row["日期"]),
                    "open": round(float(row["开盘"]), 3),
                    "close": round(float(row["收盘"]), 3),
                    "high": round(float(row["最高"]), 3),
                    "low": round(float(row["最低"]), 3),
                    "volume": int(row["成交量"]),
                    "amount": round(float(row["成交额"]), 2),
                    "amplitude": round(float(row["振幅"]), 2),
                    "change_pct": round(float(row["涨跌幅"]), 2),
                    "change_amt": round(float(row["涨跌额"]), 3),
                    "turnover": round(float(row["换手率"]), 2),
                })
            return {
                "code": symbol, "source": source, "total": len(records),
                "start_date": start_date, "end_date": end_date, "adjust": adjust,
                "daily": records,
            }
    except Exception:
        pass  # Fall through to sina

    # Fallback: sina (no adjust, no amplitude/turnover, but more stable)
    source = "sina"
    try:
        # sina uses exchange prefix: sz for Shenzhen, sh for Shanghai
        prefix = "sz" if symbol.startswith("1") else "sh"
        df = ak.fund_etf_hist_sina(symbol=f"{prefix}{symbol}")
        if df is None or df.empty:
            return {"error": f"No daily data returned for ETF {symbol}"}

        # Filter by date range
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

        records = []
        for _, row in df.iterrows():
            records.append({
                "date": str(row["date"].date()),
                "open": round(float(row["open"]), 3),
                "close": round(float(row["close"]), 3),
                "high": round(float(row["high"]), 3),
                "low": round(float(row["low"]), 3),
                "volume": int(row["volume"]),
                "amount": round(float(row["amount"]), 2),
            })

        return {
            "code": symbol, "source": source, "total": len(records),
            "start_date": start_date, "end_date": end_date, "adjust": "none (sina)",
            "daily": records,
        }
    except Exception as e:
        return {"error": f"Failed to fetch ETF {symbol} daily data: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Fetch financial data for investment research")
    parser.add_argument(
        "--mode",
        choices=["stock", "etf", "etf-daily", "etf-cross-border", "etf-sector", "valuation"],
        required=True,
        help="Data fetch mode",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        default=None,
        help="Comma-separated stock/ETF codes (e.g., 002463,300724 or 510300,159967)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Keyword filter for ETF search",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date in YYYYMMDD format (for etf-daily mode)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date in YYYYMMDD format (for etf-daily mode)",
    )
    args = parser.parse_args()

    if args.mode == "stock":
        if not args.symbols:
            print(json.dumps({"error": "Must provide --symbols for stock mode"}, ensure_ascii=False))
            sys.exit(1)
        codes = [c.strip() for c in args.symbols.split(",")]
        results = [fetch_stock_financials(code) for code in codes]
        print(json.dumps({"mode": "stock", "stocks": results}, ensure_ascii=False, indent=2))

    elif args.mode == "etf-daily":
        if not args.symbols:
            print(json.dumps({"error": "Must provide --symbols for etf-daily mode"}, ensure_ascii=False))
            sys.exit(1)
        codes = [c.strip() for c in args.symbols.split(",")]
        results = [fetch_etf_daily(code, start_date=args.start, end_date=args.end) for code in codes]
        output = results[0] if len(results) == 1 else {"mode": "etf-daily", "etfs": results}
        print(json.dumps(output, ensure_ascii=False, indent=2))

    elif args.mode == "etf":
        result = fetch_etf_list(keyword=args.filter)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.mode == "etf-cross-border":
        result = fetch_cross_border_etfs()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.mode == "etf-sector":
        result = fetch_sector_etfs()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.mode == "valuation":
        if not args.symbols:
            print(json.dumps({"error": "Must provide --symbols for valuation mode"}, ensure_ascii=False))
            sys.exit(1)
        codes = [c.strip() for c in args.symbols.split(",")]
        results = [fetch_stock_financials(code) for code in codes]
        # Valuation mode returns same data but formatted for valuation analysis
        print(json.dumps({"mode": "valuation", "stocks": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
