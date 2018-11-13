from libs.strategy import basicStrategy
import libs.indicator as ind 
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
    params = (('fast', 19), ('slow', 39),)

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume
        self.volume_ma = bt.indicators.SMA(self.volume, period=10)
        self.ema_fast = bt.indicators.EMA(self.dataclose, period=self.p.fast)
        self.ema_slow = bt.indicators.EMA(self.dataclose, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.ema_fast, self.ema_slow)
        self.ADX_DI = ind.ADX_DI(self.datas[0])
        self.ADX = self.ADX_DI.ADX
        self.DIPlus = self.ADX_DI.DIPlus
        self.DIMinus = self.ADX_DI.DIMinus
        self.FI = ind.ForceIndex(self.data)
        self.FI2 = bt.indicators.EMA(self.FI, period=2)
        self.FI13 = bt.indicators.EMA(self.FI, period=13)

    def next(self):
        data = self.datas[0]
        dt = bt.num2date(data.datetime[0])
        dt = dt + timedelta(seconds=3600*8)
        #  print('*' * 5, 'NEXT:', dt, data._name, 
                #  data.open[0], data.high[0], data.low[0], data.close[0], data.volume[0],
                #  bt.TimeFrame.getname(data._timeframe), len(data))
        if self.order:
            return
        ADX_slope_positive = (self.ADX[0] - self.ADX[-5]) > 0
        DIP_slope_positive = (self.DIPlus[0] - self.DIPlus[-5]) > 0
        DIM_slope_positive = (self.DIMinus[0] - self.DIMinus[-5]) > 0
        crossover_pos_in_period = 1.0 in self.crossover.get(size=5) 
        crossover_neg_in_period = -1.0 in self.crossover.get(size=5)
        if not self.position:
            if (crossover_pos_in_period and 
                    self.volume[0] > self.volume_ma[0] and 
                    ADX_slope_positive and
                    DIP_slope_positive):
                self.order = self.buy()
            if (crossover_neg_in_period and 
                    self.volume[0] > self.volume_ma[0] and 
                    ADX_slope_positive and 
                    DIM_slope_positive):
                self.order = self.sell()

        elif self.position:
            price_diff_rate = (self.dataclose[0]-self.position.price)/self.position.price
            if self.position.size > 0:
                if price_diff_rate < -0.02 or price_diff_rate > 0.08:
                    self.order = self.close()
                if self.crossover[0] < 0:
                    self.order = self.close()
            elif self.position.size < 0:
                if price_diff_rate > 0.02 or price_diff_rate < -0.08:
                    self.order = self.close()
                if self.crossover[0] > 0:
                    self.order = self.close()
    def stop(self):
        self.log('(MA Period fast: %2d, slow: %2d) Ending Value %.8f' %
            (self.params.fast, self.params.slow, self.broker.getvalue()), doprint=True)
