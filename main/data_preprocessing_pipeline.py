"""
Data preprocessing pipeline:
involves functions to handle missing values, outliers, standardize data, label encoding, one hot encoding
implemented as a context manager
required args:  file path
returns: data pre processing results upon invoking the get_result method

"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, MinMaxScaler, RobustScaler
from scipy.stats import zscore
from scipy.interpolate import UnivariateSpline
from scipy.stats.mstats import winsorize
from . import constants as c
import matplotlib
matplotlib.use('agg')



class DataPreprocessor:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.dataframe: pd.DataFrame = pd.read_csv(self.file_name)
        self.returnLogs: list = []
        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            self.save()

    def save(self) -> None:
        self.dataframe.to_csv(f"{self.file_name}", index=False)

    def handle_na(self, method: str):
        # drop missing columns
        self.dataframe = self.dataframe.dropna(axis=1, how="all")
        # drop missing values
        if method == c.DROPNA:
            self.dataframe = self.dataframe.dropna(axis=0, inplace=True)
            self.returnLogs.append("dropped all null values") 

        elif method == c.MEAN:
            numeric_columns = self.dataframe.select_dtypes(
                include=["float64", "int64"]
            ).columns
            self.dataframe[numeric_columns] = self.dataframe[numeric_columns].fillna(
                self.dataframe[numeric_columns].mean()
            )
            self.returnLogs.append("imputation with mean successful")

        elif method == c.MEDIAN:
            numeric_columns = self.dataframe.select_dtypes(
                include=["float64", "int64"]
            ).columns
            self.dataframe[numeric_columns] = self.dataframe[numeric_columns].fillna(
                self.dataframe[numeric_columns].median()
            )
            self.returnLogs.append("imputation with median successful")

        elif method == c.MODE:
            all_columns = self.dataframe.select_dtypes(include=["object"]).columns
            for col in all_columns:
                if self.dataframe[col].notna().any():
                    mode_value = self.dataframe[col].mode()[0]

                    self.dataframe[col] = self.dataframe[col].fillna(mode_value)

            self.returnLogs.append("imputation with mode successful")

        else:
            raise ValueError("invalid operation")

    # label encoding
    def label_encoding(self):
        label_encoder = LabelEncoder()
        for column in self.dataframe.select_dtypes(include="object").columns:
            self.dataframe[column] = label_encoder.fit_transform(self.dataframe[column])
        self.returnLogs.append('label encoding successful')

    # one hot encoding
    def one_hot_encoding(self):
        one_hot_encoder = OneHotEncoder(sparse=False)

        object_columns = self.dataframe.select_dtypes(include="object").columns

        encoded_df = pd.DataFrame()

        for column in object_columns:
            column_data = self.dataframe[column].values.reshape(-1, 1)

            encoded_data = one_hot_encoder.fit_transform(column_data)

            encoded_df_temp = pd.DataFrame(
                encoded_data, columns=one_hot_encoder.get_feature_names_out([column])
            )

            encoded_df = pd.concat([encoded_df, encoded_df_temp], axis=1)

        self.dataframe = pd.concat([self.dataframe, encoded_df], axis=1)

        self.dataframe.drop(object_columns, axis=1, inplace=True)
        self.returnLogs.append('one hot encoding successful')

    # outlier handling
    def handle_outliers(self, method: str):
        numeric_columns = self.dataframe.select_dtypes(
            include=["float64", "int64"]
        ).columns
        if method == c.SPLINE:

            def spline_columns(column):
                x = np.arange(len(column))
                y = column.values
                spline = UnivariateSpline(x, y)
                return spline(x)

            self.dataframe[numeric_columns] = self.dataframe[numeric_columns].apply(
                spline_columns
            )
            self.returnLogs.append('splined outliers')

        elif method == c.WINSORIZE:

            def winsorize_columns(column, lower_limit=0.01, upper_limit=0.01):
                return winsorize(column, limits=[lower_limit, upper_limit])

            self.dataframe[numeric_columns] = self.dataframe[numeric_columns].apply(
                winsorize_columns
            )
            self.returnLogs.append('winsorized outliers')

        elif method == c.DROP_OUTLIERS:

            def drop_outliers(df: pd.DataFrame, z_threshold=3):
                z_scores = zscore(self.dataframe[numeric_columns])
                outlier_indices = (abs(z_scores) > z_threshold).any(axis=1)
                cleaned_df = df[~outlier_indices]

                return cleaned_df

            self.dataframe[numeric_columns] = drop_outliers(
                self.dataframe[numeric_columns]
            )
            self.returnLogs.append('dropped outliers')

        else:
            raise ValueError("invalid operation")

    # standardize data (only after encoding)
    # def standardize_data(self):
    #     self.dataframe.columns = self.dataframe.columns.astype(str)

    #     # Standardize numeric
    #     numeric_columns = self.dataframe.select_dtypes(
    #         include=["float64", "int64"]
    #     ).columns
    #     scaler = StandardScaler()
    #     self.dataframe[numeric_columns] = scaler.fit_transform(
    #         self.dataframe[numeric_columns]
    #     )
    #     self.returnLogs.append("standardized data")

    # scale data 
    def scale_data(self, method:str, target_column:str):
        # standard scaling
        if method==c.STANDARD_SCALING:
            scaler=StandardScaler()
        elif method==c.MINMAX_SCALING:
            scaler=MinMaxScaler()
        elif method==c.ROBUST_SCALING:
            scaler=RobustScaler()
        else: 
            raise ValueError("invaid scaler type")
        df=self.dataframe.drop(columns=[target_column])
        feature_columns=df.columns

        scaled_data=scaler.fit_transform(self.dataframe[feature_columns])

        scaled_dataframe=pd.DataFrame(scaled_data,columns=self.dataframe[feature_columns].columns)

        self.dataframe[feature_columns]=scaled_dataframe

        self.returnLogs.append(f'{method} scaling applied')

    def get_result(self) -> dict:
        context: dict = {}
        if self.dataframe is not None:
            context["dataframe"] = self.dataframe
            context["logs"] = self.returnLogs
            return context
        else:
            context["error"] = f"something went wrong!"
            return context
