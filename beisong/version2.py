import pandas as pd
import random

# 读取Excel文件（根据实际路径修改）
df = pd.read_excel('/Users/jianaoli/Quant/quant1/beisong/as.xlsx', sheet_name='全部A股')

# 选择需要的列并重命名
df = df.rename(columns={
    '证券代码': '股票代码',
    '证券名称': '股票简称'
})

# 提取需要的列并转换为字典
companies = df[['股票代码', '股票简称', '一级行业', '二级行业', '三级行业', '公司简介']].dropna().to_dict('records')

def generate_question(companies):
    # 随机选择一家公司
    current_company = random.choice(companies)
    correct_industry = f"{current_company['一级行业']}-{current_company['二级行业']}-{current_company['三级行业']}"
    company_intro = current_company['公司简介']

    # 收集所有其他行业的唯一值（格式为 一级行业-二级行业-三级行业）
    other_industries = list(set(
        [f"{c['一级行业']}-{c['二级行业']}-{c['三级行业']}" 
         for c in companies if f"{c['一级行业']}-{c['二级行业']}-{c['三级行业']}" != correct_industry]
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
    
    return correct_index, correct_industry, company_intro

sum, right, wrong = 0, 0, 0

# 主循环
while True:
    correct_num, correct_industry, company_intro = generate_question(companies)
    
    # 获取用户输入
    while True:
        user_input = input("请输入正确答案序号（1-4），输入q退出：").strip()
        sum += 1
        if user_input.lower() == 'q':
            print(f"答题总数：{sum-1}，正确：{right}，错误：{wrong}")
            exit()
        if user_input.isdigit() and 1 <= int(user_input) <= 4:
            break
        print("输入无效，请重新输入数字1-4")
    
    # 验证答案
    if int(user_input) == correct_num:
        print("✅ 正确！进入下一题\n")
        right += 1
    else:
        print(f"❌ 错误，正确答案是：{correct_num} -> {correct_industry}")
        print(f"📌 公司介绍：{company_intro}\n")
        wrong += 1
