# -*- coding: utf-8 -*-

import datetime
import json
import urllib.parse
from collections import namedtuple
import sys

import requests

import pandas as pd

TWSE_BASE_URL = 'http://www.twse.com.tw/'
TPEX_BASE_URL = 'http://www.tpex.org.tw/'

class ChipFetcher(object):
    REPORT_URL = urllib.parse.urljoin(TWSE_BASE_URL, 'fund/T86')

    def __init__(self):
        self.df = None

    def fetch(self, year, month, day, sid, retry=5):
        params = {'date': '%d%02d%02d' % (year, month, day), 'selectType': "ALL"}
        r = requests.get(self.REPORT_URL, params=params)
        if sys.version_info < (3, 5):
            try:
                data = r.json()
            except ValueError:
                if retry:
                    return self.fetch(year, month, day, sid, retry - 1)
                data = {'stat': '', 'data': []}
        else:
            try:
                data = r.json()
            except json.decoder.JSONDecodeError:
                if retry:
                    return self.fetch(year, month, day, sid, retry - 1)
                data = {'stat': '', 'data': []}

        if data["stat"] == 'OK':
            if self.df is None:
                self.df = pd.DataFrame(data["data"], columns = data["fields"])
                self.df = self.df[self.df["證券代號"] == sid]
                self.df["date"] = datetime.datetime(year, month, day)
            else:
                df = pd.DataFrame(data["data"], columns = data["fields"])
                df = df[df["證券代號"] == sid]
                df["date"] = datetime.datetime(year, month, day)
                self.df = self.df.append(df, ignore_index=True)

