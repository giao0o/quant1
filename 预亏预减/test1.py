import akshare as ak

# 获取指定日期的业绩预告数据
stock_yjyg_em_df = ak.stock_yjyg_em(date="20241231")

# 打印数据
print(stock_yjyg_em_df)

# 导出为 CSV 文件
stock_yjyg_em_df.to_csv("stock_yjyg_em_20241231.csv", index=False, encoding="utf_8_sig")

print("数据已导出为 stock_yjyg_em_20241231.csv")