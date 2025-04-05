import pandas as pd
import akshare as ak
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# 获取当前脚本所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 切换工作目录
os.chdir(script_dir)

# 现在可以使用相对路径
data_file = "temp.xlsx"
df = pd.read_excel(data_file)

# 格式化日期列
df['选样日期'] = pd.to_datetime(df['选样日期'])

# 提取所需列
dates = df['选样日期']
strategy = df['多头策略:上涨(无止损)']

# 使用 akshare 获取中证1000指数数据
hs300_data = ak.index_zh_a_hist(symbol='000852', period='daily', start_date='20070101', end_date='20241231')
print(hs300_data)
hs300_data['date'] = pd.to_datetime(hs300_data['日期'])
hs300_data.set_index('date', inplace=True)

# 提取收盘价数据
hs300_close = hs300_data['收盘']

# 初始化变量
position = 0  # 持仓状态，1 表示持仓，0 表示空仓
entry_price = 0  # 建仓价格
returns = []  # 存储每次交易的收益记录

# 遍历选样数据进行回测
for i in range(len(dates)):
    date = dates.iloc[i]
    signal = strategy.iloc[i]

    if date in hs300_close.index:
        close_price = hs300_close[date]

        if position == 0 and signal == 0: #空仓且当日滤网未触发
            # 开仓：买入
            position = 1
            entry_price = close_price
            print(f"[{date}] 开仓，开仓价: {entry_price}")

        elif position == 1 and signal != 0: #滤网触发，平仓
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


