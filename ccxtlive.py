from BitFetcher.bitfinex import BfxFetcher
from libs.ccxt_startegy import MaCross, TestStrategy

import backtrader as bt
import ccxt
import pandas as pd

from datetime import datetime, timedelta

def main():
    cerebro = bt.Cerebro()
    symbol = "BTC/USD"
    hist_start_date = datetime.utcnow() - timedelta(days=5)
    data = bt.feeds.CCXT(exchange='bitfinex',
            symbol=symbol,
            timeframe=bt.TimeFrame.Minutes,
            compression=30,
            fromdate=hist_start_date,
            config={'rateLimit': 10000}
            )
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.003)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.addstrategy(TestStrategy)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrat = thestrats[0]
    cerebro.plot()

if __name__ == '__main__':
    main()
