import akshare as ak
import pandas as pd

def is_nday_minus(stock_code: str, date_str: str, N: int) -> bool:
    """
    检查股票是否在最近 N 个交易日是否持续下跌。

    :param stock_code: 股票代码
    :param date_str: 当前日期（字符串格式，如 '2023-10-30'）
    :param N: 检查的区间天数（最近 N 个交易日）
    :return: 是否持续下跌（True/False）
    """
    try:
        # 将字符串日期转换为 pd.Timestamp 类型
        current_date = pd.to_datetime(date_str)

        # 动态获取数据，确保数据量达到 N 行
        lookback_days = N * 2  # 初始回溯天数，考虑非交易日
        while True:
            start_date = (current_date - pd.Timedelta(days=lookback_days)).strftime("%Y%m%d")
            
            # 获取股票历史数据
            stock_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, adjust="hfq")
            
            # 检查数据是否足够
            if not stock_df.empty and len(stock_df) >= N:
                # 截取最近 N 行数据
                stock_df = stock_df.tail(N)
                stock_df['fail'] = stock_df['涨跌幅'].astype(float)
                
                # 计算最近 N 是否连续下跌
                return all(fail < 0.0 for fail in stock_df['fail'])
            
            # 数据不足，扩大回溯范围
            lookback_days += N  # 增加回溯的天数
    except Exception as e:
        print(f"Error checking stock {stock_code}: {e}")
        return False

# 测试示例
def test_with_input_date(stock_code: str, date_str: str, N: int):
    result = is_nday_minus(stock_code, date_str, N)
    print(f"在 {date_str} 的 {N} 个交易日是否持续下跌：{result}")

# # 示例调用
# test_with_input_date("300640", "2024-11-21", 2)  # 
