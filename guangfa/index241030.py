import akshare as ak
import pandas as pd

# 获取中证1000指数（000852.SH）的日线数据
index_df = ak.index_zh_a_hist(symbol="000852", period="daily", start_date="20200101", end_date="20231029")

# 确认数据结构
print(index_df.columns)

# 将“日期”列转换为日期格式，并将其设为索引
index_df['日期'] = pd.to_datetime(index_df['日期'])
index_df.set_index('日期', inplace=True)

# 选择我们需要的收盘价数据进行策略运算
df = index_df[['收盘']].copy()
df.rename(columns={'收盘': 'close'}, inplace=True)  # 重命名列方便后续操作

# 计算每日收益率
df['return'] = df['close'].pct_change()

# 计算其他指标
df['ma_long_period'] = df['close'].rolling(window=5).mean()
df['sigma'] = df['close'].rolling(window=10).std()
df['Momentum1'] = df['return'].rolling(window=8).sum()
df['index_value'] = df['close'] / df.iloc[0]['close'] - 1

# 参数设置
threshold1 = 0
threshold2 = 0
multiplier = 3

# 信号生成
df['signal'] = 0
df.loc[((df['close'] > df['ma_long_period'] * (1 + threshold1)) | (df['Momentum1'] > threshold2))
       & (df['close'] < df['ma_long_period'] + df['sigma'] * multiplier), 'signal'] = 1
df.loc[((df['close'] < df['ma_long_period'] * (1 - threshold1)) | (df['Momentum1'] < -threshold2))
       & (df['close'] > df['ma_long_period'] - df['sigma'] * multiplier), 'signal'] = -1
df.loc[(df['close'] > df['ma_long_period'] + df['sigma'] * multiplier), 'signal'] = -1
df.loc[(df['close'] < df['ma_long_period'] - df['sigma'] * multiplier), 'signal'] = 1
df.loc[((df['close'] > df['ma_long_period'] * (1 + threshold1)) | (df['Momentum1'] > threshold2))
       & ((df['close'] < df['ma_long_period'] * (1 - threshold1)) | (df['Momentum1'] < -threshold2)), 'signal'] = 0

# 输出结果
print(df[['close', 'return', 'ma_long_period', 'sigma', 'Momentum1', 'signal']].tail(20))
