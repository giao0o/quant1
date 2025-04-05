import pandas as pd
import random

# 读取Excel文件（根据实际路径修改）
df = pd.read_excel('/Users/jianaoli/Quant/quant1/beisong/stocks.xlsx', sheet_name='选股结果')

# 预处理：确保列名正确
df = df.rename(columns={'所属同花顺行业': '行业'})  # 将列名简化为'行业'

# 提取需要的列：股票代码、股票简称、行业
companies = df[['股票代码', '股票简称', '行业']].dropna().to_dict('records')

def generate_question(companies):
    # 随机选择一家公司
    current_company = random.choice(companies)
    correct_industry = current_company['行业']
    
    # 收集所有其他行业的唯一值
    other_industries = list(set(
        [c['行业'] for c in companies if c['行业'] != correct_industry]
    ))
    
    # 随机选择3个不重复的错误选项
    wrong_choices = random.sample(other_industries, 3) if len(other_industries) >= 3 else []
    
    # 构造选项列表（正确+错误）
    options = [correct_industry] + wrong_choices
    random.shuffle(options)  # 打乱选项顺序
    
    # 记录正确答案的位置
    correct_index = options.index(correct_industry) + 1
    
    # 打印问题
    print(f"\n股票代码：{current_company['股票代码']}  名称：{current_company['股票简称']}")
    for idx, opt in enumerate(options, 1):
        print(f"{idx}. {opt}")
    
    return correct_index

# 主循环
while True:
    correct_num = generate_question(companies)
    
    # 获取用户输入
    while True:
        user_input = input("请输入正确答案序号（1-4），输入q退出：").strip()
        if user_input.lower() == 'q':
            exit()
        if user_input.isdigit() and 1 <= int(user_input) <=4:
            break
        print("输入无效，请重新输入数字1-4")
    
    # 验证答案
    if int(user_input) == correct_num:
        print("✅ 正确！进入下一题\n")
    else:
        print(f"❌ 错误，正确答案是：{correct_num}\n")