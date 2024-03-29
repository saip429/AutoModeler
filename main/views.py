'''
views summary:
home(): render home page, accept file upload and save file to backend, call EDA pipeline and render results, serve pairplot
analyze(): perform data preprocessing, accept user parameters and render results, server cleaned data
train_test_split(): perform data splitting, serve split data
train_model(): train model as per user requirements, render train results, evaluation metrics and serve model as joblib file
'''

from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse
from .forms import FileModelForm
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, r2_score
from .data_prep_pipeline import DataPrep 
from .data_preprocessing_pipeline import DataPreprocessor
from .data_splitting import DataSplitter
from .purge import PurgeDirectory
import matplotlib.pyplot as plt  
import xgboost as xgb

import numpy as np    
import seaborn as sns
import io
import os
import joblib


def home(request):
    # take file from user 
    try:
        if request.method=='POST':
            form=FileModelForm(request.POST, request.FILES)
            if form.is_valid():
                file=request.FILES['file']

                if file.name.endswith('.csv'):
                    file=form.save()
                else:
                    # convert file to csv
                    pass
            
            
                # extract file location
                file_path=file.file.path
                #extract absolute path
                absolute_path=os.path.join(settings.BASE_DIR, file_path)

                #pass file to EDA tool
                
                my_pipeline=DataPrep(absolute_path)
                result_dict:dict=my_pipeline.get_result()
                dataframe=result_dict.get('dataframe').to_html()
                
                
                
                info=result_dict.get('info')
                
                outliers=result_dict.get('outliers')
                missing_values=result_dict.get('missing values')
                pairplot=result_dict.get('pairplot')
                summary=result_dict.get('summary').to_html()
               
                file_logs = result_dict.get('file_logs')
                image_logs=result_dict.get('image_logs')

                try:
                    with open('file_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)
                    with open('image_delete_logs.txt','a') as f:
                        for item in image_logs:
                            f.write("%s\n" % item)
                except Exception as e:
                    print("An error occurred while writing to the file:", e)

                return render(request,'main/second.html',{'name':absolute_path,
                                                          'info':info,
                                                        'summary':summary,
                                                          'pairplot':pairplot,
                                                      'dataframe':dataframe,
                                                      'outliers':outliers,
                                                      'missing_values':missing_values,
                                                      
                                                      })
            else:
                return render(request,'main/error.html',{'error':form})
    except Exception as e:
        return render(request,'main/error.html',{'error':e})
            
    else:
        form=FileModelForm()

        return render( request,'main/home.html',{'form':form})
    



def analyze(request, file_path:str):      
    if request.method=='POST':
        my_pipeline=DataPreprocessor(file_path)
        imputation_method=request.POST.get('imputation-method')
        encoding_method=request.POST.get('encoding-method')
        outlier_method=request.POST.get('outlier-method')
        scaling_method=request.POST.get('scaling-method')
        target_column=request.POST.get('target column')
       
        my_pipeline.handle_na(imputation_method)
        my_pipeline.handle_na('mode')
        if encoding_method == 'label-encoding':
            my_pipeline.label_encoding()
        elif encoding_method=='one-hot-encoding':
            my_pipeline.one_hot_encoding()
        my_pipeline.handle_outliers(outlier_method)
        if scaling_method != 'none':
            my_pipeline.scale_data(scaling_method,target_column)
        my_pipeline.save()
        result_dict=my_pipeline.get_result()
        
        dataframe=result_dict.get('dataframe').to_html()
        logs=result_dict.get('logs')
        error=result_dict.get('error')
        return render(request, 'main/analysis.html',{'file_path':file_path,
                                                   'dataframe':dataframe,
                                                   'logs':logs,
                                                   'error':error
                                                   })

    return render(request,'main/preprocessing.html',{'file_path':file_path})



def train_test_split(request, file_path):
     
    if request.method=='POST':
        target_column=request.POST.get('target')
        
        result_dict= DataSplitter(file_path,target_column).split_data()
        train_path=result_dict.get('train_path')
        test_path=result_dict.get('test_path')
        file_logs=result_dict.get('file_logs')
        with open('file_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)

        return render(request,'main/split.html',{'train_path':train_path,'test_path':test_path, 'file_path':file_path})
    return render(request,'main/split.html',{'file_path':file_path})



# train model 

def train_model(request):
    try:
        filename=request.POST.get('file_path')
        data=pd.read_csv(filename)
        filename=os.path.basename(filename)
        filename=filename.split('.')[0]
        train_path=request.POST.get('train_path')
        test_path=request.POST.get('test_path')
        model_type=request.POST.get('model-type')
        target_column=request.POST.get('target')
        train_data=pd.read_csv(train_path)
        test_data=pd.read_csv(test_path)
        X_train=train_data.drop(columns=[target_column])
        y_train=train_data[target_column]
        X_test=test_data.drop(columns=[target_column])
        y_test=test_data[target_column]
        
        saved_file=''
        eval_metrics:dict={}
        eval_metrics['model']=model_type
        if model_type=='linear regression':
            model=LinearRegression()
            model.fit(X_train,y_train)
            y_pred=model.predict(X_test)            
            mae=round(mean_absolute_error(y_true=y_test,y_pred=y_pred),2)        
            r2=round(r2_score(y_test,y_pred),2)        
            eval_metrics['Mean Absolute Error']=mae            
            eval_metrics['R2 Score']=r2
            saved_file=os.path.join(settings.BASE_DIR,'data\\modelsDump\\') +filename+'_linear_'+'.joblib'
            joblib.dump(model, saved_file)       
            y_true=y_test
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))         
            residuals = y_test - y_pred
           # Create a residual plot            
            ax1.scatter(y_pred, residuals, color='blue', alpha=0.5)
            ax1.axhline(y=0, color='red', linestyle='--')
            ax1.set_xlabel('Predicted Values')
            ax1.set_ylabel('Residuals')
            ax1.set_title('Residual Plot')        
            coefficients = model.coef_
            feature_names = data.columns             

            # Sort coefficients in descending order
            sorted_indices = coefficients.argsort()[::-1]
            sorted_coefficients = coefficients[sorted_indices]
            sorted_feature_names = feature_names[sorted_indices]

            # Create a bar plot of feature coefficients
            
            ax2.bar(sorted_feature_names, sorted_coefficients, color='blue')
            ax2.set_xlabel('Features')
            ax2.set_ylabel('Importance')
            ax2.set_title('Feature Importance Plot')
            ax2.set_xticklabels(sorted_feature_names,rotation=90)
            plt.show()    
            plt.tight_layout()
            plot_name=os.path.join(settings.BASE_DIR,'images\\')+filename+"_plot"+'.png'
            plt.savefig(plot_name)
            purger=PurgeDirectory(os.path.join(settings.BASE_DIR,'images'),3)
            file_logs=purger.logs
            with open('image_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)

        # Logistic regression
        elif model_type=='logistic regression':
            target_column_type=data[target_column].dtype
            if target_column_type in [float,int]:
                raise Exception('The target variable is likeley continious, can not use logistic regression')
            model=LogisticRegression()
            model.fit(X_train,y_train)
            y_pred=model.predict(X_test)            
            mae=round(mean_absolute_error(y_true=y_test,y_pred=y_pred),2)          
            r2=round(r2_score(y_test,y_pred),2)
            eval_metrics['Mean Absolute Error']=mae
            eval_metrics['R2 Score']=r2
            saved_file=os.path.join(settings.BASE_DIR,'data\\modelsDump\\') +filename+'_logistic_'+'.joblib'
            joblib.dump(model, saved_file)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))         
            residuals = y_test - y_pred

           # Create a residual plot            
            ax1.scatter(y_pred, residuals, color='blue', alpha=0.5)
            ax1.axhline(y=0, color='red', linestyle='--')
            ax1.set_xlabel('Predicted Values')
            ax1.set_ylabel('Residuals')
            ax1.set_title('Residual Plot')
            coefficients = model.coef_
            feature_names = data.columns             

            # Sort coefficients in descending order
            sorted_indices = coefficients.argsort()[::-1]
            sorted_coefficients = coefficients[sorted_indices]
            sorted_feature_names = feature_names[sorted_indices]

            # Create a bar plot of feature coefficients
            
            ax2.bar(sorted_feature_names, sorted_coefficients, color='blue')
            ax2.set_xlabel('Features')
            ax2.set_ylabel('Importance')
            ax2.set_title('Feature Importance Plot')
            ax2.set_xticklabels(sorted_feature_names,rotation=90)
            plt.show()
    
            plt.tight_layout()
            
            
            plot_name=os.path.join(settings.BASE_DIR,'images\\')+filename+"_plot"+'.png'
            plt.savefig(plot_name)
            purger=PurgeDirectory(os.path.join(settings.BASE_DIR,'images'),3)
            file_logs=purger.logs
            with open('image_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)
        
        # Decision Tree regressor
        elif model_type=='decision tree':
            model=DecisionTreeRegressor()
            model.fit(X_train,y_train)
            y_pred=model.predict(X_test)
            mae=round(mean_absolute_error(y_true=y_test,y_pred=y_pred),2)
            r2=round(r2_score(y_test,y_pred),2)
            eval_metrics['Mean Absolute Error']=mae
            eval_metrics['R2 score']=r2
            plot_name=None
            saved_file=os.path.join(settings.BASE_DIR,'data\\modelsDump\\') +filename+'_decisionTree_'+'.joblib'
            joblib.dump(model, saved_file)
        
        # XGBoost regression
        elif model_type=='XGBoost':
            model = xgb.XGBRegressor(objective ='reg:squarederror', colsample_bytree = 0.3, learning_rate = 0.1,
                max_depth = 5, alpha = 10, n_estimators = 10)
            model.fit(X_train,y_train)
            y_pred=model.predict(X_test)
            mae=round(mean_absolute_error(y_test,y_pred),2)
            r2=round(r2_score(y_test,y_pred),2)
            eval_metrics['Mean Absolute Error']=mae
            eval_metrics['R2 score']=r2
            saved_file=os.path.join(settings.BASE_DIR,'data\\modelsDump\\') +filename+'_XGBoost_'+'.joblib'
            joblib.dump(model, saved_file)
            plt.subplots( figsize=(12, 6))
            residuals = y_test - y_pred
           # Create a residual plot            
            plt.scatter(y_pred, residuals, color='blue', alpha=0.5)
            plt.axhline(y=0, color='red', linestyle='--')
            plt.xlabel('Predicted Values')
            plt.ylabel('Residuals')
            plt.title('Residual Plot')
            

            
            plt.show()
    
            plt.tight_layout()
            
            
            plot_name=os.path.join(settings.BASE_DIR,'images\\')+filename+"_plot"+'.png'
            plt.savefig(plot_name)
            purger=PurgeDirectory(os.path.join(settings.BASE_DIR,'images'),3)
            file_logs=purger.logs
            with open('image_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)

        elif model_type=='SVM':
            model = SVR(kernel='rbf', C=1.0, epsilon=0.1)
            model.fit(X_train,y_train)
            y_pred=model.predict(X_test)

            mae=round(mean_absolute_error(y_test,y_pred),2)
            r2=round(r2_score(y_test,y_pred),2)
            
            
            eval_metrics['Mean Absolute Error']=mae

            
            eval_metrics['R2 Score']=r2
            residuals = y_test - y_pred
            plt.scatter(y_pred, residuals)
            plt.xlabel("Predicted Values")
            plt.ylabel("Residuals")
            plt.title("Residual Plot")
            plt.axhline(y=0, color='k', linestyle='--')
            plt.show()
            plt.tight_layout()
            saved_file=os.path.join(settings.BASE_DIR,'data\\modelsDump\\') +filename+'_SVM_'+'.joblib'
            joblib.dump(model, saved_file)
            
            plot_name=os.path.join(settings.BASE_DIR,'images\\')+filename+"_plot"+'.png'
            plt.savefig(plot_name)
            purger=PurgeDirectory(os.path.join(settings.BASE_DIR,'images'),3)
            file_logs=purger.logs
            with open('image_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)

        else:
            raise ValueError(f'{model_type} is not a valid model')
        
        purger=PurgeDirectory(os.path.join(settings.BASE_DIR,'data\\modelsDump\\'),3)
        file_logs=purger.logs
        with open('file_delete_logs.txt', 'a') as f:
                        for item in file_logs:
                         f.write("%s\n" % item)
        return render(request,'main/model.html',{'eval_metrics':eval_metrics,
                                         'file_path':saved_file,
                                         'plot_name':plot_name})


        

    except Exception as e:
        return render(request,'main/error.html',{'error':e})
    
# UTILITY FUNCTIONS 

# serve pairplot
def get_pairplot(request, image_path):
    with open(image_path,'rb') as f:
        iamge_data=f.read()
    return HttpResponse(iamge_data, content_type='image/png')

# serve csv file
def get_csv(request, file_path):
    with open(file_path,'rb') as f:
        file_data=f.read()
    return HttpResponse(file_data, content_type='file/csv')

# serve trained model as joblib file
def download_joblib(request, file_path):
    with open(file_path,'rb') as f:
        file_data=f.read()
    return HttpResponse(file_data, content_type='file/joblib')
    


    
