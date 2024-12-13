import akshare as ak
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 获取沪深300指数成分股
def get_hs300_components():
    hs300 = ak.index_stock_cons(symbol="000300")  # 沪深300
    print(hs300)
    return hs300['品种代码'].tolist()

# 获取个股的历史数据
def get_stock_data(stock_code, start_date, end_date):
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="hfq")
        if df.empty:
            return None
        df = df[['日期', '收盘', '开盘', '最高', '最低', '涨跌幅']]  # 选取需要的列
        df.columns = ['date', 'close', 'open', 'high', 'low', 'pct_chg']
        df['date'] = pd.to_datetime(df['date'])
        print(f"{stock_code} is done")
        return stock_code, df
    except Exception as e:
        print(f"Error processing stock {stock_code}: {e}")
        return stock_code, None

# 回测策略
def backtest_hs300(start_date, end_date, initial_balance):
    components = get_hs300_components()
    all_data = {}

    # 多线程下载所有股票的数据
    with ThreadPoolExecutor(max_workers=32) as executor:
        results = executor.map(lambda stock: get_stock_data(stock, start_date, end_date), components)
        for stock, data in results:
            if data is not None:
                all_data[stock] = data

    # 提取所有股票的实际交易日期，取交集
    trade_dates = set()
    for data in all_data.values():
        trade_dates.update(data['date'])
    trade_dates = sorted(list(trade_dates))  # 转换为排序列表

    # 回测变量
    balance = initial_balance
    holdings = {}  # 当前持仓
    trade_log = []  # 交易记录
    transaction_fee_rate = 0.001  # 交易费用千分之一

    for i in range(len(trade_dates) - 2):  # 确保有足够的时间进行 t+1 和 t+2
        t_date = trade_dates[i]
        t1_date = trade_dates[i + 1]

        print(f"Date: {t_date.date()} | Starting Balance: {balance:.2f}")

        # 获取 t 日下跌 -9%的股票, 且t+1日没涨
        candidates = []
        for stock, data in all_data.items():
            row = data[data['date'] == t_date]
            # t1_row = data[data['date'] == t1_date]  # 获取 t+1 日数据
            if not row.empty and row.iloc[0]['pct_chg'] <= -9:
                # if not t1_row.empty and t1_row.iloc[0]['pct_chg'] <= 0:
                print(f"{stock} on {t_date.date()} is -9%")
                candidates.append(stock)

        # 在 t+2 日卖出持仓
        for stock, holding in list(holdings.items()):
            sell_data = all_data[stock][all_data[stock]['date'] == t1_date]
            if not sell_data.empty:
                sell_price = sell_data.iloc[0]['close']
                sell_amount = holding['shares'] * sell_price
                sell_fee = sell_amount * transaction_fee_rate
                balance += sell_amount - sell_fee
                trade_log.append({
                    'date': t1_date,
                    'stock': stock,
                    'action': 'sell',
                    'price': sell_price,
                    'shares': holding['shares'],
                    'fee': sell_fee
                })
                print(f"Sold {holding['shares']} shares of {stock} at {sell_price:.2f} on {t1_date.date()}, Fee: {sell_fee:.2f}")

        holdings = {}

        # 在 t+1 日买入t日下跌8%且t+1日低收或平收的股票，控制仓位，个股最高25%
        if candidates:
            equal_allocation = balance / len(candidates)
            # if equal_allocation >= balance / 4:
            #     equal_allocation = balance / 4
            for stock in candidates:
                # buy_data0 = all_data[stock][all_data[stock]['date'] == t_date]
                buy_data = all_data[stock][all_data[stock]['date'] == t1_date]
                if not buy_data.empty:
                    # price0 = buy_data0.iloc[0]['close']
                    buy_price = buy_data.iloc[0]['close']
                    shares = equal_allocation // buy_price
                    # if buy_price > price0:
                    #     shares = 0
                    buy_amount = shares * buy_price
                    buy_fee = buy_amount * transaction_fee_rate
                    if shares > 0:
                        holdings[stock] = {'shares': shares, 'buy_price': buy_price}
                        balance -= buy_amount + buy_fee
                        trade_log.append({
                            'date': t1_date,
                            'stock': stock,
                            'action': 'buy',
                            'price': buy_price,
                            'shares': shares,
                            'fee': buy_fee
                        })
                        print(f"Bought {shares} shares of {stock} at {buy_price:.2f} on {t1_date.date()}, Fee: {buy_fee:.2f}")

    return pd.DataFrame(trade_log), balance

# 运行回测
if __name__ == "__main__":
    start_date = "20201201"  # 回测开始日期
    end_date = "20241201"  # 回测结束日期
    initial_balance = 1000000  # 初始资金

    trade_log, final_balance = backtest_hs300(start_date, end_date, initial_balance)
    print(f"Final Balance: {final_balance:.2f}")
    print(f"Total Trades: {len(trade_log)}")
    print(trade_log)
    

