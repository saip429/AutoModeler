from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse
from .forms import FileModelForm
import pandas as pd


from .data_prep_pipeline import DataPrep 
from .data_preprocessing_pipeline import DataPreprocessor
from .data_splitting import DataSplitter
import io
import os
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
        standardize= True if request.POST.get('standardize') == 'yes' else False 
        my_pipeline.handle_na(imputation_method)
        my_pipeline.handle_na('mode')
        if encoding_method == 'label-encoding':
            my_pipeline.label_encoding()
        elif encoding_method=='one-hot-encoding':
            my_pipeline.one_hot_encoding()
        my_pipeline.handle_outliers(outlier_method)
        if standardize:
            my_pipeline.standardize_data()
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

        return render(request,'main/split.html',{'train_path':train_path,'test_path':test_path})
    return render(request,'main/split.html',{'file_path':file_path})

    


    
