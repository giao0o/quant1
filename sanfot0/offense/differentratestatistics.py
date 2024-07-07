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
            day_traded = False
            old_cash = cash

            open_return = (open_price - previous_close_price) / previous_close_price

            if open_return <= open_threshold_low:
                buy_shares = int(buy_amount / open_price)
                while cash < (buy_shares * open_price) * (1 + fee_rate) and buy_shares > 0:
                    buy_shares -= 1
                if buy_shares > 0:
                    cost = buy_shares * open_price * (1 + fee_rate)
                    cash -= cost
                    shares_held += buy_shares
                    day_traded = True

                    intraday_return = (high_price - previous_close_price) / previous_close_price
                    if intraday_return >= open_threshold_high:
                        sell_price = (1 + open_threshold_high) * previous_close_price
                        revenue = buy_shares * sell_price * (1 - fee_rate - stamp_duty_rate)
                        cash += revenue
                        shares_held -= buy_shares
                        day_traded = True

            elif open_return >= open_threshold_high:
                sell_shares = int(buy_amount / open_price)
                while sell_shares > shares_held - 1000 and sell_shares > 0:
                    sell_shares -= 1
                if sell_shares > 0:
                    revenue = sell_shares * open_price * (1 - fee_rate - stamp_duty_rate)
                    cash += revenue
                    shares_held -= sell_shares
                    day_traded = True

                    intraday_return = (low_price - previous_close_price) / previous_close_price
                    if intraday_return <= open_threshold_low:
                        buy_price = previous_close_price * (1 + open_threshold_low)
                        buy_shares = int(revenue / buy_price)
                        while cash < (buy_shares * buy_price) * (1 + fee_rate) and buy_shares > 0:
                            buy_shares -= 1
                        if buy_shares > 0:
                            cost = buy_shares * buy_price * (1 + fee_rate)
                            cash -= cost
                            shares_held += buy_shares
                            day_traded = True

            else:
                intraday_return = (low_price - previous_close_price) / previous_close_price
                if intraday_return <= open_threshold_low:
                    buy_price = previous_close_price * (1 + open_threshold_low)
                    buy_shares = int(buy_amount / buy_price)
                    while cash < (buy_shares * buy_price) * (1 + fee_rate) and buy_shares > 0:
                        buy_shares -= 1
                    if buy_shares > 0:
                        cost = buy_shares * buy_price * (1 + fee_rate)
                        cash -= cost
                        shares_held += buy_shares
                        day_traded = True

                elif intraday_return >= open_threshold_high:
                    sell_price = (1 + open_threshold_high) * previous_close_price
                    sell_shares = int(buy_amount / sell_price)
                    while sell_shares > shares_held - 1000 and sell_shares > 0:
                        sell_shares -= 1
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
    total_return = close_price / first_openprice - 1

    return total_trading_days, total_return, final_return, days_with_trades, days_with_profit, days_with_loss

def main():
    symbol = "002780"
    start_date = "20240412"
    end_date = "20240705"
    initial_cash = 10000
    shares_held = 1000
    buy_amount = 10000
    fee_rate = 0.0002
    stamp_duty_rate = 0.0005

    stock_data = get_data(symbol, start_date, end_date)

    results = []
    for open_threshold_low in np.arange(-0.02, 0.00, 0.001):
        for open_threshold_high in np.arange(0.00, 0.02, 0.001):
            stop_loss_threshold = open_threshold_low
            intraday_threshold = open_threshold_high
            total_trading_days, total_return, final_return, days_with_trades, days_with_profit, days_with_loss = execute_strategy(
                stock_data, initial_cash, shares_held, buy_amount, open_threshold_low, open_threshold_high, fee_rate, stamp_duty_rate
            )
            results.append([
                open_threshold_low, open_threshold_high, total_trading_days, total_return, final_return, days_with_trades, days_with_profit, days_with_loss
            ])
            print(f"open_threshold_low: {open_threshold_low}, open_threshold_high: {open_threshold_high}, final_return: {final_return}")

    results_df = pd.DataFrame(results, columns=[
        "open_threshold_low", "open_threshold_high", "total_trading_days", "total_return", "final_return", "days_with_trades", "days_with_profit", "days_with_loss"
    ])

    results_df.to_excel("trading_strategy_results.xlsx", index=False)
    print("Results exported to trading_strategy_results.xlsx")

if __name__ == "__main__":
    main()
