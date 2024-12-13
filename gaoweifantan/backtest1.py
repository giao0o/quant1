import akshare as ak  # 引入 AkShare 库，用于获取股票和指数数据
import pandas as pd  # 引入 Pandas 库，用于数据处理
from concurrent.futures import ThreadPoolExecutor, as_completed  # 引入并发库，用于多线程加速
from tqdm import tqdm  # 引入 tqdm 库，用于显示进度条

# 假设的交易费用率（0.1%）
TRANSACTION_FEE = 0.0005

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
                stock_df['close'] = stock_df['收盘'].astype(float)  # 提取收盘价并转为浮点型
                historical_high = stock_df['close'].max()  # 计算 M 天内的最高价
                recent_high = stock_df['close'].iloc[-N:].max()  # 计算最近 N 天的最高价
                
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
        with ThreadPoolExecutor(max_workers=64) as executor:
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

def backtest(stock_market: str, start_date: str, end_date: str, initial_capital: float, minus: float, nday_minus: int, nday_new_high: int, total_new_high: int, vs_index_days: int, excess: int) -> pd.DataFrame:
    """
    回测交易策略，模拟从 start_date 到 end_date 的股票买卖过程。

    :param stock_market: 股票指数代码
    :param start_date: 回测开始日期
    :param end_date: 回测结束日期
    :param initial_capital: 初始资金
    :param minus: 筛选跌幅的阈值
    :param nday_minus: 连续跌幅天数
    :param nday_new_high: 新高阈值
    :param total_new_high: 总新高次数
    :param vs_index_days: 对比指数几天来
    :param excess: 跑赢指数的超额收益要求
    :return: 回测结果 DataFrame
    """
    # 转换为日期格式
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # 初始化资金和股票持仓
    capital = initial_capital
    stocks_held = []  # 当前持有的股票代码
    stocks_bought = {}  # 记录买入的股票及其买入价格
    daily_capital = []  # 每日的资金变化
    
    # 获取日期范围
    date_range = pd.date_range(start=start_date, end=end_date)
    
    for current_date in tqdm(date_range, desc="Backtesting"):
        date_str = current_date.strftime("%Y-%m-%d")
        
        # 获取当天筛选出的股票
        selected_stocks_df = findstocks(stock_market, date_str, minus, nday_minus, nday_new_high, total_new_high, vs_index_days, excess)
        
        # 若当天没有选出股票，则跳过交易
        if selected_stocks_df.empty:
            daily_capital.append({"date": date_str, "capital": capital, "action": "No trade"})
            continue
        
        # 若有选股，进行交易
        if stocks_held:
            # 卖出所有股票（按当天收盘价）
            for stock in stocks_held:
                stock_price = ak.stock_zh_a_hist(stock, period="daily", start_date=date_str, end_date=date_str)["收盘"].iloc[-1]
                capital += stock_price * stocks_bought[stock] * (1 - TRANSACTION_FEE)  # 卖出股票并扣除交易费用
            stocks_held.clear()  # 清空持仓
            stocks_bought.clear()  # 清空买入记录
        
        # 均分资金买入当天选中的股票
        num_stocks = len(selected_stocks_df)
        if num_stocks > 0:
            amount_per_stock = capital / num_stocks  # 每支股票投入的金额
            for stock in selected_stocks_df['stock']:
                stock_price = ak.stock_zh_a_hist(stock, period="daily", start_date=date_str, end_date=date_str)["收盘"].iloc[-1]
                num_shares = amount_per_stock / stock_price
                stocks_held.append(stock)
                stocks_bought[stock] = num_shares  # 记录买入的股票及其数量
                capital -= amount_per_stock * (1 + TRANSACTION_FEE)  # 扣除买入股票的费用
        
        # 记录当天资金
        daily_capital.append({"date": date_str, "capital": capital, "action": "Trade"})

    # 将回测结果保存为 DataFrame
    capital_df = pd.DataFrame(daily_capital)
    return capital_df

# 示例调用
stock_market = "000906"  # 指数代码
start_date = "2024-11-01" # 回测开始日期
end_date = "2024-11-21"  # 回测结束日期
initial_capital = 1000000  # 初始资金
minus = -3.0  # 筛选跌幅小于等于-3%的股票
nday_minus = 2  # 连续几日跌幅
nday_new_high = 7  # 最近n日内的新高
total_new_high = 100  # 总天数
vs_index_days = 20  # 指数比较天数
excess = 0  # 超额收益要求为0%

result_df = backtest(stock_market, start_date, end_date, initial_capital, minus, nday_minus, nday_new_high, total_new_high, vs_index_days, excess)

# 输出回测结果
print(result_df)

# 计算并输出最终的资金增长情况
final_capital = result_df['capital'].iloc[-1]
print(f"最终资金: {final_capital:.2f}")