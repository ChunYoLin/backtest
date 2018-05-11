from BitFetcher.bitfinex import BfxFetcher
from libs.ccxt_startegy import MaCross

import backtrader as bt
import ccxt
import pandas as pd

from datetime import datetime, timedelta

def main():
    bfxfetcher = BfxFetcher('BTC/USD', '30m')
    bfxfetcher.fetch_from(datetime(2018, 5, 1))
    data = bfxfetcher.data
    header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    data_pd = pd.DataFrame(data, columns=header)
    data_pd['Timestamp'] = pd.to_datetime(data_pd['Timestamp'], unit='ms')
    data_pd = data_pd.set_index('Timestamp')
    datafeed = bt.feeds.PandasData(
            dataname=data_pd,
            open="Open",
            high="High",
            close="Close",
            low="Low",
            volume="volume"
            )

    cerebro = bt.Cerebro()
    cerebro.adddata(datafeed)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.003)
    #  cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    #  strats = cerebro.optstrategy(
            #  MaCross,
            #  fast=range(13, 16),
            #  slow=range(50, 61))
    cerebro.addstrategy(MaCross)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrat = thestrats[0]
    #  print(thestrat.analyzers.SQN.get_analysis())
    #  print(thestrat.analyzers.Trade.get_analysis())
    cerebro.plot()

if __name__ == '__main__':
    main()
