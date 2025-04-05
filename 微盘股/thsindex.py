import akshare as ak


stock_board_industry_summary_ths_df = ak.stock_board_industry_summary_ths()
# print(stock_board_industry_summary_ths_df)
for x in stock_board_industry_summary_ths_df['板块']:
    print(f"当前值: '{x}'")
    if x == '微盘股':
        print(True)

# stock_board_industry_index_ths_df = ak.stock_board_industry_index_ths(symbol="微盘股", start_date="20240705", end_date="20241220")
# print(stock_board_industry_index_ths_df)