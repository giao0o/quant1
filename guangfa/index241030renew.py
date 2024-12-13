import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 获取中证1000指数的日线数据
index_df = ak.index_zh_a_hist(symbol="000852", period="daily", start_date="20050101", end_date="20241029")

# 将日期列转换为日期格式
index_df['日期'] = pd.to_datetime(index_df['日期'])

# 将日期列设置为索引
index_df.set_index('日期', inplace=True)

# 仅提取收盘价，并将其复制为新的数据框
df = index_df[['收盘']].copy()

# 重命名收盘价列为“close”以便后续计算
df.rename(columns={'收盘': 'close'}, inplace=True)

# 计算每日收益率
df['return'] = df['close'].pct_change()

# 计算5日均线
df['ma_long_period'] = df['close'].rolling(window=5).mean()

# 计算10日波动率（标准差）
df['sigma'] = df['close'].rolling(window=10).std()

# 计算8日动量（收益率之和）
df['Momentum1'] = df['return'].rolling(window=8).sum()

# 参数设置
threshold1 = 0  # 阈值1
threshold2 = 0  # 阈值2
multiplier = 3  # 波动率倍数

# 生成交易信号（根据策略规则）
df['signal'] = 0
df.loc[((df['close'] > df['ma_long_period'] * (1 + threshold1)) | (df['Momentum1'] > threshold2))
       & (df['close'] < df['ma_long_period'] + df['sigma'] * multiplier), 'signal'] = 1  # 买入信号
df.loc[((df['close'] < df['ma_long_period'] * (1 - threshold1)) | (df['Momentum1'] < -threshold2))
       & (df['close'] > df['ma_long_period'] - df['sigma'] * multiplier), 'signal'] = -1  # 卖出信号
df.loc[(df['close'] > df['ma_long_period'] + df['sigma'] * multiplier), 'signal'] = -1  # 超买，产生卖出信号
df.loc[(df['close'] < df['ma_long_period'] - df['sigma'] * multiplier), 'signal'] = 1  # 超卖，产生买入信号
df['signal'] = df['signal'].shift(1)  # 信号前移1天，避免未来数据偏差

# 根据每日持仓信号与每日收益率计算策略每日收益率
df['strategy_return'] = df['signal'] * df['return']

# 设置初始资金
initial_capital = 1000000  # 初始资金 1,000,000 元

# 将每日收益率的 NaN 值（首行）填充为 0
df['return'] = df['return'].fillna(0)

# 计算指数累积收益
df['cumulative_index_return'] = (1 + df['return']).cumprod() - 1

# 计算每日策略资金变化
df['portfolio_value'] = initial_capital * (1 + df['strategy_return']).cumprod()

# 提取最终资金值
final_capital = df['portfolio_value'].iloc[-1]  # 最终资金

# 输出初始资金和最终资金值
print("Initial Capital:", initial_capital)  # 初始资金
print("Final Capital:", final_capital)  # 最终资金

# 绘制指数和策略的累积收益曲线
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['cumulative_index_return'], label='Index Cumulative Return', color='blue')
plt.plot(df.index, df['portfolio_value'] / initial_capital - 1, label='Strategy Cumulative Return', color='orange')
plt.title("Strategy vs. Index Cumulative Return")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.show()

# 绘制策略每日收益曲线
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['strategy_return'], label='Strategy Daily Return', color='green')
plt.title("Strategy Daily Returns Over Time")
plt.xlabel("Date")
plt.ylabel("Daily Return")
plt.legend()
plt.show()

# 导出数据到Excel文件
df.to_excel("strategy_backtest_results.xlsx", sheet_name="Backtest Results")

# 将结果输出到Excel，包含每日收益和累积收益
output_columns = ['close', 'return', 'strategy_return', 'cumulative_index_return', 'portfolio_value']
df[output_columns].to_excel("strategy_backtest_results.xlsx", sheet_name="Backtest Detailed Results")
