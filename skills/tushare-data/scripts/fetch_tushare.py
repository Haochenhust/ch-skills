#!/usr/bin/env python3
"""Tushare Pro data fetcher for investment research.

Usage:
    python fetch_tushare.py --mode stock_basic [--market 主板]
    python fetch_tushare.py --mode daily --symbols 000001.SZ --start 20260101 --end 20260317
    python fetch_tushare.py --mode daily_basic --symbols 000001.SZ --start 20260101
    python fetch_tushare.py --mode income --symbols 000001.SZ
    python fetch_tushare.py --mode balancesheet --symbols 000001.SZ
    python fetch_tushare.py --mode cashflow --symbols 000001.SZ
    python fetch_tushare.py --mode fina_indicator --symbols 000001.SZ
    python fetch_tushare.py --mode index_daily --symbols 000300.SH --start 20260101
    python fetch_tushare.py --mode concept [--src ts]
    python fetch_tushare.py --mode concept_detail --id TS0001
    python fetch_tushare.py --mode top_list --date 20260317
    python fetch_tushare.py --mode moneyflow --symbols 000001.SZ --start 20260101
    python fetch_tushare.py --mode margin --start 20260101
    python fetch_tushare.py --mode forecast --symbols 000001.SZ
    python fetch_tushare.py --mode express --symbols 000001.SZ
    python fetch_tushare.py --mode pledge_stat --symbols 000001.SZ
    python fetch_tushare.py --mode top10_holders --symbols 000001.SZ
    python fetch_tushare.py --mode stk_holdernumber --symbols 000001.SZ
    python fetch_tushare.py --mode index_weight --symbols 000300.SH
    python fetch_tushare.py --mode fund_basic [--market E]
    python fetch_tushare.py --mode trade_cal --start 20260101 --end 20261231

Token: Set TUSHARE_TOKEN env var or pass --token.
"""

import argparse
import os
import sys

try:
    import tushare as ts
    import pandas as pd
except ImportError:
    print("ERROR: tushare not installed. Run: pip install tushare")
    sys.exit(1)


def get_api(token: str):
    ts.set_token(token)
    return ts.pro_api()


def fmt(df, max_rows=50):
    """Format DataFrame for terminal output."""
    if df is None or df.empty:
        print("No data returned.")
        return
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 30)
    if len(df) > max_rows:
        print(f"Showing {max_rows} of {len(df)} rows:")
        print(df.head(max_rows).to_string(index=False))
    else:
        print(df.to_string(index=False))
    print(f"\n--- Total: {len(df)} rows ---")


def stock_basic(pro, args):
    """Get stock basic info list."""
    params = {"list_status": "L"}
    if args.market:
        params["market"] = args.market
    if args.symbols:
        params["ts_code"] = args.symbols
    df = pro.stock_basic(**params,
        fields="ts_code,symbol,name,area,industry,market,list_date,is_hs,act_name")
    fmt(df, max_rows=100)


def daily(pro, args):
    """Get daily OHLCV data."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    if args.date:
        params["trade_date"] = args.date
    df = pro.daily(**params)
    fmt(df)


def daily_basic(pro, args):
    """Get daily basic metrics (PE, PB, turnover, etc)."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    if args.date:
        params["trade_date"] = args.date
    df = pro.daily_basic(**params,
        fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,"
               "pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,"
               "free_share,total_mv,circ_mv")
    fmt(df)


def income(pro, args):
    """Get income statement."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.income(ts_code=args.symbols,
        fields="ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,"
               "basic_eps,diluted_eps,total_revenue,revenue,total_cogs,operate_profit,"
               "n_income,n_income_attr_p,ebit,ebitda")
    fmt(df)


def balancesheet(pro, args):
    """Get balance sheet."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.balancesheet(ts_code=args.symbols,
        fields="ts_code,ann_date,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,"
               "cap_rese,money_cap,accounts_receiv,inventories,fix_assets,total_cur_assets,"
               "total_cur_liab,lt_borr,st_borr")
    fmt(df)


def cashflow(pro, args):
    """Get cash flow statement."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.cashflow(ts_code=args.symbols,
        fields="ts_code,ann_date,end_date,n_cashflow_act,n_cashflow_inv_act,"
               "n_cash_flows_fnc_act,c_fr_sale_sg,free_cashflow")
    fmt(df)


def fina_indicator(pro, args):
    """Get financial indicators (ROE, margins, etc)."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.fina_indicator(ts_code=args.symbols,
        fields="ts_code,ann_date,end_date,eps,bps,current_ratio,quick_ratio,"
               "roe,roe_waa,roa,grossprofit_margin,netprofit_margin,debt_to_assets,"
               "netprofit_yoy,or_yoy,equity_yoy")
    fmt(df)


def weekly(pro, args):
    """Get weekly OHLCV data."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.weekly(**params)
    fmt(df)


def monthly(pro, args):
    """Get monthly OHLCV data."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.monthly(**params)
    fmt(df)


