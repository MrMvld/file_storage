from django.db import models
from django.contrib.auth.models import User


class FileUpload(models.Model):
    file_id = models.CharField(max_length=100, unique=True)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ActionLog(models.Model):
    ACTION_CHOICES = (('upload', 'Upload'), ('download', 'Download'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    file_id = models.CharField(max_length=100)