import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 获取中证1000指数的日线数据
index_df = ak.index_zh_a_hist(symbol="000852", period="daily", start_date="20240101", end_date="20241029")

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

# 计算指数与策略的累积收益
df['cumulative_index_return'] = (1 + df['return']).cumprod() - 1  # 指数累积收益
df['cumulative_strategy_return'] = (1 + df['strategy_return']).cumprod() - 1  # 策略累积收益

# 计算年化收益和波动率以及最大回撤
trading_days_per_year = 252  # 每年交易日数量
annualized_return = df['strategy_return'].mean() * trading_days_per_year  # 策略年化收益率
annualized_volatility = df['strategy_return'].std() * np.sqrt(trading_days_per_year)  # 策略年化波动率
max_drawdown = (df['cumulative_strategy_return'].cummax() - df['cumulative_strategy_return']).max()  # 策略最大回撤

# 输出回测结果
print("Annualized Return:", annualized_return)  # 策略年化收益率
print("Annualized Volatility:", annualized_volatility)  # 策略年化波动率
print("Max Drawdown:", max_drawdown)  # 策略最大回撤

# 绘制指数和策略的累积收益曲线
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['cumulative_index_return'], label='Index Cumulative Return', color='blue')
plt.plot(df.index, df['cumulative_strategy_return'], label='Strategy Cumulative Return', color='orange')
plt.legend()
plt.title("Strategy vs Index Cumulative Return")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.show()

# 绘制每日策略收益率曲线
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['strategy_return'], label='Strategy Daily Return', color='green')
plt.legend()
plt.title("Strategy Daily Return")
plt.xlabel("Date")
plt.ylabel("Daily Return")
plt.show()

# 导出数据到Excel文件
df.to_excel("strategy_backtest_results.xlsx")
