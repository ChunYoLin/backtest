from datetime import datetime
from datetime import date
import pandas as pd
import sys

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

def _get_chip_info_pd_months(stock_no="0050", start_date=None):
    if start_date == None:
        print("please specify the start date")
        sys.exit(0)

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
    df.columns = ['DomInvest', 'InvestTrust', 'ForeignInvest ']
    return df
    
