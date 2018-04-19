import os
import re
import sys

import pandas as pd
from datetime import datetime
from datetime import date

#  get stocks pd
def get_stock_all(year):
    db_path = "./static_database/"
    start = 0
    end = 0
    for csvfile in os.listdir(db_path):
        m = re.match(r"(.*)-(.*).csv", csvfile)
        if m:
           start = int(m.group(1))
           end = int(m.group(2))
        if (str(year) in csvfile) or (int(year) in range(start, end+1)):
            break
    stocks = pd.read_csv('{}/{}'.format(db_path, csvfile))
    stocks = stocks.set_index("證券代碼")
    stocks["年月日"] = pd.to_datetime(stocks["年月日"], format="%Y%m%d")
    stocks = stocks[stocks["年月日"].dt.year == int(year)]
    stocks.year = int(year)
    return stocks

def get_stock(stock_no, year):
    stock = get_stock_all(year)
    stock = stock.loc[int(stock_no)]
    return stock

