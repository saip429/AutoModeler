from django.urls import path 
from .views import *

urlpatterns = [
    path('',home, name='home'),
    path('get_pairplot/<str:image_path>/', get_pairplot, name='pairplot'),
    path('preprocess/<str:file_path>/', analyze, name='preprocess'),
    path('get_csv/<str:file_path>/',get_csv, name='csv'),
    path('train-test-split/<str:file_path>/',train_test_split,name='split'),
    path('train-model/', train_model, name='train-model'),
    path('get-joblib/<str:file_path>/',download_joblib, name='get-joblib')
]
