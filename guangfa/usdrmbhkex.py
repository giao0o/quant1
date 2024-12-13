import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: 获取页面内容
url = "https://www.hkex.com.hk/Products/Listed-Derivatives/Foreign-Exchange/USD-CNH-Futures?sc_lang=zh-HK#&product=CUS"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Step 2: 解析HTML内容
soup = BeautifulSoup(response.text, 'html.parser')

# Step 3: 定位表格并提取数据
# 假设数据在HTML中的一个表格内
table = soup.find("table")  # 找到第一个表格，调整选择器以匹配页面结构
rows = table.find_all("tr")

# Step 4: 处理表格数据
data = []
columns = ["到期月份", "最後成交價", "變動", "上日結算價", "買入價", "賣出價", "開盤價", "最高價", "最低價", "成交數量", "上日未平倉合約"]

for row in rows[1:]:  # 跳过表头
    cols = row.find_all("td")
    data.append([col.text.strip() for col in cols])

# Step 5: 数据输出到终端
df = pd.DataFrame(data, columns=columns)

# 打印到终端
print(df.to_string(index=False))  # 格式化输出，不显示索引
