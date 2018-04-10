import pandas as pd

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
