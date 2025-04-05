import akshare as ak
import pandas as pd

weipan_df = ak.stock_board_industry_index_ths(symbol="元件", start_date="20240101", end_date="20241231")
print(weipan_df)

# 确认列名并重命名
weipan_df.rename(columns={'日期': 'date', '收盘价': 'close'}, inplace=True)

# 确保 'date' 列存在
weipan_df['date'] = pd.to_datetime(weipan_df['date'])

# 设置索引
weipan_df.set_index('date', inplace=True)
weipan_df['change_pct'] = weipan_df['close'].pct_change() * 100  # 转换为百分比

# 提取日期、信号和收盘价数据
dates = weipan_df.index  # 日期作为索引后，直接使用 index
strategy = weipan_df['change_pct']  # 涨跌幅
hs300_close = weipan_df['close']  # 收盘价

# 初始化变量
position = 0  # 持仓状态，1 表示持仓，0 表示空仓
entry_price = 0  # 建仓价格
returns = []  # 存储每次交易的收益记录
sig = 0.5

# 遍历选样数据进行回测
for i in range(len(dates)):
    date = dates[i]
    signal = strategy.iloc[i]

    close_price = hs300_close.iloc[i]

    if position == 0 and signal >= sig:  # 空仓且当日中证1000涨跌幅大于0.5%
        # 开仓：买入
        position = 1
        entry_price = close_price
        print(f"[{date}] 开仓，开仓价: {entry_price}")

    elif position == 1 and signal < sig:  # 持仓且当日中证1000涨跌幅小于0.5%
        # 平仓：卖出多头
        profit = (close_price - entry_price) / entry_price
        returns.append(profit)
        position = 0
        print(f"[{date}] 平仓，平仓价: {close_price}，收益率: {profit:.2%}")

# 计算总收益
cumulative_returns = (1 + pd.Series(returns)).cumprod()

# 总收益率的最后一个值
final_cumulative_return = cumulative_returns.iloc[-1] - 1  # 从 Series 中提取最后一个值

print(f"总收益率: {final_cumulative_return:.2%}")

# 计算最大回撤
drawdowns = cumulative_returns / cumulative_returns.cummax() - 1
max_drawdown = drawdowns.min()

# 打印最大回撤
print(f"最大回撤: {max_drawdown:.2%}")