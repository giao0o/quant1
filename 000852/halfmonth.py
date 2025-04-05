# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime

# 设置中文显示格式
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

def get_index_data(symbol="000852", start_date="2004-01-01", end_date=None):
    """获取指数历史行情数据"""
    # 日期处理
    end_date = end_date or datetime.now().strftime("%Y-%m-%d")
    
    # 获取数据
    df = ak.index_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date
    )
    
    # 数据清洗
    df = df[['日期', '收盘']].copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df.rename(columns={'收盘': 'close'}, inplace=True)
    df.sort_values('日期', inplace=True)
    
    # 生成完整交易日序列
    full_dates = pd.date_range(start=df['日期'].min(), end=df['日期'].max())
    df = df.set_index('日期').reindex(full_dates).rename_axis('日期').reset_index()
    
    # 前向填充缺失值
    df['close'] = df['close'].ffill()
    return df.set_index('日期')

def calculate_half_month_returns(df):
    """计算半月收益率"""
    # 生成半月标签
    df['month'] = df.index.month
    df['half'] = np.where(df.index.day <= 15, 1, 2)
    
    # 获取每半月最后一个交易日
    last_days = df.groupby([df.index.year, 'month', 'half']).tail(1)
    last_days = last_days[~last_days.index.duplicated(keep='last')]
    
    # 计算收益率
    last_days['return'] = last_days['close'].pct_change()
    return last_days.dropna()

def generate_statistics(df):
    """生成统计报表"""
    # 基础统计
    stats = {
        '半月度收益': df.groupby(['month', 'half'])['return'].mean(),
        '上涨半月度收益': df[df['return'] > 0].groupby(['month', 'half'])['return'].mean(),
        '下跌半月度收益': df[df['return'] < 0].groupby(['month', 'half'])['return'].mean(),
        '上涨最大涨幅': df[df['return'] > 0].groupby(['month', 'half'])['return'].max(),
        '下跌最大跌幅': df[df['return'] < 0].groupby(['month', 'half'])['return'].min()
    }
    
    # 次数统计
    counts = df.groupby(['month', 'half'])['return'].agg([
        ('上涨次数', lambda x: (x > 0).sum()),
        ('下跌次数', lambda x: (x < 0).sum()),
        ('总次数', 'count')
    ])
    counts['上涨比例'] = counts['上涨次数'] / counts['总次数']
    counts['下跌比例'] = counts['下跌次数'] / counts['总次数']
    
    # 合并结果
    result = pd.concat([pd.DataFrame(stats), counts], axis=1)
    result.index = result.index.map(lambda x: f"{x[0]}_{x[1]}")
    return result[['半月度收益', '上涨半月度收益', '下跌半月度收益', 
                 '上涨最大涨幅', '下跌最大跌幅',
                 '上涨次数', '下跌次数', '上涨比例', '下跌比例']]

def format_output(df):
    """格式化输出"""
    format_rules = {
        '半月度收益': '{:.2%}',
        '上涨半月度收益': '{:.2%}',
        '下跌半月度收益': '{:.2%}',
        '上涨最大涨幅': '{:.2%}',
        '下跌最大跌幅': '{:.2%}',
        '上涨比例': '{:.1%}',
        '下跌比例': '{:.1%}'
    }
    
    formatted_df = df.copy()
    for col, fmt in format_rules.items():
        formatted_df[col] = formatted_df[col].apply(lambda x: fmt.format(x) if pd.notnull(x) else 'N/A')
    return formatted_df

if __name__ == "__main__":
    # 参数设置
    INDEX_CODE = "000852"  # 指数代码
    START_DATE = "2004-01-01"
    
    # 数据获取
    raw_data = get_index_data(symbol=INDEX_CODE, start_date=START_DATE)
    
    # 计算半月收益率
    processed_data = calculate_half_month_returns(raw_data)
    
    # 生成统计结果
    stats_result = generate_statistics(processed_data)
    
    # 格式化输出
    final_output = format_output(stats_result)
    
    # 打印结果
    print(tabulate(final_output, headers='keys', tablefmt='pretty', showindex=True))