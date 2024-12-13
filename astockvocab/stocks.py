import akshare as ak
import pandas as pd
import concurrent.futures

# 获取所有 A 股上市公司基本信息
stock_info_df = ak.stock_info_a_code_name()

# 提取股票代码和名称列表
stock_data = stock_info_df.to_dict(orient="records")

# 获取行业信息的函数
def get_industry_info(stock):
    stock_code = stock['code']
    stock_name = stock['name']
    try:
        # 获取个股基本面信息，包含行业字段
        stock_fundamental_df = ak.stock_individual_info_em(symbol=stock_code)
    
        # 提取行业信息，确保可以安全访问
        industry = stock_fundamental_df.loc[stock_fundamental_df['item'] == '行业', 'value'].values[0]
    
        # 获取股票名称
        stock_name = stock_fundamental_df.loc[stock_fundamental_df['item'] == '股票简称', 'value'].values[0]
    
        # 返回结果
        return {'股票代码': stock_code, '股票名称': stock_name, '行业': industry}
    except Exception as e:
        print(f"获取 {stock_code} 的行业信息时出错: {e}")
        return None  # 出错时返回 None

# 使用线程池来加速请求
industry_list = []
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    # 使用 map 方法来并行化处理
    results = executor.map(get_industry_info, stock_data)
    
    # 过滤掉出错返回的 None 值
    for result in results:
        if result:
            industry_list.append(result)
            print(f"{result['股票名称']}的行业：{result['行业']}")

# 将数据分割为多个部分，每个部分小于 4000 行
def split_data(data, max_size=800):
    # 拆分数据为多个部分
    return [data[i:i + max_size] for i in range(0, len(data), max_size)]

# 将数据分割为多个文件
industry_data_parts = split_data(industry_list)

# 保存每个部分为独立的 JSON 文件
for i, part in enumerate(industry_data_parts):
    json_file = f"a股上市公司行业信息_part{i + 1}.json"
    industry_df = pd.DataFrame(part)
    industry_df.to_json(json_file, orient="records", force_ascii=False, indent=4)
    print(f"行业信息第 {i + 1} 部分已保存为 JSON 格式文件：{json_file}")
