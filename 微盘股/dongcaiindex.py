import akshare as ak

# 获取概念板块历史数据
stock_board_concept_hist_em_df = ak.stock_board_concept_hist_em(
    symbol="微盘股",
    period="daily",
    start_date="20240207",
    end_date="20241219",
    adjust=""
)

# 统计涨跌幅小于各阈值的数量和具体日期
thresholds = [-3, -4, -5, -6, -7]
results = {}

for threshold in thresholds:
    filtered_data = stock_board_concept_hist_em_df[
        stock_board_concept_hist_em_df['涨跌幅'] < threshold
    ]
    results[threshold] = {
        "count": len(filtered_data),
        "dates": filtered_data['日期'].tolist()
    }

# 输出结果
for threshold, data in results.items():
    print(f"涨跌幅小于 {threshold}% 的天数: {data['count']}")
    print(f"具体日期: {data['dates']}")

thresholds1 = [3, 4, 5, 6, 7]
results1 = {}

for threshold in thresholds1:
    filtered_data = stock_board_concept_hist_em_df[
        stock_board_concept_hist_em_df['涨跌幅'] > threshold
    ]
    results1[threshold] = {
        "count": len(filtered_data),
        "dates": filtered_data['日期'].tolist()
    }

# 输出结果
for threshold, data in results1.items():
    print(f"涨跌幅大于 {threshold}% 的天数: {data['count']}")
    print(f"具体日期: {data['dates']}")
