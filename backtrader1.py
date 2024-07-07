from datetime import datetime
import backtrader as bt
import matplotlib.pyplot as plt
import akshare as ak
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# Fetch the stock data
stock_hfq_df = ak.stock_zh_a_hist(symbol="000001", adjust="hfq").iloc[:, :6]
# Rename columns
stock_hfq_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
# Convert 'date' column to datetime
stock_hfq_df['date'] = pd.to_datetime(stock_hfq_df['date'])
# Set 'date' column as the index
stock_hfq_df.set_index('date', inplace=True)
# Convert relevant columns to numeric data types
stock_hfq_df[['open', 'close', 'high', 'low', 'volume']] = stock_hfq_df[['open', 'close', 'high', 'low', 'volume']].apply(pd.to_numeric)

class MyStrategy(bt.Strategy):
    params = (("maperiod", 20),)

    def __init__(self):
        self.data_close = self.datas[0].close
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

    def next(self):
        if self.order:
            return
        if not self.position:
            if self.data_close[0] > self.sma[0]:
                self.order = self.buy(size=100)
        else:
            if self.data_close[0] < self.sma[0]:
                self.order = self.sell(size=100)

cerebro = bt.Cerebro()
start_date = datetime(2020, 4, 3)
end_date = datetime(2020, 6, 16)
data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=start_date, todate=end_date)
cerebro.adddata(data)
cerebro.addstrategy(MyStrategy)
start_cash = 1000000
cerebro.broker.setcash(start_cash)
cerebro.broker.setcommission(commission=0.002)
cerebro.run()

port_value = cerebro.broker.getvalue()
pnl = port_value - start_cash
print(f"初始资金: {start_cash}\n回测期间：{start_date.strftime('%Y%m%d')}:{end_date.strftime('%Y%m%d')}")
print(f"总资金: {round(port_value, 2)}")
print(f"净收益: {round(pnl, 2)}")

cerebro.plot(style='candlestick')
