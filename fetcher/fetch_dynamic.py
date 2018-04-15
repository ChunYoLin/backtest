from collections import namedtuple
from datetime import datetime
from datetime import date
import csv
import os.path
import sys

from twstock import Stock


database_path = "/home/chunyo/work/backtest/database/"
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

def get_twstock(stock_no="0050", fetch_from=None):
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

