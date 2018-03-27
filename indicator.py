import backtrader as bt


class ChangePerVolume(bt.Indicator):
    lines = ('cpv',)

    def __init__(self):
        self.lines.cpv = self.datas[0].change / self.datas[0].volume

class RelativePriceLevel(bt.Indicator):
    lines = ('rpl',)
    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.talib.SMA(self.data, timeperiod=self.p.period)
        self.lines.rpl = self.datas[0].close - self.sma
        

