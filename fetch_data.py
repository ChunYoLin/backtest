from twstock import Stock
import pandas as pd
from pandas import Series, DataFrame

def get_stock_pd(stock_no="0050", fetch_from=None):
    S = Stock(stock_no)
    if fetch_from:
        S.fetch_from(fetch_from[0], fetch_data[1])
    keys = list(S.data[0]._fields)
    return DataFrame(S.data, columns=keys).set_index("date")
