import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

class basic_strategy(bt.Strategy):
    params = (
        ('exitbars', 5),
        ('printlog', False),
        ('maperiod_fast', 10),
        ('maperiod_slow', 30),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.ema_fast = bt.indicators.ExponentialMovingAverage(
                self.datas[0], period=self.params.maperiod_fast)
        self.ema_slow = bt.indicators.ExponentialMovingAverage(
                self.datas[0], period=self.params.maperiod_slow)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
        # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                       'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                       (order.executed.price,
                        order.executed.value,
                        order.executed.comm,),
                        doprint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            elif order.issell():
                self.log(
                       'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                       (order.executed.price,
                        order.executed.value,
                        order.executed.comm),
                        doprint=True)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                (trade.pnl, trade.pnlcomm), doprint=True)

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        if not self.position:
            if self.ema_fast[0] > self.ema_slow[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.ema_fast[0] < self.ema_slow[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period fast %2d) (MA Period slow %2d) Ending Value %.2f' %
               (self.params.maperiod_fast,
                self.params.maperiod_slow, 
                self.broker.getvalue()), 
                doprint=True)

