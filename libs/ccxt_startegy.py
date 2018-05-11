from libs.strategy import basicStrategy
import backtrader as bt
from datetime import timedelta

class TestStrategy(bt.Strategy):
    def next(self):
        data = self.datas[0]
        print('*' * 5, 'NEXT:', bt.num2date(data.datetime[0]), data._name, data.open[0], data.high[0],
                data.low[0], data.close[0], data.volume[0],
                bt.TimeFrame.getname(data._timeframe), len(data))
            #  if not self.getposition(data):
                #  order = self.buy(data, exectype=bt.Order.Limit, size=10, price=data.close[0])
            #  else:
                #  order = self.sell(data, exectype=bt.Order.Limit, size=10, price=data.close[0])
        print(self.position)

    def notify_order(self, order):
        print('*' * 5, "NOTIFY ORDER", order)


class MaCross(basicStrategy):
    params = (('fast', 15), ('slow', 55),)

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume
        self.volume_ma = bt.indicators.SMA(self.volume, period=10)
        self.ema_fast = bt.indicators.EMA(self.dataclose, period=self.p.fast)
        self.ema_slow = bt.indicators.EMA(self.dataclose, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.ema_fast, self.ema_slow)

    def next(self):
        data = self.datas[0]
        dt = bt.num2date(data.datetime[0])
        dt = dt + timedelta(seconds=3600*8)
        print('*' * 5, 'NEXT:', dt, data._name, 
                data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0],
                bt.TimeFrame.getname(data._timeframe), len(data))
        self.log(self.dataclose[0], doprint=False)
        if self.order:
            return
        if not self.position:
            if self.crossover[0] > 0 and self.volume[0] > self.volume_ma[0]:
                self.order = self.buy()
            if self.crossover[0] < 0 and self.volume[0] > self.volume_ma[0]:
                self.order = self.sell()

        elif self.position:
            lost = (self.dataclose[0]-self.position.price)/self.position.price
            if self.position.size > 0:
                if lost < -0.02:
                    self.order = self.close()
                if self.crossover[0] < 0:
                    self.order = self.close()
            elif self.position.size < 0:
                if lost > 0.02:
                    self.order = self.close()
                if self.crossover[0] > 0:
                    self.order = self.close()
    def stop(self):
        self.log('(MA Period fast: %2d, slow: %2d) Ending Value %.2f' %
            (self.params.fast, self.params.slow, self.broker.getvalue()), doprint=True)