def adj_factor(pro, args):
    """Get adjustment factor for forward/backward price adjustment."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    if args.date:
        params["trade_date"] = args.date
    df = pro.adj_factor(**params)
    fmt(df)


def dividend(pro, args):
    """Get dividend and stock distribution data."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.dividend(ts_code=args.symbols,
        fields="ts_code,end_date,ann_date,div_proc,stk_div,stk_bo_rate,"
               "stk_co_rate,cash_div,cash_div_tax,record_date,ex_date,pay_date")
    fmt(df)


def index_daily(pro, args):
    """Get index daily data."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.index_daily(**params)
    fmt(df)


def concept(pro, args):
    """Get concept/theme list."""
    src = args.src if args.src else "ts"
    df = pro.concept(src=src)
    fmt(df, max_rows=100)


def concept_detail(pro, args):
    """Get stocks in a concept/theme."""
    if not args.id:
        print("ERROR: --id required (concept ID like TS0001)")
        return
    df = pro.concept_detail(id=args.id)
    fmt(df, max_rows=100)


def top_list(pro, args):
    """Get dragon-tiger list (龙虎榜)."""
    if not args.date:
        print("ERROR: --date required (YYYYMMDD)")
        return
    df = pro.top_list(trade_date=args.date)
    fmt(df, max_rows=100)


def moneyflow(pro, args):
    """Get individual stock money flow."""
    params = {}
    if args.symbols:
        params["ts_code"] = args.symbols
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.moneyflow(**params)
    fmt(df)


def margin(pro, args):
    """Get market-wide margin trading data."""
    params = {}
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.margin(**params)
    fmt(df)


def forecast(pro, args):
    """Get earnings forecast (业绩预告)."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.forecast(ts_code=args.symbols)
    fmt(df)


def express(pro, args):
    """Get earnings express (业绩快报)."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.express(ts_code=args.symbols)
    fmt(df)


def pledge_stat(pro, args):
    """Get equity pledge statistics."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.pledge_stat(ts_code=args.symbols)
    fmt(df)


def top10_holders(pro, args):
    """Get top 10 holders."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.top10_holders(ts_code=args.symbols)
    fmt(df)


def stk_holdernumber(pro, args):
    """Get shareholder count."""
    if not args.symbols:
        print("ERROR: --symbols required")
        return
    df = pro.stk_holdernumber(ts_code=args.symbols)
    fmt(df)


def index_weight(pro, args):
    """Get index component weights."""
    if not args.symbols:
        print("ERROR: --symbols required (index code like 000300.SH)")
        return
    params = {"index_code": args.symbols}
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.index_weight(**params)
    fmt(df, max_rows=100)


def fund_basic(pro, args):
    """Get fund basic info."""
    params = {}
    if args.market:
        params["market"] = args.market
    df = pro.fund_basic(**params,
        fields="ts_code,name,management,custodian,fund_type,found_date,market,type")
    fmt(df, max_rows=100)


def trade_cal(pro, args):
    """Get trading calendar."""
    params = {"exchange": "SSE"}
    if args.start:
        params["start_date"] = args.start
    if args.end:
        params["end_date"] = args.end
    df = pro.trade_cal(**params,
        fields="exchange,cal_date,is_open,pretrade_date")
    # Only show trading days
    if df is not None and not df.empty:
        df = df[df["is_open"] == 1]
    fmt(df, max_rows=100)


MODE_MAP = {
    "stock_basic": stock_basic,
    "daily": daily,
    "weekly": weekly,
    "monthly": monthly,
    "daily_basic": daily_basic,
    "adj_factor": adj_factor,
    "dividend": dividend,
    "income": income,
    "balancesheet": balancesheet,
    "cashflow": cashflow,
    "fina_indicator": fina_indicator,
    "index_daily": index_daily,
    "concept": concept,
    "concept_detail": concept_detail,
    "top_list": top_list,
    "moneyflow": moneyflow,
    "margin": margin,
    "forecast": forecast,
    "express": express,
    "pledge_stat": pledge_stat,
    "top10_holders": top10_holders,
    "stk_holdernumber": stk_holdernumber,
    "index_weight": index_weight,
    "fund_basic": fund_basic,
    "trade_cal": trade_cal,
}


def main():
    parser = argparse.ArgumentParser(description="Tushare Pro data fetcher")
    parser.add_argument("--mode", required=True, choices=list(MODE_MAP.keys()),
                        help="Data mode to fetch")
    parser.add_argument("--symbols", help="Stock/index code (e.g. 000001.SZ, 000300.SH)")
    parser.add_argument("--start", help="Start date YYYYMMDD")
    parser.add_argument("--end", help="End date YYYYMMDD")
    parser.add_argument("--date", help="Specific date YYYYMMDD")
    parser.add_argument("--market", help="Market filter")
    parser.add_argument("--id", help="Concept ID for concept_detail")
    parser.add_argument("--src", help="Source for concept list")
    parser.add_argument("--token", help="Tushare token (or set TUSHARE_TOKEN env)")

    args = parser.parse_args()

    token = args.token or os.environ.get("TUSHARE_TOKEN")
    if not token:
        print("ERROR: No token. Set TUSHARE_TOKEN env or pass --token.")
        sys.exit(1)

    pro = get_api(token)
    MODE_MAP[args.mode](pro, args)


if __name__ == "__main__":
    main()
