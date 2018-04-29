from fetcher.fetch_data import get_stock_pd
from libs.strategy import myStrategy
from libs.strategy import ChipStrategy
import backtrader as bt
import sys


class PandasDataBasic(bt.feeds.PandasData):
    lines=('change',)
    params = (('change', 8),)

class PandasDataWithChip(PandasDataBasic):
    lines=('DomInvest', 'InvestTrust', 'ForeignInvest')
    params = (('DomInvest', 9), ('InvestTrust', 10), ('ForeignInvest', 11))

def main():
    stock_pd = get_stock_pd(sys.argv[1], fetch_from=(2013, 1), scale="D", chip=True, mode="dynamic", update=True)
    data = PandasDataWithChip(
            dataname=stock_pd, 
            volume='capacity',
            )
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
    cerebro.broker.setcommission(commission=0.003)
    cerebro.addstrategy(ChipStrategy)
    cerebro.addanalyzer(bt.analyzers.SQN, _name='SQN')
    #  cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='Trade')
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrat = thestrats[0]
    print(thestrat.analyzers.SQN.get_analysis())
    #  print(thestrat.analyzers.Trade.get_analysis())
    cerebro.plot()

if __name__ == '__main__':
    main()
