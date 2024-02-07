# Auto ML   
> Automatic tool to analyze and operate on time series data  

## features  
### coming soon ...  

##  Docs  
* ### data_prep_pipeline.py:  
Script to perform EDA on files. Accepts .csv, .xls files. returns data summary, missing values, data types and other info. Use as a context manager

* ### data_preprocessing_pipeline.py:  
Script to perform data preprocessing. Includes handling NaN values (imputation), handling outliers (splining, winsorizing), data encoding (label, One hot encoding), standardize data. Use as a context manager     

* ### data_splitting.py:  
Script to split data into training, and testing, takes file path and target column as argument, returns file path of training and testing data . Use as a context manager

* ### utils/:  
utility scripts directory for automatic file purge  
* ### images/:  
Image dump directory  


