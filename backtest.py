from fetch_data import get_stock_pd
from strategy import basic_strategy
import backtrader as bt
import sys


class myPandasData(bt.feeds.PandasData):
    lines=('change', 'DI', 'Dealer', 'FI')
    params = (('change', 8), ('DI', 9), ('Dealer', 10), ('FI', 11))


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    stock_pd = get_stock_pd(sys.argv[1], fetch_from=(2015, 1), scale="day")
    data =  myPandasData(
            dataname=stock_pd, 
            volume='capacity',
            change='change'
            )
    
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
    cerebro.broker.setcommission(commission=0.003)
    cerebro.addstrategy(basic_strategy)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    #  cerebro.plot()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
