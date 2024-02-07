from django.shortcuts import render,redirect
from django.conf import settings
from django.http import HttpResponse
from .forms import FileModelForm
import pandas as pd
# from scripts.data_prep_pipeline import DataPrep
# from scripts.data_preprocessing_pipeline import DataPreprocessor 
# from scripts.data_splitting import  DataSplitter
# import scripts.constants as c

#from .scripts import data_prep_pipeline

from .data_prep_pipeline import DataPrep 
from .data_preprocessing_pipeline import DataPreprocessor
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
    # get saved file from path in file_path



    # pass saved path to data preprocessing script
    pass



