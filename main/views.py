from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse
from .forms import FileModelForm
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .data_prep_pipeline import DataPrep 
from .data_preprocessing_pipeline import DataPreprocessor
from .data_splitting import DataSplitter
from .purge import PurgeDirectory
import matplotlib.pyplot as plt 
import seaborn as sns
import io
import os
import joblib
# Create your views here.

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
                    with open('image_delte_logs.txt','a') as f:
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
    

def get_pairplot(request, image_path):
    with open(image_path,'rb') as f:
        iamge_data=f.read()
    return HttpResponse(iamge_data, content_type='image/png')

def analyze(request, file_path:str):
    
   
    if request.method=='POST':
        my_pipeline=DataPreprocessor(file_path)
        imputation_method=request.POST.get('imputation-method')
        encoding_method=request.POST.get('encoding-method')
        outlier_method=request.POST.get('outlier-method')
        scaling_method=request.POST.get('scaling-method')
       
        my_pipeline.handle_na(imputation_method)
        my_pipeline.handle_na('mode')
        if encoding_method == 'label-encoding':
            my_pipeline.label_encoding()
        elif encoding_method=='one-hot-encoding':
            my_pipeline.one_hot_encoding()
        my_pipeline.handle_outliers(outlier_method)
        if scaling_method is not None:
            my_pipeline.scale_data(scaling_method)
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

def get_csv(request, file_path):
    with open(file_path,'rb') as f:
        file_data=f.read()
    return HttpResponse(file_data, content_type='file/csv')

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
        if model_type=='linear regression':
            model=LinearRegression()
            model.fit(X_train,y_train)

            y_pred=model.predict(X_test)

            mae=mean_absolute_error(y_test,y_pred)
            mse=mean_squared_error(y_test,y_pred)
            rmse=mean_squared_error(y_test, y_pred, squared=False)
            r2=r2_score(y_test,y_pred)
            
            eval_metrics['Mean Square Error']=mse
            eval_metrics['Mean Absolute Error']=mae
            eval_metrics['Root Mean Square Error']=rmse
            eval_metrics['R2 Score']=r2
            saved_file=os.path.join(settings.BASE_DIR,'data\\modelsDump\\') +filename+'.joblib'
            joblib.dump(model, saved_file)
         
         
            y_true=y_test
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
            # Scatter plot of predicted vs. true values
            ax1.scatter(y_true, y_pred, color='blue', label='predicted vs actual')
            ax1.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], color='red', linestyle='--', label='perfect prediction')
            ax1.set_xlabel('True Values', fontsize=14)
            ax1.set_ylabel('Predicted Values', fontsize=14)
            ax1.set_title('Scatter Plot: Actual vs. Predicted Values', fontsize=16)
            ax1.tick_params(axis='both', labelsize=12)
            ax1.grid(True)
            ax1.legend(fontsize=12)
    
            # Box plot of predicted and true values
            sns.boxplot(data=[y_true, y_pred], ax=ax2, palette=['blue', 'red'])
            ax2.set_xlabel('Values', fontsize=14)
            ax2.set_ylabel('Distribution', fontsize=14)
            ax2.set_title('Box Plot: Actual vs. Predicted Values', fontsize=16)
            ax2.tick_params(axis='both', labelsize=12)
            ax2.grid(True)
            ax2.legend(['True Values', 'Predicted Values'], fontsize=12)
    
            plt.tight_layout()
            
            
            plot_name=os.path.join(settings.BASE_DIR,'images\\')+filename+"_scatterplot"+'.png'
            plt.savefig(plot_name)
            PurgeDirectory(os.path.join(settings.BASE_DIR,'images'),3)
        else:
            pass
        return render(request,'main/model.html',{'eval_metrics':eval_metrics,
                                         'file_path':saved_file,
                                         'plot_name':plot_name})








    except Exception as e:
        return render(request,'main/error.html',{'error':e})


def download_joblib(request, file_path):
    with open(file_path,'rb') as f:
        file_data=f.read()
    return HttpResponse(file_data, content_type='file/joblib')
    


    
