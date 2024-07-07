import matplotlib.pyplot as plt
import akshare as ak
import pandas as pd

def get_data(symbol, start_date, end_date):
    stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="")
    stock_data['日期'] = pd.to_datetime(stock_data['日期'])
    stock_data.set_index('日期', inplace=True)
    return stock_data

def main():
    symbol = "002780"
    start_date = "20240212"
    end_date = "20240605"
    initial_cash = 10000
    cash = initial_cash
    shares_held = 1000
    buy_amount = 10000
    open_threshold_low = -0.006  # 早盘低开阈值
    stop_loss_threshold = -0.006  # 盘中跌幅阈值
    open_threshold_high = 0.014  # 早盘高开阈值
    intraday_threshold = 0.014  # 盘中涨跌幅阈值
    
    fee_rate = 0.0002  # 手续费率
    stamp_duty_rate = 0.0005  # 印花税率（只在卖出时计算）

    stock_data = get_data(symbol, start_date, end_date)
    print(stock_data.head())
    first_openprice = stock_data.iloc[0]['开盘']

    total_trading_days = len(stock_data)
    days_with_trades = 0
    days_with_loss = 0
    days_with_profit = 0

    profits = []  # 每日收益
    cumulative_profits = []  # 累计收益
    cumulative_profit = 0
    no_trades_days = []  # 记录没有交易的交易日

    previous_close_price = None

    for index, row in stock_data.iterrows():
        # 获取当日开盘、收盘价格和最高价
        open_price = row['开盘']
        close_price = row['收盘']
        high_price = row['最高']
        low_price = row['最低']

        if previous_close_price is not None:
            day_traded = False  # 增加一个布尔变量来跟踪当天是否有交易
            old_cash = cash
            daily_profit = 0  # 当天的盈亏

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
                    day_traded = True

                    # 判断盘中涨幅是否超过阈值，进行卖出
                    intraday_return = (high_price - previous_close_price) / previous_close_price
                    if intraday_return >= intraday_threshold:
                        sell_price = (1 + intraday_threshold) * previous_close_price
                        revenue = buy_shares * sell_price * (1 - fee_rate - stamp_duty_rate)
                        cash += revenue
                        shares_held -= buy_shares
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

                    # 判断盘中跌幅是否超过阈值，进行买入
                    intraday_return = (low_price - previous_close_price) / previous_close_price
                    if intraday_return <= stop_loss_threshold:
                        buy_price = previous_close_price * (1 + stop_loss_threshold)
                        buy_shares = int(revenue / buy_price)
                        while cash < (buy_shares * buy_price) * (1 + fee_rate) and buy_shares > 0:
                            buy_shares -= 1
                        if buy_shares > 0:
                            cost = buy_shares * buy_price * (1 + fee_rate)
                            cash -= cost
                            shares_held += buy_shares
                            day_traded = True

            else:  # 早盘未低开未高开，进行盘中交易
                intraday_return = (low_price - previous_close_price) / previous_close_price
                if intraday_return <= stop_loss_threshold:  # 盘中跌幅超过阈值
                    buy_price = previous_close_price * (1 + stop_loss_threshold)
                    buy_shares = int(buy_amount / buy_price)
                    while cash < (buy_shares * buy_price) * (1 + fee_rate) and buy_shares > 0:
                        buy_shares -= 1
                    if buy_shares > 0:
                        cost = buy_shares * buy_price * (1 + fee_rate)
                        cash -= cost
                        shares_held += buy_shares
                        day_traded = True

                elif intraday_return >= intraday_threshold:  # 盘中涨幅超过阈值
                    sell_price = (1 + intraday_threshold) * previous_close_price
                    sell_shares = int(buy_amount / sell_price)
                    while sell_shares > shares_held - 1000 and sell_shares > 0:
                        sell_shares -= 1
                    if sell_shares > 0:
                        revenue = sell_shares * sell_price * (1 - fee_rate - stamp_duty_rate)
                        cash += revenue
                        shares_held -= sell_shares
                        day_traded = True

            # 收盘前调整仓位，确保持有1000股
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
                    daily_profit = cash - old_cash
                else:
                    days_with_profit += 1
                    daily_profit = cash - old_cash
                
                cumulative_profit += daily_profit
            else:
                no_trades_days.append(index)
                daily_profit = 0
            
            profits.append(daily_profit)
            cumulative_profits.append(cumulative_profit)
        else:
            profits.append(0)
            cumulative_profits.append(cumulative_profit)

        previous_close_price = close_price

    # 提取 yearmonth 信息
    yearmonth = stock_data.index.to_period('M').strftime('%Y-%m')

    # 创建双 y 轴图
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 绘制累计收益曲线
    ax1.plot(stock_data.index, cumulative_profits, label='Cumulative Profits', color='b')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Cumulative Profits', fontsize=12, color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # 创建第二个 y 轴并绘制股票收盘价曲线
    ax2 = ax1.twinx()
    ax2.plot(stock_data.index, stock_data['收盘'], label='Stock Close Price', color='purple')
    ax2.set_ylabel('Stock Close Price', fontsize=12, color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')

    # 增加日收益曲线
    ax1.plot(stock_data.index, profits, label='Daily Profit (0 for No Trades)', color='g')

    # 增加水平线
    ax1.axhline(y=0, color='r', linestyle='--', linewidth=0.8, label='0 Line')

    # 设置图例和标题
    fig.suptitle('T+0 Trading Strategy Performance', fontsize=16)
    fig.tight_layout()
    fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))

    # 保存图表为图片
    plt.savefig('trading_strategy_performance.png')

    # 显示图表
    plt.show()

    # 打印总结信息
    print(f"总交易日: {total_trading_days}, 期间涨跌幅：{(close_price / first_openprice - 1):.4f}, 做T收益率: {(cash / initial_cash - 1):.4f}, 有交易的天数: {days_with_trades}, 盈利的天数: {days_with_profit}, 亏损的天数: {days_with_loss}")

if __name__ == "__main__":
    main()
