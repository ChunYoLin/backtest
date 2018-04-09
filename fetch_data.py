from collections import namedtuple
from pandas import Series, DataFrame
from twstock import Stock
from twstock import chip
import pandas as pd

from datetime import datetime
from datetime import date
import requests
import csv
import os.path
import sys
import json
import urllib.parse
import sys

database_path = "./database/"
def _get_twstock_online(stock_no="0050", fetch_from=None, save=False):
    S = Stock(stock_no)
    if fetch_from:
        S.fetch_from(fetch_from[0], fetch_from[1])
    if save:
        with open("{}/{}.csv".format(database_path, stock_no), 'w') as f:
            w = csv.writer(f)
            w.writerow(S.data[0]._fields)
            w.writerows(data for data in S.data)
    return S.data

def _get_twstock_local(stock_no="0050"):
    with open("{}/{}.csv".format(database_path, stock_no)) as infile:
        reader = csv.reader(infile)
        Datas = []
        Data = namedtuple("Data", next(reader))
        for data in map(Data._make, reader):
            data = data._replace(date = datetime.strptime(data.date, "%Y-%m-%d %H:%M:%S"))
            Datas.append(data)
        return Datas

def _get_twstock(stock_no="0050", fetch_from=None):
    if fetch_from == None:
        print("please specify the start date")
        sys.exit(0)
    if os.path.isfile("{}/{}.csv".format(database_path, stock_no)):
        print("local data found!")
        S =  _get_twstock_local(stock_no)
        #  if data too old download it again
        end_datetime = Stock(stock_no).date[-1]
        local_end_datetime = S[-1].date
        if local_end_datetime != end_datetime:
            print("end date not found, re-fetch online...")
            S = _get_twstock_online(stock_no, fetch_from, save=True)
            return S
        #  if data start date mismatched dowload it again
        start_day = Stock(stock_no).fetch(fetch_from[0], fetch_from[1])[0].date.day
        start_datetime = datetime(fetch_from[0], fetch_from[1], start_day)
        for idx, s in enumerate(S):
            if s.date == start_datetime:
                return S[idx:]
        print("start date not found, re-fetch online...")
        S = _get_twstock_online(stock_no, fetch_from, save=True)
        return S

    else:
        print("no local date, fetch online...")
        S = _get_twstock_online(stock_no, fetch_from, save=True)
    return S

    
def _get_chip_info_pd(stock_no="0050", Year=None, month=None):
    url = "https://stock.wearn.com/netbuy.asp?Year={}&month={:02d}&kind={}".format(int(Year), int(month), str(stock_no))
    df = pd.read_html(url, skiprows=[-1, 0], header=0)[0]

    def _dateplus1911(date):
        tmp = date.split("/")
        y = str(int(tmp[0]) + 1911)
        m = tmp[1]
        d = tmp[2]
        return "{}/{}/{}".format(y, m, d)

    df["日期"] = df["日期"].apply(lambda x: _dateplus1911(x))
    df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
    return df

def _get_stock_pd_in_day(stock_no="0050", fetch_from=None):
    S = _get_twstock(stock_no, fetch_from)
    keys = list(S[0]._fields)
    S = DataFrame(S, columns=keys)    
    S["weekday"] = S["date"].apply(lambda x: x.date().weekday())
    S = S.set_index("date").apply(pd.to_numeric)
    S["change"] = S["change"] / S["close"].shift(1)
    start_date = S.index[0]
    end_date = date.today()
    daterange = pd.date_range(start_date, end_date, freq="M")
    df = pd.DataFrame()
    for single_date in daterange:
        year = single_date.year
        month = single_date.month
        df = df.append(_get_chip_info_pd(stock_no, year-1911, month), ignore_index=True)
    df = df.append(_get_chip_info_pd(stock_no, end_date.year-1911, end_date.month), ignore_index=True)
    df = df.drop_duplicates()
    df = df.set_index("日期").apply(pd.to_numeric)
    df.columns = ['DI', 'Dealer', 'FI']
    S = pd.concat([S, df], axis=1)
    return S

def _get_stock_pd_in_week(stock_no="0050", fetch_from=None):
    S_day = _get_stock_pd_in_day(stock_no, fetch_from)
    S_week = S_day.resample(
            'W', 
            how=
            {"capacity": 'sum',
             "turnover": 'sum',   
             "open": 'first',   
             "high": 'max',
             "low": 'min',
             "close": 'last',
             "change": 'sum',
             "transaction": 'sum',
             "DI": 'sum',
             "Dealer": 'sum',
             "FI": 'sum',
            })
    S_week = S_week.dropna()
    return S_week

def _get_stock_pd_in_month(stock_no="0050", fetch_from=None):
    S_day = _get_stock_pd_in_day(stock_no, fetch_from)
    S_month = S_day.resample(
            'M', 
            how=
            {"capacity": 'sum',
             "turnover": 'sum',   
             "open": 'first',   
             "high": 'max',
             "low": 'min',
             "close": 'last',
             "change": 'sum',
             "transaction": 'sum',
             "DI": 'sum',
             "Dealer": 'sum',
             "FI": 'sum',
            })
    S_month = S_month.dropna()
    return S_month


def get_stock_pd(stock_no="0050", fetch_from=None, scale="day"):
    if scale == "day":
        return _get_stock_pd_in_day(stock_no, fetch_from)
    if scale == "week":
        return _get_stock_pd_in_week(stock_no, fetch_from)
    if scale == "month":
        return _get_stock_pd_in_month(stock_no, fetch_from)

