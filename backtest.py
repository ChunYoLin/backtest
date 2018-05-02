from fetcher.fetch_data import get_stock_pd
from libs.strategy import myStrategy
from libs.strategy import ChipStrategy
import backtrader as bt
import ccxt
import pandas as pd

from datetime import datetime, timedelta

if __name__ == '__main__':
    symbol = str('BTC/USDT')
    timeframe = str('4h')
    exchange = str('poloniex')
    exchange_out = str(exchange)
    start_date = str('2018-1-16 00:00:00')
    end_date = str('2018-3-17 19:00:00')

    # Get our Exchange
    exchange = getattr(ccxt, exchange)()
    exchange.load_markets()

    def to_unix_time(timestamp):
        epoch = datetime.utcfromtimestamp(0)  # start of epoch time
        my_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")  # plugin your time object
        delta = my_time - epoch
        return delta.total_seconds() * 1000

    hist_start_date = int(to_unix_time(start_date))
    hist_end_date = int(to_unix_time(end_date))
    data = exchange.fetch_ohlcv(symbol, timeframe, since=hist_start_date, limit=hist_end_date)
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
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.addstrategy(basic_strategy)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrat = thestrats[0]
    print(thestrat.analyzers.SQN.get_analysis())
    #  print(thestrat.analyzers.Trade.get_analysis())
    cerebro.plot()

if __name__ == '__main__':
    main()
