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
        
class ADX_DI(bt.Indicator):
    lines = ('ADX', 'DIPlus', 'DIMinus')
    params = (('period', 14),)

    def __init__(self):
        self.lines.ADX = bt.indicators.AverageDirectionalMovementIndex(self.data, period=self.p.period) 
        self.lines.DIPlus = bt.indicators.PlusDirectionalIndicator(self.data, period=self.p.period)
        self.lines.DIMinus = bt.indicators.MinusDirectionalIndicator(self.data, period=self.p.period)

class ChipDI(bt.Indicator):
    lines = ('DI',)
    def __init__(self):
        self.lines.DI = self.datas[0].DI

class ChipDealer(bt.Indicator):
    lines = ('Dealer',)
    def __init__(self):
        self.lines.Dealer = self.datas[0].Dealer

class ChipFI(bt.Indicator):
    lines = ('FI',)
    def __init__(self):
        self.lines.FI = self.datas[0].FI
