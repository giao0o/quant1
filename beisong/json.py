import pandas as pd  # ← 必须添加
import json

# 读取Excel文件
df = pd.read_excel('/Users/jianaoli/Quant/quant1/beisong/as.xlsx', sheet_name='全部A股')

# 筛选需要的列
df = df[['证券代码', '证券名称', '一级行业', '二级行业', '三级行业', '公司简介']]

# 转换为字典列表
data = df.to_dict(orient='records')

# 保存为JSON文件
with open('companies.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 转换完成！生成文件：companies.json")