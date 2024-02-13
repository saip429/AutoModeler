# Auto Modeler
> Automatic tool to analyze, operate on, and train models on time series data  

## features    
* > Allows user to upload csv files and perform EDA operations  
* > Allows user to perform data preprocessing operations and download cleaned data  
* > Allows user to perform data splitting and download train and test datasets  
#### EDA Operations  
* Provide summary of the dataset (data elements datatype, number of entries and more)
* Provide number of outliers based on Z-Score
* Provide number of missing values  

#### Data preprocessing operations  
* Handle missing values by either dropping them or imputation with mean, median or mode  
* Encode data using label encoding or one hot encoding  
* Handle outleirs using splining or winsorizing  
* scale data with standard, MinMax and robust scaling

#### Model training  
Allows the user to train models on the cleaned data   

Available models:
* Linear Regression  
* XG Boost
* Support Vector Machine  
* Decision Tree Regressor  
* Logistic Regression
 

##  Docs    
withing main/ you will find-
* ### data_prep_pipeline.py:  
Script to perform EDA on files. Accepts .csv, .xls files. returns data summary, missing values, data types and other info.

* ### data_preprocessing_pipeline.py:  
Script to perform data preprocessing. Includes handling NaN values (imputation), handling outliers (splining, winsorizing), data encoding (label, One hot encoding), standardize data.   

* ### data_splitting.py:  
Script to split data into training, and testing, takes file path and target column as argument, returns file path of training and testing data .   

* ### views.py:  
Django views that include functions to train models

* ### purge.py:  
utility script for automatic file purge  
* ### images/:  
Image dump directory    
* ### data/:  
files dump directory   

### Run locally:  
* download requirements after cloning repository
> ####  pip install -m requirements.txt
* Run django app 
> #### python manage.py runserver



