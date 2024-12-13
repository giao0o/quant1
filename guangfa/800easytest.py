import akshare as ak
import pandas as pd
import time

# 示例股票列表，仅取部分股票用于测试
test_stocks = ["000001", "000002", "000004"]  # 测试用股票代码
current_date = pd.Timestamp("2023-10-30")  # 假设当前日期
start_date = (current_date - pd.Timedelta(days=100)).strftime("%Y%m%d")
end_date = current_date.strftime("%Y%m%d")

for stock in test_stocks:
    print(f"Processing stock: {stock}")
    try:
        start_time = time.time()  # 开始计时
        stock_df = ak.stock_zh_a_hist(symbol=stock, period="daily",
                                      start_date=start_date, end_date=end_date, adjust="hfq")
        duration = time.time() - start_time  # 记录耗时
        print(f"Data fetched for {stock}, rows: {len(stock_df)}; Time taken: {duration:.2f} seconds")

        # 检查数据完整性
        if stock_df.empty or len(stock_df) < 100:
            print(f"Stock {stock} skipped: insufficient data")
            continue
        
        print(f"Stock {stock} data processed successfully")
    except Exception as e:
        print(f"Error processing stock {stock}: {e}")
