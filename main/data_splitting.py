from sklearn.model_selection import train_test_split
import pandas as pd
import os
from django.conf import settings
from .purge import PurgeDirectory

class DataSplitter:
    def __init__(self, file_path: str, target_column) -> None:
        self.file_path = file_path
        self.target_column = target_column
        file_purger=PurgeDirectory(settings.TRAIN_FILES_UPLOAD_DIR,3)
        file_purger=PurgeDirectory(settings.TEST_FILES_UPLOAD_DIR,3)

        self.file_logs=file_purger.returnLogs()

    def __enter__(self):
        return self.split_data()

    def split_data(self):
        self.df = pd.read_csv(self.file_path)
        X = self.df.drop(self.target_column, axis=1)
        y = self.df[self.target_column]
        train_df, test_df = train_test_split(self.df, test_size=0.2, random_state=42)

        directory, filename = os.path.split(self.file_path)

        train_filename = filename.split(".")[0] + "_train." + filename.split(".")[1]
        test_filename = filename.split(".")[0] + "_test." + filename.split(".")[1]

        train_directory = os.path.join(os.path.dirname(directory), "train_files")
        train_path = os.path.join(train_directory, train_filename)
        train_path = os.path.abspath(train_path)

        test_directory = os.path.join(os.path.dirname(directory), "test_files")
        test_path = os.path.join(test_directory, test_filename)
        test_path = os.path.abspath(test_path)

        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        context={}
        context['train_path']=train_path
        context['test_path']=test_path
        context['file_logs']=self.file_logs
        return context

    def __exit__(self, exc_tb, exc_type, exc_value):
        pass
