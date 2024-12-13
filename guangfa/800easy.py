import akshare as ak
import pandas as pd
import numpy as np
from tqdm import tqdm

# 获取中证500和沪深300成分股
index_500_stocks = ak.index_stock_cons_csindex(symbol="000905")  # 中证500成分股
index_300_stocks = ak.index_stock_cons_csindex(symbol="000300")  # 沪深300成分股

# 合并成分股代码并去重
all_stocks = list(set(index_500_stocks['成分券代码'].tolist() + index_300_stocks['成分券代码'].tolist()))

# 设置回测参数
start_date = "20241101"  # 回测开始日期
end_date = "20241118"  # 回测结束日期
capital = 1000000  # 初始资金
holding_stocks = {}  # 持仓记录，格式为 {股票代码: 买入价格}

# 获取中证800指数每日收益率，用于计算相对涨幅
benchmark_df = ak.index_zh_a_hist(symbol="000906", period="daily", start_date=start_date, end_date=end_date)
benchmark_df['日期'] = pd.to_datetime(benchmark_df['日期'])
benchmark_df.set_index('日期', inplace=True)
benchmark_df['收盘'] = benchmark_df['收盘'].astype(float)
benchmark_df['20d_return'] = benchmark_df['收盘'].pct_change(periods=20)  # 20日涨跌幅

# 构建交易日序列
dates = pd.date_range(start=start_date, end=end_date, freq="B")  # freq="B" 表示仅包含工作日

# 开始回测
for current_date in tqdm(dates, desc="Backtesting"):
    print(f"Processing date: {current_date}")
    
    # 卖出逻辑：仅在持仓不为空时执行
    if holding_stocks:
        daily_return = 0
        for stock, buy_price in holding_stocks.items():
            try:
                print(f"Attempting to sell stock: {stock}")
                stock_df = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date=current_date.strftime("%Y%m%d"),
                                              end_date=current_date.strftime("%Y%m%d"), adjust="hfq")
                if not stock_df.empty:
                    sell_price = stock_df['收盘'].iloc[0]
                    daily_return += (sell_price / buy_price - 1) * (capital / len(holding_stocks))
            except Exception as e:
                print(f"Error selling {stock}: {e}")
        
        # 更新资金
        capital *= (1 + daily_return)
        holding_stocks = {}  # 清空持仓记录
    
    # 买入逻辑：筛选符合条件的股票
    print(f"Selecting stocks for {current_date}")
    selected_stocks = []
    for stock in all_stocks:
        try:
            stock_df = ak.stock_zh_a_hist(symbol=stock, period="daily",
                                          start_date=(current_date - pd.Timedelta(days=100)).strftime("%Y%m%d"),
                                          end_date=current_date.strftime("%Y%m%d"), adjust="hfq")
            if stock_df.empty or len(stock_df) < 100:
                continue

            stock_df['close'] = stock_df['收盘'].astype(float)
            stock_df['return'] = stock_df['close'].pct_change()
            stock_df['100d_high'] = stock_df['close'].rolling(window=100).max()
            stock_df['20d_return'] = stock_df['close'].pct_change(periods=20)
            
            if (stock_df['close'].iloc[-1] >= stock_df['100d_high'].iloc[-1] and
                stock_df['return'].iloc[-2] <= 0 and
                stock_df['return'].iloc[-3] <= 0 and
                stock_df['return'].iloc[-1] < -0.03 and
                stock_df['20d_return'].iloc[-1] >= benchmark_df['20d_return'].loc[current_date] + 0.15):
                selected_stocks.append(stock)
                print(f"Stock {stock} selected")
        except Exception as e:
            print(f"Error processing {stock}: {e}")
    
    print(f"Stocks selected for {current_date}: {selected_stocks}")
    
    # 均匀分配资金买入
    if selected_stocks:
        per_stock_capital = capital / len(selected_stocks)
        for stock in selected_stocks:
            try:
                buy_price = stock_df['close'].iloc[-1]
                holding_stocks[stock] = buy_price
            except Exception as e:
                print(f"Error buying {stock}: {e}")

# 输出回测结束后的总资金
print(f"Final capital: {capital}")
