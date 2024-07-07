import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 获取数据
def get_stock_data(symbol, start_date, end_date):
    stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="")
    stock_data['日期'] = pd.to_datetime(stock_data['日期'])
    stock_data.set_index('日期', inplace=True)
    return stock_data

# 计算每日最大涨幅和最大跌幅
def calculate_daily_changes(stock_data):
    stock_data['Max Increase'] = (stock_data['最高'] - stock_data['开盘']) / stock_data['开盘']
    stock_data['Max Decrease'] = (stock_data['最低'] - stock_data['开盘']) / stock_data['开盘']
    return stock_data

# 计算平均值和中位数
def calculate_statistics(stock_data):
    avg_max_increase = stock_data['Max Increase'].mean()
    avg_max_decrease = stock_data['Max Decrease'].mean()
    median_max_increase = stock_data['Max Increase'].median()
    median_max_decrease = stock_data['Max Decrease'].median()
    
    return avg_max_increase, avg_max_decrease, median_max_increase, median_max_decrease

# 可视化
def visualize_statistics(stock_data, avg_max_increase, avg_max_decrease, median_max_increase, median_max_decrease):
    plt.figure(figsize=(14, 7))

    # 绘制每日最大涨幅和最大跌幅
    plt.plot(stock_data.index, stock_data['Max Increase'], label='Daily Max Increase', color='g')
    plt.plot(stock_data.index, stock_data['Max Decrease'], label='Daily Max Decrease', color='r')

    # 绘制平均值和中位数
    plt.axhline(y=avg_max_increase, color='g', linestyle='--', label=f'Avg Max Increase: {avg_max_increase:.4f}')
    plt.axhline(y=avg_max_decrease, color='r', linestyle='--', label=f'Avg Max Decrease: {avg_max_decrease:.4f}')
    plt.axhline(y=median_max_increase, color='g', linestyle=':', label=f'Median Max Increase: {median_max_increase:.4f}')
    plt.axhline(y=median_max_decrease, color='r', linestyle=':', label=f'Median Max Decrease: {median_max_decrease:.4f}')

    plt.title('SZ002780 Daily Max Increase and Decrease')
    plt.xlabel('Date')
    plt.ylabel('Change')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 格式化日期显示
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.gcf().autofmt_xdate()

    plt.show()

def main():
    symbol = "002780"
    start_date = "20240415"
    end_date = "20240630"
    
    stock_data = get_stock_data(symbol, start_date, end_date)
    stock_data = calculate_daily_changes(stock_data)
    avg_max_increase, avg_max_decrease, median_max_increase, median_max_decrease = calculate_statistics(stock_data)
    
    print(f"Avg Max Increase: {avg_max_increase:.4f}")
    print(f"Avg Max Decrease: {avg_max_decrease:.4f}")
    print(f"Median Max Increase: {median_max_increase:.4f}")
    print(f"Median Max Decrease: {median_max_decrease:.4f}")
    
    visualize_statistics(stock_data, avg_max_increase, avg_max_decrease, median_max_increase, median_max_decrease)

if __name__ == "__main__":
    main()
