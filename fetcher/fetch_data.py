import numpy as np
import pandas as pd
from pandas import Series, DataFrame

from .fetch_dynamic import get_twstock
from .fetch_static import get_stock
from .fetch_chip import get_chip_info_pd_months

from datetime import datetime
from datetime import date

basic_headers = ["date", "capacity", "turnover", "open" , "high", "low" , "close", "change", "transaction"]

def _get_stock_pd_in_day(stock_no="0050", fetch_from=None, mode="", update=False):
    if mode == "dynamic":
        S = get_twstock(stock_no, fetch_from, update)
        keys = list(S[0]._fields)
        S = DataFrame(S, columns=keys)   
        S["capacity"] = S["capacity"].apply(pd.to_numeric)/1000.
    elif mode == "static":
        start_year = fetch_from[0]
        start_month = fetch_from[1]
        S = DataFrame()
        for year in range(start_year, 2018, 1):
            stock = get_stock(stock_no, year)
            if year == start_year:
                stock = stock.loc[stock["年月日"].dt.month >= start_month]
            S = pd.concat([S, stock])
        S = S[["年月日", "成交量(千股)", "成交值(千元)", "開盤價(元)", "最高價(元)", "最低價(元)", "收盤價(元)", "報酬率％", "成交筆數(筆)"]]
        S.columns = basic_headers

    assert (sorted(S.columns.values.tolist()) == sorted(basic_headers))
    S["weekday"] = S["date"].apply(lambda x: x.date().weekday())
    S = S.set_index("date").apply(pd.to_numeric)
    S["change"] = S["change"] / S["close"].shift(1)
    S = S.dropna()

    return S

def get_stock_pd(stock_no="0050", fetch_from=None, chip=False, scale="D", mode="dynamic", update=False):
    S = _get_stock_pd_in_day(stock_no, fetch_from, mode, update)

    if chip:
        start_date = S.index[0]
        S_chip = get_chip_info_pd_months(stock_no, start_date)
        S = pd.concat([S, S_chip], axis=1)
        S = S.dropna()

    def _stock_pd_resample(S, scale):
        S = S.resample(
                scale, 
                how=
                {"capacity": 'sum',
                 "turnover": 'sum',   
                 "open": 'first',   
                 "high": 'max',
                 "low": 'min',
                 "close": 'last',
                 "change": 'sum',
                 "transaction": 'sum',
                 "DomInvest": 'sum',
                 "InvestTrust": 'sum',
                 "ForeignInvest": 'sum',
                })
        S = S.dropna()
        return S

    if scale != "D": 
        S = _stock_pd_resample(S, scale)

    return S

