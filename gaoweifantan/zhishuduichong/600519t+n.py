import akshare as ak
import pandas as pd

# 获取个股数据
stock_data = ak.stock_zh_a_hist(symbol='300073', period='daily', start_date='20220701', end_date='20250124', adjust="hfq")

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

# 准备记录不同 sig 的测试结果
results = []

# sig 从 0.1 到 9.9，每次递增 0.1
for sig in [round(x * 0.1, 1) for x in range(1, 100)]:
    position = 0  # 持仓状态，1 表示持仓，0 表示空仓
    entry_price = 0  # 建仓价格
    returns = []  # 存储每次交易的收益记录

    # 遍历选样数据进行回测
    for i in range(len(dates)):
        date = dates[i]
        signal = strategy.iloc[i]
        close_price = stock_close.iloc[i]

        if position == 0 and signal >= sig:  # 空仓且当日个股涨跌幅
            # 开仓：买入
            position = 1
            entry_price = close_price

        elif position == 1 and signal < sig:  # 持仓，尾盘卖出
            # 平仓：卖出多头
            profit = (close_price - entry_price) / entry_price
            returns.append(profit)
            position = 0

    # 计算总收益率
    cumulative_returns = (1 + pd.Series(returns)).cumprod()
    final_cumulative_return = cumulative_returns.iloc[-1] - 1 if not cumulative_returns.empty else 0

    # 计算最大回撤
    if not cumulative_returns.empty:
        drawdowns = cumulative_returns / cumulative_returns.cummax() - 1
        max_drawdown = drawdowns.min()
    else:
        max_drawdown = 0

    # 保存结果
    results.append({
        'sig': sig,
        'final_cumulative_return': final_cumulative_return,
        'max_drawdown': max_drawdown
    })

# 转换为 DataFrame 以便分析
results_df = pd.DataFrame(results)

# 打印结果
print(results_df)

# 保存结果到 CSV 文件
results_df.to_csv('maotai_sig_analysis_results.csv', index=False)
