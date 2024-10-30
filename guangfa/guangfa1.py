import akshare as ak
import pandas as pd

# 获取数据
code = "000521"
res = ak.stock_zh_a_hist(symbol=code, adjust="hfq", start_date='20200101', end_date='20210617')

# 打印数据的列名
print("数据列名：", res.columns)

# 选择需要的列并重新命名
res = res[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
res.columns = ['date', 'open', 'close', 'high', 'low', 'volume']

# 将列名装入字典
fields = ['date', 'open', 'close', 'high', 'low', 'volume']
data = {}

for field in fields:
    data[field] = res[field]

df = pd.DataFrame(data)

# 将时间格式数据修改为 datetime 格式
df['Datetime'] = pd.to_datetime(res['date'])

# 将 Datetime 列设置为 DataFrame 的索引
df.set_index("Datetime", inplace=True)

# 计算动量效应因子
df['returns'] = df['close'].pct_change()  # 计算每个5分钟的收益率
df['Momentum'] = df['close'] - df['close'].shift(1)  # 计算过去1个5分钟的累积收益率

# 生成信号和交易决策
df['signal'] = 0
df.loc[df['Momentum'] >= 1, 'signal'] = 1
df.loc[df['Momentum'] <= -1, 'signal'] = -1

# 计算策略收益率
df['strategy_returns'] = df['returns'] * df['signal'].shift(1)

# 计算交易佣金
df['commission'] = 0
df.loc[abs(df['signal'] - df['signal'].shift(1)) == 2, 'commission'] = 2
df.loc[abs(df['signal'] - df['signal'].shift(1)) == 1, 'commission'] = 1

# 计算累积收益率，并创建一个新的列来存储它
stoploss = 5
multiplier = 30
ticker = 1 * multiplier
commission_rate = 0.0008

df['stoploss_strategy_returns'] = df['strategy_returns']
df.loc[(df['signal'].shift(1) == 1) & ((df['low'] / df['close'].shift(1) - 1) <= -stoploss / df['close'] / multiplier), 'stoploss_strategy_returns'] = -stoploss / df['close'] / multiplier
df.loc[(df['signal'].shift(1) == 1) & ((df['low'] / df['close'].shift(1) - 1) > -stoploss / df['close'] / multiplier), 'stoploss_strategy_returns'] = df['strategy_returns']
df.loc[(df['signal'].shift(1) == -1) & ((df['high'] / df['close'].shift(1) - 1) >= stoploss / df['close'] / multiplier), 'stoploss_strategy_returns'] = -stoploss / df['close'] / multiplier
df.loc[(df['signal'].shift(1) == -1) & ((df['high'] / df['close'].shift(1) - 1) < stoploss / df['close'] / multiplier), 'stoploss_strategy_returns'] = df['strategy_returns']

# 计算累积收益率
df['cum_return'] = (1 + df['strategy_returns'] - df['commission'] * (commission_rate + ticker / df['close'])).cumprod()
df['cum_NV'] = (1 + df['strategy_returns'] - df['commission'] * (commission_rate + ticker / df['close'])).cumprod()
df['max_drawdown'] = (df['cum_NV'].cummax() - df['cum_NV']) / df['cum_NV'].cummax()

# 计算止损策略累积收益率
df['stoploss_cum_return'] = (1 + df['stoploss_strategy_returns'] - df['commission'] * (commission_rate + ticker / df['close'])).cumprod()
df['stoploss_cum_NV'] = (1 + df['stoploss_strategy_returns'] - df['commission'] * (commission_rate + ticker / df['close'])).cumprod()
df['stoploss_max_drawdown'] = (df['stoploss_cum_NV'].cummax() - df['stoploss_cum_NV']) / df['stoploss_cum_NV'].cummax()

# 保存结果到 CSV 文件
output_file = "/Users/jianaoli/Quant/quant1/strategy_output.csv"
df.to_csv(output_file, encoding='utf-8-sig')

print(f"数据已保存到 {output_file}")
