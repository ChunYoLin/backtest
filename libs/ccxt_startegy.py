from libs.strategy import basicStrategy
import backtrader as bt


class S(basicStrategy):
    params = (('fast', 10), ('slow', 100),)

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.sma_fast = bt.indicators.SMA(self.data, period=self.p.fast)
        self.sma_slow = bt.indicators.SMA(self.data, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        self.log(self.dataclose[0], doprint=True)
        if self.order:
            return
        if self.crossover[0] > 0:
            self.order = self.buy()
        if self.crossover[0] < 0:
            self.order = self.sell()
