from twstock import Stock
import pandas as pd
from pandas import Series, DataFrame

def get_stock_pd(stock_no = "0050"):
    S = Stock(stock_no)
    keys = list(S.data[0]._fields)
    return DataFrame(S.data, columns=keys).set_index("date")
