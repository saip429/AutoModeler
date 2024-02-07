from django.db import models
from django.conf import settings
# Create your models here.

class FileModel(models.Model):
    file=models.FileField( upload_to= settings.FILES_UPLOAD_DIR , max_length=100)
    
