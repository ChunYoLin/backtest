from fetch_data import get_stock_pd
from strategy import myStrategy
from strategy import ChipStrategy
import backtrader as bt
import sys


class PandasDataBasic(bt.feeds.PandasData):
    lines=('change',)
    params = (('change', 8),)

class PandasDataWithChip(PandasDataBasic):
    lines=('DomInvest', 'InvestTrust', 'ForeignInvest')
    params = (('DomInvest', 9), ('InvestTrust', 10), ('ForeignInvest', 11))

def main():
    cerebro = bt.Cerebro()

    stock_pd = get_stock_pd(sys.argv[1], fetch_from=(2015, 1), scale="day", chip=True)
    data = PandasDataWithChip(
            dataname=stock_pd, 
            volume='capacity',
            change='change'
            )
    
    cerebro.adddata(data)
    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
    cerebro.broker.setcommission(commission=0.003)
    cerebro.addstrategy(ChipStrategy)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade')

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    thestrat = thestrats[0]
    print('Sharpe Ratio:', thestrat.analyzers.trade.get_analysis())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #  cerebro.plot()

if __name__ == '__main__':
    main()
