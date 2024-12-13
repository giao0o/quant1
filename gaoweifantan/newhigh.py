import akshare as ak
import pandas as pd

def is_new_high(stock_code: str, date_str: str, N: int, M: int) -> bool:
    """
    检查股票是否在最近 N 个交易日内创过去 M 个交易日以来的新高（包括最近 N 天）。

    :param stock_code: 股票代码
    :param date_str: 当前日期（字符串格式，如 '2023-10-30'）
    :param N: 检查的区间天数（最近 N 个交易日）
    :param M: 回溯的区间天数（M 个交易日以来）
    :return: 是否达到新高（True/False）
    """
    try:
        # 将字符串日期转换为 pd.Timestamp 类型
        current_date = pd.to_datetime(date_str)
        
        # 动态获取数据，确保数据量达到 M 行
        lookback_days = M * 2  # 初始回溯天数，考虑非交易日可能需要更多天数
        while True:
            start_date = (current_date - pd.Timedelta(days=lookback_days)).strftime("%Y%m%d")
            
            # 获取股票历史数据
            stock_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, adjust="hfq")
            
            # 检查数据是否足够
            if not stock_df.empty and len(stock_df) >= M:
                # 截取最近 M 行数据
                stock_df = stock_df.tail(M)
                stock_df['close'] = stock_df['收盘'].astype(float)
                
                # 计算过去 M 天的最高价（包括最近 N 天）
                historical_high = stock_df['close'].max()
                
                # 计算最近 N 天的最高价
                recent_high = stock_df['close'].iloc[-N:].max()
                
                # 判断最近 N 天的最高价是否等于过去 M 天的最高价
                return recent_high == historical_high
            
            # 数据不足，扩大回溯范围
            lookback_days += M  # 增加回溯的天数
    except Exception as e:
        print(f"Error checking stock {stock_code}: {e}")
        return False

# 测试示例
def test_with_input_date(stock_code: str, date_str: str, N: int, M: int):
    result = is_new_high(stock_code, date_str, N, M)
    print(f"在 {date_str} 的 {N} 个交易日内，股票 {stock_code} 是否创过去 {M} 个交易日的新高：{result}")

# # 示例调用
# test_with_input_date("603039", "2024-11-21", 7, 100)  # 测试浦发银行（股票代码 "600000"）在 2023-10-30 的最近 5 个交易日是否创过去 20 个交易日的新高
