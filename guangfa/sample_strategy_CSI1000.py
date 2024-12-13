# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 22:09:16 2024

@author: luzm8
"""
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt

df = ak.stock_zh_index_daily(symbol="sh000852")
df = df.sort_index()
df.set_index('date', inplace=True)

df['return'] = df['close'].pct_change()

def rsi_strategy(df):
    # 计算价格变化
    price_change = df['close'].diff()
    # 区分上涨和下跌的价格变化
    up = [max(change, 0) for change in price_change]
    down = [abs(min(change, 0)) for change in price_change]
    # 计算平均上涨和平均下跌
    window = 10
    avg_up = [sum(up[max(0, i - window + 1):i + 1]) / min(i + 1, window) if i >= window - 1 else sum(up[:i + 1]) / (i + 1) for i in range(len(up))]
    avg_down = [sum(down[max(0, i - window + 1):i + 1]) / min(i + 1, window) if i >= window - 1 else sum(down[:i + 1]) / (i + 1) for i in range(len(down))]
    # 计算相对强弱指数 RSI
    rs = [up_value / down_value if down_value > 0 else 0 for up_value, down_value in zip(avg_up, avg_down)]
    rsi = [100 - (100 / (1 + r_value)) if r_value > 0 else 0 for r_value in rs]
    df['rsi'] = rsi
    return df
df = rsi_strategy(df)


#策略一：突破前高/低、均线与RSI结合策略
cycle=4
df['ma'] = df['close'].rolling(window=cycle).mean()

df['signal1'] = 0
df.loc[(df['close']>df['ma'])
       &(df['rsi']<85), 'signal1'] = 1
df.loc[(df['close']<df['ma'])
       &(df['rsi']>15), 'signal1'] = 0
df.loc[(df['rsi']<5), 'signal1'] = 1
df.loc[(df['rsi']>95), 'signal1'] = 0

# 计算每日收益率，并创建一个新的列来存储它们

df['Strategy Returns']  = df['return'] * df['signal1'].shift(1)

# 计算累积收益率，并创建一个新的列来存储它
df['Cumulative Returns'] = (1 + df['Strategy Returns']-0.000023).cumprod()-1  # 计算累积收益率
df['cum_NV'] = (1 + df['Strategy Returns']-0.000023).cumprod().ffill()
df['max_drawdown'] = (df['cum_NV'].cummax() - df['cum_NV']) / df['cum_NV'].cummax()
df['index_return'] = df['close']/df['close'].iloc[0]-1

# 输出交易结果
pd.set_option('expand_frame_repr', False)
print(df[-50:])
# 计算每个周期的胜率和盈亏比
period_returns1 = df['Strategy Returns'][df['signal1'].shift(1) != 0]
period_wins1 = period_returns1[period_returns1 > 0]
period_losses1 = period_returns1[period_returns1 < 0]
win_rate1 = len(period_wins1) / len(period_returns1)
loss_rate1 = len(period_losses1) / len(period_returns1)
win_loss_ratio1 = -period_wins1.mean() / period_losses1.mean()

print("Win Rate1: {:.2%}".format(win_rate1))
print("Loss Rate1: {:.2%}".format(loss_rate1))
print("Win/Loss Ratio1: {:.2f}".format(win_loss_ratio1))

print("Cumulative Returns: {:.2%}".format(df['Cumulative Returns'].iloc[-1]))
print('Max Drawdown: {:.2%}'.format(df['max_drawdown'].max()))

# 绘制累积收益率的时间序列图
plt.figure(figsize=(28, 8))
plt.plot(df['Cumulative Returns'], label='Cumulative Returns')
plt.plot(df['index_return'], label='Index_return' )
plt.title('Cumulative Returns')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.legend()
plt.grid(True) 
plt.show()

df.to_excel('中证1000_result.xlsx')



