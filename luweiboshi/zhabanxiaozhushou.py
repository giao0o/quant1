import akshare as ak
import pandas as pd

# 获取个股数据
stock_data = ak.stock_zh_a_hist(symbol='002780', period='daily', start_date='20170101', end_date='20250124', adjust="qfq")
print(stock_data.head())

# 确认列名并重命名
stock_data.rename(columns={'日期': 'date', '涨跌幅': 'change_pct', '收盘': 'close'}, inplace=True)

# 确保 'date' 列存在
stock_data['date'] = pd.to_datetime(stock_data['date'])

# 设置索引
stock_data.set_index('date', inplace=True)

# 提取日期、信号和收盘价数据
dates = stock_data.index  # 日期作为索引后，直接使用 index
strategy = stock_data['change_pct']  # 涨跌幅
stock_close = stock_data['close']  # 收盘价

# 初始化变量
position = 0  # 持仓状态，1 表示持仓，0 表示空仓
entry_price = 0  # 建仓价格
returns = []  # 存储每次交易的收益记录
sig = 9.9  # 涨幅超过9.9%时候买入（打板）

# 遍历选样数据进行回测
for i in range(len(dates)):
    date = dates[i]
    signal = strategy.iloc[i]

    close_price = stock_close.iloc[i]

    if position == 0 and signal >= sig:  # 空仓且当日个股涨跌幅
        # 开仓：买入
        position = 1
        entry_price = close_price
        print(f"[{date}] 开仓，开仓价: {entry_price}")

    elif position == 1 and signal < sig:  # 持仓，尾盘卖出
        # 平仓：卖出多头
        profit = (close_price - entry_price) / entry_price
        returns.append(profit)
        position = 0
        print(f"[{date}] 平仓，平仓价: {close_price}，收益率: {profit:.2%}")

# 计算总收益
cumulative_returns = (1 + pd.Series(returns)).cumprod()

# 总收益率的最后一个值
final_cumulative_return = cumulative_returns.iloc[-1] - 1 if not cumulative_returns.empty else 0  # 避免空值错误

print(f"总收益率: {final_cumulative_return:.2%}")

# 计算最大回撤
if not cumulative_returns.empty:
    drawdowns = cumulative_returns / cumulative_returns.cummax() - 1
    max_drawdown = drawdowns.min()
else:
    max_drawdown = 0

# 打印最大回撤
print(f"最大回撤: {max_drawdown:.2%}")
