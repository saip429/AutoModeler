from django import forms 
from .models import FileModel 

class FileModelForm(forms.ModelForm):
    class Meta:
        model=FileModel
        fields=['file']