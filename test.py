'''
TEMPORARY FILE
'''

import pandas as pd 
import constants as c
from data_prep_pipeline import DataPrep as p
from data_preprocessing_pipeline import DataPreprocessor as q 
result_dict:dict= p('./sample_excel copy.xls').print_result()

with q(result_dict.get('dataframe'),'sample_csv copy.csv') as q_ctx:
    q_ctx.handle_na(c.MEAN)
    q_ctx.handle_na(c.MODE)
    q_ctx.handle_outliers(c.SPLINE)
    q_ctx.label_encoding()
    q_ctx.standardize_data()
    res:dict=q_ctx.get_result()





print(result_dict.get('inspect results' ).get('summary'))
print(result_dict.get('inspect results' ).get('pairplot'))
print(result_dict.get('dataframe'))
print(res.get('dataframe'))

