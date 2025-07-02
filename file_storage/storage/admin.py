from django.contrib import admin
from .models import FileUpload, ActionLog


admin.site.register(FileUpload)


admin.site.register(ActionLog)
