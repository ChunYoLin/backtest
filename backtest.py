from fetch_data import get_stock_pd
import backtrader as bt

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    stock_pd = get_stock_pd('2454')
    data = bt.feeds.PandasData(
            dataname=stock_pd, 
            volume='transaction'
            )
    
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

