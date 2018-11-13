from BitFetcher.BitFetcher import BitFetcher
from libs.ccxt_startegy import MaCross

import backtrader as bt
import ccxt
import pandas as pd
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo

import datetime
from datetime import datetime, timedelta


def main():
    poloFetcher = BitFetcher("poloniex", 'ETH/BTC', '30m')
    poloFetcher.fetch_from(datetime(2016, 5, 1))
    data = poloFetcher.data
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
    cerebro.broker.setcash(0.0108)
    cerebro.broker.setcommission(commission=0.003)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
    cerebro.addstrategy(MaCross)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="Trade")
    print('Starting Portfolio Value: %.8f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()

    print('Final Portfolio Value: %.8f' % cerebro.broker.getvalue())
    thestrat = thestrats[0]
    trade_analyze = thestrat.analyzers.Trade.get_analysis()
    for key, value in trade_analyze.items():
        print(key, value)
    cerebro.plot()

if __name__ == '__main__':
    main()
