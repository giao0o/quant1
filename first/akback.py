from datetime import datetime
import akshare as ak
import backtrader as bt
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

class MyStrategy(bt.Strategy):
    params = (("maperiod", 20), ('printlog', False),)

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
                self.log("BUY CREATE, %.2f" % self.data_close[0])
                self.order = self.buy()
        else:
            if self.data_close[0] < self.sma[0]:
                self.log("SELL CREATE, %.2f" % self.data_close[0])
                self.order = self.sell()

    def log(self, txt, dt=None, do_print=False):
        if self.params.printlog or do_print:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"买入:\n价格:{order.executed.price}, 成本:{order.executed.value}, 手续费:{order.executed.comm}")
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f"卖出:\n价格：{order.executed.price}, 成本: {order.executed.value}, 手续费:{order.executed.comm}")
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("交易失败")
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f"策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}")

    def stop(self):
        self.log("(MA均线： %2d日) 期末总资金 %.2f" % (self.params.maperiod, self.broker.getvalue()), do_print=True)


def main(code="600070", start_cash=1000000, stake=100, commission_fee=0.001):
    cerebro = bt.Cerebro()
    cerebro.optstrategy(MyStrategy, maperiod=range(3, 31))

    stock_hfq_df = ak.stock_zh_a_hist(symbol=code, adjust="hfq", start_date='20000101', end_date='20210617').iloc[:, :6]
    stock_hfq_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    stock_hfq_df[['open', 'close', 'high', 'low', 'volume']] = stock_hfq_df[['open', 'close', 'high', 'low', 'volume']].astype(float)
    stock_hfq_df.index = pd.to_datetime(stock_hfq_df['date'])
    stock_hfq_df.drop(columns=['date'], inplace=True)

    start_date = datetime(2000, 1, 1)  # 回测开始时间
    end_date = datetime(2021, 6, 16)  # 回测结束时间
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=start_date, todate=end_date)
    cerebro.adddata(data)
    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=commission_fee)
    cerebro.addsizer(bt.sizers.FixedSize, stake=stake)
    
    print("期初总资金: %.2f" % cerebro.broker.getvalue())
    cerebro.run(maxcpus=1)
    print("期末总资金: %.2f" % cerebro.broker.getvalue())

if __name__ == '__main__':
    main(code="600070", start_cash=1000000, stake=100, commission_fee=0.001)
