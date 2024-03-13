"""
Data preparation pipeline:
input: file path name
this module reads the file path and processes it based on file type 

read_use_csv(): process files of type csv
read_user_excel(): process files of type xls or xlsx 
read_user_pdf(): process files of type pdf

output: pandas dataframe, EDA results, purge logs

get_results(): returns dataframe as str
inspectData(): performs EDA and returns output in dict
recommend)na_ops(): recommends ways to handle NaN values



"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from scipy.stats import zscore
from main.purge import PurgeDirectory
import os
import io
from django.conf import settings
from .purge import PurgeDirectory


class DataPrep:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.file_type: str = os.path.basename(self.file_path)[-1]
        self.file_name: str = os.path.basename(self.file_path).split(".")[0]
        self.df: pd.DataFrame = None
        self.inspectResults: dict = {}
        self.recommendation: str = None
        self.processData()
        self.inspectData()
        self.recommend_na_ops()
        file_purger=PurgeDirectory(settings.FILES_UPLOAD_DIR,3)
        self.file_logs=file_purger.returnLogs()
        image_purger=PurgeDirectory(settings.IMAGES_UPLOAD_DIR,3)
        self.image_logs=image_purger.returnLogs()
    # context manager functions
    def __enter__(self):
        return self

    # context manager functions
    def __exit__(self, exc_tb, exc_type, exc_value):
        pass

    def read_user_csv(self) -> None:
        self.df = pd.read_csv(self.file_path)

    # def read_user_excel(self)->None:
    #     self.df=pd.read_excel(self.file_path)

    # def read_user_pdf(self)->None:

    #     try:
    #         with pdfplumber.open(self.file_path) as pdf:
    #              text = pdf.pages[0].extract_text()

    #         # Convert the extracted text to a DataFrame
    #         rows = [line.split('\t') for line in text.split('\n')]
    #         columns = rows[0]
    #         data = rows[1:]

    #         self.df = pd.DataFrame(data, columns=columns)

    #     except Exception as e:
    #         raise ValueError('Error while reading from file path')

    def processData(self):
        try:
            self.read_user_csv()
        except Exception as e:
            raise TypeError(e)

    # Analyse Data (EDA)
    def inspectData(self):
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()

        self.info = info_str.replace('\n','<br>')

        self.summary = self.df.describe()

        self.missing_values = self.df.isnull().sum().sum()

        numeric_columns = self.df.select_dtypes(include=["number"]).columns

        z_scores = pd.DataFrame(
            zscore(self.df[numeric_columns]),
            columns=numeric_columns,
            index=self.df.index,
        )

        z_score_threshold = 3

        # self.outliers = (
        #     self.df[(z_scores > z_score_threshold)].any(axis=1).to_html(index=False)
        # )

        df_outliers = self.df.loc[(z_scores > z_score_threshold).any(axis=1)]
        
        if df_outliers.empty:
            self.outliers='<h1> no outliers found </h1>'
        else:
            self.outliers=df_outliers.to_html(index=False)
        plt.figure(figsize=(10, 6))
        sns.pairplot(self.df)
        image_id = random.randint(100, 999)
        plt.savefig(f"images/{self.file_name}_{image_id}.png")
        path = f"images/{self.file_name}_{image_id}.png"
        abs_path = os.path.abspath(path)
        self.pairplot = f"{abs_path}"

    def recommend_na_ops(self):
        if self.df.isna().sum().sum() > (self.df.shape[0] * 0.2):
            self.recommendation = "impute missing values"

        elif self.df.isna().sum().sum() == 0:
            self.recommendation = "no missing values"
        else:
            self.recommendation = "drop missing values"

    def get_result(self) -> dict:
        context = {}
        if self.df is not None:
            context["dataframe"] = self.df
            context['info']=self.info
            context['summary']=self.summary
            context['missing values']=self.missing_values
            context['outliers']=self.outliers
            context['pairplot']=self.pairplot

            context["recommendation"] = self.recommendation
            context['file_logs']=self.file_logs
            context['image_logs']=self.image_logs
            return context
        else:
            context["error"] = "Oops something went wrong"
            return context
