import akshare as ak
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # 进度条库

# from ndayminus import is_nday_minus
# from newhigh import is_new_high

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

def index_performance(vsindex_days: int, stock_market: str, date_str: str) -> float:
    """
    计算指定指数在指定交易日内的涨幅

    :param vsindex_days: 指定的交易日数
    :param stock_market: 股票市场指数代码
    :param date_str: 当前日期（字符串格式，如 '2024-11-21'）
    :return: 指数在 vsindex_days 天内的涨幅（百分比）
    """
    try:
        # 将输入的日期字符串转换为日期类型
        current_date = pd.to_datetime(date_str)
        
        # 设置开始日期（假设交易日不连续，抓取的范围需要更大）
        start_date = (current_date - pd.Timedelta(days=vsindex_days * 2)).strftime("%Y%m%d")
        end_date = current_date.strftime("%Y%m%d")
        
        # 获取指数的历史数据
        index_df = ak.index_zh_a_hist(symbol=stock_market, period="daily", start_date=start_date, end_date=end_date)
        
        # 检查数据是否为空
        if index_df.empty:
            print(f"警告: 指数 {stock_market} 在过去 {vsindex_days} 天内没有数据")
            return None
        
        # 确保数据按照日期排序
        index_df.sort_values(by='日期', inplace=True)
        
        # 筛选最后 vsindex_days 天的数据
        recent_data = index_df.tail(vsindex_days+1)
        if len(recent_data) < vsindex_days:
            print(f"警告: 指数 {stock_market} 在过去 {vsindex_days} 天内的数据不足")
            return None
        
        # 获取开始日期和结束日期的收盘价
        start_close = recent_data['收盘'].iloc[0]
        end_close = recent_data['收盘'].iloc[-1]
        
        # 计算涨幅百分比
        performance = (end_close - start_close) / start_close * 100
        
        return performance
    except Exception as e:
        print(f"获取指数 {stock_market} 数据时出错: {e}")
        return None
    
def stock_performance(vsindex_days: int, stock_code: str, date_str: str) -> float:
    """
    计算指定股票在指定交易日内的涨幅

    :param vsindex_days: 指定的交易日数
    :param stock_code: 股票代码
    :param date_str: 当前日期（字符串格式，如 '2024-11-21'）
    :return: 股票在 vsindex_days 天内的涨幅（百分比）
    """
    try:
        # 将输入的日期字符串转换为日期类型
        current_date = pd.to_datetime(date_str)
        
        # 设置开始日期（抓取范围比交易日多，以适应可能的非交易日）
        start_date = (current_date - pd.Timedelta(days=vsindex_days * 2)).strftime("%Y%m%d")
        end_date = current_date.strftime("%Y%m%d")
        
        # 获取股票的历史数据，为了避免除权除息！后复权！会导致与同花顺查询结果的不同
        stock_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="hfq")
        
        # 检查数据是否为空
        if stock_df.empty:
            print(f"警告: 股票 {stock_code} 在过去 {vsindex_days} 天内没有数据")
            return None
        
        # 确保数据按照日期排序
        stock_df.sort_values(by='日期', inplace=True)
        
        # 筛选最后 vsindex_days 天的数据
        recent_data = stock_df.tail(vsindex_days+1)
        if len(recent_data) < vsindex_days:
            print(f"警告: 股票 {stock_code} 在过去 {vsindex_days} 天内的数据不足")
            return None
        
        # 获取开始日期和结束日期的收盘价
        start_close = recent_data['收盘'].iloc[0]
        end_close = recent_data['收盘'].iloc[-1]
        
        # 计算涨幅百分比
        performance = (end_close - start_close) / start_close * 100
        
        return performance
    except Exception as e:
        print(f"获取股票 {stock_code} 数据时出错: {e}")
        return None




def fetch_stock_data(stock: str, date_str: str, minus: float, minus_days: int, nday_new_high: int, total_new_high: int, vs_index_days: int, index_performance_value: float, excess: int) -> str:
    """
    获取单只股票的历史数据并检查是否符合跌幅条件。

    :param stock: 股票代码
    :param date_str: 当前日期（字符串格式，如 '2023-10-30'）
    :param minus: 跌幅阈值
    :return: 符合条件的股票代码
    """
    try:
        # 将字符串日期转换为 pd.Timestamp 类型
        current_date = pd.to_datetime(date_str)
        
        # 获取股票历史数据，设置 start_date 为目标日期前一天
        start_date = (current_date - pd.Timedelta(days=1)).strftime("%Y%m%d")
        end_date = current_date.strftime("%Y%m%d")
        
        # 获取股票历史数据
        stock_df = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        
        # 打印获取的数据，用于调试
        # print(f"Fetching data for {stock} on {date_str}")
        # print(stock_df)
        
        # 检查股票数据是否为空
        if not stock_df.empty:
            # 确保数据中包含 '涨跌幅' 列
            if '涨跌幅' in stock_df.columns:
                stock_df['涨跌幅'] = stock_df['涨跌幅'].astype(float)
                
                # 获取最后一行的涨跌幅值
                last_day_change = stock_df['涨跌幅'].iloc[-1]
                # print(f"最后一行的涨跌幅值: {last_day_change}")
                
                # 如果最后一行的涨跌幅小于等于 minus，则符合条件
                if last_day_change <= minus:
                    if is_nday_minus(stock, date_str, minus_days) == True:
                        if is_new_high(stock, date_str, nday_new_high, total_new_high) == True:
                            stock_performance_value = stock_performance(vs_index_days, stock, date_str)
                            if stock_performance_value is not None:
                                if stock_performance_value >= (index_performance_value + excess):
                                    return stock
            else:
                print(f"警告: 股票 {stock} 没有 '涨跌幅' 列")
        else:
            print(f"警告: 股票 {stock} 在 {date_str} 的数据为空")
    except Exception as e:
        print(f"Error fetching data for stock {stock}: {e}")
    return None




