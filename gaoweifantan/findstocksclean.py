import akshare as ak  # 引入 AkShare 库，用于获取股票和指数数据
import pandas as pd  # 引入 Pandas 库，用于数据处理
from concurrent.futures import ThreadPoolExecutor, as_completed  # 引入并发库，用于多线程加速
from tqdm import tqdm  # 引入 tqdm 库，用于显示进度条

# 检查股票是否在最近 N 个交易日内创过去 M 个交易日以来的新高
def is_new_high(stock_code: str, date_str: str, N: int, M: int) -> bool:
    """
    检查股票是否在最近 N 个交易日内创过去 M 个交易日以来的新高。

    :param stock_code: 股票代码
    :param date_str: 当前日期（字符串格式，如 '2023-10-30'）
    :param N: 检查的区间天数（最近 N 个交易日）
    :param M: 回溯的区间天数（M 个交易日以来）
    :return: 是否达到新高（True/False）
    """
    try:
        # 将字符串日期转换为 Pandas 日期类型
        current_date = pd.to_datetime(date_str)
        
        # 动态扩展获取的历史数据范围
        lookback_days = M * 2  # 初始回溯天数，考虑非交易日
        while True:
            start_date = (current_date - pd.Timedelta(days=lookback_days)).strftime("%Y%m%d")
            # **获取股票历史数据**
            stock_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, adjust="hfq")
            
            # 检查数据是否足够
            if not stock_df.empty and len(stock_df) >= M:
                stock_df = stock_df.tail(M)  # 取过去 M 天的数据
                stock_df['high'] = stock_df['最高'].astype(float)  # 提取最高价并转为浮点型，也可以改成收盘价，但是看k线最高价更有代表性
                historical_high = stock_df['high'].max()  # 计算 M 天内的最高价
                recent_high = stock_df['high'].iloc[-N:].max()  # 计算最近 N 天的最高价
                
                # 判断最近 N 天最高价是否等于过去 M 天最高价
                return recent_high == historical_high
            
            lookback_days += M  # 如果数据不足，扩大回溯范围
    except Exception as e:
        print(f"Error checking stock {stock_code}: {e}")
        return False

# 检查股票是否在最近 N 个交易日内持续下跌
def is_nday_minus(stock_code: str, date_str: str, N: int) -> bool:
    """
    检查股票是否在最近 N 个交易日内持续下跌。

    :param stock_code: 股票代码
    :param date_str: 当前日期（字符串格式，如 '2023-10-30'）
    :param N: 检查的区间天数（最近 N 个交易日）
    :return: 是否持续下跌（True/False）
    """
    try:
        current_date = pd.to_datetime(date_str)  # 将字符串日期转换为 Pandas 日期
        lookback_days = N * 2  # 初始回溯天数
        
        while True:
            start_date = (current_date - pd.Timedelta(days=lookback_days)).strftime("%Y%m%d")
            # **获取股票历史数据**
            stock_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, adjust="hfq")
            
            if not stock_df.empty and len(stock_df) >= N:
                stock_df = stock_df.tail(N)  # 取最近 N 天的数据
                stock_df['fail'] = stock_df['涨跌幅'].astype(float)  # 提取涨跌幅并转为浮点型
                
                # 判断最近 N 天是否全部为负涨跌幅
                return all(fail < 0.0 for fail in stock_df['fail'])
            
            lookback_days += N  # 数据不足时扩大回溯范围
    except Exception as e:
        print(f"Error checking stock {stock_code}: {e}")
        return False

