import akshare as ak
import pandas as pd

def get_minute_data(symbol, period):
    stock_data = ak.stock_zh_a_minute(symbol=symbol, period=period, adjust="qfq")
    stock_data['day'] = pd.to_datetime(stock_data['day'])
    stock_data.set_index('day', inplace=True)
    return stock_data

def main():
    symbol = "sh600751"
    period = "1"  # 1分钟数据
    initial_cash = 10000
    cash = initial_cash
    shares_held = 1000
    buy_amount = 10000
    open_threshold_low = -0.005  # 早盘低开阈值
    open_threshold_high = 0.005  # 早盘高开阈值
    intraday_threshold = 0.005  # 盘中涨跌幅阈值
    stop_loss_threshold = -0.005  # 盘中跌幅阈值
    fee_rate = 0.0002  # 手续费率
    stamp_duty_rate = 0.0005  # 印花税率（只在卖出时计算）

    stock_data = get_minute_data(symbol, period)
    print(stock_data.head())

    previous_close_price = None
    previous_date = None

    for index, row in stock_data.iterrows():
        # 获取当前时间点的价格
        open_price = row['open']
        close_price = row['close']
        high_price = row['high']
        low_price = row['low']
        current_date = index.date()

        # 打印日期信息
        if previous_date != current_date:
            print(f"日期: {current_date}")
            previous_date = current_date

        if previous_close_price is not None and current_date != index.date():
            # 计算早盘涨跌幅
            open_return = (open_price - previous_close_price) / previous_close_price

            # 策略逻辑
            # 日内交易逻辑
            if open_return <= open_threshold_low:  # 早盘低开
                buy_shares = int(buy_amount / open_price)
                while cash < (buy_shares * open_price) * (1 + fee_rate) and buy_shares > 0:
                    buy_shares -= 1
                if buy_shares > 0:
                    cost = buy_shares * open_price * (1 + fee_rate)
                    cash -= cost
                    shares_held += buy_shares
                    print(f"买入 {buy_shares} 股，买入价格 {open_price}，买入时机 早盘低开，现金余额 {cash}")

                    # 判断盘中涨幅是否超过阈值，进行卖出
                    intraday_return = (high_price - open_price) / open_price
                    if intraday_return >= intraday_threshold:
                        revenue = buy_shares * high_price * (1 - fee_rate - stamp_duty_rate)
                        cash += revenue
                        shares_held -= buy_shares
                        print(f"盘中卖出 {buy_shares} 股，卖出价格 {high_price}，现金余额 {cash}")

            elif open_return >= open_threshold_high:  # 早盘高开
                sell_shares = int(buy_amount / open_price)
                while sell_shares > shares_held - 1000 and sell_shares > 0:
                    sell_shares -= 1
                if sell_shares > 0:
                    revenue = sell_shares * open_price * (1 - fee_rate - stamp_duty_rate)
                    cash += revenue
                    shares_held -= sell_shares
                    print(f"卖出 {sell_shares} 股，卖出价格 {open_price}，卖出时机 早盘高开，现金余额 {cash}")

                    # 判断盘中跌幅是否超过阈值，进行买入
                    intraday_return = (low_price - open_price) / open_price
                    if intraday_return <= stop_loss_threshold:
                        buy_shares = int(revenue / low_price)
                        while cash < (buy_shares * low_price) * (1 + fee_rate) and buy_shares > 0:
                            buy_shares -= 1
                        if buy_shares > 0:
                            cost = buy_shares * low_price * (1 + fee_rate)
                            cash -= cost
                            shares_held += buy_shares
                            print(f"盘中买入 {buy_shares} 股，买入价格 {low_price}，现金余额 {cash}")

            else:  # 早盘未低开未高开，进行盘中交易
                intraday_return = (low_price - open_price) / open_price
                if intraday_return <= stop_loss_threshold:  # 盘中跌幅超过阈值
                    buy_shares = int(buy_amount / low_price)
                    while cash < (buy_shares * low_price) * (1 + fee_rate) and buy_shares > 0:
                        buy_shares -= 1
                    if buy_shares > 0:
                        cost = buy_shares * low_price * (1 + fee_rate)
                        cash -= cost
                        shares_held += buy_shares
                        print(f"盘中买入 {buy_shares} 股，买入价格 {low_price}，现金余额 {cash}")

                elif intraday_return >= intraday_threshold:  # 盘中涨幅超过阈值
                    sell_shares = int(buy_amount / high_price)
                    while sell_shares > shares_held - 1000 and sell_shares > 0:
                        sell_shares -= 1
                    if sell_shares > 0:
                        revenue = sell_shares * high_price * (1 - fee_rate - stamp_duty_rate)
                        cash += revenue
                        shares_held -= sell_shares
                        print(f"盘中卖出 {sell_shares} 股，卖出价格 {high_price}，现金余额 {cash}")

            # 收盘前调整仓位，确保持有1000股
            if shares_held > 1000:
                sell_shares = shares_held - 1000
                revenue = sell_shares * close_price * (1 - fee_rate - stamp_duty_rate)
                cash += revenue
                shares_held = 1000
                print(f"收盘调整卖出 {sell_shares} 股，卖出价格 {close_price}，现金余额 {cash}")

            elif shares_held < 1000:
                buy_shares = 1000 - shares_held
                while cash < (buy_shares * close_price) * (1 + fee_rate) and buy_shares > 0:
                    buy_shares -= 1
                if buy_shares > 0:
                    cost = buy_shares * close_price * (1 + fee_rate)
                    cash -= cost
                    shares_held += buy_shares
                    print(f"收盘调整买入 {buy_shares} 股，买入价格 {close_price}，现金余额 {cash}")

        previous_close_price = close_price

if __name__ == "__main__":
    main()
