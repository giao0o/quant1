import akshare as ak
import pandas as pd
import numpy as np

# Get Trading Data of Sanfo Outdoor 002780
stock_data = ak.stock_zh_a_hist(symbol='301125', period='daily', start_date='20220630', end_date='20241231', adjust="qfq")

# 确认列名并重命名
stock_data.rename(columns={'日期': 'date', '涨跌幅': 'change_pct', '收盘': 'close'}, inplace=True)

# 确保 'date' 列存在
stock_data['date'] = pd.to_datetime(stock_data['date'])

# 设置索引
stock_data.set_index('date', inplace=True)

# 提取必要数据
dates = stock_data.index
strategy = stock_data['change_pct']
stock_close = stock_data['close']

# 定义一个函数进行回测
def backtest(sig):
    position = 0  # 持仓状态
    entry_price = 0  # 建仓价格
    trades = []  # 存储每次交易的日期和收益

    for i in range(len(dates)):
        date = dates[i]
        signal = strategy.iloc[i]
        close_price = stock_close.iloc[i]

        if position == 0 and signal >= sig:  # 开仓条件
            position = 1
            entry_price = close_price

        elif position == 1 and signal < sig:  # 平仓条件
            profit = (close_price - entry_price) / entry_price
            trades.append({'date': date, 'profit': profit})
            position = 0

    # 如果没有交易，返回空的 DataFrame
    if not trades:
        return pd.DataFrame(columns=['date', 'profit'])

    # 转换交易记录为 DataFrame
    trades_df = pd.DataFrame(trades)
    trades_df['year'] = trades_df['date'].dt.year  # 添加年份列
    return trades_df

# 测试不同的 sig 值
sig_values = np.arange(1.5, 2.5, 0.1).tolist()
yearly_results = {}

for sig in sig_values:
    trades_df = backtest(sig)

    # 按年统计收益率
    if not trades_df.empty:
        yearly_returns = trades_df.groupby('year')['profit'].sum()  # 按年求和
        yearly_results[sig] = yearly_returns
    else:
        yearly_results[sig] = pd.Series([], dtype='float64')

# 汇总所有 sig 值的年收益率
yearly_results_df = pd.DataFrame(yearly_results).fillna(0)

# 打印每年的收益率
print("Yearly Returns for Different Sig Values:")
print(yearly_results_df)

# 计算总收益率
total_returns = yearly_results_df.sum(axis=0)
print("\nTotal Returns for Different Sig Values:")
print(total_returns)
