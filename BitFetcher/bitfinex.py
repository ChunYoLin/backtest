# -*- coding: utf-8 -*-

import re
import os
import sys
import time
from datetime import datetime

# -----------------------------------------------------------------------------

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

# -----------------------------------------------------------------------------

import ccxt  # noqa: E402

class BfxFetcher(object):

    def __init__(self, symbol, timescale):
        self.exchange = ccxt.bitfinex({
            'rateLimit': 10000,
            'enableRateLimit': True,
            # 'verbose': True,
            })
        self.symbol = symbol
        self.timescale = timescale
        self.timescale_msec = self._timescale_to_msec()
        self.data = []
    
    def _timescale_to_msec(self):
        msec = 1000
        minute = 60 * msec
        hour = 60 * minute
        day = 24 * hour
        m = re.match("([0-9]+)(.*)", self.timescale)
        assert m
        num = int(m.group(1))
        scale = m.group(2)
        if scale == 'm':
            return num * minute
        elif scale == 'h':
            return num * hour
        elif scale == 'd':
            return num * day
        elif scale == 'M':
            print("not support month scale")
            sys.exit()
        
    
    def fetch_from(self, dt):

        from_datetime = str(dt)
        from_timestamp = self.exchange.parse8601(from_datetime)
        now = self.exchange.milliseconds()
        hold = 30
        while from_timestamp < now:
            try:

                print(self.exchange.milliseconds(), 'Fetching candles starting from', self.exchange.iso8601(from_timestamp))
                ohlcvs = self.exchange.fetch_ohlcv(self.symbol, self.timescale, from_timestamp)
                print(self.exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')
                first = ohlcvs[0][0]
                last = ohlcvs[-1][0]
                print('First candle epoch', first, self.exchange.iso8601(first))
                print('Last candle epoch', last, self.exchange.iso8601(last))
                from_timestamp += len(ohlcvs) * self.timescale_msec
                self.data += ohlcvs

            except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:

                print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
                time.sleep(hold)
