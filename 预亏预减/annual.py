import akshare as ak
import pandas as pd
import datetime
import time

# 获取所有A股股票代码
def get_all_stock_codes():
    # 使用AKShare获取所有A股股票代码
    stock_info_a_code_name_df = ak.stock_info_a_code_name()
    # 返回股票代码列表
    return stock_info_a_code_name_df['code'].tolist()

# 获取某只股票的年报预告信息
def get_annual_report_forecast(stock_code):
    # 使用AKShare获取某只股票的年报预告信息
    forecast_df = ak.stock_em_yjyg(stock_code)
    # 返回年报预告信息
    return forecast_df

# 筛选出预告亏损的股票
def filter_loss_stocks(forecast_df):
    # 筛选出预告净利润为负的股票
    loss_stocks = forecast_df[forecast_df['净利润'] < 0]
    # 返回预告亏损的股票代码列表
    return loss_stocks['股票代码'].tolist()

# 获取某只股票的历史行情数据
def get_stock_history(stock_code, start_date, end_date):
    # 使用AKShare获取某只股票的历史行情数据
    stock_df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
    # 返回历史行情数据
    return stock_df

# 获取最近的交易日
def get_nearest_trade_date(date):
    # 获取A股交易日历
    trade_date_df = ak.tool_trade_date_hist_sina()
    # 将日期转换为datetime格式
    date = pd.to_datetime(date)
    # 找到最近的交易日
    nearest_date = trade_date_df[trade_date_df['trade_date'] <= date].max()['trade_date']
    return nearest_date

# 回测策略
def backtest_strategy(start_year, end_year):
    # 记录开始时间
    start_time = time.time()
    
    # 获取所有A股股票代码
    all_stock_codes = get_all_stock_codes()
    
    # 初始化每年的收益率
    annual_returns = {}
    
    # 遍历每一年
    for year in range(start_year, end_year + 1):
        # 2月1日买入
        buy_date = datetime.date(year, 2, 1)
        buy_date = get_nearest_trade_date(buy_date)  # 调整为最近的交易日
        print(f"Buying on {buy_date}")
        
        # 获取所有预告亏损的股票
        loss_stocks = []
        for stock_code in all_stock_codes:
            try:
                forecast_df = get_annual_report_forecast(stock_code)
                loss_stocks.extend(filter_loss_stocks(forecast_df))
            except Exception as e:
                print(f"Error fetching data for {stock_code}: {e}")
        
        # 去重
        loss_stocks = list(set(loss_stocks))
        print(f"Number of loss stocks in {year}: {len(loss_stocks)}")
        
        # 计算买入价格
        buy_prices = {}
        for stock_code in loss_stocks:
            try:
                stock_df = get_stock_history(stock_code, buy_date, buy_date)
                if not stock_df.empty:
                    buy_prices[stock_code] = stock_df.iloc[0]['收盘']
            except Exception as e:
                print(f"Error fetching history for {stock_code}: {e}")
        
        # 次年1月31日卖出
        sell_date = datetime.date(year + 1, 1, 31)
        sell_date = get_nearest_trade_date(sell_date)  # 调整为最近的交易日
        print(f"Selling on {sell_date}")
        
        # 计算卖出价格
        sell_prices = {}
        for stock_code in buy_prices.keys():
            try:
                stock_df = get_stock_history(stock_code, sell_date, sell_date)
                if not stock_df.empty:
                    sell_prices[stock_code] = stock_df.iloc[0]['收盘']
            except Exception as e:
                print(f"Error fetching history for {stock_code}: {e}")
        
        # 计算每只股票的收益率
        returns = []
        for stock_code in buy_prices.keys():
            if stock_code in sell_prices:
                buy_price = buy_prices[stock_code]
                sell_price = sell_prices[stock_code]
                returns.append((sell_price - buy_price) / buy_price)
        
        # 计算等权平均收益率
        if returns:
            annual_return = sum(returns) / len(returns)
            annual_returns[year] = annual_return
            print(f"Annual return for {year}: {annual_return:.2%}")
        else:
            annual_returns[year] = 0
            print(f"No valid trades in {year}")
    
    # 记录结束时间
    end_time = time.time()
    print(f"Total runtime: {end_time - start_time:.2f} seconds")
    
    # 返回每年的收益率
    return annual_returns

# 设置回测的起始年份和结束年份
start_year = 2020
end_year = 2022

# 运行回测
annual_returns = backtest_strategy(start_year, end_year)

# 输出每年的收益率
for year, return_rate in annual_returns.items():
    print(f"Year {year} return: {return_rate:.2%}")