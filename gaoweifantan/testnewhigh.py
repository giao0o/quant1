import datetime
import pandas as pd

# 导入修改后的函数
from newhigh import is_new_high

def test_is_new_high():
    """
    测试 is_new_high 函数
    """
    test_stock = "600967"  # 股票代码
    test_date = pd.Timestamp(datetime.date(2024, 11, 21))
    N = 7  # 最近 7 个交易日
    M = 100  # 回溯 100 个交易日

    print("Testing stock:", test_stock)
    result = is_new_high(test_stock, test_date, N, M)
    if result:
        print(f"{test_stock} 在最近 {N} 天内创了过去 {M} 天的新高（包括最近 {N} 天）！")
    else:
        print(f"{test_stock} 在最近 {N} 天内没有创过去 {M} 天的新高。")

if __name__ == "__main__":
    test_is_new_high()
