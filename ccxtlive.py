from BitFetcher.bitfinex import BfxFetcher
from libs.ccxt_startegy import MaCross, TestStrategy

import backtrader as bt
import ccxt
import pandas as pd

import time
from datetime import datetime, timedelta

def main():
    cerebro = bt.Cerebro()
    exchange = 'poloniex'
    symbol = "BTC/USDT"
    # Create data
    hist_start_date = datetime.utcnow() - timedelta(days=2)
    data = bt.feeds.CCXT(
            exchange=exchange,
            symbol=symbol,
            timeframe=bt.TimeFrame.Minutes,
            compression=30,
            fromdate=hist_start_date,
            )
    cerebro.adddata(data)
    # Create broker
    broker_config = {
            'apiKey': 'EPVO08EX-PKVA9TJG-M32OZ7VC-VSUIPK0U',
            'secret': '50a04da13773071fa7349f843aea59810104c78ac4ff7e62cec406a2b3c2b707879aa03d47dfcaad307865cdb2d470b5ed72612b18fa954ee95ea7842004fe80',
            'nonce': lambda: str(int(time.time() * 1000))
            }
    broker = bt.brokers.CCXTBroker(
            exchange=exchange, 
            currency='USDT', 
            config=broker_config
            )
    cerebro.setbroker(broker)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.addstrategy(TestStrategy)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrat = thestrats[0]
    cerebro.plot()

if __name__ == '__main__':
    main()
