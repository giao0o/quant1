import akshare as ak
import pandas as pd
import numpy as np

def get_data(symbol, start_date, end_date):
    stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="")
    stock_data['日期'] = pd.to_datetime(stock_data['日期'])
    stock_data.set_index('日期', inplace=True)
    return stock_data

def execute_strategy(stock_data, initial_cash, shares_held, buy_amount, open_threshold_low, open_threshold_high, fee_rate, stamp_duty_rate):
    cash = initial_cash
    total_trading_days = len(stock_data)
    days_with_trades = 0
    days_with_loss = 0
    days_with_profit = 0
    previous_close_price = None
    first_openprice = stock_data.iloc[0]['开盘']
    
    for index, row in stock_data.iterrows():
        open_price = row['开盘']
        close_price = row['收盘']
        high_price = row['最高']
        low_price = row['最低']

        if previous_close_price is not None:
            day_traded = False  # 增加一个布尔变量来跟踪当天是否有交易
            old_cash = cash

            open_return = (open_price - previous_close_price) / previous_close_price

            if open_return <= open_threshold_low:  # 早盘低开
                buy_shares = int(buy_amount / open_price)
                while cash < (buy_shares * open_price) * (1 + fee_rate) and buy_shares > 0:
                    buy_shares -= 1
                if buy_shares > 0:
                    cost = buy_shares * open_price * (1 + fee_rate)
                    cash -= cost
                    shares_held += buy_shares
                    day_traded = True
                    
            elif open_return >= open_threshold_high:  # 早盘高开
                sell_shares = int(buy_amount / open_price)
                while sell_shares > shares_held - 1000 and sell_shares > 0:
                    sell_shares -= 1
                if sell_shares > 0:
                    revenue = sell_shares * open_price * (1 - fee_rate - stamp_duty_rate)
                    cash += revenue
                    shares_held -= sell_shares
                    day_traded = True

            else:  # 早盘未低开未高开，进行盘中交易
                intraday_return = (high_price - previous_close_price) / previous_close_price
                if intraday_return >= open_threshold_high:  # 盘中涨幅超过阈值
                    sell_price = (1 + open_threshold_high) * previous_close_price
                    sell_shares = shares_held
                    if sell_shares > 0:
                        revenue = sell_shares * sell_price * (1 - fee_rate - stamp_duty_rate)
                        cash += revenue
                        shares_held -= sell_shares
                        day_traded = True
                      
            if shares_held > 1000:
                sell_shares = shares_held - 1000
                revenue = sell_shares * close_price * (1 - fee_rate - stamp_duty_rate)
                cash += revenue
                shares_held = 1000
                day_traded = True

            elif shares_held < 1000:
                buy_shares = 1000 - shares_held
                while cash < (buy_shares * close_price) * (1 + fee_rate) and buy_shares > 0:
                    buy_shares -= 1
                if buy_shares > 0:
                    cost = buy_shares * close_price * (1 + fee_rate)
                    cash -= cost
                    shares_held += buy_shares
                    day_traded = True

            if day_traded:
                days_with_trades += 1
                if old_cash >= cash:
                    days_with_loss += 1
                else:
                    days_with_profit += 1    

        
        previous_close_price = close_price
    
    final_return = cash / initial_cash - 1
    return total_trading_days, final_return, days_with_trades, days_with_profit, days_with_loss
    
    

def main():
    symbol = "002780" #可修改 股票代码
    start_date = "20240930" #可修改 起始日
    end_date = "20241030" #可修改 终止日
    initial_cash = 10000 #可修改 可用现金（用于先低买后高卖）
    shares_held = 1000 #可修改 可用来卖出的股票数量，现金和股价*股票数量大体得相等
    buy_amount = 10000
    fee_rate = 0.0002
    stamp_duty_rate = 0.0005

    stock_data = get_data(symbol, start_date, end_date)

    results = []
    for open_threshold_low in np.arange(-0.005, 0.00, 0.001): #跌多少买入
        for open_threshold_high in np.arange(0.00, 0.005, 0.001): #涨多少卖出
            total_trading_days, final_return, days_with_trades, days_with_profit, days_with_loss = execute_strategy(
                stock_data, initial_cash, shares_held, buy_amount, open_threshold_low, open_threshold_high, fee_rate, stamp_duty_rate
            )
            results.append([
                open_threshold_low, open_threshold_high, total_trading_days, final_return, days_with_trades, days_with_profit, days_with_loss
            ])
            print(f"open_threshold_low: {open_threshold_low}, open_threshold_high: {open_threshold_high}, final_return: {final_return}")

    results_df = pd.DataFrame(results, columns=[
        "open_threshold_low", "open_threshold_high", "total_trading_days", "final_return", "days_with_trades", "days_with_profit", "days_with_loss"
    ])

    results_df.to_excel("trading_strategy_results002780241005.xlsx", index=False)
    print("Results exported to trading_strategy_results.xlsx")

if __name__ == "__main__":
    main()