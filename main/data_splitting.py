from sklearn.model_selection import train_test_split
import pandas as pd
import os


class DataSplitter:
    def __init__(self, file_path: str, target_column: str) -> None:
        self.file_path = file_path
        self.target_column = target_column

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

        return train_path, test_path

    def __exit__(self, exc_tb, exc_type, exc_value):
        pass
