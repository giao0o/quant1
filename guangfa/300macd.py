import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 获取沪深300指数历史数据（使用通用指数数据，时间跨度较长）
index_df = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20050101", end_date="20241029")

# 数据预处理
index_df['日期'] = pd.to_datetime(index_df['日期'])
index_df.set_index('日期', inplace=True)
df = index_df[['收盘']].copy()
df.rename(columns={'收盘': 'close_price'}, inplace=True)

# 计算 MACD 指标
short_window = 12
long_window = 26
signal_window = 9

df['EMA_12'] = df['close_price'].ewm(span=short_window, adjust=False).mean()
df['EMA_26'] = df['close_price'].ewm(span=long_window, adjust=False).mean()
df['DIF'] = df['EMA_12'] - df['EMA_26']  # 计算 DIF
df['DEA'] = df['DIF'].ewm(span=signal_window, adjust=False).mean()  # 计算 DEA
df['MACD'] = df['DIF'] - df['DEA']  # 计算 MACD

# 生成买卖信号
df['signal'] = 0
df.loc[df['DIF'] > df['DEA'], 'signal'] = 1  # 金叉信号
df.loc[df['DIF'] < df['DEA'], 'signal'] = -1  # 死叉信号
df['signal'] = df['signal'].shift(1)  # 避免未来数据偏差

# 计算策略每日收益率
df['return'] = df['close_price'].pct_change()  # 计算每日收益率
df['strategy_return'] = df['signal'] * df['return']  # 策略收益

# 设置初始资金
initial_capital = 1000000  # 初始资金 1,000,000 元
df['portfolio_value'] = initial_capital * (1 + df['strategy_return']).cumprod()

# 输出最终资金
final_capital = df['portfolio_value'].iloc[-1]
print("Initial Capital:", initial_capital)
print("Final Capital:", final_capital)

# 绘制策略表现
plt.figure(figsize=(14, 7))
plt.plot(df.index, (1 + df['return']).cumprod() * initial_capital, label='Market Portfolio', color='blue')
plt.plot(df.index, df['portfolio_value'], label='MACD Strategy Portfolio', color='orange')
plt.xlabel('Date')
plt.ylabel('Portfolio Value (RMB)')
plt.legend()
plt.title("MACD Strategy Backtest on CSI 300 Index Over 10+ Years")
plt.show()