# 计算指数在指定交易日内的涨幅
def index_performance(vsindex_days: int, stock_market: str, date_str: str) -> float:
    """
    计算指定指数在指定交易日内的涨幅。

    :param vsindex_days: 指定的交易日数
    :param stock_market: 股票市场指数代码
    :param date_str: 当前日期（字符串格式，如 '2024-11-21'）
    :return: 指数在 vsindex_days 天内的涨幅（百分比）
    """
    try:
        current_date = pd.to_datetime(date_str)  # 转换日期
        start_date = (current_date - pd.Timedelta(days=vsindex_days * 2)).strftime("%Y%m%d")  # 开始日期
        end_date = current_date.strftime("%Y%m%d")  # 结束日期
        # **获取指数历史数据**
        index_df = ak.index_zh_a_hist(symbol=stock_market, period="daily", start_date=start_date, end_date=end_date)
        
        if index_df.empty:
            print(f"警告: 指数 {stock_market} 在过去 {vsindex_days} 天内没有数据")
            return None
        
        # index_df.sort_values(by='日期', inplace=True)  # 按日期排序
        recent_data = index_df.tail(vsindex_days+1)  # 取最近 vsindex_days 天的数据
        if len(recent_data) < vsindex_days:
            print(f"警告: 指数 {stock_market} 在过去 {vsindex_days} 天内的数据不足")
            return None
        
        start_close = recent_data['收盘'].iloc[0]  # 起始收盘价
        end_close = recent_data['收盘'].iloc[-1]  # 结束收盘价
        
        # 计算涨幅百分比
        return (end_close - start_close) / start_close * 100
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
    :param minus_days: 连续几日的跌幅阈值
    :param nday_new_high: 最近 n 日的新高阈值
    :param total_new_high: 总的新高次数
    :param vs_index_days: 与指数对比的时间段
    :param index_performance_value: 指数的表现值
    :param excess: 股票相对指数的超额收益要求
    :return: 符合条件的股票代码，或者 None
    """
    try:
        # 转换字符串日期为 Pandas 时间戳
        current_date = pd.to_datetime(date_str)
        
        # 计算目标日期前一天
        start_date = (current_date - pd.Timedelta(days=1)).strftime("%Y%m%d")
        end_date = current_date.strftime("%Y%m%d")
        
        # 获取股票的日线历史数据
        stock_df = ak.stock_zh_a_hist(
            symbol=stock, period="daily", start_date=start_date, end_date=end_date, adjust="qfq"
        )
        
        # 检查数据是否为空
        if not stock_df.empty:
            # 确保数据中包含 '涨跌幅' 列
            if '涨跌幅' in stock_df.columns:
                stock_df['涨跌幅'] = stock_df['涨跌幅'].astype(float)  # 转换列数据类型
                
                # 获取最后一天的涨跌幅
                last_day_change = stock_df['涨跌幅'].iloc[-1]
                
                # 判断涨跌幅是否低于阈值
                if last_day_change <= minus:
                    # 检查是否符合连续 n 天的跌幅条件
                    if is_nday_minus(stock, date_str, minus_days):
                        # 检查是否达到新高条件
                        if is_new_high(stock, date_str, nday_new_high, total_new_high):
                            # 计算股票与指数的对比表现
                            stock_performance_value = stock_performance(vs_index_days, stock, date_str)
                            if stock_performance_value is not None:
                                # 判断超额收益是否满足条件
                                if stock_performance_value >= (index_performance_value + excess):
                                    # 检查股票代码是否以 '3' 或 '8' 开头
                                    if stock.startswith("3") or stock.startswith("68"):
                                        # 判断最后一天涨跌幅是否小于等于 19.9%
                                        if last_day_change >= -19.9:
                                            return stock
                                    else:
                                        if last_day_change >= -9.9:
                                            return stock  # 返回符合条件的股票代码
            else:
                print(f"警告: 股票 {stock} 没有 '涨跌幅' 列")
        else:
            print(f"警告: 股票 {stock} 在 {date_str} 的数据为空")
    except Exception as e:
        print(f"Error fetching data for stock {stock}: {e}")
    return None

# 筛选股票数据的主函数
def findstocks(stock_market: str, date_str: str, minus: float, nday_minus: int, nday_new_high: int, total_new_high: int, vs_index_days: int, excess: int) -> pd.DataFrame:
    """
    根据股票代码和日期字符串，筛选出符合条件的股票。

    :param stock_market: 股票指数代码
    :param date_str: 当前日期
    :param minus: 筛选跌幅的阈值
    :return: 符合条件的股票数据的 DataFrame
    """
    try:
        current_date = pd.to_datetime(date_str)  # 转换日期
        
        # 获取股票成分股列表
        index_stocks_df = ak.index_stock_cons_csindex(symbol=stock_market)
        index_stocks_df['stock'] = index_stocks_df['成分券代码'].astype(str)  # 提取成分券代码
        
        # **计算指数涨幅**
        index_performance_value = index_performance(vs_index_days, stock_market, date_str)
        if index_performance_value is None:
            print(f"无法获取指数 {stock_market} 的涨幅")
            return pd.DataFrame()
        else:
            print(f"指数 {stock_market} 在截止 {date_str} 的 {vs_index_days} 个交易日内涨幅为 {index_performance_value:.3f}%")
        
        # 创建线程池，用于并行处理
        minus_stocks = []
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = [
                executor.submit(
                    fetch_stock_data,
                    stock,
                    date_str,
                    minus,
                    nday_minus,
                    nday_new_high,
                    total_new_high,
                    vs_index_days,
                    index_performance_value,
                    excess
                ) for stock in index_stocks_df['stock']
            ]
            # 使用 tqdm 显示进度条
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing stocks"):
                result = future.result()
                if result:
                    minus_stocks.append(result)
        
        # 返回符合条件的股票代码
        return pd.DataFrame(minus_stocks, columns=["stock"])
    except Exception as e:
        print(f"获取股票 {stock_market} 数据时出错: {e}")
        return pd.DataFrame()

# 示例调用

stock_market = "000906"  # 指数代码
date_str = "2024-11-25" # 日期
minus = -3.000  #  筛选当日跌幅小于等于几的股票
minus_days = 2 # 连跌天数
nday_new_high = 7 # 几日内创过
total_new_high = 100 # 几天来新高
vs_index_days = 20 # 对比指数几天来
excess = 0 # 跑赢百分之几（取0-100 integer）

result_df = findstocks(stock_market, date_str, minus, minus_days, nday_new_high, total_new_high, vs_index_days, excess)
print(result_df)