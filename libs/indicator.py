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

class ContinuousBool(bt.Indicator):
    lines = ('ContinuousBool',)
    params = (('period', 3), ('function', lambda x: x>0),)

    def next(self):
        self.lines.ContinuousBool[0] = all(map(self.p.function, self.datas[0].get(size=self.p.period)))

class ForceIndex(bt.Indicator):
    lines = ('ForceIndex', )
    
    def next(self):
        self.lines.ForceIndex[0] = (self.data.close[0]-self.data.close[-1])/(self.data.volume[0] + 0.00000001)
