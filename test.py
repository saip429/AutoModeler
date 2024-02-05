'''
TEMPORARY FILE
'''

import pandas as pd 
import constants as c
from data_prep_pipeline import DataPrep as p
from data_preprocessing_pipeline import DataPreprocessor as q 
result_dict:dict= p('./sample_excel copy.xls').print_result()

preprocess=q(result_dict.get('dataframe'))
# for k,v in result_dict.items():
#     print(k,':',v) \

res_preprocess=preprocess.handle_na(c.MEAN) 
res_preprocess=preprocess.handle_na(c.MODE) 
res_preprocess=preprocess.handle_outliers(c.SPLINE) 
res_preprocess=preprocess.label_encoding()

res_preprocess=preprocess.standardize_data()


#res_preprocess=preprocess.handle_outliers(c.DROP_OUTLIERS)


df=preprocess.get_result().get('dataframe') 
df.to_csv('sample_csv copy.csv', index=False) 
print('replaced')

print(result_dict.get('inspect results' ).get('summary'))
print(result_dict.get('dataframe'))
print(preprocess.get_result().get('dataframe'))

