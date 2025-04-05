import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ========== 基础数据准备 ==========
def get_all_stocks():
    """获取全市场股票列表"""
    stock_info = ak.stock_info_a_code_name()
    return stock_info[stock_info['code'].str.startswith(('00', '60', '30'))]  # 仅A股

def get_ipo_date():
    """获取IPO日期"""
    ipo_data = ak.stock_ipo_info()
    return ipo_data[['code', 'listing_date']]

# ========== 财务数据获取 ==========
def get_financial_data(year):
    """获取指定年份的年报财务数据"""
    financial_df = ak.stock_financial_report_sina(2023)  # 需要根据年份调整
    # 选取需要的字段：营业收入、净利润、ROE、毛利率、营业利润率
    return financial_df[['code', '报表日期', '营业收入', '净利润', '净资产收益率', '销售毛利率', '营业利润率']]

# ========== 员工数据获取 ==========
def get_employee_data(year):
    """获取员工数据"""
    employee_df = ak.stock_employee_analysis_em(symbol="SH600000")  # 示例接口，需要遍历个股
    # 需要自行实现全市场获取逻辑
    return employee_df[['code', '员工人数', '应付职工薪酬']]

# ========== 机构预测数据获取 ==========
def get_eps_forecast():
    """获取机构预测EPS数据"""
    forecast_df = ak.stock_profit_forecast()
    return forecast_df[['code', '预测年度', '预测EPS']]

# ========== 策略筛选逻辑 ==========
class StrategyFilter:
    def __init__(self, current_date):
        self.current_date = current_date
        
    def filter_ipo_age(self, stocks):
        """IPO时间筛选"""
        ipo_date = get_ipo_date()
        merged = pd.merge(stocks, ipo_date, on='code')
        merged['ipo_years'] = (self.current_date - merged['listing_date']).dt.days / 365
        return merged[(merged['ipo_years'] >= 1) & (merged['ipo_years'] <= 8)]
    
    def filter_financials(self, stocks):
        """财务指标筛选"""
        financials = get_financial_data(self.current_date.year-1)  # 使用上一年年报
        merged = pd.merge(stocks, financials, on='code')
        return merged[
            (merged['营业收入'] >= 1e8) & (merged['营业收入'] <= 1e10) &
            (merged['净利润'] >= 1e7) & (merged['净利润'] <= 1e9) &
            (merged['净资产收益率'] > 5) &
            (merged['销售毛利率'] > 20) &
            (merged['营业利润率'] > 5)
        ]
    
    def filter_employee(self, stocks):
        """人均指标筛选"""
        employee = get_employee_data(self.current_date.year-1)
        merged = pd.merge(stocks, employee, on='code')
        merged['人均营收'] = merged['营业收入'] / merged['员工人数']
        merged['人均利润'] = merged['净利润'] / merged['员工人数']
        merged['人均薪酬'] = merged['应付职工薪酬'] / merged['员工人数']
        return merged[
            (merged['员工人数'] >= 1000) & (merged['员工人数'] <= 10000) &
            (merged['人均营收'] > 5e5) &
            (merged['人均利润'] > 1e4) &
            (merged['人均薪酬'] > 8e4)
        ]
    
    def filter_eps_growth(self, stocks):
        """EPS增长预测筛选"""
        eps = get_eps_forecast()
        # 需要处理预测数据的时间维度
        # 此处为示意逻辑，实际需要计算复合增长率
        return stocks

# ========== 回测引擎 ==========
class BacktestEngine:
    def __init__(self, start_date, end_date):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.capital = 1e6  # 初始资金
        self.positions = {}
        
    def get_rebalance_dates(self):
        """生成调仓日期序列"""
        dates = []
        current = self.start_date
        while current <= self.end_date:
            if current.month == 6 and current.day == 30:
                dates.append(current)
            current += timedelta(days=1)
        return dates
    
    def run_backtest(self):
        rebalance_dates = self.get_rebalance_dates()
        portfolio_values = []
        
        for date in rebalance_dates:
            # 执行筛选逻辑
            filter = StrategyFilter(date)
            stocks = get_all_stocks()
            stocks = filter.filter_ipo_age(stocks)
            stocks = filter.filter_financials(stocks)
            stocks = filter.filter_employee(stocks)
            stocks = filter.filter_eps_growth(stocks)
            
            # 获取价格数据
            selected_codes = stocks['code'].tolist()
            prices = ak.stock_zh_a_hist(symbol=selected_codes, period="daily", start_date=date.strftime('%Y%m%d'), end_date=date.strftime('%Y%m%d'))
            
            # 计算等权重持仓
            if len(selected_codes) > 0:
                position_size = self.capital / len(selected_codes)
                self.positions = {code: position_size / prices[code]['收盘'].iloc[0] for code in selected_codes}
            
            # 计算组合净值
            # 此处需要实现持仓市值计算逻辑
            portfolio_values.append(self.capital)
            
        return portfolio_values

# ========== 执行回测 ==========
if __name__ == "__main__":
    engine = BacktestEngine('2015-06-30', '2023-06-30')
    results = engine.run_backtest()
    print(pd.Series(results, index=engine.get_rebalance_dates()).plot())