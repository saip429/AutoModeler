"""
Test cases for data_prep_pipeline
cases tested:
1. reads csv file
2. reads excel (.xls, .xlsx) file
3. reads pdf file
4. invalid filetypes throw ValueError

"""

import os
import pandas as pd
import pytest
from data_prep_pipeline import DataPrep


CSV_FILE_PATH = os.path.abspath("sample_csv.csv")

EXCEL_FILE_PATH = os.path.abspath("sample_excel.xls")

PDF_FILE_PATH = os.path.abspath("sample_pdf.pdf")

ERROR_PATH = "errorpath.txt"


def test_read_csv():
    my_pipeline = DataPrep(CSV_FILE_PATH)
    # test weather data is being read as pandas dataframe
    assert isinstance(my_pipeline.df, pd.DataFrame)

    # check if df exists
    assert len(my_pipeline.df) > 0

    assert isinstance(my_pipeline.print_result(), dict)


def test_read_excel():
    my_pipeline = DataPrep(EXCEL_FILE_PATH)

    assert isinstance(my_pipeline.df, pd.DataFrame)

    assert len(my_pipeline.df) > 0

    assert isinstance(my_pipeline.print_result(), dict)


def test_read_pdf():
    my_pipeline = DataPrep(PDF_FILE_PATH)
    # check if not none
    assert my_pipeline.df is not None

    assert len(my_pipeline.df) > 0

    assert isinstance(my_pipeline.print_result(), dict)


def test_invalid_path():
    # check for invalid file type
    with pytest.raises(ValueError, match="unsupported file type: txt"):
        my_pipeline = DataPrep(ERROR_PATH)