def findstocks(stock_market: str, date_str: str, minus: float, nday_minus: int, nday_new_high: int, total_new_high: int, vs_index_days: int, excess: int) -> pd.DataFrame:
    """
    根据股票代码和日期字符串，查找股票的历史数据，并筛选出跌幅小于等于给定值的股票。

    :param stock_market: 股票指数代码
    :param date_str: 当前日期（字符串格式，如 '2023-10-30'）
    :param minus: 用于筛选跌幅的阈值
    :return: 符合条件的股票数据的 DataFrame
    """
    try:
        # 将字符串日期转换为 pd.Timestamp 类型
        current_date = pd.to_datetime(date_str)
        
        # 获取股票成分股列表
        index_stocks_df = ak.index_stock_cons_csindex(symbol=stock_market)
        index_stocks_df['stock'] = index_stocks_df['成分券代码'].astype(str)
        
        # Calculate index performance
        index_performance_value = index_performance(vs_index_days, stock_market, date_str)
        if index_performance_value is None:
            print(f"无法获取指数 {stock_market} 的涨幅")
            return pd.DataFrame()
        else:
            print(f"指数{stock_market}在{vs_index_days}个交易日以来的涨幅为{index_performance_value}%")
        
        # 创建一个新的 DataFrame 用于存储符合条件的股票
        minus_stocks = []

        # 使用 ThreadPoolExecutor 进行并行查询，使用线程数量max_workers可根据计算机性能修改
        with ThreadPoolExecutor(max_workers=64) as executor:  # 可以设置 max_workers 为适合的并行数量
            futures = []
            for stock in index_stocks_df['stock']:
                futures.append(executor.submit(fetch_stock_data, stock, date_str, minus, nday_minus, nday_new_high, total_new_high, vs_index_days, index_performance_value, excess))
            
            # 使用 tqdm 显示进度条
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing stocks"):
                result = future.result()
                if result is not None:
                    minus_stocks.append(result)
        
        # 将符合条件的股票代码创建为新的 DataFrame
        minus_df = pd.DataFrame(minus_stocks, columns=["stock"])

        # 返回符合条件的股票 DataFrame
        return minus_df

    except Exception as e:
        print(f"获取股票 {stock_market} 数据时出错: {e}")
        return pd.DataFrame()  # 如果发生错误，返回空的 DataFrame


# 示例调用

stock_market = "000300"  # 指数代码
date_str = "2024-11-22"
minus = -3.000  # 筛选跌幅小于等于 的股票
minus_days = 2 #连跌天数
nday_new_high = 7 #几日内创过
total_new_high = 100 #几天来新高
vs_index_days = 20
excess = 0

result_df = findstocks(stock_market, date_str, minus, minus_days, nday_new_high, total_new_high, vs_index_days, excess)
print(result_df)




# # # 测试数据：某只股票和日期
# stock_code = '600233'  # 示例股票代码
# date_str = '2024-11-21'  # 测试日期
# minus = -3.0  # 跌幅阈值

# # 调用 fetch_stock_data 函数
# result = fetch_stock_data(stock_code, date_str, minus)

# # 输出结果
# if result:
#     print(f"符合条件的股票：{result}")
# else:
#     print(f"股票 {stock_code} 在 {date_str} 不符合条件")

# stock_market = "000300"  # 示例指数代码（沪深300）
# vsindex_days = 5
# date_str = "2024-11-21"  # 当前日期

# performance = index_performance(vsindex_days, stock_market, date_str)
# if performance is not None:
#     print(f"{stock_market} 指数过去 {vsindex_days} 天内涨幅为: {performance:.2f}%")
# else:
#     print(f"无法计算 {stock_market} 指数的涨幅")

# stock_code = "600519"  # 示例股票代码（贵州茅台）
# vsindex_days = 5
# date_str = "2024-11-21"

# performance = stock_performance(vsindex_days, stock_code, date_str)
# if performance is not None:
#     print(f"{stock_code} 股票过去 {vsindex_days} 天内涨幅为: {performance:.2f}%")
# else:
#     print(f"无法计算 {stock_code} 股票的涨幅")

