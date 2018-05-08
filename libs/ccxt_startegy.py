from libs.strategy import basicStrategy
import backtrader as bt


class MaCross(basicStrategy):
    params = (('fast', 5), ('slow', 60),)

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume
        self.volume_ma = bt.indicators.SMA(self.volume, period=10)
        self.ema_fast = bt.indicators.EMA(self.data, period=self.p.fast)
        self.ema_slow = bt.indicators.EMA(self.data, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.ema_fast, self.ema_slow)

    def next(self):
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
