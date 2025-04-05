import pandas as pd
import akshare as ak

# 获取概念板块历史数据
stock_board_concept_hist_em_df = ak.stock_board_concept_hist_em(
    symbol="微盘股",
    period="daily",
    start_date="20240207",
    end_date="20241219",
    adjust=""
)

# 数据预处理，确保列名和数据类型正确
stock_board_concept_hist_em_df['日期'] = pd.to_datetime(stock_board_concept_hist_em_df['日期'])
stock_board_concept_hist_em_df['涨跌幅'] = stock_board_concept_hist_em_df['涨跌幅'].astype(float)
stock_board_concept_hist_em_df = stock_board_concept_hist_em_df.sort_values(by='日期')

# 初始资金
initial_balance = 1_000_000
balance = initial_balance
position = 0  # 持仓数量
total_value = initial_balance  # 总资产价值记录
transaction_log = []  # 记录交易信息

# 回测策略
for index, row in stock_board_concept_hist_em_df.iterrows():
    date = row['日期']
    price_change = row['涨跌幅'] / 100
    close_price = row['收盘']  # 假设有收盘价字段
    
    if price_change <= -0.03 and balance > 0:
        # 全仓买入
        position = balance / close_price
        balance = 0
        transaction_log.append((date, "买入", close_price, position, balance))
    
    elif price_change >= 0.03 and position > 0:
        # 全仓卖出
        balance = position * close_price
        position = 0
        transaction_log.append((date, "卖出", close_price, position, balance))
    
    # 记录总资产价值
    total_value = balance + position * close_price

# 输出交易日志
for log in transaction_log:
    print(f"日期: {log[0]}, 操作: {log[1]}, 收盘价: {log[2]}, 持仓: {log[3]:.2f}, 账户余额: {log[4]:.2f}")

# 最终收益结果
final_balance = balance + position * stock_board_concept_hist_em_df.iloc[-1]['收盘']
print(f"初始资金: {initial_balance} 元")
print(f"最终总资产: {final_balance} 元")
print(f"收益率: {(final_balance / initial_balance - 1) * 100:.2f}%")
