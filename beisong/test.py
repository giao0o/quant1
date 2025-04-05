import os
import pandas as pd
import time
from tqdm import tqdm
import akshare as ak


class THSIndustry(object):
    """同花顺行业"""

    def __init__(self, concept_file):
        self.concept_file = concept_file

    def update(self):
        stock_industry_df = ak.stock_board_industry_summary_ths()  # 同花顺
        industry_list = []
        for concept_dict_data in tqdm(stock_industry_df.to_dict(orient="records"), desc="更新同花顺行业"):
            time.sleep(3)
            stock_board_concept_df = ak.stock_board_industry_cons_ths(symbol=concept_dict_data['板块'])
            stock_board_concept_df['行业'] = concept_dict_data['板块']
            [industry_list.append(_) for _ in stock_board_concept_df.to_dict(orient="records")]
        # 导出结果
        pd.DataFrame(industry_list).to_csv(self.concept_file)

    def get_industry_df(self):
        if not os.path.exists(self.concept_file):
            return None
        industry_df = pd.read_csv(self.concept_file, index_col=0)
        industry_df.reset_index(inplace=True, drop=True)
        return industry_df


def main():
    industry_info = THSIndustry("ths_concept.csv")
    industry_info.update() # 更新列表
    industry_df = industry_info.get_industry_df() # 获取行业全列表


if __name__ == '__main__':
    main()
