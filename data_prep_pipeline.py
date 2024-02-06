
'''
Data preparation pipeline:
input: file path name
this module reads the file path and processes it based on file type 

read_use_csv(): process files of type csv
read_user_excel(): process files of type xls or xlsx 
read_user_pdf(): process files of type pdf

output: pandas dataframe, EDA results, purge logs

print_results(): returns dataframe as str
inspectData(): performs EDA and returns output in dict


'''

import pandas as pd 
import pdfplumber
import matplotlib.pyplot as plt 
import seaborn as sns
import random
from scipy.stats import zscore
from utils.purge import PurgeDirectory
import os
import io


class DataPrep:
    def __init__(self, file_path:str)->None:
        self.file_path:str=file_path
        self.file_type:str= file_path.split('.')[-1]
        self.file_name:str=file_path.split('.')[1]
        self.df:pd.DataFrame=None
        self.inspectResults:dict={}
        self.recommendation:str=None
        self.processData()
       
        self.inspectData()
        self.recommend_na_ops()
        purger=PurgeDirectory('./images',3)
        self.logs=purger.returnLogs()
        



    def read_user_csv(self)->None:
        self.df=pd.read_csv(self.file_path)

    def read_user_excel(self)->None:
        self.df=pd.read_excel(self.file_path)

    def read_user_pdf(self)->None:
       
        try:
            with pdfplumber.open(self.file_path) as pdf: 
                 text = pdf.pages[0].extract_text()

            # Convert the extracted text to a DataFrame 
            rows = [line.split('\t') for line in text.split('\n')]
            columns = rows[0]
            data = rows[1:]

            self.df = pd.DataFrame(data, columns=columns) 

        except Exception as e: 
            raise ValueError('Error while reading from file path')


    def processData(self):
        if self.file_type=='csv':
            self.read_user_csv()
        elif self.file_type=='xls' or self.file_type=='xlsx':
            self.read_user_excel()
        elif self.file_type=='pdf':
            self.read_user_pdf()
        else:
            raise ValueError(f'unsupported file type: {self.file_type}')
        
        
    # Analyse Data (EDA)
    def inspectData(self):
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()

        self.inspectResults['info']= info_str
       
        self.inspectResults['summary'] = self.df.describe().to_dict()
        
        self.inspectResults['missing_values']= self.df.isnull().sum()
        
        numeric_columns = self.df.select_dtypes(include=['number']).columns
        

        z_scores = pd.DataFrame(zscore(self.df[numeric_columns]), columns=numeric_columns, index=self.df.index)


        z_score_threshold = 3
        
        self.inspectResults['outliers']=self.df[(z_scores > z_score_threshold)].any(axis=1).to_dict()

        plt.figure(figsize=(10,6))
        sns.pairplot(self.df)
        image_id= random.randint(100,999)
        plt.savefig(f'images/{self.file_name}_{image_id}.png')
        path=f'images/{self.file_name}_{image_id}.png'
        abs_path= os.path.abspath(path)
        self.inspectResults['pairplot']=f'{abs_path}'

        



    
    def recommend_na_ops(self):
        if self.df.isna().sum().sum() > (self.df.shape[0] * 0.2):
            self.recommendation='impute missing values'

        elif self.df.isna().sum().sum() == 0:
            self.recommendation='no missing values'
        else:
            self.recommendation='drop missing values'
            
        

    def print_result(self)->dict:
        context={}
        if self.df is not None:
            context['dataframe']=self.df
            context['inspect results']=self.inspectResults
            context['purge logs']=self.logs 
            context['recommendation']=self.recommendation
            
            return context
        else:
            return 'no data to display'
        
# test
if __name__=='__main__':
    my_pipeline=DataPrep('./sample_excel.xls')
    result=my_pipeline.print_result()
    print(result)
        
