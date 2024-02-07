from django.urls import path 
from .views import *

urlpatterns = [
    path('',home, name='home'),
    path('get_pairplot/<str:image_path>/', get_pairplot, name='pairplot'),
    path('preprocess/<str:file_path>/', analyze, name='preprocess')
]
