import sys

import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
import quandl

from btgym import BTgymEnv


class MyTest(bt.Strategy):
    params = (('fast', 20), ('slow', 60),)

    def __init__(self):
        self.sma_fast = btind.SMA(period=self.p.fast)
        self.sma_slow = btind.SMA(period=self.p.slow)
        self.sma_cross = btind.CrossOver(self.sma_fast, self.sma_slow)

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                stop_loss = order.executed.price * 0.98
                sl_ord = self.sell(data=order.data,
                                   exectype=bt.Order.Stop,
                                   price=stop_loss)

    def next(self):
        if (self.sma_cross[0] == 1):
            self.buy()
        if (self.sma_cross[0] == -1):
            self.close()


def main():
    quandl.ApiConfig.api_key = '9rtGDsF3JKZLcWAxGbY5'
    data = quandl.get_table('WIKI/PRICES', ticker=['NVDA'], date={'gte': '2000-12-31', 'lte': '2018-12-31'})
    data = data.sort_values(by="date")
    bt_data = bt.feeds.PandasData(dataname=data, datetime="date", open="adj_open", high="adj_high", close="adj_close", low="adj_low", volume="adj_volume")
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100.0)
    cerebro.adddata(bt_data)
    cerebro.addstrategy(MyTest)
    BTgymEnv(engine=cerebro)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()


if __name__ == '__main__':
    main()
